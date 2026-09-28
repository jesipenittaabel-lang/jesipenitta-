import os
import sys

from pathlib import Path


sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parents[1]
    ),
)


os.environ["DATABASE_URL"] = (
    "sqlite:///./test_pocketsmart.db"
)

os.environ["SECRET_KEY"] = (
    "test-secret"
)

os.environ["GEMINI_API_KEY"] = ""


from fastapi.testclient import TestClient

from app.main import app

from app.database import init_db


init_db()


def test_health():

    with TestClient(app) as client:

        response = client.get(
            "/health"
        )

        assert response.status_code == 200


def test_register_login_and_home_plan():

    with TestClient(app) as client:

        response = client.post(
            "/register",

            json={
                "username":
                    "testuser123",

                "email":
                    "test123@example.com",

                "password":
                    "secret123",
            },
        )

        assert response.status_code in (
            200,
            400,
        )


        if response.status_code == 400:

            response = client.post(
                "/login",

                json={
                    "username":
                        "testuser123",

                    "password":
                        "secret123",
                },
            )

            assert response.status_code == 200


        response = client.post(
            "/generate-home",

            json={
                "budget": 20000,

                "rooms": [
                    "Living Room"
                ],

                "items": [
                    "Lights",
                    "Fan",
                ],

                "style":
                    "modern",

                "notes":
                    "",
            },
        )


        assert response.status_code == 200


        body = response.json()


        assert body["planner"] == "home"


        assert (
            body["allocated_total"]
            <= body["budget"]
        )