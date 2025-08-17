from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect

from db import db_health, engine
from routes.exception_types import router as et_router
from routes.exceptions import router as ex_router
from routes.users import router as users_router
from routes.attachments import router as att_router
from scheeduler import maybe_start_scheduler

ALLOWED_ORIGINS = ["http://localhost:5173"]  # dev frontend

app = FastAPI(title="EMS API", version="0.1.0")

app.on_event("startup")
def _start_scheduler():
    maybe_start_scheduler(app)

@app.on_event("shutdown")
def _stop_scheduler():
    sched = getattr(app.state, "scheduler", None)
    if sched:
        sched.shutdown(wait=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    print("REQ", request.method, request.url.path)
    resp = await call_next(request)
    print("RES", resp.status_code, request.method, request.url.path)
    return resp

@app.get("/healthz")
def healthz():
    return {"status": "ok", "api": "up", **db_health()}

@app.get("/debug/db/tables")
def list_tables():
    with engine.connect() as conn:
        insp = inspect(conn)
        return {"tables": insp.get_table_names()}

@app.get("/debug/dsn")
def debug_dsn():
    from config import settings
    url = settings.DATABASE_URL.replace(settings.db_password, "******")
    return {"database_url": url}

@app.get("/debug/routes")
def debug_routes():
    out = []
    for r in app.router.routes:
        methods = sorted(m for m in getattr(r, "methods", set()) if m != "HEAD")
        path = getattr(r, "path", None) or getattr(r, "path_format", None)
        out.append({"path": path, "methods": methods})
    return out

app.include_router(et_router)
app.include_router(ex_router)
app.include_router(users_router)
app.include_router(att_router)
