# Cyber & Privacy Assessment Platform

Plataforma web para diagnóstico integral de ciberseguridad y protección de
datos personales. Permite a una organización responder un cuestionario
basado en **ISO/IEC 27001:2022**, **ISO/IEC 27002:2022** y la **LOPDP
(Ecuador)**, y obtener automáticamente madurez, gap analysis, matriz de
riesgos, plan de tratamiento, roadmap 90/180/365 días, un dashboard
ejecutivo y un informe PDF profesional que puede enviarse por correo
mediante [Resend](https://resend.com).

> Este sistema entrega una **evaluación de referencia / diagnóstico de
> cumplimiento**. No constituye asesoría legal ni una certificación oficial.

## Funcionalidades (MVP)

- Autenticación con roles: **Administrador**, **Evaluador**, **Cliente**.
- Organizaciones con aislamiento de datos (un cliente solo ve su propia
  organización; protección contra IDOR).
- Evaluaciones (assessments) por organización, con estados
  Borrador/En progreso/Completada/Archivada.
- Cuestionario configurable (banco de preguntas en base de datos) con
  progreso, notas y registro de evidencias por pregunta.
- Motor de madurez (escala 0-5), Gap Analysis ISO 27001/27002 y
  diagnóstico de referencia LOPDP.
- Motor de riesgos (probabilidad × impacto, matriz 5×5, riesgo residual).
- Plan de tratamiento de riesgos y roadmap 90/180/365 días.
- Dashboard ejecutivo con KPIs, gráficos de barras y matriz de riesgo
  (sin dependencias externas de JS/CDN).
- Generación de informe PDF profesional con ReportLab.
- Envío del informe por correo vía Resend (con degradación segura si no
  está configurado).
- Registro de auditoría (login, respuestas, riesgos, acciones, informes).
- Panel de administración (usuarios, banco de preguntas, auditoría).

## Stack tecnológico

Python 3.11+, Flask, SQLAlchemy (Flask-SQLAlchemy), SQLite, Flask-Login,
Flask-WTF/WTForms, Jinja2, ReportLab, Resend, Werkzeug, python-dotenv.
Sin Django, FastAPI, PostgreSQL, MongoDB, Redis, Celery, Docker ni Node.js
como requisitos.

## Arquitectura

```
cyber-privacy-platform/
├── app/
│   ├── models/        # SQLAlchemy: User, Organization, Framework/Domain,
│   │                    Question, Assessment, Response, Evidence, Risk,
│   │                    Action, EmailLog, AuditLog
│   ├── routes/         # Blueprints: auth, dashboard, organizations,
│   │                    assessment, risks, actions, reports, admin
│   ├── services/        # maturity_engine, compliance_engine, risk_engine,
│   │                    roadmap_engine, pdf_service, email_service,
│   │                    audit_service, report_data
│   ├── data/            # Banco de preguntas ISO 27001/27002/LOPDP
│   ├── templates/       # Jinja2
│   └── static/css/      # Hoja de estilos propia
├── tests/               # pytest
├── docs/PYTHONANYWHERE.md
├── config.py
├── run.py               # entrypoint de desarrollo + comandos CLI (seed, init-db)
└── wsgi.py              # entrypoint de producción (PythonAnywhere)
```

## Instalación local

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # y edita los valores
```

## Variables de entorno

| Variable | Descripción |
|---|---|
| `SECRET_KEY` | Clave secreta de Flask (sesiones, CSRF). Obligatoria en producción. |
| `DATABASE_URL` | URI de SQLAlchemy. Por defecto SQLite en `instance/`. |
| `RESEND_API_KEY` | API key de Resend. Vacío = envío de correo deshabilitado (degradación segura). |
| `RESEND_FROM_EMAIL` | Correo remitente verificado en Resend. |
| `RESEND_FROM_NAME` | Nombre del remitente. |
| `MAX_CONTENT_LENGTH` | Tamaño máximo de subida de archivos (bytes). |
| `SEED_ADMIN_PASSWORD` | Contraseña usada por `flask seed` para los usuarios de demostración. |

## Ejecución local

```bash
export FLASK_APP=run.py          # Windows (PowerShell): $env:FLASK_APP="run.py"
flask init-db                    # crea las tablas
flask seed                       # carga banco de preguntas + datos de demo
python run.py                    # http://127.0.0.1:5000
```

Usuarios de demostración creados por `flask seed` (contraseña =
`SEED_ADMIN_PASSWORD` del `.env`):

- `admin@demo-corp.ec` — Administrador
- `evaluador@demo-corp.ec` — Evaluador
- `cliente@demo-corp.ec` — Cliente (organización "Empresa Demo S.A.")

## Flujo de uso

Login → Organización → Evaluación → Cuestionario → Evidencias → Madurez →
Gap ISO → Privacidad (LOPDP) → Riesgos → Plan de tratamiento → Roadmap →
Dashboard → PDF → Envío por Resend → Auditoría.

## Tests

```bash
pip install -r requirements.txt   # incluye pytest
pytest -q
```

Cobertura: autenticación y autorización por rol, aislamiento de
organizaciones (IDOR), creación/edición de organizaciones y evaluaciones,
guardado de respuestas del cuestionario, motores de madurez/gap/riesgo/
roadmap, generación de PDF y envío de correo (con y sin Resend configurado).

## Cambiar la contraseña de administrador

La contraseña de demostración **no debe usarse en producción**. Cámbiala
desde la aplicación (`Cambiar contraseña` en el menú lateral) o define un
`SEED_ADMIN_PASSWORD` fuerte antes de ejecutar `flask seed` por primera vez
en un entorno nuevo.

## Seguridad

- Contraseñas con hash (Werkzeug/PBKDF2), nunca en texto plano.
- Protección CSRF (Flask-WTF) en todos los formularios.
- Autorización por rol y por organización (protección IDOR) verificada en
  cada ruta que accede a datos de una organización o evaluación.
- Cabeceras de seguridad (`X-Content-Type-Options`, `X-Frame-Options`,
  `Referrer-Policy`, `HSTS` en HTTPS).
- Validación y restricción de extensiones/tamaño en la carga de evidencias.
- Registro de auditoría de eventos sensibles.
- Ningún secreto se guarda en el repositorio (`.env` está en `.gitignore`;
  usa `.env.example` como plantilla).

## Despliegue en PythonAnywhere

Ver [`docs/PYTHONANYWHERE.md`](docs/PYTHONANYWHERE.md) para la guía paso a
paso (clonar repositorio, virtualenv, `wsgi.py`, variables de entorno,
inicialización de SQLite y actualización desde Git).

## Configurar Resend

1. Crea una cuenta en [resend.com](https://resend.com) y verifica un
   dominio o usa el remitente de pruebas que Resend provee.
2. Genera una API key y colócala en `RESEND_API_KEY`.
3. Define `RESEND_FROM_EMAIL` con un remitente verificado.
4. Sin estas variables, la aplicación sigue funcionando: el PDF se genera
   y descarga normalmente, y el envío queda registrado con estado
   `skipped` indicando que Resend no está configurado.

## Roadmap del producto

- **V1 (este MVP):** autenticación, organizaciones, evaluaciones,
  cuestionarios ISO 27001/27002/LOPDP, motores de scoring, riesgos,
  acciones, dashboard, PDF, envío por Resend.
- **V2:** multi-tenant avanzado, gestión documental de evidencias, firma
  de informes, gestión de proveedores/Third Party Risk, auditorías,
  notificaciones.
- **V3:** IA para análisis de evidencias y recomendaciones, Compliance
  Copilot, generación asistida de planes de tratamiento.
