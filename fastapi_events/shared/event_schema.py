from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime
from uuid import UUID

class EventEnvelope(BaseModel):
    event_id: UUID = Field(..., description="Unique identifier for the event")
    event_type: str = Field(..., description="Type of the event")
    client_id: UUID
    auth_token: str
    correlation_id: Optional[UUID] = Field(None, description="Correlation ID for tracing the event")
    timestamp: datetime = Field(..., description="Timestamp when the event was created")
    payload: Dict = Field(..., description="Payload of the event")
    source: Optional[str] = Field(None, description="Source of the event")