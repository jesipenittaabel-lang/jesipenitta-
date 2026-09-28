from typing import Literal

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)


class RegisterRequest(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=40,
    )

    email: str = Field(
        min_length=5,
        max_length=120,
    )

    password: str = Field(
        min_length=6,
        max_length=128,
    )

    @field_validator("username")
    @classmethod
    def clean_username(cls, value: str) -> str:
        value = value.strip()

        if not value.replace("_", "").isalnum():
            raise ValueError(
                "Username may contain letters, numbers and underscores only"
            )

        return value

    @field_validator("email")
    @classmethod
    def clean_email(cls, value: str) -> str:
        value = value.strip().lower()

        if (
            "@" not in value
            or "." not in value.rsplit("@", 1)[-1]
        ):
            raise ValueError(
                "Enter a valid email address"
            )

        return value


class LoginRequest(BaseModel):
    username: str
    password: str


class HomeRequest(BaseModel):
    budget: float = Field(
        gt=0,
        le=10_000_000,
    )

    rooms: list[str] = Field(
        min_length=1
    )

    items: list[str] = Field(
        min_length=1
    )

    style: str = Field(
        default="modern",
        max_length=60,
    )

    notes: str = Field(
        default="",
        max_length=500,
    )


class PartyRequest(BaseModel):
    budget: float = Field(
        gt=0,
        le=10_000_000,
    )

    guests: int = Field(
        gt=0,
        le=5000,
    )

    event_type: str = Field(
        min_length=2,
        max_length=60,
    )

    venue: str = Field(
        default="Home",
        max_length=120,
    )

    city: str = Field(
        default="",
        max_length=80,
    )

    notes: str = Field(
        default="",
        max_length=500,
    )


class JewelryRequest(BaseModel):
    budget: float = Field(
        gt=0,
        le=10_000_000,
    )

    occasion: str = Field(
        min_length=2,
        max_length=80,
    )

    style: str = Field(
        default="classic",
        max_length=60,
    )

    metal: str = Field(
        default="Any",
        max_length=40,
    )

    notes: str = Field(
        default="",
        max_length=500,
    )


class RecommendationItem(BaseModel):
    category: str
    name: str
    description: str
    estimated_price: float
    quantity: int = 1
    platform: str
    search_url: str = ""
    reason: str = ""


class RecommendationResponse(BaseModel):
    planner: Literal[
        "home",
        "party",
        "jewelry",
    ]

    title: str

    budget: float

    allocated_total: float

    remaining: float

    summary: str

    items: list[RecommendationItem]

    tips: list[str] = []

    source: Literal[
        "gemini",
        "fallback",
    ]