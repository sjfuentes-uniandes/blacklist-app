"""Test que falla intencionalmente para verificar que el pipeline
detiene el despliegue cuando hay pruebas fallidas (caso negativo de CD).
"""


def test_should_fail():
    """Este test falla a propósito para demostrar el caso negativo de CD.

    Cuando este test está activo, el pipeline de CodeBuild falla en la
    fase 'build' (pytest) y NO ejecuta el build de Docker ni el push
    a ECR, garantizando que código con errores nunca llega a producción.
    """
    assert 1 == 2, "Fallo intencional: simula un error de regresión en el pipeline de CD"
