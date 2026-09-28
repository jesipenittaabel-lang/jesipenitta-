import json

from pathlib import Path

from .gemini_service import generate
from ..database import get_db


def save_recommendation(
    user_id: int,
    planner: str,
    request_data: dict,
    result: dict,
) -> None:

    with get_db() as db:
        db.execute(
            """
            INSERT INTO recommendations(
                user_id,
                planner,
                request_json,
                response_json
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                user_id,
                planner,
                json.dumps(request_data),
                json.dumps(result),
            ),
        )


def get_history(user_id: int):
    with get_db() as db:
        rows = db.execute(
            """
            SELECT
                id,
                planner,
                request_json,
                response_json,
                created_at
            FROM recommendations
            WHERE user_id=?
            ORDER BY id DESC
            LIMIT 50
            """,
            (user_id,),
        ).fetchall()

    return [
        dict(row)
        for row in rows
    ]


def make_plan(
    user_id: int,
    planner: str,
    request_data: dict,
    image_path: Path | None = None,
):

    result = generate(
        planner,
        request_data,
        image_path,
    )

    save_recommendation(
        user_id,
        planner,
        request_data,
        result,
    )

    return result