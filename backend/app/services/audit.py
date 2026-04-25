import json
from typing import Any

from sqlmodel import Session

from app.models.audit_event import AuditEvent


def write_audit_event(
    session: Session,
    entity_name: str,
    entity_id: str,
    action: str,
    actor_user_id: str,
    actor_role: str,
    old_values: dict[str, Any],
    new_values: dict[str, Any],
) -> None:
    event = AuditEvent(
        entity_name=entity_name,
        entity_id=entity_id,
        action=action,
        actor_user_id=actor_user_id,
        actor_role=actor_role,
        old_values=json.dumps(old_values, default=str),
        new_values=json.dumps(new_values, default=str),
    )
    session.add(event)
