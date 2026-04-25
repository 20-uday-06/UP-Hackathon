from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db.session import get_session
from app.services.alerts import mandatory_30_day_hrp_alerts, run_alert_escalations

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/run-daily")
def run_daily_jobs(session: Session = Depends(get_session)) -> dict[str, int]:
    created_alerts = mandatory_30_day_hrp_alerts(session)
    escalated_alerts = run_alert_escalations(session)
    session.commit()
    return {
        "created_alerts": created_alerts,
        "escalated_alerts": escalated_alerts,
    }
