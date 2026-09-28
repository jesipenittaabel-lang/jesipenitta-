import json
import uuid

from pathlib import Path

from fastapi import (
    FastAPI,
    Request,
    UploadFile,
    File,
    HTTPException,
    Depends,
    Form,
)

from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
    JSONResponse,
)

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import get_settings
from .database import init_db, get_db
from .auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)

from .schemas import (
    RegisterRequest,
    LoginRequest,
    HomeRequest,
    PartyRequest,
    JewelryRequest,
)

from .services.recommendation_service import (
    make_plan,
    get_history,
)


BASE = Path(__file__).resolve().parent

UPLOADS = (
    BASE
    / "static"
    / "uploads"
)

UPLOADS.mkdir(
    parents=True,
    exist_ok=True,
)


app = FastAPI(
    title=get_settings().app_name,
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


app.mount(
    "/static",
    StaticFiles(
        directory=BASE / "static"
    ),
    name="static",
)


templates = Jinja2Templates(
    directory=BASE / "templates"
)


@app.on_event("startup")
def startup():
    init_db()


def page(
    request: Request,
    template: str,
    **context,
):
    user = None

    token = request.cookies.get(
        "access_token"
    )

    if token:
        try:
            user = get_current_user(
                request,
                token,
            )
        except Exception:
            user = None

return templates.TemplateResponse(
    request=request,
    name=template,
    context={
        "request": request,
        "user": user,
        **context,
    },
)
def index(request: Request):
    return page(
        request,
        "index.html",
    )


@app.get(
    "/register",
    response_class=HTMLResponse,
)
def register_page(
    request: Request,
):
    return page(
        request,
        "register.html",
    )


@app.post("/register")
def register(
    data: RegisterRequest,
):
    with get_db() as db:
        try:
            cur = db.execute(
                """
                INSERT INTO users(
                    username,
                    email,
                    password_hash
                )
                VALUES (?, ?, ?)
                """,
                (
                    data.username,
                    data.email,
                    hash_password(
                        data.password
                    ),
                ),
            )

            user_id = cur.lastrowid

except Exception as exc:
    print("REGISTER ERROR:", repr(exc))
    raise HTTPException(
        400,
        "Username or email is already registered",
    ) from exc
    token = create_access_token(
        user_id
    )

    response = JSONResponse(
        {
            "message":
                "Registration successful",

            "redirect":
                "/dashboard",
        }
    )

    response.set_cookie(
        "access_token",
        token,
        httponly=True,
        samesite="lax",
        max_age=3600,
    )

    return response


@app.get(
    "/login",
    response_class=HTMLResponse,
)
def login_page(
    request: Request,
):
    return page(
        request,
        "login.html",
    )


@app.post("/login")
def login(
    data: LoginRequest,
):
    with get_db() as db:
        row = db.execute(
            """
            SELECT *
            FROM users
            WHERE username=?
            """,
            (
                data.username.strip(),
            ),
        ).fetchone()

    if (
        not row
        or not verify_password(
            data.password,
            row["password_hash"],
        )
    ):
        raise HTTPException(
            401,
            "Invalid username or password",
        )

    token = create_access_token(
        row["id"]
    )

    response = JSONResponse(
        {
            "message":
                "Login successful",

            "redirect":
                "/dashboard",
        }
    )

    response.set_cookie(
        "access_token",
        token,
        httponly=True,
        samesite="lax",
        max_age=3600,
    )

    return response


@app.get("/logout")
def logout():
    response = RedirectResponse(
        "/",
        status_code=303,
    )

    response.delete_cookie(
        "access_token"
    )

    return response


@app.post("/token")
def token(
    data: LoginRequest,
):
    with get_db() as db:
        row = db.execute(
            """
            SELECT *
            FROM users
            WHERE username=?
            """,
            (
                data.username.strip(),
            ),
        ).fetchone()

    if (
        not row
        or not verify_password(
            data.password,
            row["password_hash"],
        )
    ):
        raise HTTPException(
            401,
            "Invalid username or password",
        )

    return {
        "access_token":
            create_access_token(
                row["id"]
            ),

        "token_type":
            "bearer",
    }


@app.get(
    "/dashboard",
    response_class=HTMLResponse,
)
def dashboard(
    request: Request,
    user=Depends(get_current_user),
):
    return page(
        request,
        "dashboard.html",
        user=user,
    )


@app.get(
    "/planner/{planner}",
    response_class=HTMLResponse,
)
def planner_page(
    planner: str,
    request: Request,
    user=Depends(get_current_user),
):
    if planner not in {
        "home",
        "party",
        "jewelry",
    }:
        raise HTTPException(
            404,
            "Planner not found",
        )

    return page(
        request,
        f"{planner}_planner.html",
        user=user,
    )


@app.get(
    "/history",
    response_class=HTMLResponse,
)
def history_page(
    request: Request,
    user=Depends(get_current_user),
):
    rows = get_history(
        user["id"]
    )

    parsed = []

    for row in rows:
        item = dict(row)

        item["request"] = json.loads(
            item.pop("request_json")
        )

        item["response"] = json.loads(
            item.pop("response_json")
        )

        parsed.append(item)

    return page(
        request,
        "history.html",
        user=user,
        history=parsed,
    )


@app.get("/session-info")
def session_info(
    user=Depends(get_current_user),
):
    return {
        "authenticated": True,
        "user": user,
    }


@app.get("/session-data")
def session_data(
    user=Depends(get_current_user),
):
    rows = get_history(
        user["id"]
    )

    return {
        "user": user,
        "recommendation_count": len(rows),
        "history": rows,
    }


@app.post("/generate-home")
def generate_home(
    payload: HomeRequest,
    user=Depends(get_current_user),
):
    return make_plan(
        user["id"],
        "home",
        payload.model_dump(),
    )


@app.post("/generate-party")
def generate_party(
    payload: PartyRequest,
    user=Depends(get_current_user),
):
    return make_plan(
        user["id"],
        "party",
        payload.model_dump(),
    )


@app.post("/generate-jewelry")
async def generate_jewelry(
    budget: float = Form(...),
    occasion: str = Form(...),
    style: str = Form("classic"),
    metal: str = Form("Any"),
    notes: str = Form(""),
    outfit_image: UploadFile | None = File(None),
    user=Depends(get_current_user),
):

    payload = JewelryRequest(
        budget=budget,
        occasion=occasion,
        style=style,
        metal=metal,
        notes=notes,
    )

    image_path = None

    if (
        outfit_image
        and outfit_image.filename
    ):
        allowed = {
            "image/jpeg",
            "image/png",
            "image/webp",
        }

        if (
            outfit_image.content_type
            not in allowed
        ):
            raise HTTPException(
                400,
                "Only JPG, PNG or WEBP images are supported",
            )

        data = await outfit_image.read()

        if len(data) > (
            get_settings().max_upload_mb
            * 1024
            * 1024
        ):
            raise HTTPException(
                413,
                "Image is too large",
            )

        safe = (
            f"{uuid.uuid4().hex}"
            f"{Path(outfit_image.filename).suffix.lower()}"
        )

        image_path = UPLOADS / safe

        image_path.write_bytes(
            data
        )

    return make_plan(
        user["id"],
        "jewelry",
        payload.model_dump(),
        image_path,
    )


@app.get("/health")
def health():
    return {
        "status":"ok",
        "service":get_settings().app_name, 
    }


return {
  "name": "LED ceiling light",
  "price": 1800,
  "image": "https://m.media-amazon.com/images/I/51T6U3z7LAL._AC_UF1000,1000_QL80_.jpg"
}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )