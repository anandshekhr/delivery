from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
import os
import uuid
import json
from datetime import datetime
from django.utils import timezone
from shared.jwt_utils import verify_jwt
from shared.event_schema import EventEnvelope
from .models import Delivery, DeliveryOTP
from rest_framework import status
from .utils import generate_otp, hash_otp, otp_expiry_time
# from kafka import KafkaProducer


# producer = KafkaProducer(bootstrap_servers=os.environ['KAFKA_BOOTSTRAP_SERVERS'],
#                            value_serializer=lambda v: json.dumps(v).encode('utf-8'))

class CompleteDelivery(APIView):

    def post(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response({"error": "Authorization required"}, status=401)

        token = auth_header.split(" ")[1]

        try:
            decoded = verify_jwt(token)
        except Exception as e:
            return Response({"error": str(e)}, status=401)

        client_id = decoded["client_id"]

        event = EventEnvelope(
            event_id=str(uuid.uuid4()),
            event_type="delivery.completed",
            client_id=uuid.UUID(client_id),
            auth_token=token,
            correlation_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            payload=request.data,
            source="delivery_service"
        )

        # producer.send('delivery.events', event.dict())
        # producer.flush()

        return Response({'status': 'published'}, status=200)


class AssignDelivery(APIView):
    def post(self, request):
        token = request.headers["Authorization"].split()[1]
        payload = verify_jwt(token)

        order_id = request.data["order_id"]
        delivery_partner_id = request.data["delivery_partner_id"]

        delivery = Delivery.objects.create(
            order_id=order_id,
            delivery_partner_id=delivery_partner_id,
            status="ASSIGNED"
        )

        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": "DELIVERY_ASSIGNED",
            "client_id": payload["client_id"],
            "auth_token": token,
            "timestamp": datetime.utcnow().isoformat(),
            "correlation_id": str(uuid.uuid4()),
            "payload": {
                "order_id": order_id,
                "delivery_partner_id": delivery_partner_id
            }
        }

        # producer.send("delivery.events", event)
        return Response({"status": "assigned"})

class RespondDelivery(APIView):
    def post(self, request):
        token = request.headers["Authorization"].split()[1]
        payload = verify_jwt(token)

        order_id = request.data["order_id"]
        action = request.data["action"]  # ACCEPT / REJECT
        reason = request.data.get("reason")

        delivery = Delivery.objects.get(order_id=order_id)

        if action == "ACCEPT":
            delivery.status = "ACCEPTED"
            event_type = "DELIVERY_ACCEPTED"
        else:
            delivery.status = "REJECTED"
            event_type = "DELIVERY_REJECTED"

        delivery.save()

        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "client_id": payload["client_id"],
            "auth_token": token,
            "timestamp": datetime.utcnow().isoformat(),
            "correlation_id": str(uuid.uuid4()),
            "payload": {
                "order_id": order_id,
                "delivery_partner_id": delivery.delivery_partner_id,
                "reason": reason
            }
        }

        # producer.send("delivery.events", event)
        return Response({"status": event_type})

class VerifyOTP(APIView):
    def post(self, request):
        order_id = request.data["order_id"]
        otp = request.data["otp"]

        otp_obj = DeliveryOTP.objects.get(order_id=order_id)

        if otp_obj.verified:
            return Response({"error": "Already verified"}, status=400)

        if otp_obj.otp != otp:
            return Response({"error": "Invalid OTP"}, status=400)

        otp_obj.verified = True
        otp_obj.save()

        Delivery.objects.filter(order_id=order_id).update(status="COMPLETED")

        return Response({"status": "Delivered"})

class GenerateDeliveryOTP(APIView):
    def post(self, request):
        # 🔐 Auth
        token = request.headers["Authorization"].split()[1]
        payload = verify_jwt(token)

        order_id = request.data.get("order_id")

        delivery = Delivery.objects.filter(order_id=order_id).first()
        if not delivery:
            return Response(
                {"error": "Delivery not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if delivery.status not in ["ACCEPTED", "IN_PROGRESS"]:
            return Response(
                {"error": "OTP not allowed in current state"},
                status=status.HTTP_400_BAD_REQUEST
            )

        otp = generate_otp()
        otp_hashed = hash_otp(otp)

        otp_obj, _ = DeliveryOTP.objects.update_or_create(
            order_id=delivery.order_id,
            defaults={
                "otp_hash": otp_hashed,
                "expires_at": otp_expiry_time(),
                "attempts": 0,
                "verified": False,
            }
        )

        # 🔔 Emit OTP GENERATED event
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": "DELIVERY_OTP_GENERATED",
            "client_id": payload["client_id"],
            "auth_token": token,
            "timestamp": timezone.now().isoformat(),
            "correlation_id": str(uuid.uuid4()),
            "payload": {
                "order_id": str(order_id),
                "expires_at": otp_obj.expires_at.isoformat()
            }
        }

        # producer.send("delivery.events", event)

        # 📲 Send OTP (mock – integrate SMS/WhatsApp here)
        print(f"📩 OTP for order {order_id}: {otp}")

        return Response({
            "status": "OTP_SENT",
            "expires_in_seconds": 300
        })