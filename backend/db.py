from sqlalchemy import create_engine, text
from config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, future=True)

def db_health() -> dict:
    try:
        print(settings.DATABASE_URL)
        with engine.connect() as conn:
            r = conn.execute(text("SELECT 1")).scalar_one()
        return {"db": "up", "ping": r}
    except Exception as e:
        return {"db": "down", "error": str(e)}
