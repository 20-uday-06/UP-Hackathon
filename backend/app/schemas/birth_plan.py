from datetime import date
from typing import Optional

from pydantic import BaseModel, Field

from app.models.birth_plan import BirthPlanStatus, DeliveryFacilityType, TransportMode


class BirthPlanCreate(BaseModel):
    pregnancy_id: str
    delivery_facility_id: str = Field(min_length=2)
    delivery_facility_type: DeliveryFacilityType
    edd_confirmed_date: date
    transport_mode: TransportMode
    transport_confirmed_by: Optional[str] = None
    emergency_contact_1_name: str = Field(min_length=2)
    emergency_contact_1_phone: str = Field(min_length=10, max_length=20)
    emergency_contact_2_name: Optional[str] = None
    emergency_contact_2_phone: Optional[str] = Field(default=None, min_length=10, max_length=20)
    blood_donor_arranged: bool
    blood_group: Optional[str] = None


class BirthPlanRead(BaseModel):
    birth_plan_id: str
    pregnancy_id: str
    delivery_facility_id: str
    delivery_facility_type: DeliveryFacilityType
    transport_mode: TransportMode
    emergency_contact_1_name: str
    emergency_contact_1_phone: str
    birth_plan_status: BirthPlanStatus
