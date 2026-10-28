from app.feed.generator import generate_ticks


def test_same_seed_gives_same_ticks():
    a = list(generate_ticks(["TCS", "INFY"], n=20, seed=7))
    b = list(generate_ticks(["TCS", "INFY"], n=20, seed=7))
    assert a == b
    assert len(a) == 40


def test_different_seeds_differ():
    a = list(generate_ticks(["TCS"], n=20, seed=1))
    b = list(generate_ticks(["TCS"], n=20, seed=2))
    assert a != b


def test_prices_stay_positive():
    for tick in generate_ticks(["TCS"], n=500, seed=3):
        assert tick.price > 0
        assert tick.volume >= 0