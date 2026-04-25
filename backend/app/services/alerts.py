from datetime import datetime, timedelta, timezone
from typing import Iterable
from uuid import UUID

from sqlmodel import Session, select

from app.models.alert_event import AlertEvent, AlertStatus, AlertType
from app.models.pregnancy import Pregnancy


def create_stakeholder_alerts(
    session: Session,
    pregnancy: Pregnancy,
    alert_type: AlertType,
    message: str,
    stakeholders: Iterable[tuple[str, str]],
) -> list[AlertEvent]:
    alerts: list[AlertEvent] = []
    for stakeholder_type, stakeholder_id in stakeholders:
        alert = AlertEvent(
            pregnancy_id=pregnancy.pregnancy_id,
            alert_type=alert_type,
            stakeholder_type=stakeholder_type,
            stakeholder_id=stakeholder_id,
            message=message,
        )
        session.add(alert)
        alerts.append(alert)
    return alerts


def mandatory_30_day_hrp_alerts(session: Session, today: datetime | None = None) -> int:
    run_date = (today or datetime.now(timezone.utc)).date()
    targets = session.exec(select(Pregnancy).where(Pregnancy.hrp_flag == True)).all()  # noqa: E712
    created = 0

    for pregnancy in targets:
        if (pregnancy.edd_date - run_date).days != 30:
            continue

        message = (
            f"Mandatory HRP 30-day alert for pregnancy {pregnancy.pregnancy_id}. "
            f"EDD is {pregnancy.edd_date}. Acknowledge within 24 hours."
        )
        stakeholders = [
            ("beneficiary", pregnancy.mobile_primary),
            ("family", pregnancy.mobile_alternate or pregnancy.mobile_primary),
            ("asha", pregnancy.assigned_asha_id or "unassigned_asha"),
            ("anm", pregnancy.assigned_anm_id or "unassigned_anm"),
            ("chc", pregnancy.assigned_chc_id or "unassigned_chc"),
            ("doctor", pregnancy.assigned_chc_id or "unassigned_doctor"),
            ("transport_desk", "102_108_desk"),
            ("district_team", pregnancy.address_district),
        ]
        create_stakeholder_alerts(
            session=session,
            pregnancy=pregnancy,
            alert_type=AlertType.hrp_30_day,
            message=message,
            stakeholders=stakeholders,
        )
        created += 8

    return created


def run_alert_escalations(session: Session, now: datetime | None = None) -> int:
    clock = now or datetime.now(timezone.utc)
    pending_alerts = session.exec(
        select(AlertEvent).where(AlertEvent.status == AlertStatus.pending)
    ).all()
    escalated = 0

    for alert in pending_alerts:
        created_at = alert.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        age = clock - created_at
        if age >= timedelta(hours=24):
            alert.status = AlertStatus.escalated
            alert.escalated_at = clock
            session.add(alert)
            escalated += 1

    return escalated


def acknowledge_alert(
    session: Session,
    alert_id: UUID,
    actor_user_id: str,
) -> AlertEvent | None:
    alert = session.get(AlertEvent, alert_id)
    if not alert:
        return None

    alert.status = AlertStatus.acknowledged
    alert.acknowledged_at = datetime.now(timezone.utc)
    alert.acknowledged_by_user_id = actor_user_id
    session.add(alert)
    return alert
