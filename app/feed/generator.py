import random
from collections.abc import Iterable, Iterator

from app.models import Tick


def generate_ticks(
    symbols: Iterable[str],
    n: int | None = None,
    seed: int = 42,
    start_ts: float = 1_700_000_000.0,
    shock_prob: float = 0.01,
) -> Iterator[Tick]:
    """Yield a seeded random-walk tick stream, one tick per symbol per step.

    n=None runs forever. Occasionally a symbol gets a big price move and a
    volume burst, so the alert detector (step 4) has something to find.
    """
    symbols = list(symbols)
    rng = random.Random(seed)
    prices = {s: rng.uniform(200.0, 3500.0) for s in symbols}
    step = 0
    while n is None or step < n:
        for symbol in symbols:
            move = rng.gauss(0.0, 0.0008)
            volume = int(rng.uniform(100, 1000))
            if rng.random() < shock_prob:
                move += rng.choice((-1, 1)) * rng.uniform(0.01, 0.03)
                volume *= 10
            prices[symbol] = max(1.0, prices[symbol] * (1.0 + move))
            yield Tick(
                symbol=symbol,
                price=round(prices[symbol], 2),
                volume=volume,
                ts=start_ts + step,
            )
        step += 1