from fastapi import FastAPI
from db import db_health

app = FastAPI(title="EMS API", version="0.1.0")

@app.get("/healthz")
def healthz():
    health = db_health()
    return {"status": "ok", "api": "up", **health}

