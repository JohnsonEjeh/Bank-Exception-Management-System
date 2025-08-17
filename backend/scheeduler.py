from __future__ import annotations

import os
from datetime import datetime, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import and_
from sqlalchemy.orm import Session

from db_session import SessionLocal
from models.exception import Exception as ExceptionModel
from models.audit_event import AuditEvent

TERMINAL = {"CLOSED", "RESOLVED", "REJECTED"}

def escalate_overdue():
    # run in its own session
    with SessionLocal() as db:  # type: Session
        now = datetime.now(timezone.utc)
        q = (
            db.query(ExceptionModel)
            .filter(
                ExceptionModel.due_at.isnot(None),
                ExceptionModel.due_at < now,
                ExceptionModel.status.notin_(TERMINAL),
                ExceptionModel.status != "ESCALATED",
            )
            .order_by(ExceptionModel.id)
        )
        rows = q.all()
        if not rows:
            return
        for obj in rows:
            old = {"status": obj.status}
            obj.status = "ESCALATED"
            obj.escalated_at = now
            db.add(
                AuditEvent(
                    at=now,
                    actor_id=None,
                    action="AUTO_ESCALATED",
                    entity_type="exception",
                    entity_id=obj.id,
                    old=old,
                    new={"status": obj.status, "reason": "due_at passed"},
                )
            )
        db.commit()

def maybe_start_scheduler(app) -> BackgroundScheduler | None:
    if os.getenv("EMS_SCHEDULER", "0") not in {"1", "true", "TRUE"}:
        print("SLA scheduler disabled (EMS_SCHEDULER not set).")
        return None
    sched = BackgroundScheduler(timezone="UTC")
    # run every minute
    sched.add_job(escalate_overdue, trigger=IntervalTrigger(minutes=1), id="escalate_overdue", replace_existing=True)
    sched.start()
    app.state.scheduler = sched
    print("SLA scheduler started.")
    return sched
