import os
import click
from dotenv import load_dotenv

load_dotenv()

from app import create_app
from app.extensions import db

app = create_app(os.environ.get("FLASK_ENV", "development"))


@app.cli.command("init-db")
def init_db():
    """Create database tables."""
    with app.app_context():
        db.create_all()
    click.echo("Base de datos inicializada.")


@app.cli.command("seed")
def seed():
    """Seed the question bank and demo data."""
    from app.seed import run_seed

    with app.app_context():
        db.create_all()
        run_seed(app.config["SEED_ADMIN_PASSWORD"])
    click.echo("Datos de demostración cargados correctamente.")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=app.config.get("DEBUG", False), host="127.0.0.1", port=5000)
