from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    PasswordField,
    SelectField,
    IntegerField,
    TextAreaField,
    DateField,
    SubmitField,
)
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange, EqualTo

from app.models.user import ROLES
from app.models.risk import TREATMENT_LABELS, RISK_STATUS_LABELS
from app.models.action import PRIORITY_LABELS, ACTION_STATUS_LABELS
from app.models.question import ANSWER_LABELS


class LoginForm(FlaskForm):
    email = StringField("Correo electrónico", validators=[DataRequired(), Email()])
    password = PasswordField("Contraseña", validators=[DataRequired()])
    submit = SubmitField("Ingresar")


class UserForm(FlaskForm):
    name = StringField("Nombre", validators=[DataRequired(), Length(max=150)])
    email = StringField("Correo electrónico", validators=[DataRequired(), Email(), Length(max=150)])
    role = SelectField("Rol", choices=[(r, r) for r in ROLES], validators=[DataRequired()])
    organization_id = SelectField("Organización", coerce=int, validators=[Optional()])
    password = PasswordField(
        "Contraseña", validators=[Optional(), Length(min=8, message="Mínimo 8 caracteres")]
    )
    submit = SubmitField("Guardar")


class OrganizationForm(FlaskForm):
    legal_name = StringField("Razón social", validators=[DataRequired(), Length(max=200)])
    trade_name = StringField("Nombre comercial", validators=[Optional(), Length(max=200)])
    tax_id = StringField("RUC", validators=[Optional(), Length(max=30)])
    sector = StringField("Sector", validators=[Optional(), Length(max=120)])
    employee_count = IntegerField("Número de empleados", validators=[Optional(), NumberRange(min=0)])
    country = StringField("País", validators=[Optional(), Length(max=100)])
    city = StringField("Ciudad", validators=[Optional(), Length(max=100)])
    contact_name = StringField("Persona de contacto", validators=[Optional(), Length(max=150)])
    contact_email = StringField("Email de contacto", validators=[Optional(), Email(), Length(max=150)])
    contact_phone = StringField("Teléfono", validators=[Optional(), Length(max=40)])
    evaluation_date = DateField("Fecha de evaluación", validators=[Optional()])
    responsible_evaluator = StringField("Responsable de evaluación", validators=[Optional(), Length(max=150)])
    submit = SubmitField("Guardar")


class AssessmentForm(FlaskForm):
    name = StringField("Nombre de la evaluación", validators=[DataRequired(), Length(max=200)])
    submit = SubmitField("Crear evaluación")


class ResponseForm(FlaskForm):
    answer = SelectField(
        "Respuesta", choices=[(k, v) for k, v in ANSWER_LABELS.items()], validators=[DataRequired()]
    )
    notes = TextAreaField("Notas", validators=[Optional(), Length(max=2000)])
    submit = SubmitField("Guardar respuesta")


class EvidenceForm(FlaskForm):
    name = StringField("Nombre", validators=[DataRequired(), Length(max=200)])
    description = TextAreaField("Descripción", validators=[Optional(), Length(max=1000)])
    responsible = StringField("Responsable", validators=[Optional(), Length(max=150)])
    file = FileField(
        "Archivo",
        validators=[
            Optional(),
            FileAllowed(["pdf", "png", "jpg", "jpeg", "docx", "xlsx", "txt"], "Tipo de archivo no permitido"),
        ],
    )
    submit = SubmitField("Registrar evidencia")


class RiskForm(FlaskForm):
    code = StringField("Código", validators=[DataRequired(), Length(max=30)])
    name = StringField("Nombre del riesgo", validators=[DataRequired(), Length(max=200)])
    description = TextAreaField("Descripción", validators=[Optional(), Length(max=2000)])
    asset = StringField("Activo/Proceso", validators=[Optional(), Length(max=200)])
    threat = StringField("Amenaza", validators=[Optional(), Length(max=200)])
    vulnerability = StringField("Vulnerabilidad", validators=[Optional(), Length(max=200)])
    probability = SelectField("Probabilidad", choices=[(i, str(i)) for i in range(1, 6)], coerce=int)
    impact = SelectField("Impacto", choices=[(i, str(i)) for i in range(1, 6)], coerce=int)
    existing_controls = TextAreaField("Controles existentes", validators=[Optional(), Length(max=2000)])
    residual_probability = SelectField(
        "Probabilidad residual", choices=[("", "-")] + [(i, str(i)) for i in range(1, 6)], validators=[Optional()]
    )
    residual_impact = SelectField(
        "Impacto residual", choices=[("", "-")] + [(i, str(i)) for i in range(1, 6)], validators=[Optional()]
    )
    owner = StringField("Propietario", validators=[Optional(), Length(max=150)])
    treatment = SelectField("Tratamiento", choices=[(k, v) for k, v in TREATMENT_LABELS.items()])
    target_date = DateField("Fecha objetivo", validators=[Optional()])
    status = SelectField("Estado", choices=[(k, v) for k, v in RISK_STATUS_LABELS.items()])
    submit = SubmitField("Guardar riesgo")


class ActionForm(FlaskForm):
    title = StringField("Acción", validators=[DataRequired(), Length(max=200)])
    description = TextAreaField("Descripción", validators=[Optional(), Length(max=2000)])
    risk_id = SelectField("Riesgo asociado", coerce=int, validators=[Optional()])
    control_ref = StringField("Control asociado", validators=[Optional(), Length(max=120)])
    responsible = StringField("Responsable", validators=[Optional(), Length(max=150)])
    priority = SelectField("Prioridad", choices=[(k, v) for k, v in PRIORITY_LABELS.items()])
    start_date = DateField("Fecha de inicio", validators=[Optional()])
    target_date = DateField("Fecha objetivo", validators=[Optional()])
    status = SelectField("Estado", choices=[(k, v) for k, v in ACTION_STATUS_LABELS.items()])
    progress = IntegerField("Avance (%)", validators=[Optional(), NumberRange(min=0, max=100)])
    closure_evidence = TextAreaField("Evidencia de cierre", validators=[Optional(), Length(max=2000)])
    submit = SubmitField("Guardar acción")


class SendReportForm(FlaskForm):
    recipient = StringField("Destinatario", validators=[DataRequired(), Email()])
    subject = StringField("Asunto", validators=[DataRequired(), Length(max=200)])
    message = TextAreaField("Mensaje", validators=[Optional(), Length(max=2000)])
    submit = SubmitField("Enviar informe")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Contraseña actual", validators=[DataRequired()])
    new_password = PasswordField("Nueva contraseña", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(
        "Confirmar contraseña", validators=[DataRequired(), EqualTo("new_password", message="Las contraseñas no coinciden")]
    )
    submit = SubmitField("Cambiar contraseña")
