"""Jednorazowo: zaloguj się do Facebooka w oknie przeglądarki i zapisz sesję.

Uruchom lokalnie:
    python make_session.py

Otworzy się Chromium. Zalogujesz się SAM, jak zwykle — ten skrypt nie zna i nie
zapisuje hasła, zapisuje wyłącznie stan sesji po Twoim zalogowaniu. Gdy
zobaczysz tablicę, wróć do terminala i naciśnij Enter. Sesja trafi do
state/fb_storage_state.json.

Do GitHub Actions wklej ZAWARTOŚĆ tego pliku jako sekret FB_STORAGE_STATE.
Plik zawiera ciasteczka logowania — traktuj go jak hasło: nie commituj,
nie wysyłaj mailem. Jest w .gitignore.
"""

import os

from playwright.sync_api import sync_playwright

OUT = os.environ.get("FB_STORAGE_STATE_FILE", "state/fb_storage_state.json")


def main() -> None:
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        ctx = browser.new_context(locale="pl-PL", viewport={"width": 1280, "height": 900})
        page = ctx.new_page()
        page.goto("https://www.facebook.com/")
        input("\nZaloguj się w oknie przeglądarki, potem naciśnij Enter tutaj... ")
        page.goto("https://www.facebook.com/")
        page.wait_for_timeout(3000)
        if "login" in page.url:
            print("Nadal ekran logowania — sesja NIE została zapisana.")
        else:
            ctx.storage_state(path=OUT)
            print(f"Zapisano sesję do {OUT}")
            print("GitHub: Settings -> Secrets and variables -> Actions -> "
                  "New secret FB_STORAGE_STATE = zawartość tego pliku.")
        browser.close()


if __name__ == "__main__":
    main()
