from plugin import event

@event
def test(param, **_):
    param.add(1)

@event('test')
def nottest(param, **_):
    param.add(2)

@event
def fake(param, **_):
    param.add(3)

@event('fake')
def isfake(param, **_):
    param.add(4)
