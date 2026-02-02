from shared.jwt_utils import verify_jwt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
import os
import uuid
import json
from datetime import datetime
from shared.event_schema import EventEnvelope
from kafka import KafkaProducer


producer = KafkaProducer(bootstrap_servers=os.environ['KAFKA_BOOTSTRAP_SERVERS'],
                           value_serializer=lambda v: json.dumps(v).encode('utf-8'))

class CompleteDelivery(APIView):

    def post(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response({"error": "Authorization required"}, status=401)

        token = auth_header.split(" ")[1]

        try:
            decoded = verify_jwt(token)
            print("Decoded JWT:", decoded)
        except Exception as e:
            return Response({"error": str(e)}, status=401)

        client_id = decoded["client_id"]

        event = EventEnvelope(
            event_id=uuid.uuid4(),
            event_type="delivery.completed",
            client_id=uuid.UUID(client_id),
            auth_token=request.auth,  # raw token used for the request
            correlation_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            payload=request.data,
            source="delivery_service"
        )

        producer.send('delivery.events', event.dict())
        producer.flush()

        return Response({'status': 'published'}, status=200)
