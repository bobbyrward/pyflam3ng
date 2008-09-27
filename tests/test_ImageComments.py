
def test():
    import _flam3
    i = _flam3.ImageComments()
    assert '' == i.genome
    assert '' == i.badvals
    assert '' == i.numiters
    assert '' == i.rtime
    del i

if __name__ == '__main__':
    test()
