from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.birth_plan import BirthPlan, BirthPlanStatus, DeliveryFacilityType
from app.models.pregnancy import Pregnancy
from app.schemas.birth_plan import BirthPlanCreate, BirthPlanRead
from app.services.audit import write_audit_event

router = APIRouter(prefix="/birth-plans", tags=["birth-plans"])


@router.post("", response_model=BirthPlanRead, status_code=201)
def create_birth_plan(
    payload: BirthPlanCreate,
    session: Session = Depends(get_session),
) -> BirthPlanRead:
    try:
        pregnancy_uuid = UUID(payload.pregnancy_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid pregnancy_id") from exc

    pregnancy = session.get(Pregnancy, pregnancy_uuid)
    if not pregnancy:
        raise HTTPException(status_code=404, detail="pregnancy not found")

    if pregnancy.hrp_flag and payload.delivery_facility_type not in {
        DeliveryFacilityType.fru,
        DeliveryFacilityType.dh,
        DeliveryFacilityType.medical_college,
    }:
        raise HTTPException(
            status_code=400,
            detail="HRP pregnancy must select FRU or higher delivery facility",
        )

    existing = session.exec(
        select(BirthPlan).where(BirthPlan.pregnancy_id == pregnancy_uuid)
    ).first()
    if existing:
        existing.delivery_facility_id = payload.delivery_facility_id
        existing.delivery_facility_type = payload.delivery_facility_type
        existing.edd_confirmed_date = payload.edd_confirmed_date
        existing.transport_mode = payload.transport_mode
        existing.transport_confirmed_by = payload.transport_confirmed_by
        existing.emergency_contact_1_name = payload.emergency_contact_1_name
        existing.emergency_contact_1_phone = payload.emergency_contact_1_phone
        existing.emergency_contact_2_name = payload.emergency_contact_2_name
        existing.emergency_contact_2_phone = payload.emergency_contact_2_phone
        existing.blood_donor_arranged = payload.blood_donor_arranged
        existing.blood_group = payload.blood_group
        existing.birth_plan_status = BirthPlanStatus.updated
        existing.birth_plan_updated_at = datetime.now(timezone.utc)
        session.add(existing)
        write_audit_event(
            session,
            entity_name="birth_plan",
            entity_id=str(existing.birth_plan_id),
            action="update",
            actor_user_id=payload.transport_confirmed_by or "system",
            actor_role="worker",
            old_values={},
            new_values={"birth_plan_status": existing.birth_plan_status},
        )
        session.commit()
        session.refresh(existing)
        result = existing
    else:
        plan = BirthPlan(
            pregnancy_id=pregnancy_uuid,
            delivery_facility_id=payload.delivery_facility_id,
            delivery_facility_type=payload.delivery_facility_type,
            edd_confirmed_date=payload.edd_confirmed_date,
            transport_mode=payload.transport_mode,
            transport_confirmed_by=payload.transport_confirmed_by,
            emergency_contact_1_name=payload.emergency_contact_1_name,
            emergency_contact_1_phone=payload.emergency_contact_1_phone,
            emergency_contact_2_name=payload.emergency_contact_2_name,
            emergency_contact_2_phone=payload.emergency_contact_2_phone,
            blood_donor_arranged=payload.blood_donor_arranged,
            blood_group=payload.blood_group,
            birth_plan_status=BirthPlanStatus.confirmed,
        )
        session.add(plan)
        write_audit_event(
            session,
            entity_name="birth_plan",
            entity_id=str(plan.birth_plan_id),
            action="create",
            actor_user_id=payload.transport_confirmed_by or "system",
            actor_role="worker",
            old_values={},
            new_values={"birth_plan_status": plan.birth_plan_status},
        )
        session.commit()
        session.refresh(plan)
        result = plan

    return BirthPlanRead(
        birth_plan_id=str(result.birth_plan_id),
        pregnancy_id=str(result.pregnancy_id),
        delivery_facility_id=result.delivery_facility_id,
        delivery_facility_type=result.delivery_facility_type,
        transport_mode=result.transport_mode,
        emergency_contact_1_name=result.emergency_contact_1_name,
        emergency_contact_1_phone=result.emergency_contact_1_phone,
        birth_plan_status=result.birth_plan_status,
    )
