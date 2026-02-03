from fastapi import FastAPI, Header, HTTPException
from kafka import KafkaProducer
import time, json, uuid
from redis_utils import r
from models import LocationPayload
from shared.jwt_utils import verify_jwt
app= FastAPI()

producer = KafkaProducer(
    bootstrap_servers="kafka:9092",
    value_serializer=lambda v: json.dumps(v).encode()
)

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/tracking/location")
def update_location(
    data: LocationPayload,
    authorization: str = Header(...)
):
    token = authorization.split()[1]
    payload = verify_jwt(token)

    redis_key = f"delivery:location:{data.order_id}"

    r.hmset(redis_key, {
        "lat": data.lat,
        "lng": data.lng,
        "speed": data.speed or 0,
        "updated_at": int(time.time())
    })
    r.expire(redis_key, 60)

    event = {
        "event_id": str(uuid.uuid4()),
        "event_type": "DELIVERY_LOCATION_UPDATE",
        "client_id": payload["client_id"],
        "auth_token": token,
        "timestamp": time.time(),
        "correlation_id": str(uuid.uuid4()),
        "payload": data.dict()
    }

    producer.send("delivery.events", event)
    return {"status": "location_updated"}


@app.get("/tracking/order/{order_id}")
def get_order_location(order_id: str):
    redis_key = f"delivery:location:{order_id}"
    data = r.hgetall(redis_key)

    if not data:
        raise HTTPException(status_code=404, detail="Location not available")

    return {
        "lat": float(data[b"lat"]),
        "lng": float(data[b"lng"]),
        "speed": float(data[b"speed"]),
        "updated_at": int(data[b"updated_at"])
    }
