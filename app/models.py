from pydantic import BaseModel, Field, field_validator


class Tick(BaseModel):
    symbol: str
    price: float = Field(gt=0)
    volume: int = Field(ge=0)
    ts: float

    @field_validator("symbol")
    @classmethod
    def clean_symbol(cls, v: str) -> str:
        return v.strip().upper()

class Alert(BaseModel):
    symbol: str
    kind: str  # "price_spike" or "volume_spike"
    message: str
    price: float
    ts: float