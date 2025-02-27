from pydantic import BaseModel, field_validator
from typing import Optional


class KeywordExtractor(BaseModel):
    keyword: str

    @field_validator("keyword")
    @classmethod
    def validate_ticker(cls, value: str) -> str:
        value = value.strip()
        if value.isupper() and 1 < len(value) <= 6:
            return value
        return value.title()  # Capitalize other words


class ExtractedEntities(BaseModel):
    crypto: Optional[str] = None
    stock: Optional[str] = None
    location: Optional[str] = None


class TickerValue(BaseModel):
    ticker: str
    category: str

    @field_validator("ticker")
    @classmethod
    def validate_and_transform(cls, value: str, info) -> str:
        value = value.strip()
        category = info.data.get("category")

        if category in ["stock", "crypto"]:
            if value.isupper() and len(value) <= 6:
                return f"{value}-USD" if category == "crypto" else value

        return value.title()
