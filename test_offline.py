"""Testy offline — bez API, bez przeglądarki, bez sieci.

    python test_offline.py

Sprawdzają logikę, którą da się sprawdzić na sucho: parsery, formatowanie,
białą listę linków, stan, konfigurację grup. Nie dotykają Playwrighta ani Twilio.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import types

# --- stub SDK, żeby import nie wymagał klucza ani pakietu ---
_stub = types.ModuleType("anthropic")


class _A:
    def __init__(self, **kw):
        pass


_stub.Anthropic = _A
sys.modules.setdefault("anthropic", _stub)
# requests jest potrzebny tylko do realnych wywołań Twilio — tu ich nie ma
sys.modules.setdefault("requests", types.SimpleNamespace(post=None, get=None))
sys.modules.setdefault("playwright", types.ModuleType("playwright"))
sys.modules.setdefault("playwright.sync_api", types.SimpleNamespace(sync_playwright=None))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config          # noqa: E402
import groups          # noqa: E402
import fb_browser      # noqa: E402
import whatsapp_notifier as wa  # noqa: E402
import responder       # noqa: E402
import classifier      # noqa: E402

FAILS = 0


def check(label: str, cond: bool, detail: str = "") -> None:
    global FAILS
    FAILS += not cond
    print(f"{'OK ' if cond else 'ZLE'} {label}{'  <- ' + detail if detail and not cond else ''}")


# 1. wiek posta
for label, lo, hi in [
    ("5 godz.", 0.19, 0.22), ("Wczoraj o 15:43", 1, 1), ("2 dni", 2, 2),
    ("12 min", 0, 0), ("1 dzień", 1, 1), ("3 tyg.", 21, 21),
]:
    v = fb_browser.parse_age_days(label)
    check(f"wiek '{label}' -> {v}", v is not None and lo <= v <= hi)
v = fb_browser.parse_age_days("30 sierpnia o 18:12")
check(f"wiek '30 sierpnia o 18:12' -> {v:.1f} dni (data absolutna)", v is not None and 5 <= v <= 40)
v = fb_browser.parse_age_days("6 lipca")
check(f"wiek '6 lipca' -> {v:.0f} dni (poza oknem)", v is not None and v > config.MAX_POST_AGE_DAYS)
check("wiek nieznany -> None", fb_browser.parse_age_days("bla") is None)

# 2. parser modalu
dialog = """Post Tomasz
Giełda sprzętu siłowego i fitness
Tomasz Sikora · Wczoraj o 15:43
Kupię puzzle 100x100cm na podłogę do siłowni 50-80 M2 , grubość 15-20mm. Opole
Lubię to!
13
Piotr Brot · 1 dzień
www.grand-fitness.pl
Odpowiedz
"""
info = fb_browser.parse_post_dialog(dialog)
check("modal: autor", info["author"] == "Tomasz Sikora", info["author"])
check("modal: czas", info["age_label"] == "Wczoraj o 15:43", info["age_label"])
check("modal: treść bez komentarzy", info["text"].startswith("Kupię puzzle") and "grand-fitness" not in info["text"], info["text"])

# 3. WhatsApp: format i parser odpowiedzi
lead = {"market": "PL", "group_name": "Giełda", "age_label": "5 godz.",
        "permalink": "https://www.facebook.com/groups/1/permalink/2/", "text": "Szukam puzzli 130 m2"}
msg = wa.format_lead("L7", lead, ["A", "B", "C"])
check("format: zawiera ID, link, 3 warianty i instrukcję",
      all(x in msg for x in ["LEAD L7", "permalink/2", "1) A", "2) B", "3) C", "L7 0"]))
check("parser: 'L7 2'", wa.parse_approvals("L7 2") == [("L7", 2)])
check("parser: 'l7-0'", wa.parse_approvals("l7-0") == [("L7", 0)])
check("parser: '7 3' bez L", wa.parse_approvals("7 3") == [("L7", 3)])
check("parser: kilka naraz", wa.parse_approvals("L1 2, L2 3") == [("L1", 2), ("L2", 3)])
check("parser: śmieci -> pusto", wa.parse_approvals("dzięki!") == [])
long = "\n\n".join(["x" * 700] * 4)
check("chunk: dzieli długie po akapitach", all(len(c) <= wa.MAX_CHARS for c in wa._chunk(long)))

# 4. responder: prompt i biała lista
p = responder._variants_prompt("PL", "limited", None)
check("prompt PL: zawiera siatkę grubości i realizacje", "20 mm" in p and "elevatestore.pl/realizacje" in p)
check("prompt PL: brak linków .de", "elevatestore.de" not in p)
pde = responder._variants_prompt("DE", "allowed", None)
check("prompt DE: język niemiecki, landingi .de", "niemiecki" in pde and "elevatestore.de/fitnessboeden" in pde)
ok_url = config.REALIZACJE[0]["url"]
check("whitelist: link z listy przechodzi",
      responder._check_links([f"tekst {ok_url}"] * 3, "PL", "limited")[0].endswith(ok_url))
try:
    responder._check_links(["tekst https://evil.example/x"] * 3, "PL", "limited")
    check("whitelist: obcy link odrzucony", False)
except ValueError:
    check("whitelist: obcy link odrzucony", True)
stripped = responder._check_links([f"tekst {ok_url}"] * 3, "PL", "banned")
check("banned: link usunięty", "http" not in stripped[0])
check("parse: tablica JSON", responder._parse_variants('["a","b","c"]') == ["a", "b", "c"])
check("parse: otoczka tekstowa", responder._parse_variants('Oto: ["a","b","c"] koniec') == ["a", "b", "c"])
try:
    responder._parse_variants('["a","b"]')
    check("parse: 2 warianty -> błąd", False)
except ValueError:
    check("parse: 2 warianty -> błąd", True)
ex = responder._examples_block([{"post": "P", "chosen": "C"}])
check("few-shot: przykłady trafiają do promptu", "Wybrana odpowiedź: C" in ex)

# 5. grupy
mon = groups.monitored()
check(f"monitored(): {len(mon)} grup", len(mon) == len(groups.MONITORED_URLS))
check("monitored(): każda ma market i link_policy", all(g.get("market") and g.get("link_policy") for g in mon))
check("monitored(): Giełda sprzętu siłowego = limited",
      next(g for g in mon if "2106445906400441" in g["url"])["link_policy"] == "limited")

# 6. stan (roundtrip w katalogu tymczasowym)
with tempfile.TemporaryDirectory() as d:
    os.environ["STATE_DIR"] = d
    import importlib
    import state as st
    importlib.reload(st)
    s = st.State()
    lid = s.new_lead_id()
    s.add_lead(lid, {"text": "Szukam puzzli", "permalink": "https://x/1", "market": "PL", "group_name": "G"}, ["a", "b", "c"])
    check("state: approve nieznany -> False", s.approve("L999", 1) is False)
    check("state: approve zły wariant -> False", s.approve(lid, 4) is False)
    check("state: approve 2 -> True", s.approve(lid, 2) is True)
    check("state: pending zawiera lead", lid in s.pending_approvals())
    s.mark_published(lid, True)
    check("state: feedback zapisany z wybranym wariantem", s.feedback and s.feedback[0]["chosen"] == "b")
    check("state: examples_for(PL)", len(s.examples_for("PL")) == 1 and s.examples_for("DE") == [])
    s.save()
    s2 = st.State()
    check("state: roundtrip po zapisie", lid in s2.leads and s2.leads[lid]["status"] == "published")
    check("state: seen działa", (s2.mark_seen("https://x/2"), s2.is_seen("https://x/2"))[1])

# 7. klasyfikator nadal działa po zmianach
ok, lvl = classifier._matches_keywords("Kupię puzzle 100x100cm na podłogę do siłowni 50-80 M2", "PL")
check("prefiltr: realny lead przechodzi jako strong", ok and lvl == "strong")

print(f"\n{'WSZYSTKO OK' if not FAILS else str(FAILS) + ' BŁĘDÓW'}")
sys.exit(1 if FAILS else 0)
