from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class AuditEvent(SQLModel, table=True):
    audit_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    entity_name: str = Field(index=True)
    entity_id: str = Field(index=True)
    action: str
    actor_user_id: str
    actor_role: str
    old_values: str
    new_values: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)
