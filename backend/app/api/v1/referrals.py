from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db.session import get_session
from app.models.referral import Referral, ReferralStatus
from app.schemas.referral import ReferralCreate, ReferralRead, ReferralStageUpdate
from app.services.audit import write_audit_event

router = APIRouter(prefix="/referrals", tags=["referrals"])


@router.post("", response_model=ReferralRead, status_code=201)
def create_referral(
    payload: ReferralCreate,
    session: Session = Depends(get_session),
) -> ReferralRead:
    try:
        pregnancy_uuid = UUID(payload.pregnancy_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid pregnancy_id") from exc

    referral = Referral(
        pregnancy_id=pregnancy_uuid,
        initiated_by_user_id=payload.initiated_by_user_id,
        referral_reason=payload.referral_reason,
        urgency_level=payload.urgency_level,
        origin_facility_id=payload.origin_facility_id,
        destination_facility_id=payload.destination_facility_id,
        clinical_summary_shared=True,
        clinical_summary_shared_timestamp=datetime.now(timezone.utc),
        referral_status=ReferralStatus.open,
    )
    session.add(referral)
    write_audit_event(
        session,
        entity_name="referral",
        entity_id=str(referral.referral_id),
        action="create",
        actor_user_id=payload.initiated_by_user_id,
        actor_role="clinician",
        old_values={},
        new_values={"status": referral.referral_status},
    )
    session.commit()
    session.refresh(referral)

    return ReferralRead(
        referral_id=str(referral.referral_id),
        pregnancy_id=str(referral.pregnancy_id),
        referral_reason=referral.referral_reason,
        urgency_level=referral.urgency_level,
        referral_status=referral.referral_status,
        ambulance_id=referral.ambulance_id,
        admission_id=referral.admission_id,
        outcome=referral.outcome,
    )


@router.post("/{referral_id}/stage", response_model=ReferralRead)
def update_referral_stage(
    referral_id: str,
    payload: ReferralStageUpdate,
    session: Session = Depends(get_session),
) -> ReferralRead:
    try:
        referral_uuid = UUID(referral_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid referral_id") from exc

    referral = session.get(Referral, referral_uuid)
    if not referral:
        raise HTTPException(status_code=404, detail="referral not found")

    now = datetime.now(timezone.utc)
    stage = payload.stage.lower().strip()

    if stage == "facility_ack":
        referral.facility_ack_timestamp = now
    elif stage == "doctor_viewed":
        referral.doctor_viewed_timestamp = now
    elif stage == "dispatch":
        referral.dispatch_timestamp = now
        referral.ambulance_id = payload.ambulance_id
    elif stage == "pickup":
        referral.pickup_timestamp = now
        referral.referral_status = ReferralStatus.in_transit
    elif stage == "arrival":
        referral.arrival_timestamp = now
    elif stage == "admission":
        referral.admission_timestamp = now
        referral.admission_id = payload.admission_id
        referral.referral_status = ReferralStatus.admitted
    elif stage == "outcome":
        referral.outcome = payload.outcome
        referral.referral_status = ReferralStatus.closed
    else:
        raise HTTPException(status_code=400, detail="unsupported stage")

    referral.updated_at = now
    session.add(referral)
    write_audit_event(
        session,
        entity_name="referral",
        entity_id=str(referral.referral_id),
        action="stage_update",
        actor_user_id=payload.actor_user_id,
        actor_role="workflow",
        old_values={},
        new_values={"stage": stage, "status": referral.referral_status},
    )
    session.commit()
    session.refresh(referral)

    return ReferralRead(
        referral_id=str(referral.referral_id),
        pregnancy_id=str(referral.pregnancy_id),
        referral_reason=referral.referral_reason,
        urgency_level=referral.urgency_level,
        referral_status=referral.referral_status,
        ambulance_id=referral.ambulance_id,
        admission_id=referral.admission_id,
        outcome=referral.outcome,
    )
