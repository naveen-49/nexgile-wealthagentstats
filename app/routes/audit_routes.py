from flask import Blueprint

from app.models import AuditLog
from app.utils.auth import role_required


audit_bp = Blueprint(
    "audit",
    __name__
)


@audit_bp.get("/")
@role_required("ADMIN")
def get_audit_logs():

    logs = AuditLog.query.order_by(
        AuditLog.created_at.desc()
    ).all()

    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "description": log.description,
            "created_at":
                log.created_at.isoformat()
        }
        for log in logs
    ]