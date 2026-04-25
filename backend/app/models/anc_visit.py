from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class TTVaccinationStatus(str, Enum):
    tt1_given = "TT1_given"
    tt2_given = "TT2_given"
    booster = "booster"
    not_due = "not_due"
    refused = "refused"


class UrineScale(str, Enum):
    nil = "nil"
    trace = "trace"
    one_plus = "1+"
    two_plus = "2+"
    three_plus = "3+"
    four_plus = "4+"


class FetalPresentation(str, Enum):
    cephalic = "cephalic"
    breech = "breech"
    transverse = "transverse"
    other = "other"


class LabStatus(str, Enum):
    negative = "negative"
    positive = "positive"
    pending = "pending"
    declined = "declined"


class ANCVisit(SQLModel, table=True):
    visit_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    pregnancy_id: UUID = Field(index=True)
    visit_date: date
    gestational_age_weeks: int
    facility_id: Optional[str] = None
    recorded_by_user_id: str
    bp_systolic: int
    bp_diastolic: int
    weight_kg: float
    hb_gdl: float
    fundal_height_cm: Optional[int] = None
    fetal_heart_rate_bpm: Optional[int] = None
    fetal_presentation: Optional[FetalPresentation] = None
    urine_albumin: UrineScale
    urine_sugar: UrineScale
    hiv_status: Optional[LabStatus] = None
    syphilis_rpr_result: Optional[LabStatus] = None
    gdm_ogtt_2hr_pg_mgdl: Optional[float] = None
    tsh_miul: Optional[float] = None
    ft4_low: Optional[bool] = None
    convulsions_documented: bool = False
    tt_vaccination: TTVaccinationStatus
    next_anc_due_date: date
    hrp_engine_run: bool = False
    hrp_flags_triggered: str = "[]"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
