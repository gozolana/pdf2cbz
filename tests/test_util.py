import pytest

from pdf2cbz.util import add


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        pytest.param(1, 2, 3, id="positive integers"),
        pytest.param(-1, 1, 0, id="negative and positive"),
        pytest.param(0, 0, 0, id="zeros"),
        pytest.param(2.5, 2.5, 5.0, id="floats"),
    ],
)
def test_add(a: float, b: float, expected: float) -> None:
    assert add(a, b) == expected
