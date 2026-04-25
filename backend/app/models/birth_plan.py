from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class DeliveryFacilityType(str, Enum):
    phc = "PHC"
    chc = "CHC"
    fru = "FRU"
    dh = "DH"
    medical_college = "Medical_College"


class TransportMode(str, Enum):
    mode_102 = "102"
    mode_108 = "108"
    private = "private"
    community = "community"


class BirthPlanStatus(str, Enum):
    draft = "draft"
    confirmed = "confirmed"
    updated = "updated"
    executed = "executed"


class BirthPlan(SQLModel, table=True):
    birth_plan_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    pregnancy_id: UUID = Field(index=True)
    delivery_facility_id: str
    delivery_facility_type: DeliveryFacilityType
    edd_confirmed_date: date
    transport_mode: TransportMode
    transport_confirmed_by: Optional[str] = None
    emergency_contact_1_name: str
    emergency_contact_1_phone: str
    emergency_contact_2_name: Optional[str] = None
    emergency_contact_2_phone: Optional[str] = None
    blood_donor_arranged: bool
    blood_group: Optional[str] = None
    birth_plan_status: BirthPlanStatus = BirthPlanStatus.draft
    birth_plan_created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    birth_plan_updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
