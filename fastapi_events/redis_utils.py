import redis

r = redis.Redis(host='redis', port=6379, db=2)
def is_duplicate(event_id: str) -> bool:
    """Check if the event ID already exists in Redis."""
    return r.get("processed_events", event_id) is not None

def mark_as_processed(event_id: str, expiration: int = 3600):
    """Mark the event ID as processed by adding it to Redis with an expiration time."""
    r.setex("processed_events", expiration, event_id, 1)