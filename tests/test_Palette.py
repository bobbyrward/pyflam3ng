
def test():
    import pyflam3ng._flam3
    palette = _flam3.Palette()

    palette[0] = (1, 2, 3)

    assert (1, 2, 3) == palette[0]

    palette = pyflam3ng._flam3.standard_palette()

    print palette[0]

    palette2 = pyflam3ng._flam3.Palette.from_string(palette.to_string())

    print palette[0]
    print palette[1]


if __name__ == '__main__':
    test()


