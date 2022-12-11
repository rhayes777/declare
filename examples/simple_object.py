def test_true():
    simple_object = SimpleObject()

    simple_object.add(1)
    simple_object.add(2)

    assert simple_object.is_sequential() is True


def test_false():
    simple_object = SimpleObject()

    simple_object.add(2)
    simple_object.add(2)

    assert simple_object.is_sequential() is False
