"""Facebook przez Playwright: zbieranie postów z wyszukiwarki grup i publikacja komentarzy.

Działa na ZAPISANEJ SESJI właściciela (storage_state z Playwright). To jest
automatyczny dostęp do konta — regulamin Facebooka tego nie dopuszcza, decyzja
o użyciu należy do właściciela konta i została podjęta świadomie. Kod zachowuje
się jak człowiek (opóźnienia, limity, publikacja tylko po akceptacji), ale
ryzyka nie zeruje.

Selektory Facebooka zmieniają się bez ostrzeżenia. Wszystko, co dotyka DOM,
jest w tym jednym pliku i loguje, co znalazło — żeby awarię było widać od razu.
"""

from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

import config

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    sync_playwright = None


class SessionExpired(RuntimeError):
    """Facebook pokazał ekran logowania — storage_state jest nieaktualny."""


# --------------------------------------------------------------------------
# Sesja
# --------------------------------------------------------------------------

def _storage_state():
    if config.FB_STORAGE_STATE:
        return json.loads(config.FB_STORAGE_STATE)
    if os.path.isfile(config.FB_STORAGE_STATE_FILE):
        return config.FB_STORAGE_STATE_FILE
    raise RuntimeError(
        "Brak sesji Facebooka. Ustaw FB_STORAGE_STATE (JSON) albo wygeneruj plik "
        f"{config.FB_STORAGE_STATE_FILE} przez make_session.py."
    )


def _open(p, headless: bool = True):
    browser = p.chromium.launch(headless=headless)
    ctx = browser.new_context(
        storage_state=_storage_state(),
        locale="pl-PL",
        timezone_id="Europe/Warsaw",
        viewport={"width": 1280, "height": 900},
    )
    page = ctx.new_page()
    page.set_default_timeout(20_000)
    return browser, ctx, page


