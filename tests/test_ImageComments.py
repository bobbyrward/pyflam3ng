
def test():
    import pyflam3ng._flam3
    i = pyflam3ng._flam3.ImageComments()
    assert '' == i.genome
    assert '' == i.badvals
    assert '' == i.numiters
    assert '' == i.rtime
    del i

if __name__ == '__main__':
    test()
