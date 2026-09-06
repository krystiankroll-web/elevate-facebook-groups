"""Test pętli WhatsApp na jednym prawdziwym leadzie — bez Facebooka, bez modelu.

    python test_whatsapp.py            # wysyła demo-lead i czeka 3 min na Twoją odpowiedź
    python test_whatsapp.py --dry-run  # tylko pokazuje wiadomość, nic nie wysyła

Sprawdza pełną drogę: Twilio -> Twój telefon -> Twoja odpowiedź "T1 2" -> odczyt
przez REST -> parser. Jeśli to przejdzie, cała reszta pipeline'u ma czym mówić.
Wymaga: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER, WHATSAPP_TO.
"""

from __future__ import annotations

import sys
import time
from datetime import datetime, timedelta, timezone

import whatsapp_notifier as wa

# Prawdziwy post z 2026-09-01 (Giełda sprzętu siłowego i fitness) i trzy warianty
# napisane dziś na Waszych realizacjach — dokładnie to, co będzie przychodzić.
LEAD = {
    "market": "PL",
    "group_name": "Giełda sprzętu siłowego i fitness",
    "age_label": "5 dni",
    "permalink": "https://www.facebook.com/groups/2106445906400441/permalink/2900685233643167/",
    "text": "Ma ktoś na sprzedaż podłogę pod siłownię? Chcę położyć gumową podłogę "
            "na płytki ceramiczne w domu żeby zrobić na tym siłownię.",
}
VARIANTS = [
    "Płytki nie są problemem, o ile trzymają się mocno - gorzej, gdy któraś klekocze, "
    "bo pod matą zacznie pękać. Grubość dobierz do sprzętu: 15 mm pod maszyny i trening "
    "funkcjonalny, 20 mm pod wolne ciężary. Tu 16 m2 w domu na puzzlach 15 mm: "
    "https://elevatestore.pl/realizacje/silownia-domowa-16m2-puzzle-premium",
    "Na płytki się kładzie, tylko sprawdź fugi - jeśli są głębokie, mata z czasem się "
    "w nie wypcha i zrobią się nierówności. Robiliśmy 70 m2 na trudnym podłożu, montaż "
    "zszedł w 5-6 godzin: "
    "https://elevatestore.pl/realizacje/montaz-podlogi-gumowej-mosaic-pro-15mm-trudne-podloze "
    "Napisz metraż i co ma stać.",
    "Najbliższa Twojej sytuacji realizacja to 16 m2 w domu na puzzlach 15 mm: "
    "https://elevatestore.pl/realizacje/silownia-domowa-16m2-puzzle-premium "
    "Na płytkach kluczowe jest, żeby żadna nie była luźna - puzzle wiernie kopiują "
    "to, co pod spodem. Jaki masz metraż?",
]
LEAD_ID = "T1"   # testowy, nie koliduje z L-numeracją produkcyjną


def main(argv: list[str]) -> int:
    dry = "--dry-run" in argv
    print(wa.format_lead(LEAD_ID, LEAD, VARIANTS))
    print("\n" + "=" * 60)
    if dry:
        print("dry-run: nic nie wysłano.")
        return 0

    started = datetime.now(timezone.utc) - timedelta(seconds=5)
    sids = wa.send_lead(LEAD_ID, LEAD, VARIANTS)
    print(f"Wysłano ({len(sids)} część/części). Odpisz na WhatsAppie: {LEAD_ID} 1, {LEAD_ID} 2 albo {LEAD_ID} 3.")
    print("Czekam do 3 minut na odpowiedź...")

    deadline = time.time() + 180
    while time.time() < deadline:
        time.sleep(10)
        for r in wa.fetch_replies(started):
            choices = wa.parse_approvals(r["body"])
            print(f"  odebrano: {r['body']!r} -> {choices or 'nie rozpoznano formatu'}")
            for lead_id, no in choices:
                if lead_id == f"L{LEAD_ID[1:]}" or lead_id == LEAD_ID:
                    msg = f"Wybór przyjęty: wariant {no}." if no else "Pominięto."
                    wa.send_text(f"{LEAD_ID}: {msg} (test, nic nie publikuję)")
                    print("  " + msg + " Pętla działa w obie strony.")
                    return 0
    print("Brak odpowiedzi w 3 minuty — wysyłka działa, odbiór do sprawdzenia "
          "(czy telefon dołączył do sandboxa Twilio?).")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
