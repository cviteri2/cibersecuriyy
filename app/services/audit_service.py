from flask import request
from flask_login import current_user

from app.extensions import db
from app.models.audit import AuditLog


def log_action(action, entity=None, entity_id=None, detail=None):
    try:
        user_id = current_user.id if current_user and current_user.is_authenticated else None
    except Exception:
        user_id = None
    try:
        ip = request.remote_addr
    except Exception:
        ip = None

    entry = AuditLog(
        user_id=user_id,
        action=action,
        entity=entity,
        entity_id=entity_id,
        detail=detail,
        ip_address=ip,
    )
    db.session.add(entry)
    db.session.commit()
    return entry
