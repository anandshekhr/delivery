import json
from kafka import KafkaConsumer
from shared.jwt_utils import verify_jwt
from redis_utils import is_duplicate, mark_as_processed

consumer = KafkaConsumer(
    'delivery.events',
    bootstrap_servers='kafka:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

for msg in consumer:
    event = msg.value
    event_id = event.get('event_id')
    auth_token = event.get('auth_token')

    if is_duplicate(event_id):
        print(f"Duplicate event {event_id} skipped.")
        continue

    try:
        decoded_token = verify_jwt(auth_token)
        print(f"Processed event {event_id} for client {decoded_token['client_id']}.")
        mark_as_processed(event_id)
    except ValueError as e:
        print(f"Failed to verify token for event {event_id}: {str(e)}")