from collections import deque
from threading import RLock
from typing import Any

from .domain import AuditRecord, new_id


class MemoryStore:
    def __init__(self):
        self.lock = RLock()
        self.sessions: dict[str, list[dict[str, Any]]] = {}
        self.actions: dict[str, dict[str, Any]] = {}
        self.reviews: dict[str, dict[str, Any]] = {}
        self.audits: deque[dict[str, Any]] = deque(maxlen=1000)
        self.config_version = 12

    def append_message(self, session_id, message):
        with self.lock:
            self.sessions.setdefault(session_id, []).append(message)

    def save_action(self, action):
        with self.lock:
            self.actions[action["id"]] = action

    def audit(self, trace_id, event, actor, detail):
        record = AuditRecord(new_id("audit"), trace_id, event, actor, detail).to_dict()
        with self.lock:
            self.audits.appendleft(record)
        return record

    def create_review(self, action, query, intent):
        review = {
            "id": new_id("review"), "action_id": action["id"], "status": "pending",
            "priority": "P0" if action["risk"] == "L4" else "P1", "query": query,
            "intent": intent, "risk": action["risk"], "action": action,
        }
        with self.lock:
            self.reviews[review["id"]] = review
        return review

    def metrics(self):
        with self.lock:
            total = sum(len(v) for v in self.sessions.values())
            pending = sum(1 for r in self.reviews.values() if r["status"] == "pending")
            executed = sum(1 for a in self.actions.values() if a["status"] == "executed")
            return {"conversations": total, "pending_reviews": pending, "executed_actions": executed, "config_version": self.config_version, "intent_accuracy": 0.926, "automation_rate": 0.684}

