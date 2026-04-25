from datetime import datetime

from pydantic import BaseModel, Field

from app.models.alert_event import AlertStatus, AlertType


class AlertRead(BaseModel):
    alert_id: str
    pregnancy_id: str
    alert_type: AlertType
    stakeholder_type: str
    stakeholder_id: str
    message: str
    status: AlertStatus
    created_at: datetime
    acknowledged_at: datetime | None = None
    escalated_at: datetime | None = None


class AlertAcknowledgeRequest(BaseModel):
    actor_user_id: str = Field(min_length=2)
