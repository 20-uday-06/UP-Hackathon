from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class UrgencyLevel(str, Enum):
    routine = "routine"
    urgent = "urgent"
    emergency = "emergency"


class ReferralStatus(str, Enum):
    open = "open"
    in_transit = "in_transit"
    admitted = "admitted"
    closed = "closed"
    escalated = "escalated"


class ReferralOutcome(str, Enum):
    delivered = "delivered"
    transferred_again = "transferred_again"
    maternal_death = "maternal_death"
    fetal_death = "fetal_death"
    other = "other"


class Referral(SQLModel, table=True):
    referral_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    pregnancy_id: UUID = Field(index=True)
    initiated_by_user_id: str
    referral_reason: str
    urgency_level: UrgencyLevel
    origin_facility_id: str
    destination_facility_id: str
    clinical_summary_shared: bool = False
    clinical_summary_shared_timestamp: Optional[datetime] = None
    facility_ack_timestamp: Optional[datetime] = None
    doctor_viewed_timestamp: Optional[datetime] = None
    ambulance_id: Optional[str] = None
    dispatch_timestamp: Optional[datetime] = None
    pickup_timestamp: Optional[datetime] = None
    arrival_timestamp: Optional[datetime] = None
    admission_id: Optional[str] = None
    admission_timestamp: Optional[datetime] = None
    outcome: Optional[ReferralOutcome] = None
    referral_status: ReferralStatus = ReferralStatus.open
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
