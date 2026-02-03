import uuid, json
from datetime import datetime
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from kafka import KafkaProducer
from shared.jwt_utils import verify_token
from .serializers import OrderCreateSerializer
from .models import Order, OrderItem, Location, OrderRoute, Payment
# from payments.models import Payment

producer = KafkaProducer(
    bootstrap_servers="kafka:9092",
    value_serializer=lambda v: json.dumps(v).encode()
)

class CreateOrder(APIView):
    def post(self, request):
        # 🔐 Auth
        token = request.headers["Authorization"].split()[1]
        jwt_payload = verify_token(token)

        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        with transaction.atomic():
            order = Order.objects.create(
                client_id=jwt_payload["client_id"],
                customer_name=data["customer"]["name"],
                customer_phone=data["customer"]["phone"],
                status="CREATED"
            )

            for item in data["items"]:
                OrderItem.objects.create(order=order, **item)

            pickup = Location.objects.create(**data["pickup"])
            drop = Location.objects.create(**data["drop"])

            OrderRoute.objects.create(
                order=order,
                pickup=pickup,
                drop=drop
            )

            Payment.objects.create(
                order=order,
                method=data["payment"]["method"],
                amount=data["payment"]["amount"],
                cash_to_collect=data["payment"]["amount"]
                if data["payment"]["method"] == "COD" else 0,
                status="PENDING"
            )

        # 📢 Emit ORDER_CREATED event
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": "ORDER_CREATED",
            "client_id": jwt_payload["client_id"],
            "auth_token": token,
            "timestamp": datetime.utcnow().isoformat(),
            "correlation_id": str(uuid.uuid4()),
            "payload": {
                "order_id": str(order.id),
                "pickup": data["pickup"],
                "drop": data["drop"]
            }
        }

        producer.send("order.events", event)

        return Response(
            {
                "order_id": order.id,
                "status": "CREATED"
            },
            status=status.HTTP_201_CREATED
        )
