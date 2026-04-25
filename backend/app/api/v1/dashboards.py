from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.alert_event import AlertEvent, AlertStatus, AlertType
from app.models.pregnancy import Pregnancy
from app.models.referral import Referral, ReferralStatus

router = APIRouter(prefix="/dashboards", tags=["dashboards"])


@router.get("/state-summary")
def state_summary(session: Session = Depends(get_session)) -> dict[str, int]:
    pregnancies = session.exec(select(Pregnancy)).all()
    referrals = session.exec(select(Referral)).all()
    alerts = session.exec(select(AlertEvent)).all()

    return {
        "total_registered_pregnancies": len(pregnancies),
        "total_hrp": sum(1 for p in pregnancies if p.hrp_flag),
        "open_referrals": sum(1 for r in referrals if r.referral_status != ReferralStatus.closed),
        "closed_referrals": sum(1 for r in referrals if r.referral_status == ReferralStatus.closed),
        "pending_hrp_30_day_alerts": sum(
            1
            for a in alerts
            if a.alert_type == AlertType.hrp_30_day and a.status == AlertStatus.pending
        ),
        "escalated_alerts": sum(1 for a in alerts if a.status == AlertStatus.escalated),
    }
