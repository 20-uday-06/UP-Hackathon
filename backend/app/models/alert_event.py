from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class AlertType(str, Enum):
    hrp_flag = "hrp_flag"
    hrp_30_day = "hrp_30_day"
    anc_due = "anc_due"
    anc_missed = "anc_missed"
    referral = "referral"


class AlertStatus(str, Enum):
    pending = "pending"
    acknowledged = "acknowledged"
    escalated = "escalated"


class AlertEvent(SQLModel, table=True):
    alert_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    pregnancy_id: UUID = Field(index=True)
    alert_type: AlertType
    stakeholder_type: str
    stakeholder_id: str
    message: str
    status: AlertStatus = AlertStatus.pending
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    acknowledged_at: Optional[datetime] = None
    acknowledged_by_user_id: Optional[str] = None
    escalated_at: Optional[datetime] = None
