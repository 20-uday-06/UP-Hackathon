from datetime import datetime, timezone
import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.pregnancy import Pregnancy
from app.schemas.pregnancy import (
    PregnancyCreate,
    PregnancyHrpResolutionRequest,
    PregnancyRead,
    calculate_edd,
)
from app.services.audit import write_audit_event

router = APIRouter(prefix="/pregnancies", tags=["pregnancies"])


def _to_read_model(record: Pregnancy) -> PregnancyRead:
    return PregnancyRead(
        pregnancy_id=str(record.pregnancy_id),
        beneficiary_name=record.beneficiary_name,
        age=record.age,
        husband_name=record.husband_name,
        mobile_primary=record.mobile_primary,
        address_village_ward=record.address_village_ward,
        address_block=record.address_block,
        address_district=record.address_district,
        lmp_date=record.lmp_date,
        edd_date=record.edd_date,
        registration_source=record.registration_source,
        hrp_flag=record.hrp_flag,
        hrp_conditions=json.loads(record.hrp_conditions),
        status=record.status,
    )


@router.post("", response_model=PregnancyRead, status_code=201)
def create_pregnancy(
    payload: PregnancyCreate,
    session: Session = Depends(get_session),
) -> PregnancyRead:
    pregnancy = Pregnancy(
        beneficiary_name=payload.beneficiary_name,
        age=payload.age,
        husband_name=payload.husband_name,
        mobile_primary=payload.mobile_primary,
        mobile_alternate=payload.mobile_alternate,
        address_village_ward=payload.address_village_ward,
        address_block=payload.address_block,
        address_district=payload.address_district,
        lmp_date=payload.lmp_date,
        edd_date=calculate_edd(payload.lmp_date),
        aadhaar_masked=payload.aadhaar_masked,
        abha_id=payload.abha_id,
        rch_id=payload.rch_id,
        registration_source=payload.registration_source,
        previous_lscs=payload.previous_lscs,
        placenta_previa=payload.placenta_previa,
        boh_positive=payload.boh_positive,
        rh_negative=payload.rh_negative,
        twin_multiple=payload.twin_multiple,
        systemic_illness_description=payload.systemic_illness_description,
    )
    session.add(pregnancy)
    write_audit_event(
        session=session,
        entity_name="pregnancy",
        entity_id=str(pregnancy.pregnancy_id),
        action="create",
        actor_user_id="system",
        actor_role="registration",
        old_values={},
        new_values={"hrp_flag": pregnancy.hrp_flag},
    )
    session.commit()
    session.refresh(pregnancy)

    return _to_read_model(pregnancy)


@router.get("", response_model=list[PregnancyRead])
def list_pregnancies(
    session: Session = Depends(get_session),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[PregnancyRead]:
    rows = session.exec(select(Pregnancy).offset(offset).limit(limit)).all()
    return [_to_read_model(row) for row in rows]


@router.get("/{pregnancy_id}", response_model=PregnancyRead)
def get_pregnancy(pregnancy_id: str, session: Session = Depends(get_session)) -> PregnancyRead:
    try:
        pregnancy_uuid = UUID(pregnancy_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid pregnancy_id") from exc

    record = session.get(Pregnancy, pregnancy_uuid)
    if not record:
        raise HTTPException(status_code=404, detail="pregnancy not found")

    return _to_read_model(record)


@router.patch("/{pregnancy_id}/touch", response_model=PregnancyRead)
def touch_pregnancy(pregnancy_id: str, session: Session = Depends(get_session)) -> PregnancyRead:
    try:
        pregnancy_uuid = UUID(pregnancy_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid pregnancy_id") from exc

    record = session.get(Pregnancy, pregnancy_uuid)
    if not record:
        raise HTTPException(status_code=404, detail="pregnancy not found")

    record.updated_at = datetime.now(timezone.utc)
    session.add(record)
    session.commit()
    session.refresh(record)

    return _to_read_model(record)


@router.post("/{pregnancy_id}/resolve-hrp", response_model=PregnancyRead)
def resolve_hrp(
    pregnancy_id: str,
    payload: PregnancyHrpResolutionRequest,
    session: Session = Depends(get_session),
) -> PregnancyRead:
    if payload.actor_role.upper() != "MO":
        raise HTTPException(status_code=403, detail="only MO can resolve HRP conditions")

    try:
        pregnancy_uuid = UUID(pregnancy_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid pregnancy_id") from exc

    record = session.get(Pregnancy, pregnancy_uuid)
    if not record:
        raise HTTPException(status_code=404, detail="pregnancy not found")

    existing_conditions = json.loads(record.hrp_conditions)
    remaining_conditions = [
        code for code in existing_conditions if code not in payload.clear_conditions
    ]
    old_values = {
        "hrp_flag": record.hrp_flag,
        "hrp_conditions": existing_conditions,
    }
    record.hrp_conditions = json.dumps(remaining_conditions)
    record.hrp_flag = len(remaining_conditions) > 0
    record.updated_at = datetime.now(timezone.utc)

    session.add(record)
    write_audit_event(
        session=session,
        entity_name="pregnancy",
        entity_id=str(record.pregnancy_id),
        action="hrp_resolution",
        actor_user_id=payload.actor_user_id,
        actor_role=payload.actor_role,
        old_values=old_values,
        new_values={
            "hrp_flag": record.hrp_flag,
            "hrp_conditions": remaining_conditions,
            "note": payload.resolution_note,
        },
    )
    session.commit()
    session.refresh(record)

    return _to_read_model(record)
