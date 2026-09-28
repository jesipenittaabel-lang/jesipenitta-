import json
import re

from pathlib import Path
from typing import Any

from .catalog import fallback_recommendations
from ..config import get_settings


SYSTEM = """
You are PocketSmart AI, a budget recommendation assistant.

Generate practical, budget-aware recommendations
for home interiors, parties, and jewelry.

Do not claim live inventory or exact live prices.

Prices must be clearly labeled as estimates.

Keep the total at or below the user's budget whenever possible.

Use only these platform names when suggesting
shopping/search sources:

Amazon, Flipkart, IKEA, Swiggy, Zomato, OYO, PocketSmart.

Return ONLY valid JSON matching the requested schema.
"""


SCHEMA = {
    "type": "object",

    "properties": {
        "title": {
            "type": "string"
        },

        "summary": {
            "type": "string"
        },

        "items": {
            "type": "array",

            "items": {
                "type": "object",

                "properties": {
                    "category": {
                        "type": "string"
                    },

                    "name": {
                        "type": "string"
                    },

                    "description": {
                        "type": "string"
                    },

                    "estimated_price": {
                        "type": "number"
                    },

                    "quantity": {
                        "type": "integer"
                    },

                    "platform": {
                        "type": "string"
                    },

                    "reason": {
                        "type": "string"
                    },
                },

                "required": [
                    "category",
                    "name",
                    "description",
                    "estimated_price",
                    "quantity",
                    "platform",
                    "reason",
                ],
            },
        },

        "tips": {
            "type": "array",

            "items": {
                "type": "string"
            },
        },
    },

    "required": [
        "title",
        "summary",
        "items",
        "tips",
    ],
}


def _clean_json(
    text: str,
) -> dict[str, Any]:

    text = text.strip()

    if text.startswith("```"):
        text = re.sub(
            r"^```(?:json)?",
            "",
            text,
        ).strip()

        text = re.sub(
            r"```$",
            "",
            text,
        ).strip()

    return json.loads(text)


def _client():
    settings = get_settings()

    if not settings.gemini_api_key:
        return None

    from google import genai

    return genai.Client(
        api_key=settings.gemini_api_key
    )


def generate(
    planner: str,
    request_data: dict[str, Any],
    image_path: Path | None = None,
):
    settings = get_settings()

    client = _client()

    if not client:
        return _fallback(
            planner,
            request_data,
        )

    prompt = f"""
Planner: {planner}

User request:
{json.dumps(request_data, ensure_ascii=False)}

Return JSON with this exact top-level shape:

{{
    "title": "...",
    "summary": "...",
    "items": [
        {{
            "category": "...",
            "name": "...",
            "description": "...",
            "estimated_price": 0,
            "quantity": 1,
            "platform": "Amazon|Flipkart|IKEA|Swiggy|Zomato|OYO|PocketSmart",
            "reason": "..."
        }}
    ],
    "tips": ["..."]
}}

The sum of estimated_price * quantity
must not exceed the budget unless the budget
is too small for a meaningful plan.
"""

    contents: list[Any] = [prompt]

    if image_path:
        try:
            from PIL import Image

            contents.append(
                Image.open(image_path)
            )

            contents.append(
                "Use the uploaded outfit image only "
                "to infer broad color/style coordination. "
                "Do not identify the person or make "
                "sensitive inferences."
            )

        except Exception:
            pass

    try:
        from google.genai import types

        response = client.models.generate_content(
            model=settings.gemini_model,

            contents=contents,

            config=types.GenerateContentConfig(
                system_instruction=SYSTEM,
                response_mime_type="application/json",
                response_schema=SCHEMA,
                temperature=0.4,
                max_output_tokens=2500,
            ),
        )

        data = _clean_json(
            response.text or ""
        )

        items = data.get(
            "items",
            [],
        )

        valid = []

        total = 0.0

        budget = float(
            request_data["budget"]
        )

        for raw in items:
            price = max(
                0.0,
                float(
                    raw.get(
                        "estimated_price",
                        0,
                    )
                ),
            )

            quantity = max(
                1,
                int(
                    raw.get(
                        "quantity",
                        1,
                    )
                ),
            )

            platform = raw.get(
                "platform",
                "PocketSmart",
            )

            if platform not in {
                "Amazon",
                "Flipkart",
                "IKEA",
                "Swiggy",
                "Zomato",
                "OYO",
                "PocketSmart",
            }:
                platform = "PocketSmart"

            if (
                total + price * quantity
                > budget
            ):
                continue

            valid.append(
                {
                    "category": str(
                        raw.get(
                            "category",
                            "General",
                        )
                    ),

                    "name": str(
                        raw.get(
                            "name",
                            "Recommended option",
                        )
                    ),

                    "description": str(
                        raw.get(
                            "description",
                            "Budget-aware recommendation.",
                        )
                    ),

                    "estimated_price": round(
                        price,
                        2,
                    ),

                    "quantity": quantity,

                    "platform": platform,

                    "reason": str(
                        raw.get(
                            "reason",
                            "Fits the stated preferences.",
                        )
                    ),
                }
            )

            total += price * quantity

        if not valid:
            return _fallback(
                planner,
                request_data,
            )

        for item in valid:
            item["search_url"] = "#"

        return {
            "planner": planner,

            "title": data.get(
                "title",
                f"{planner.title()} Budget Plan",
            ),

            "budget": budget,

            "allocated_total": round(
                total,
                2,
            ),

            "remaining": round(
                budget - total,
                2,
            ),

            "summary": data.get(
                "summary",
                "AI-generated budget plan.",
            ),

            "items": valid,

            "tips": data.get(
                "tips",
                [],
            ),

            "source": "gemini",
        }

    except Exception:
        return _fallback(
            planner,
            request_data,
        )


def _fallback(
    planner: str,
    request_data: dict[str, Any],
):
    items, total = fallback_recommendations(
        planner,
        float(request_data["budget"]),
        request_data,
    )

    budget = float(
        request_data["budget"]
    )

    return {
        "planner": planner,

        "title": (
            f"{planner.title()} "
            "Budget Plan"
        ),

        "budget": budget,

        "allocated_total": total,

        "remaining": round(
            budget - total,
            2,
        ),

        "summary": (
            "A local fallback plan generated "
            "from PocketSmart's built-in catalog. "
            "Add a Gemini API key to enable "
            "live AI personalization."
        ),

        "items": items,

        "tips": [
            "Compare final prices and availability before purchasing.",
            "Keep a small contingency amount for unexpected costs.",
        ],

        "source": "fallback",
    }