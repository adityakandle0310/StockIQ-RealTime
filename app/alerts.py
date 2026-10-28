import statistics
from collections import deque

from app.models import Alert, Tick


class SpikeDetector:
    """Flags unusual price returns (z-score) and volume bursts, per symbol."""

    def __init__(self, window=30, min_samples=10, z_threshold=4.0, volume_multiple=5.0):
        self.min_samples = min_samples
        self.window = window
        self.z_threshold = z_threshold
        self.volume_multiple = volume_multiple
        self._last_price = {}
        self._returns = {}
        self._volumes = {}

    def update(self, tick: Tick) -> list[Alert]:
        alerts = []
        returns = self._returns.setdefault(tick.symbol, deque(maxlen=self.window))
        volumes = self._volumes.setdefault(tick.symbol, deque(maxlen=self.window))

        previous = self._last_price.get(tick.symbol)
        if previous:
            ret = tick.price / previous - 1.0
            if len(returns) >= self.min_samples:
                mean = statistics.fmean(returns)
                stdev = statistics.pstdev(returns)
                if stdev > 0 and abs(ret - mean) / stdev > self.z_threshold:
                    alerts.append(Alert(
                        symbol=tick.symbol,
                        kind="price_spike",
                        message=f"{tick.symbol} moved {ret * 100:+.2f}% in one tick",
                        price=tick.price,
                        ts=tick.ts,
                    ))
            returns.append(ret)
        self._last_price[tick.symbol] = tick.price

        if len(volumes) >= self.min_samples:
            mean_volume = statistics.fmean(volumes)
            if mean_volume > 0 and tick.volume > self.volume_multiple * mean_volume:
                alerts.append(Alert(
                    symbol=tick.symbol,
                    kind="volume_spike",
                    message=f"{tick.symbol} volume {tick.volume} is {tick.volume / mean_volume:.1f}x its recent average",
                    price=tick.price,
                    ts=tick.ts,
                ))
        volumes.append(tick.volume)
        return alerts