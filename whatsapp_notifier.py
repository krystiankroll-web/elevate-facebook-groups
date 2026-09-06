"""WhatsApp przez Twilio: wysyłka leadów z wariantami i odczyt odpowiedzi właściciela.

Bez serwera i webhooka. Odpowiedzi ("L7 2") pobieramy z Twilio REST API przy
każdym przebiegu — Twilio trzyma przychodzące wiadomości, więc wystarczy zapytać
o te nowsze niż ostatnie sprawdzenie.

Zmienne środowiskowe: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN,
TWILIO_WHATSAPP_NUMBER (nadawca, np. whatsapp:+14155238886),
WHATSAPP_TO (odbiorca, np. whatsapp:+48600000000).
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

import requests

import config

TWILIO_API = "https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
MAX_CHARS = 1500  # limit Twilio dla WhatsApp to 1600; zostawiamy margines

# "L7 2", "l7-2", "7 2", "T1 1", "L7:2" — dowolna litera przed numerem albo jej brak,
# wielkość liter bez znaczenia. Wymagamy separatora między numerem leada a wariantem.
APPROVAL_RE = re.compile(r"(?<![A-Za-z0-9])[A-Za-z]?\s*(\d{1,5})\s*[-:./ ]\s*([0-3])(?!\d)", re.IGNORECASE)


def _creds() -> tuple[str, str, str, str]:
    missing = [
        n for n, v in (
            ("TWILIO_ACCOUNT_SID", config.TWILIO_ACCOUNT_SID),
            ("TWILIO_AUTH_TOKEN", config.TWILIO_AUTH_TOKEN),
            ("TWILIO_WHATSAPP_NUMBER", config.TWILIO_WHATSAPP_NUMBER),
            ("WHATSAPP_TO", config.WHATSAPP_TO),
        ) if not v
    ]
    if missing:
        raise RuntimeError(f"Brak zmiennych środowiskowych Twilio: {', '.join(missing)}")
    return (config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN,
            config.TWILIO_WHATSAPP_NUMBER, config.WHATSAPP_TO)


# --------------------------------------------------------------------------
# Formatowanie
# --------------------------------------------------------------------------

def format_lead(lead_id: str, lead: dict, variants: list[str]) -> str:
    age = lead.get("age_label") or "?"
    text = (lead.get("text") or "").strip()
    if len(text) > 350:
        text = text[:347].rstrip() + "..."
    head = (
        f"LEAD {lead_id} · {lead.get('market', '?')} · {lead.get('group_name', '?')} · {age}\n"
        f"{text}\n"
        f"{lead.get('permalink', '')}\n"
    )
    body = "\n\n".join(f"{i}) {v}" for i, v in enumerate(variants, 1))
    tail = f"\n\nOdpowiedz: {lead_id} 1 / {lead_id} 2 / {lead_id} 3 — albo {lead_id} 0, żeby pominąć."
    return head + "\n" + body + tail


def _chunk(text: str, limit: int = MAX_CHARS) -> list[str]:
    """Dzieli po akapitach, żeby wariant nie został przecięty w pół zdania."""
    if len(text) <= limit:
        return [text]
    parts, cur = [], ""
    for para in text.split("\n\n"):
        cand = f"{cur}\n\n{para}" if cur else para
        if len(cand) > limit and cur:
            parts.append(cur)
            cur = para
        else:
            cur = cand
    if cur:
        parts.append(cur)
    return parts


# --------------------------------------------------------------------------
# Wysyłka
# --------------------------------------------------------------------------

def send_text(body: str, dry_run: bool = False) -> list[str]:
    """Wysyła wiadomość (dzieląc na części). Zwraca listę SID-ów Twilio."""
    sid, token, sender, to = _creds()
    sids = []
    for i, part in enumerate(_chunk(body), 1):
        if dry_run:
            print(f"[dry-run] WhatsApp część {i}:\n{part}\n")
            sids.append(f"dry-{i}")
            continue
        r = requests.post(
            TWILIO_API.format(sid=sid),
            auth=(sid, token),
            data={"From": sender, "To": to, "Body": part},
            timeout=30,
        )
        if r.status_code >= 300:
            raise RuntimeError(f"Twilio {r.status_code}: {r.text[:300]}")
        sids.append(r.json().get("sid", "?"))
    return sids


# --------------------------------------------------------------------------
# Tryb szablonowy (konto trial / poza oknem 24 h)
#
# Na koncie trial Twilio odrzuca wolny tekst kodem 21654 i pozwala wysyłać
# wyłącznie gotowe szablony. Używamy "Order Notifications":
#   "Your {{1}} order of {{2}} has shipped and should be delivered on {{3}}. Details: {{4}}"
# i wkładamy w zmienne: {{1}} = ID leada, {{2}} = treść posta, {{3}} = grupa i wiek,
# {{4}} = jeden wariant. Jedna wiadomość na wariant. Brzmi dziwnie, ale dochodzi,
# a odpowiedź "L7 2" czytamy tak samo. Po upgrade konta wolny tekst wraca sam,
# bo szablon jest tylko fallbackiem po błędzie 21654 / 63016.
# --------------------------------------------------------------------------

TEMPLATE_FALLBACK_CODES = {21654, 63016}
TWILIO_TEMPLATE_SID = None  # ustawiane z env w _template_sid()


def _template_sid() -> str | None:
    import os
    return os.environ.get("TWILIO_TEMPLATE_SID") or TWILIO_TEMPLATE_SID


def _var(text: str, limit: int) -> str:
    """Zmienna szablonu WhatsApp: bez nowych linii, bez >4 spacji, przycięta."""
    t = re.sub(r"\s+", " ", (text or "")).strip()
    return t if len(t) <= limit else t[: limit - 1].rstrip() + "…"


def send_template(content_sid: str, variables: dict, dry_run: bool = False) -> str:
    import json as _json
    sid, token, sender, to = _creds()
    if dry_run:
        print(f"[dry-run] szablon {content_sid}: {variables}")
        return "dry-template"
    r = requests.post(
        TWILIO_API.format(sid=sid),
        auth=(sid, token),
        data={"From": sender, "To": to, "ContentSid": content_sid,
              "ContentVariables": _json.dumps(variables, ensure_ascii=False)},
        timeout=30,
    )
    if r.status_code >= 300:
        raise RuntimeError(f"Twilio {r.status_code}: {r.text[:300]}")
    return r.json().get("sid", "?")


def send_lead_as_templates(lead_id: str, lead: dict, variants: list[str], dry_run: bool = False) -> list[str]:
    content_sid = _template_sid()
    if not content_sid:
        raise RuntimeError(
            "Konto trial wymaga szablonu, a TWILIO_TEMPLATE_SID nie jest ustawiony. "
            "Weź ContentSid (HX...) szablonu 'Order Notifications' z zakładki API "
            "w 'Try out WhatsApp' i wpisz do .env."
        )
    post = _var(lead.get("text", ""), 220)
    where = _var(f"{lead.get('group_name', '?')} · {lead.get('age_label', '?')}", 90)
    sids = []
    for i, v in enumerate(variants, 1):
        tail = f" — odpowiedz {lead_id} 1/2/3 lub {lead_id} 0" if i == len(variants) else ""
        detail = _var(f"WARIANT {i}: {v}{tail}", 700)
        link_note = _var(f"LINK: {lead.get('permalink', '')}", 160) if i == 1 else where
        sids.append(send_template(content_sid, {
            "1": lead_id, "2": post if i == 1 else f"{lead_id} cd.",
            "3": link_note, "4": detail,
        }, dry_run=dry_run))
    return sids


def _twilio_code(err: Exception) -> int | None:
    m = re.search(r'"code":\s*(\d+)', str(err))
    return int(m.group(1)) if m else None


def send_lead(lead_id: str, lead: dict, variants: list[str], dry_run: bool = False) -> list[str]:
    """Wolny tekst, a gdy Twilio go odrzuci (trial / poza oknem 24 h) — szablony."""
    try:
        return send_text(format_lead(lead_id, lead, variants), dry_run=dry_run)
    except RuntimeError as exc:
        if _twilio_code(exc) in TEMPLATE_FALLBACK_CODES:
            print(f"[whatsapp] wolny tekst odrzucony ({_twilio_code(exc)}), przełączam na szablon")
            return send_lead_as_templates(lead_id, lead, variants, dry_run=dry_run)
        raise


def send_alert(text: str, dry_run: bool = False) -> None:
    """Krótkie powiadomienie systemowe (np. sesja FB wygasła)."""
    send_text(f"ELEVATE BOT: {text}", dry_run=dry_run)


# --------------------------------------------------------------------------
# Odbiór odpowiedzi właściciela
# --------------------------------------------------------------------------

def fetch_replies(since: datetime | None) -> list[dict]:
    """Przychodzące wiadomości od WHATSAPP_TO nowsze niż `since` (UTC)."""
    sid, token, sender, to = _creds()
    since = since or (datetime.now(timezone.utc) - timedelta(days=3))
    params = {
        "To": sender,
        "From": to,
        "DateSent>": since.strftime("%Y-%m-%d"),
        "PageSize": 100,
    }
    r = requests.get(TWILIO_API.format(sid=sid), auth=(sid, token), params=params, timeout=30)
    if r.status_code >= 300:
        raise RuntimeError(f"Twilio {r.status_code}: {r.text[:300]}")
    out = []
    for m in r.json().get("messages", []):
        if not str(m.get("direction", "")).startswith("inbound"):
            continue
        created = parsedate_to_datetime(m["date_created"])
        if created <= since:
            continue
        out.append({"sid": m["sid"], "body": m.get("body", ""), "at": created})
    return sorted(out, key=lambda m: m["at"])


def parse_approvals(body: str) -> list[tuple[str, int]]:
    """'L7 2' -> [('L7', 2)]; 'l7-0' -> [('L7', 0)]; kilka w jednej wiadomości też działa."""
    return [(f"L{num}", int(var)) for num, var in APPROVAL_RE.findall(body or "")]


if __name__ == "__main__":
    demo_lead = {
        "market": "PL", "group_name": "Giełda sprzętu siłowego i fitness",
        "age_label": "5 godz.", "permalink": "https://www.facebook.com/groups/x/permalink/y/",
        "text": "Szukam puzzli na podłogę na siłownię około 130m2 + wysyłka",
    }
    demo_variants = ["Wariant pierwszy.", "Wariant drugi.", "Wariant trzeci."]
    print(format_lead("L1", demo_lead, demo_variants))
    print("\nParsowanie:", parse_approvals("L1 2"), parse_approvals("l1-0 i L2 3"))
