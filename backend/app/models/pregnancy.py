from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class RegistrationSource(str, Enum):
    self_registered = "self"
    asha = "asha"
    anm = "anm"
    anganwadi = "anganwadi"
    panchayat = "panchayat"
    other = "other"


class PregnancyStatus(str, Enum):
    active = "active"
    delivered = "delivered"
    lost_to_followup = "lost_to_followup"
    deceased = "deceased"


class Pregnancy(SQLModel, table=True):
    pregnancy_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    beneficiary_name: str
    age: int
    husband_name: str
    mobile_primary: str
    mobile_alternate: Optional[str] = None
    address_village_ward: str
    address_block: str
    address_district: str
    lmp_date: date
    edd_date: date
    aadhaar_masked: Optional[str] = None
    abha_id: Optional[str] = None
    rch_id: Optional[str] = None
    assigned_asha_id: Optional[str] = None
    assigned_anm_id: Optional[str] = None
    assigned_subcentre_id: Optional[str] = None
    assigned_chc_id: Optional[str] = None
    registration_source: RegistrationSource
    hrp_flag: bool = False
    hrp_conditions: str = "[]"
    previous_lscs: bool = False
    placenta_previa: bool = False
    boh_positive: bool = False
    rh_negative: bool = False
    twin_multiple: bool = False
    systemic_illness_description: Optional[str] = None
    status: PregnancyStatus = PregnancyStatus.active
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
