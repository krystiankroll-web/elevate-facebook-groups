"""Orkiestrator: zbierz -> zakwalifikuj -> wygeneruj warianty -> WhatsApp -> (po akceptacji) opublikuj.

Tryby:
    python run.py all       # pełny przebieg: odpowiedzi właściciela + nowe posty (4x dziennie)
    python run.py publish   # tylko sprawdź odpowiedzi na WhatsAppie i opublikuj zaakceptowane
    python run.py harvest   # tylko zbierz i wyślij nowe leady

Flagi: --dry-run (nic nie wysyła i nie publikuje), --headed (widoczna przeglądarka).
"""

from __future__ import annotations

import sys
import time
import traceback
from datetime import datetime, timezone

import config
import groups
from classifier import classify_post, is_qualified
from responder import generate_variants
from state import State
import fb_browser
import whatsapp_notifier as wa

MAX_LEADS_PER_RUN = 8       # więcej naraz na WhatsAppie to szum, nie pomoc
MAX_PUBLISH_PER_RUN = 3     # publikujemy jak człowiek, nie jak bot
PUBLISH_SPACING_SEC = 25


def log(msg: str) -> None:
    print(f"{datetime.now(timezone.utc).strftime('%H:%M:%S')} {msg}", flush=True)


# --------------------------------------------------------------------------
# 1. Odpowiedzi właściciela -> publikacja
# --------------------------------------------------------------------------

def process_replies(state: State, dry_run: bool, headed: bool) -> None:
    since = state.meta.get("last_reply_check")
    since_dt = datetime.fromisoformat(since) if since else None
    replies = wa.fetch_replies(since_dt)
    state.meta["last_reply_check"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    log(f"[replies] nowych wiadomości: {len(replies)}")

    for r in replies:
        for lead_id, variant_no in wa.parse_approvals(r["body"]):
            ok = state.approve(lead_id, variant_no)
            log(f"[replies] {lead_id} -> wariant {variant_no}: {'przyjęto' if ok else 'ODRZUCONO (nieznany lead albo już obsłużony)'}")

    pending = list(state.pending_approvals().items())[:MAX_PUBLISH_PER_RUN]
    for lead_id, lead in pending:
        text = lead["variants"][lead["chosen"] - 1]
        log(f"[publish] {lead_id} wariant {lead['chosen']} -> {lead['permalink']}")
        if dry_run:
            log(f"[publish] dry-run, treść:\n{text}")
            continue
        try:
            ok = fb_browser.publish_comment(lead["permalink"], text, headless=not headed, log=log)
            detail = "" if ok else "brak potwierdzenia na stronie"
        except fb_browser.SessionExpired as exc:
            wa.send_alert(str(exc))
            raise
        except Exception as exc:  # noqa: BLE001
            ok, detail = False, f"{type(exc).__name__}: {exc}"
        state.mark_published(lead_id, ok, detail)
        wa.send_text(
            f"{lead_id}: {'opublikowano wariant ' + str(lead['chosen']) if ok else 'NIE UDAŁO SIĘ opublikować — ' + detail}\n{lead['permalink']}"
        )
        state.save()
        time.sleep(PUBLISH_SPACING_SEC)


# --------------------------------------------------------------------------
# 2. Nowe posty -> kwalifikacja -> warianty -> WhatsApp
# --------------------------------------------------------------------------

def harvest_and_notify(state: State, dry_run: bool, headed: bool) -> None:
    monitored = groups.monitored()
    if config.GROUPS_LIMIT:
        monitored = monitored[: config.GROUPS_LIMIT]
    log(f"[harvest] grup: {len(monitored)}, okno: {config.MAX_POST_AGE_DAYS} dni, "
        f"budżet: {config.HARVEST_TIME_BUDGET_SEC}s")
    try:
        posts = fb_browser.harvest(
            monitored, config.SEARCH_QUERIES, config.MAX_POST_AGE_DAYS,
            max_per_query=config.MAX_POSTS_PER_QUERY, headless=not headed, log=log,
            time_budget_sec=config.HARVEST_TIME_BUDGET_SEC,
        )
    except fb_browser.SessionExpired as exc:
        wa.send_alert(str(exc), dry_run=dry_run)
        raise
    log(f"[harvest] świeżych postów: {len(posts)}")

    sent = 0
    for post in posts:
        if state.is_seen(post["permalink"]):
            continue
        state.mark_seen(post["permalink"], post["text"][:80])

        group = next((g for g in monitored if g["url"] == post["group_url"]), None)
        market = post["market"]
        cls = classify_post(post["text"], author=None, market=market)
        log(f"[classify] {'LEAD' if is_qualified(cls) else '----'} "
            f"conf={cls['confidence']:.2f} :: {post['text'][:70]}")
        if not is_qualified(cls):
            continue
        if sent >= MAX_LEADS_PER_RUN:
            log("[notify] limit leadów na przebieg — reszta poczeka do następnego")
            break

        try:
            variants = generate_variants(
                post["text"], cls, group=group, examples=state.examples_for(market)
            )
        except Exception as exc:  # noqa: BLE001
            log(f"[variants] błąd: {type(exc).__name__}: {exc}")
            continue

        lead_id = state.new_lead_id()
        lead = {**post, "classification": cls, "link_policy": (group or {}).get("link_policy")}
        state.add_lead(lead_id, lead, variants)
        wa.send_lead(lead_id, lead, variants, dry_run=dry_run)
        sent += 1
        state.save()
    log(f"[notify] wysłano leadów: {sent}")


# --------------------------------------------------------------------------

def main(argv: list[str]) -> int:
    mode = next((a for a in argv if a in ("all", "publish", "harvest")), "all")
    dry_run = "--dry-run" in argv
    headed = "--headed" in argv
    state = State()
    log(f"start mode={mode} dry_run={dry_run} tofu={config.TOFU_MODE}")
    try:
        if mode in ("all", "publish"):
            process_replies(state, dry_run, headed)
        if mode in ("all", "harvest"):
            harvest_and_notify(state, dry_run, headed)
    except Exception:  # noqa: BLE001
        traceback.print_exc()
        state.save()
        return 1
    state.save()
    log("koniec")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
