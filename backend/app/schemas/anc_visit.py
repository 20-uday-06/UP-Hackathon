from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models.anc_visit import (
    FetalPresentation,
    LabStatus,
    TTVaccinationStatus,
    UrineScale,
)


class ANCVisitCreate(BaseModel):
    pregnancy_id: str
    visit_date: date
    facility_id: Optional[str] = None
    recorded_by_user_id: str = Field(min_length=2)
    bp_systolic: int = Field(ge=60, le=260)
    bp_diastolic: int = Field(ge=40, le=180)
    weight_kg: float = Field(ge=20, le=250)
    hb_gdl: float = Field(ge=1, le=25)
    fundal_height_cm: Optional[int] = Field(default=None, ge=1, le=80)
    fetal_heart_rate_bpm: Optional[int] = Field(default=None, ge=40, le=220)
    fetal_presentation: Optional[FetalPresentation] = None
    urine_albumin: UrineScale
    urine_sugar: UrineScale
    hiv_status: Optional[LabStatus] = None
    syphilis_rpr_result: Optional[LabStatus] = None
    gdm_ogtt_2hr_pg_mgdl: Optional[float] = Field(default=None, ge=20, le=800)
    tsh_miul: Optional[float] = Field(default=None, ge=0.01, le=100)
    ft4_low: Optional[bool] = None
    convulsions_documented: bool = False
    tt_vaccination: TTVaccinationStatus
    next_anc_due_date: date

    @field_validator("visit_date")
    @classmethod
    def validate_visit_date(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("visit_date cannot be in the future")
        return value


class ANCVisitRead(BaseModel):
    visit_id: str
    pregnancy_id: str
    visit_date: date
    gestational_age_weeks: int
    hb_gdl: float
    bp_systolic: int
    bp_diastolic: int
    hrp_engine_run: bool
    hrp_flags_triggered: list[str]
