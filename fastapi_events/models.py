from pydantic import BaseModel

class LocationPayload(BaseModel):
    order_id: str
    lat: float
    lng: float
    speed: float | None = None