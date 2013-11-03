from plugin import event

@event
def test(param, **_):
    param.add(5)
