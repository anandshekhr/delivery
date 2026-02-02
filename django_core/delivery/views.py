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
    # Use JWTAuthentication
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # request.user is already populated by JWTAuthentication
        client_id = str(request.user.id)  # assuming user.id contains client_id

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
