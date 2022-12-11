def test_has_a():
    assert has_letters("apple") is True
    assert has_letters("fun") is False


def test_does_not_have_b():
    assert has_letters("banana") is False