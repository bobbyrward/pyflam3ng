
def test():
    import _flam3
    palette = _flam3.Palette()

    palette[0] = (1, 2, 3)

    assert (1, 2, 3) == palette[0]

    palette = _flam3.standard_palette()

    print palette[0]

    palette2 = _flam3.Palette.from_string(palette.to_string())

    print palette[0]
    print palette[1]


if __name__ == '__main__':
    test()


