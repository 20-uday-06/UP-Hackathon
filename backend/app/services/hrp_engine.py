from dataclasses import dataclass

from app.models.anc_visit import ANCVisit, FetalPresentation, LabStatus, UrineScale
from app.models.pregnancy import Pregnancy


@dataclass
class HRPEvaluationResult:
    hrp_flag: bool
    conditions: list[str]


def evaluate_hrp(pregnancy: Pregnancy, visit: ANCVisit) -> HRPEvaluationResult:
    """Evaluate high-risk pregnancy conditions based on available data."""
    conditions: list[str] = []

    if visit.hb_gdl < 7:
        conditions.append("HRP-001")

    if visit.bp_systolic >= 140 and visit.bp_diastolic >= 90:
        conditions.append("HRP-002")

    if (
        visit.bp_systolic >= 140
        and visit.bp_systolic < 160
        and visit.bp_diastolic >= 90
        and visit.bp_diastolic < 110
        and visit.urine_albumin
        in {
            UrineScale.trace,
            UrineScale.one_plus,
            UrineScale.two_plus,
            UrineScale.three_plus,
            UrineScale.four_plus,
        }
    ):
        conditions.append("HRP-003")

    if (
        visit.bp_systolic >= 160
        and visit.bp_diastolic >= 110
        and visit.urine_albumin in {UrineScale.three_plus, UrineScale.four_plus}
    ):
        conditions.append("HRP-004")

    if (
        visit.convulsions_documented
        and visit.bp_systolic >= 140
        and visit.bp_diastolic >= 90
        and visit.urine_albumin
        in {
            UrineScale.one_plus,
            UrineScale.two_plus,
            UrineScale.three_plus,
            UrineScale.four_plus,
        }
    ):
        conditions.append("HRP-005")

    if visit.hiv_status == LabStatus.positive:
        conditions.append("HRP-006")

    if visit.syphilis_rpr_result == LabStatus.positive:
        conditions.append("HRP-007")

    if visit.gdm_ogtt_2hr_pg_mgdl is not None and visit.gdm_ogtt_2hr_pg_mgdl >= 140:
        conditions.append("HRP-008")

    if visit.tsh_miul is not None and visit.ft4_low is False and 2.5 <= visit.tsh_miul <= 10:
        conditions.append("HRP-009")

    if visit.tsh_miul is not None and (
        visit.tsh_miul > 10 or (visit.ft4_low is True and visit.tsh_miul > 2.5)
    ):
        conditions.append("HRP-010")

    if pregnancy.age < 20:
        conditions.append("HRP-011")

    if pregnancy.age > 35:
        conditions.append("HRP-012")

    if pregnancy.twin_multiple:
        conditions.append("HRP-013")

    if visit.fetal_presentation in {
        FetalPresentation.breech,
        FetalPresentation.transverse,
        FetalPresentation.other,
    }:
        conditions.append("HRP-014")

    if pregnancy.previous_lscs:
        conditions.append("HRP-015")

    if pregnancy.placenta_previa:
        conditions.append("HRP-016")

    if pregnancy.boh_positive:
        conditions.append("HRP-017")

    if pregnancy.rh_negative:
        conditions.append("HRP-018")

    if pregnancy.systemic_illness_description:
        conditions.append("HRP-019")

    if (
        visit.gestational_age_weeks >= 20
        and visit.fundal_height_cm is not None
        and visit.fundal_height_cm < (visit.gestational_age_weeks - 3)
    ):
        conditions.append("HRP-020")

    conditions = sorted(set(conditions))

    return HRPEvaluationResult(hrp_flag=len(conditions) > 0, conditions=conditions)
