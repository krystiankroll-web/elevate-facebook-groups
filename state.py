"""Trwały stan między przebiegami: co już widzieliśmy, co wysłaliśmy, co wybrał właściciel.

Pliki JSON w katalogu state/ — w GitHub Actions są commitowane z powrotem do
repozytorium po każdym przebiegu, więc historia przeżywa restart runnera.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone

STATE_DIR = os.environ.get("STATE_DIR", "state")

SEEN_FILE = os.path.join(STATE_DIR, "seen.json")          # permalink -> data pierwszego wykrycia
LEADS_FILE = os.path.join(STATE_DIR, "leads.json")        # id -> lead + warianty + status
FEEDBACK_FILE = os.path.join(STATE_DIR, "feedback.json")  # wybrane odpowiedzi (do uczenia stylu)
META_FILE = os.path.join(STATE_DIR, "meta.json")          # znaczniki czasu, licznik ID


def _load(path: str, default):
    if not os.path.isfile(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _save(path: str, data) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class State:
    def __init__(self) -> None:
        self.seen: dict = _load(SEEN_FILE, {})
        self.leads: dict = _load(LEADS_FILE, {})
        self.feedback: list = _load(FEEDBACK_FILE, [])
        self.meta: dict = _load(META_FILE, {"next_id": 1, "last_reply_check": None})

    # --- deduplikacja postów ---
    def is_seen(self, permalink: str) -> bool:
        return permalink in self.seen

    def mark_seen(self, permalink: str, note: str = "") -> None:
        self.seen[permalink] = {"first_seen": now_iso(), "note": note}

    # --- leady wysłane na WhatsApp ---
    def new_lead_id(self) -> str:
        n = self.meta.get("next_id", 1)
        self.meta["next_id"] = n + 1
        return f"L{n}"

    def add_lead(self, lead_id: str, lead: dict, variants: list[str]) -> None:
        self.leads[lead_id] = {
            **lead,
            "variants": variants,
            "status": "sent",          # sent -> approved -> published | skipped | failed
            "sent_at": now_iso(),
            "chosen": None,
        }

    def pending_approvals(self) -> dict:
        return {k: v for k, v in self.leads.items() if v.get("status") == "approved"}

    def approve(self, lead_id: str, variant_no: int) -> bool:
        lead = self.leads.get(lead_id)
        if not lead or lead.get("status") not in ("sent",):
            return False
        if variant_no == 0:
            lead["status"] = "skipped"
            return True
        if not 1 <= variant_no <= len(lead["variants"]):
            return False
        lead["status"] = "approved"
        lead["chosen"] = variant_no
        lead["approved_at"] = now_iso()
        return True

    def mark_published(self, lead_id: str, ok: bool, detail: str = "") -> None:
        lead = self.leads[lead_id]
        lead["status"] = "published" if ok else "failed"
        lead["published_at"] = now_iso()
        lead["detail"] = detail
        if ok:
            self.feedback.append({
                "post": lead.get("text", ""),
                "chosen": lead["variants"][lead["chosen"] - 1],
                "variant_no": lead["chosen"],
                "group": lead.get("group_name"),
                "market": lead.get("market"),
                "at": now_iso(),
            })

    def examples_for(self, market: str) -> list[dict]:
        return [f for f in self.feedback if f.get("market") == market]

    def save(self) -> None:
        _save(SEEN_FILE, self.seen)
        _save(LEADS_FILE, self.leads)
        _save(FEEDBACK_FILE, self.feedback)
        _save(META_FILE, self.meta)
