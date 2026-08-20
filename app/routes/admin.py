from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app.extensions import db
from app.forms import UserForm
from app.models.user import User
from app.models.organization import Organization
from app.models.framework import Framework
from app.models.audit import AuditLog
from app.utils import admin_required
from app.services.audit_service import log_action

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/")
@login_required
@admin_required
def index():
    return render_template("admin/index.html")


@admin_bp.route("/users")
@login_required
@admin_required
def list_users():
    users = User.query.order_by(User.name).all()
    return render_template("admin/users_list.html", users=users)


def _load_org_choices(form):
    form.organization_id.choices = [(0, "— Ninguna (staff) —")] + [
        (o.id, o.display_name) for o in Organization.query.order_by(Organization.legal_name).all()
    ]


@admin_bp.route("/users/new", methods=["GET", "POST"])
@login_required
@admin_required
def create_user():
    form = UserForm()
    _load_org_choices(form)
    if form.validate_on_submit():
        if not form.password.data:
            flash("La contraseña es obligatoria para un nuevo usuario.", "danger")
        elif User.query.filter_by(email=form.email.data.lower().strip()).first():
            flash("Ya existe un usuario con ese correo electrónico.", "danger")
        else:
            user = User(
                name=form.name.data,
                email=form.email.data.lower().strip(),
                role=form.role.data,
                organization_id=form.organization_id.data or None,
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            log_action("create", entity="user", entity_id=user.id, detail=user.email)
            flash("Usuario creado correctamente.", "success")
            return redirect(url_for("admin.list_users"))
    return render_template("admin/user_form.html", form=form, title="Nuevo usuario")


@admin_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    _load_org_choices(form)
    if not form.is_submitted():
        form.organization_id.data = user.organization_id or 0
    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data.lower().strip()
        user.role = form.role.data
        user.organization_id = form.organization_id.data or None
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()
        log_action("update", entity="user", entity_id=user.id, detail=user.email)
        flash("Usuario actualizado correctamente.", "success")
        return redirect(url_for("admin.list_users"))
    return render_template("admin/user_form.html", form=form, title="Editar usuario", user=user)


@admin_bp.route("/users/<int:user_id>/toggle-active", methods=["POST"])
@login_required
@admin_required
def toggle_active(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("No puedes desactivar tu propia cuenta.", "danger")
        return redirect(url_for("admin.list_users"))
    user.is_active_flag = not user.is_active_flag
    db.session.commit()
    log_action("toggle_active", entity="user", entity_id=user.id, detail=str(user.is_active_flag))
    flash("Estado del usuario actualizado.", "success")
    return redirect(url_for("admin.list_users"))


@admin_bp.route("/questions")
@login_required
@admin_required
def question_bank():
    frameworks = Framework.query.order_by(Framework.order).all()
    return render_template("admin/questions.html", frameworks=frameworks)


@admin_bp.route("/audit-log")
@login_required
@admin_required
def audit_log():
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(300).all()
    return render_template("admin/audit_log.html", logs=logs)
