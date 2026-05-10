"""
Configuración de pytest: fijar variables de entorno antes de importar la app,
para que el import de `application` no use PostgreSQL por defecto ni un token impredecible.
"""

import os
import sys

# Debe ejecutarse antes de cualquier import que cargue `config` o `application`.
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("STATIC_TOKEN", "pytest-static-bearer-token")

# Asegurar import de `application` cuando pytest usa `tests/` como rootdir.
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import pytest

from application import create_app

TEST_STATIC_TOKEN = os.environ["STATIC_TOKEN"]


@pytest.fixture
def app():
    """App Flask con configuración de prueba y BD SQLite en memoria."""
    application = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "STATIC_TOKEN": TEST_STATIC_TOKEN,
        }
    )
    yield application


@pytest.fixture
def client(app):
    """Cliente de prueba HTTP."""
    return app.test_client()


@pytest.fixture
def auth_headers(app):
    """Cabecera Authorization Bearer alineada con `STATIC_TOKEN` de la app de prueba."""
    token = app.config["STATIC_TOKEN"]
    return {"Authorization": f"Bearer {token}"}
