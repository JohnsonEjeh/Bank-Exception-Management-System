from fastapi import FastAPI
from db import db_health, engine
from sqlalchemy import inspect

from routes.exception_types import router as et_router
from routes.exceptions import router as ex_router
from routes.users import router as users_router
from routes.attachments import router as att_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# allow your dev frontend
ALLOWED_ORIGINS = ["http://localhost:5173"]

app = FastAPI(title="EMS API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app = FastAPI(title="EMS API", version="0.1.0")

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

# register routers
app.include_router(et_router)
app.include_router(ex_router)
app.include_router(users_router)
app.include_router(att_router)


