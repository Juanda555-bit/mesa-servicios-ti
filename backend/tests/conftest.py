"""Aísla las pruebas del .env local (RF-14).

pytest importa este archivo antes que los módulos de prueba. Las variables se
asignan (no con setdefault) a nivel de módulo y antes de importar cualquier
`backend.*`: `load_dotenv` no sobrescribe lo ya definido, así ningún valor del
.env real entra en las pruebas.
"""

import os

VALORES_DE_PRUEBA = {
    "JWT_SECRET": "clave-ficticia-solo-para-pruebas-0123456789abcdef",
    "JWT_EXPIRA_MIN": "30",
    "DATABASE_URL": "sqlite:///:memory:",
    "CORS_ORIGINS": "http://localhost:5173",
}

os.environ.update(VALORES_DE_PRUEBA)

import pytest  # noqa: E402


@pytest.fixture()
def valores_de_prueba() -> dict[str, str]:
    return dict(VALORES_DE_PRUEBA)
