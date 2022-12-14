import pytest


@pytest.fixture(name="a")
def make_a():
    return Complex(3, 4)


@pytest.fixture(name="b")
def make_b():
    return Complex(1, 2)


def test_addition(a, b):
    assert a + b == Complex(4, 6)


def test_multiplication(a, b):
    assert a * b == Complex(-5, 10)


def test_division(a, b):
    assert a / b == Complex(2, 0)
