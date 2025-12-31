import pytest

from pdf2cbz.util import add


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (1, 2, 3),
        (-1, 1, 0),
        (0, 0, 0),
        (2.5, 2.5, 5.0),
    ],
)
def test_add(a: float, b: float, expected: float) -> None:
    assert add(a, b) == expected
