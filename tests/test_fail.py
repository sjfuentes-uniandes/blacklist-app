"""Test que falla intencionalmente para verificar que el pipeline
"""


def test_should_fail():
    """Este test falla a propósito para demostrar el caso negativo de CD.
    """
    assert 1 == 2, "Fallo intencional: simula un error de regresión en el pipeline de CD"
