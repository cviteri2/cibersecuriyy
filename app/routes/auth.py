from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app.extensions import db
from app.forms import LoginForm, ChangePasswordForm
from app.models.user import User
from app.services.audit_service import log_action

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user and user.is_active_flag and user.check_password(form.password.data):
            login_user(user)
            log_action("login", entity="user", entity_id=user.id)
            next_url = request.args.get("next")
            return redirect(next_url or url_for("dashboard.index"))
        flash("Credenciales inválidas.", "danger")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    log_action("logout", entity="user", entity_id=current_user.id)
    logout_user()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/account/password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash("La contraseña actual no es correcta.", "danger")
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            log_action("password_change", entity="user", entity_id=current_user.id)
            flash("Contraseña actualizada correctamente.", "success")
            return redirect(url_for("dashboard.index"))
    return render_template("auth/change_password.html", form=form)
