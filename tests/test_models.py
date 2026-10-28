import pytest
from pydantic import ValidationError

from app.models import Tick


def test_tick_holds_values():
    tick = Tick(symbol="TCS", price=3500.5, volume=120, ts=1_700_000_000.0)
    assert tick.symbol == "TCS"
    assert tick.price == 3500.5


def test_price_must_be_positive():
    with pytest.raises(ValidationError):
        Tick(symbol="TCS", price=0, volume=10, ts=1.0)


def test_volume_cannot_be_negative():
    with pytest.raises(ValidationError):
        Tick(symbol="TCS", price=10.0, volume=-1, ts=1.0)


def test_symbol_is_cleaned_and_uppercased():
    tick = Tick(symbol=" tcs ", price=10.0, volume=1, ts=1.0)
    assert tick.symbol == "TCS"