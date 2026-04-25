import json

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.audit_event import AuditEvent

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("")
def list_audit_events(
    session: Session = Depends(get_session),
    limit: int = Query(default=100, ge=1, le=500),
) -> list[dict[str, str]]:
    rows = session.exec(select(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(limit)).all()
    return [
        {
            "audit_id": str(row.audit_id),
            "entity_name": row.entity_name,
            "entity_id": row.entity_id,
            "action": row.action,
            "actor_user_id": row.actor_user_id,
            "actor_role": row.actor_role,
            "old_values": json.dumps(json.loads(row.old_values), default=str),
            "new_values": json.dumps(json.loads(row.new_values), default=str),
            "created_at": row.created_at.isoformat(),
        }
        for row in rows
    ]
