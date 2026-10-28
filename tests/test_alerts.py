from app.alerts import SpikeDetector
from app.models import Tick


def make_ticks(prices, volumes=None, symbol="TCS"):
    volumes = volumes or [500] * len(prices)
    return [
        Tick(symbol=symbol, price=p, volume=v, ts=float(i))
        for i, (p, v) in enumerate(zip(prices, volumes))
    ]


def calm_prices(n=30, base=1000.0):
    # tiny alternating moves give a small, non-zero standard deviation
    return [base + (0.1 if i % 2 else -0.1) for i in range(n)]


def test_no_alerts_on_calm_data():
    detector = SpikeDetector()
    alerts = [a for t in make_ticks(calm_prices()) for a in detector.update(t)]
    assert alerts == []


def test_price_spike_is_flagged():
    detector = SpikeDetector()
    prices = calm_prices() + [1100.0]
    alerts = [a for t in make_ticks(prices) for a in detector.update(t)]
    assert [a.kind for a in alerts] == ["price_spike"]


def test_volume_spike_is_flagged():
    detector = SpikeDetector()
    prices = calm_prices() + [1000.0]
    volumes = [500] * 30 + [5000]
    alerts = [a for t in make_ticks(prices, volumes) for a in detector.update(t)]
    assert "volume_spike" in [a.kind for a in alerts]


def test_nothing_flagged_before_min_samples():
    detector = SpikeDetector(min_samples=10)
    alerts = [a for t in make_ticks([1000.0, 1000.1, 1500.0]) for a in detector.update(t)]
    assert alerts == []


def test_symbols_are_tracked_independently():
    detector = SpikeDetector()
    for t in make_ticks(calm_prices(), symbol="TCS"):
        detector.update(t)
    assert detector.update(Tick(symbol="INFY", price=50.0, volume=500, ts=0.0)) == []