def _assert_logged_in(page) -> None:
    page.goto("https://www.facebook.com/", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    if "login" in page.url or page.locator('input[name="email"]').count():
        raise SessionExpired("Facebook żąda logowania — odśwież FB_STORAGE_STATE.")


# --------------------------------------------------------------------------
# Wiek posta z polskiego UI Facebooka
# --------------------------------------------------------------------------

_MONTHS = {
    "stycznia": 1, "lutego": 2, "marca": 3, "kwietnia": 4, "maja": 5, "czerwca": 6,
    "lipca": 7, "sierpnia": 8, "września": 9, "października": 10,
    "listopada": 11, "grudnia": 12,
}


def parse_age_days(label: str, now: datetime | None = None) -> float | None:
    """'5 godz.' -> 0.2, 'Wczoraj o 15:43' -> 1, '2 dni' -> 2, '30 sierpnia o 18:12' -> N."""
    now = now or datetime.now(timezone.utc)
    s = (label or "").strip().lower()
    if not s:
        return None
    if re.search(r"\b\d+\s*min\b", s) or "przed chwilą" in s or s == "teraz":
        return 0.0
    m = re.search(r"\b(\d+)\s*godz", s)
    if m:
        return int(m.group(1)) / 24
    if "wczoraj" in s:
        return 1.0
    m = re.search(r"\b(\d+)\s*(dzie[nń]|dni)\b", s)
    if m:
        return float(m.group(1))
    m = re.search(r"\b(\d+)\s*tyg", s)
    if m:
        return int(m.group(1)) * 7.0
    m = re.search(r"\b(\d{1,2})\s+([a-ząćęłńóśźż]+)(?:\s+(\d{4}))?", s)
    if m and m.group(2) in _MONTHS:
        day, month = int(m.group(1)), _MONTHS[m.group(2)]
        year = int(m.group(3)) if m.group(3) else now.year
        try:
            dt = datetime(year, month, day, tzinfo=timezone.utc)
        except ValueError:
            return None
        if dt > now + timedelta(days=1):  # np. "30 grudnia" czytane w styczniu
            dt = dt.replace(year=year - 1)
        return (now - dt).total_seconds() / 86400
    return None


# --------------------------------------------------------------------------
# Parsowanie modalu posta
# --------------------------------------------------------------------------

_STOP = re.compile(
    r"^(Lubię to!|Skomentuj|Udostępnij|Odpowiedz|Wszystkie reakcje|Wyświetl (więcej|\d+)|"
    r"Napisz komentarz|Skomentuj jako|Odpowiedz jako|\d+\s*(komentarz|komentarzy|odpowiedzi)?)$",
    re.IGNORECASE,
)


def parse_post_dialog(text: str) -> dict:
    """Z innerText modalu wyciąga autora, znacznik czasu i treść posta."""
    lines = [l.strip() for l in (text or "").splitlines() if l.strip()]
    author, age_label, body = "", "", []
    i = 0
    for i, line in enumerate(lines):
        if " · " in line and len(line) < 120:
            left, right = line.split(" · ", 1)
            if parse_age_days(right) is not None:
                author, age_label = left.strip(), right.strip()
                break
    for line in lines[i + 1:]:
        if _STOP.match(line) or line.startswith("Może być zdjęciem") or line == "Udostępniony post":
            if body:
                break
            continue
        body.append(line)
        if sum(len(b) for b in body) > 1500:
            break
    return {"author": author, "age_label": age_label, "text": " ".join(body).strip()}


# --------------------------------------------------------------------------
# Zbieranie
# --------------------------------------------------------------------------

_COMMENT_BTN = re.compile(r"koment|comment", re.IGNORECASE)


def harvest(groups: list[dict], queries: dict[str, list[str]], max_age_days: float,
            max_per_query: int = 12, headless: bool = True, log=print) -> list[dict]:
    """Przechodzi wyszukiwarkę każdej grupy i zwraca świeże posty z permalinkami."""
    if sync_playwright is None:
        raise RuntimeError("Brak playwright: pip install playwright && playwright install chromium")

    found: dict[str, dict] = {}
    with sync_playwright() as p:
        browser, ctx, page = _open(p, headless=headless)
        try:
            _assert_logged_in(page)
            for g in groups:
                for q in queries.get(g["market"], []):
                    url = f"{g['url'].rstrip('/')}/search/?q={quote(q)}"
                    log(f"[harvest] {g['name'][:40]} :: {q}")
                    page.goto(url, wait_until="domcontentloaded")
                    page.wait_for_timeout(4500)
                    for _ in range(3):
                        page.mouse.wheel(0, 1600)
                        page.wait_for_timeout(1200)
                    page.mouse.wheel(0, -20000)
                    page.wait_for_timeout(800)

                    buttons = page.get_by_role("button", name=_COMMENT_BTN)
                    total = buttons.count()
                    n = min(total, max_per_query)
                    log(f"[harvest]   przycisków komentarza: {total}, sprawdzam {n}")
                    for i in range(n):
                        try:
                            buttons.nth(i).scroll_into_view_if_needed()
                            buttons.nth(i).click()
                            page.wait_for_timeout(2500)
                            permalink = page.url.split("?")[0]
                            if "/permalink/" not in permalink and "/posts/" not in permalink:
                                continue
                            dialog = page.get_by_role("dialog").last
                            info = parse_post_dialog(dialog.inner_text())
                            age = parse_age_days(info["age_label"])
                            if age is not None and age <= max_age_days and info["text"]:
                                found.setdefault(permalink, {
                                    **info, "permalink": permalink, "age_days": age,
                                    "group_name": g["name"], "group_url": g["url"],
                                    "market": g["market"], "query": q,
                                })
                        except Exception as exc:  # noqa: BLE001
                            log(f"[harvest]   pominięto element {i}: {type(exc).__name__}")
                        finally:
                            page.keyboard.press("Escape")
                            page.wait_for_timeout(900)
                    time.sleep(2)
        finally:
            ctx.close()
            browser.close()
    return list(found.values())


# --------------------------------------------------------------------------
# Publikacja komentarza (wyłącznie po akceptacji właściciela)
# --------------------------------------------------------------------------

def publish_comment(permalink: str, text: str, headless: bool = True, log=print) -> bool:
    """Wpisuje komentarz pod postem i weryfikuje, że pojawił się na stronie."""
    if sync_playwright is None:
        raise RuntimeError("Brak playwright")
    probe = text[:60]
    with sync_playwright() as p:
        browser, ctx, page = _open(p, headless=headless)
        try:
            _assert_logged_in(page)
            page.goto(permalink, wait_until="domcontentloaded")
            page.wait_for_timeout(4500)
            box = page.get_by_role(
                "textbox", name=re.compile(r"(Skomentuj|Odpowiedz) jako", re.I)
            ).first
            box.scroll_into_view_if_needed()
            box.click()
            page.wait_for_timeout(800)
            page.keyboard.type(text, delay=18)
            page.wait_for_timeout(1500)
            page.keyboard.press("Enter")
            page.wait_for_timeout(6000)
            body = page.inner_text("body")
            ok = probe in body and "Publikowanie" not in body
            if not ok:
                page.wait_for_timeout(5000)
                body = page.inner_text("body")
                ok = probe in body
            log(f"[publish] {'OK' if ok else 'NIE POTWIERDZONO'} :: {permalink}")
            return ok
        finally:
            ctx.close()
            browser.close()


if __name__ == "__main__":
    for s in ["5 godz.", "Wczoraj o 15:43", "2 dni", "30 sierpnia o 18:12", "6 lipca", "12 min"]:
        print(f"{s:<22} -> {parse_age_days(s)}")
