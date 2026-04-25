from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.alert_event import AlertEvent
from app.schemas.alert import AlertAcknowledgeRequest, AlertRead
from app.services.alerts import acknowledge_alert, mandatory_30_day_hrp_alerts, run_alert_escalations

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertRead])
def list_alerts(session: Session = Depends(get_session)) -> list[AlertRead]:
    rows = session.exec(select(AlertEvent).order_by(AlertEvent.created_at.desc())).all()
    return [
        AlertRead(
            alert_id=str(row.alert_id),
            pregnancy_id=str(row.pregnancy_id),
            alert_type=row.alert_type,
            stakeholder_type=row.stakeholder_type,
            stakeholder_id=row.stakeholder_id,
            message=row.message,
            status=row.status,
            created_at=row.created_at,
            acknowledged_at=row.acknowledged_at,
            escalated_at=row.escalated_at,
        )
        for row in rows
    ]


@router.post("/{alert_id}/ack", response_model=AlertRead)
def ack_alert(
    alert_id: str,
    payload: AlertAcknowledgeRequest,
    session: Session = Depends(get_session),
) -> AlertRead:
    try:
        alert_uuid = UUID(alert_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid alert_id") from exc

    alert = acknowledge_alert(session, alert_uuid, payload.actor_user_id)
    if not alert:
        raise HTTPException(status_code=404, detail="alert not found")

    session.commit()
    session.refresh(alert)
    return AlertRead(
        alert_id=str(alert.alert_id),
        pregnancy_id=str(alert.pregnancy_id),
        alert_type=alert.alert_type,
        stakeholder_type=alert.stakeholder_type,
        stakeholder_id=alert.stakeholder_id,
        message=alert.message,
        status=alert.status,
        created_at=alert.created_at,
        acknowledged_at=alert.acknowledged_at,
        escalated_at=alert.escalated_at,
    )


@router.post("/jobs/hrp-30-day")
def trigger_hrp_30_day_job(session: Session = Depends(get_session)) -> dict[str, int]:
    created = mandatory_30_day_hrp_alerts(session)
    session.commit()
    return {"created_alerts": created}


@router.post("/jobs/escalate")
def trigger_escalation_job(session: Session = Depends(get_session)) -> dict[str, int]:
    escalated = run_alert_escalations(session)
    session.commit()
    return {"escalated_alerts": escalated}
