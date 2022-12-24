from example import add, multiply


def test_add():
    assert add(1, 2) == 3


def test_add_negative():
    assert add(-1, -2) == -3


def test_multiply():
    assert multiply(1, 2) == 2
