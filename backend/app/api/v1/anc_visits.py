from datetime import date, datetime, timezone
from uuid import UUID
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db.session import get_session
from app.models.alert_event import AlertType
from app.models.anc_visit import ANCVisit
from app.models.pregnancy import Pregnancy
from app.schemas.anc_visit import ANCVisitCreate, ANCVisitRead
from app.services.alerts import create_stakeholder_alerts
from app.services.audit import write_audit_event
from app.services.hrp_engine import evaluate_hrp

router = APIRouter(prefix="/anc-visits", tags=["anc-visits"])


def _weeks_between(start: date, end: date) -> int:
    return max(0, (end - start).days // 7)


@router.post("", response_model=ANCVisitRead, status_code=201)
def create_anc_visit(
    payload: ANCVisitCreate,
    session: Session = Depends(get_session),
) -> ANCVisitRead:
    try:
        pregnancy_uuid = UUID(payload.pregnancy_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid pregnancy_id") from exc

    pregnancy = session.get(Pregnancy, pregnancy_uuid)
    if not pregnancy:
        raise HTTPException(status_code=404, detail="pregnancy not found")

    gestational_age_weeks = _weeks_between(pregnancy.lmp_date, payload.visit_date)

    visit = ANCVisit(
        pregnancy_id=pregnancy_uuid,
        visit_date=payload.visit_date,
        gestational_age_weeks=gestational_age_weeks,
        facility_id=payload.facility_id,
        recorded_by_user_id=payload.recorded_by_user_id,
        bp_systolic=payload.bp_systolic,
        bp_diastolic=payload.bp_diastolic,
        weight_kg=payload.weight_kg,
        hb_gdl=payload.hb_gdl,
        fundal_height_cm=payload.fundal_height_cm,
        fetal_heart_rate_bpm=payload.fetal_heart_rate_bpm,
        fetal_presentation=payload.fetal_presentation,
        urine_albumin=payload.urine_albumin,
        urine_sugar=payload.urine_sugar,
        hiv_status=payload.hiv_status,
        syphilis_rpr_result=payload.syphilis_rpr_result,
        gdm_ogtt_2hr_pg_mgdl=payload.gdm_ogtt_2hr_pg_mgdl,
        tsh_miul=payload.tsh_miul,
        ft4_low=payload.ft4_low,
        convulsions_documented=payload.convulsions_documented,
        tt_vaccination=payload.tt_vaccination,
        next_anc_due_date=payload.next_anc_due_date,
    )

    evaluation = evaluate_hrp(pregnancy, visit)
    visit.hrp_engine_run = True
    visit.hrp_flags_triggered = json.dumps(evaluation.conditions)

    old_conditions = json.loads(pregnancy.hrp_conditions)
    merged_conditions = sorted(set(old_conditions + evaluation.conditions))

    if evaluation.hrp_flag:
        pregnancy.hrp_flag = True
        pregnancy.hrp_conditions = json.dumps(merged_conditions)
        pregnancy.updated_at = datetime.now(timezone.utc)

        create_stakeholder_alerts(
            session=session,
            pregnancy=pregnancy,
            alert_type=AlertType.hrp_flag,
            message=(
                f"HRP flagged for pregnancy {pregnancy.pregnancy_id}. "
                f"Conditions: {', '.join(evaluation.conditions)}"
            ),
            stakeholders=[
                ("beneficiary", pregnancy.mobile_primary),
                ("asha", pregnancy.assigned_asha_id or "unassigned_asha"),
                ("anm", pregnancy.assigned_anm_id or "unassigned_anm"),
                ("mo", pregnancy.assigned_chc_id or "unassigned_mo"),
            ],
        )

    session.add(visit)
    session.add(pregnancy)
    write_audit_event(
        session=session,
        entity_name="anc_visit",
        entity_id=str(visit.visit_id),
        action="create",
        actor_user_id=payload.recorded_by_user_id,
        actor_role="health_worker",
        old_values={},
        new_values={
            "pregnancy_id": str(visit.pregnancy_id),
            "hrp_flags_triggered": evaluation.conditions,
        },
    )
    session.commit()
    session.refresh(visit)

    return ANCVisitRead(
        visit_id=str(visit.visit_id),
        pregnancy_id=str(visit.pregnancy_id),
        visit_date=visit.visit_date,
        gestational_age_weeks=visit.gestational_age_weeks,
        hb_gdl=visit.hb_gdl,
        bp_systolic=visit.bp_systolic,
        bp_diastolic=visit.bp_diastolic,
        hrp_engine_run=visit.hrp_engine_run,
        hrp_flags_triggered=json.loads(visit.hrp_flags_triggered),
    )
