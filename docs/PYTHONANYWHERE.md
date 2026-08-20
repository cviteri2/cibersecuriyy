# Despliegue en PythonAnywhere

Esta guía asume una cuenta gratuita o de pago en
[pythonanywhere.com](https://www.pythonanywhere.com) y el repositorio Git
del proyecto ya disponible en GitHub (o accesible por HTTPS/SSH).

## 1. Crear la Web App

1. En el panel de PythonAnywhere, ve a la pestaña **Web** → **Add a new web app**.
2. Elige **Manual configuration** (no "Flask" del asistente, para tener
   control total del `wsgi.py` propio del proyecto).
3. Selecciona la versión de **Python 3.11** (o la más reciente disponible).

## 2. Clonar el repositorio

En una consola Bash de PythonAnywhere (**Consoles** → **Bash**):

```bash
cd ~
git clone https://github.com/<tu-usuario>/<tu-repo>.git cyber-privacy-platform
cd cyber-privacy-platform
```

Para actualizar más adelante desde Git:

```bash
cd ~/cyber-privacy-platform
git pull origin main
```

## 3. Crear el entorno virtual e instalar dependencias

```bash
mkvirtualenv --python=/usr/bin/python3.11 cyber-privacy-venv
# o, si prefieres venv estándar:
# python3.11 -m venv ~/.virtualenvs/cyber-privacy-venv
# source ~/.virtualenvs/cyber-privacy-venv/bin/activate

pip install -r ~/cyber-privacy-platform/requirements.txt
```

En la pestaña **Web**, en la sección **Virtualenv**, indica la ruta:

```
/home/<tu-usuario>/.virtualenvs/cyber-privacy-venv
```

## 4. Variables de entorno

Crea el archivo `.env` a partir de la plantilla (nunca subas `.env` a Git):

```bash
cd ~/cyber-privacy-platform
cp .env.example .env
nano .env
```

Completa como mínimo:

```
FLASK_ENV=production
SECRET_KEY=<genera-una-clave-larga-y-aleatoria>
DATABASE_URL=sqlite:///instance/cyber_privacy.db
RESEND_API_KEY=<tu-api-key-de-resend>
RESEND_FROM_EMAIL=<remitente-verificado>
RESEND_FROM_NAME=Cyber & Privacy Assessment Platform
SEED_ADMIN_PASSWORD=<contraseña-fuerte-para-el-usuario-demo>
```

Genera una `SECRET_KEY` segura con:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

> `wsgi.py` y `run.py` cargan `.env` automáticamente mediante
> `python-dotenv`, por lo que no es obligatorio configurar las variables
> también en la pestaña **Web → Environment variables**, aunque puedes
> duplicarlas ahí si lo prefieres.

## 5. Inicializar la base de datos SQLite

```bash
cd ~/cyber-privacy-platform
workon cyber-privacy-venv   # o: source ~/.virtualenvs/cyber-privacy-venv/bin/activate
export FLASK_APP=run.py
flask init-db
flask seed        # opcional: carga el banco de preguntas + datos de demo
```

Esto crea `instance/cyber_privacy.db`. Asegúrate de que el directorio
`instance/` y `instance/uploads/` existan y tengan permisos de escritura
(se crean automáticamente al iniciar la aplicación).

## 6. Configurar el archivo WSGI

En la pestaña **Web**, abre el enlace bajo **Code → WSGI configuration
file** (algo como `/var/www/<usuario>_pythonanywhere_com_wsgi.py`) y
reemplaza su contenido por:

```python
import sys
import os

project_home = '/home/<tu-usuario>/cyber-privacy-platform'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ.setdefault('FLASK_ENV', 'production')

from wsgi import application
```

El `wsgi.py` del proyecto ya expone la variable `application` que
PythonAnywhere necesita, y crea las tablas si no existen al arrancar.

## 7. Configurar archivos estáticos (opcional pero recomendado)

En la pestaña **Web → Static files**, agrega:

| URL | Directory |
|---|---|
| `/static/` | `/home/<tu-usuario>/cyber-privacy-platform/app/static/` |

Esto permite que Nginx sirva el CSS directamente sin pasar por Flask.

## 8. Directorios de archivos (evidencias subidas)

Las evidencias se guardan en `instance/uploads/`. Verifica que la ruta
absoluta configurada en `config.py` (`UPLOAD_FOLDER`) sea escribible por
el usuario de la Web App; en PythonAnywhere esto ya ocurre por defecto al
usar el propio directorio del proyecto en `~`.

## 9. Reiniciar la aplicación

En la pestaña **Web**, pulsa el botón verde **Reload
<tu-usuario>.pythonanywhere.com**.

## 10. Verificar logs

Si algo falla, revisa en la pestaña **Web**:

- **Error log** — tracebacks de Python/Flask.
- **Server log** — errores de Nginx/uWSGI.
- **Access log** — peticiones HTTP.

También puedes revisar la app en modo consola:

```bash
cd ~/cyber-privacy-platform
workon cyber-privacy-venv
python -c "from wsgi import application; print('OK')"
```

## 11. Actualizar la aplicación desde Git

```bash
cd ~/cyber-privacy-platform
git pull origin main
workon cyber-privacy-venv
pip install -r requirements.txt
flask init-db     # solo crea tablas nuevas si el modelo cambió; no borra datos
```

Luego vuelve a la pestaña **Web** y pulsa **Reload**.

## 12. Notas de producción

- `ProductionConfig` fuerza `SESSION_COOKIE_SECURE=True`: la aplicación
  debe servirse por HTTPS (PythonAnywhere lo hace por defecto en
  `*.pythonanywhere.com`).
- SQLite es adecuado para el volumen de uso de este MVP. Si el proyecto
  crece a nivel SaaS con alta concurrencia de escritura, evaluar migrar a
  un motor cliente-servidor en una fase posterior (fuera del alcance del
  MVP).
- No se requiere Docker, Node.js ni un proceso separado: PythonAnywhere
  ejecuta la aplicación WSGI directamente.
