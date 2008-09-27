
def test():
    import _flam3
    stats = _flam3.RenderStats()
    assert 0 == stats.badvals
    assert 0 == stats.num_iters
    assert 0 == stats.render_seconds
    del stats

if __name__ == '__main__':
    test()
