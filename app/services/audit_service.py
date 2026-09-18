from app.extensions import db
from app.models import AuditLog


def create_audit_log(
    user_id,
    action,
    entity_type=None,
    entity_id=None,
    description=None
):
    log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description
    )

    db.session.add(log)

    return log