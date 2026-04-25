from datetime import date, timedelta
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models.pregnancy import PregnancyStatus, RegistrationSource


class PregnancyCreate(BaseModel):
    beneficiary_name: str = Field(min_length=2)
    age: int = Field(ge=10, le=60)
    husband_name: str = Field(min_length=2)
    mobile_primary: str = Field(min_length=10, max_length=20)
    mobile_alternate: Optional[str] = Field(default=None, min_length=10, max_length=20)
    address_village_ward: str = Field(min_length=2)
    address_block: str = Field(min_length=2)
    address_district: str = Field(min_length=2)
    lmp_date: date
    aadhaar_masked: Optional[str] = None
    abha_id: Optional[str] = None
    rch_id: Optional[str] = None
    registration_source: RegistrationSource
    previous_lscs: bool = False
    placenta_previa: bool = False
    boh_positive: bool = False
    rh_negative: bool = False
    twin_multiple: bool = False
    systemic_illness_description: Optional[str] = None

    @field_validator("lmp_date")
    @classmethod
    def validate_lmp_date(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("lmp_date cannot be in the future")
        return value


class PregnancyRead(BaseModel):
    pregnancy_id: str
    beneficiary_name: str
    age: int
    husband_name: str
    mobile_primary: str
    address_village_ward: str
    address_block: str
    address_district: str
    lmp_date: date
    edd_date: date
    registration_source: RegistrationSource
    hrp_flag: bool
    hrp_conditions: list[str]
    status: PregnancyStatus


class PregnancyHrpResolutionRequest(BaseModel):
    actor_user_id: str = Field(min_length=2)
    actor_role: str = Field(min_length=2)
    clear_conditions: list[str] = Field(default_factory=list)
    resolution_note: Optional[str] = None


def calculate_edd(lmp_date: date) -> date:
    return lmp_date + timedelta(days=280)
