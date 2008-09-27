
def test():
    import _flam3
    frame = _flam3.Frame()
    assert 1 == frame.pixel_aspect_ratio

    def func():
        pass

    frame = _flam3.Frame(aspect=2.0, progress_func=func)
    assert 2 == frame.pixel_aspect_ratio

    del frame

if __name__ == '__main__':
    test()

