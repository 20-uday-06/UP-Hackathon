from typing import Optional

from pydantic import BaseModel, Field

from app.models.referral import ReferralOutcome, ReferralStatus, UrgencyLevel


class ReferralCreate(BaseModel):
    pregnancy_id: str
    initiated_by_user_id: str = Field(min_length=2)
    referral_reason: str = Field(min_length=3)
    urgency_level: UrgencyLevel
    origin_facility_id: str = Field(min_length=2)
    destination_facility_id: str = Field(min_length=2)


class ReferralStageUpdate(BaseModel):
    actor_user_id: str = Field(min_length=2)
    stage: str = Field(min_length=2)
    ambulance_id: Optional[str] = None
    admission_id: Optional[str] = None
    outcome: Optional[ReferralOutcome] = None


class ReferralRead(BaseModel):
    referral_id: str
    pregnancy_id: str
    referral_reason: str
    urgency_level: UrgencyLevel
    referral_status: ReferralStatus
    ambulance_id: Optional[str] = None
    admission_id: Optional[str] = None
    outcome: Optional[ReferralOutcome] = None
