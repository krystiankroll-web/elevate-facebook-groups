# Elevate Store — agent do grup na Facebooku

Dwuetapowy pipeline: tani klasyfikator odsiewa szum, drogi model pisze odpowiedź
tylko dla realnych leadów.

```
post FB → prefiltr słów kluczowych → classifier.py (Haiku) → responder.py (Sonnet) → komentarz do akceptacji
```

## Pliki

| Plik | Rola |
|---|---|
| `config.py` | marka, URL, słowa kluczowe, modele, progi, kontekst produktowy, persona |
| `classifier.py` | `classify_post()` → `{is_lead, confidence, reason}` |
| `responder.py` | `generate_response()` → treść komentarza (2–4 zdania) |

## Uruchomienie

```bash
cd ~/elevate_facebook_groups
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY='sk-ant-...'
python classifier.py    # test klasyfikacji na 5 przykładach
python responder.py     # pełny przebieg: klasyfikacja + odpowiedź
```

## Użycie w kodzie

```python
from classifier import classify_post, is_qualified
from responder import generate_response

result = classify_post(post_text)
if is_qualified(result):
    draft = generate_response(post_text, result)
```

## Strojenie

- `CONFIDENCE_THRESHOLD` (domyślnie 0.7) — niżej = więcej leadów i więcej fałszywych trafień.
- `USE_KEYWORD_PREFILTER` — `False` wyłącza prefiltr: droższe, ale łapie nietypowe sformułowania.
- `PRODUCT_CONTEXT` — jedyne źródło faktów dla respondera. Cokolwiek tu wpiszesz, model uzna za prawdę i może użyć publicznie. Nie wpisuj cen ani terminów.
- `PERSONA_RULES` — ton i zakazy. Zmiana tutaj natychmiast zmienia styl odpowiedzi.

## Czego tu nie ma i dlaczego

Nie ma warstwy pobierania postów z Facebooka ani automatycznego publikowania.
Scraping i automatyczne komentowanie łamią regulamin Facebooka i grożą blokadą
konta oraz strony firmowej. Moduły są zaprojektowane tak, żeby karmić je tekstem
z legalnego źródła (ręczne wklejenie, eksport, Graph API dla własnych grup),
a wygenerowany komentarz publikował człowiek po akceptacji.

Rekomendacja: trzymaj `generate_response()` jako generator draftów w kolejce do
zatwierdzenia. Odpowiedź podpisana jako doradca Elevate Store jest jawną obecnością
marki — to działa tylko wtedy, gdy jest naprawdę pomocna. Automat wysyłający
komentarze pod każdy pasujący post spali markę w grupach w tydzień.

## Dwa rynki: PL i DE

`elevatestore.de` to osobny sklep — polski landing nie ma wersji niemieckiej,
więc linkowanie go Niemcom jest błędem. Rynek wybiera się parametrem:

```python
classify_post(post, market="DE")
generate_response(post, result, market="DE")
```

Co zmienia `market="DE"`: język odpowiedzi, listę słów kluczowych prefiltru,
kontekst produktowy i pulę linków. Dla DE model wybiera jeden z pięciu landingów
(`club`, `homegym`, `crossfit`, `deadlift`, `plates`) zamiast jednego sztywnego
URL-a. Prompty są od siebie odizolowane — sprawdzone: w promptcie PL nie ma
ani jednego linku `.de`, w DE ani jednego `.pl`.

Nieznany kod rynku podnosi `ValueError` zamiast po cichu wracać do PL.

## Tryb TOFU

`config.TOFU_MODE = True` — decyzja biznesowa: jesteśmy na górze lejka, więc
łapiemy szeroko i odpowiadamy na wszystko, co daje jakąkolwiek szansę.

Co robi:
- prefiltr przepuszcza post, jeśli trafi w *cokolwiek* — rdzeń tematyczny
  (`gum`, `mata`, `hałas`) albo sam kontekst (`atlas`, `garaż`, `remont`).
  Odsiewa już tylko oczywisty off-top: dieta, suplementy, plany treningowe,
  praca, wydarzenia;
- próg pewności spada z 0.7 na **0.35**;
- klasyfikator dostaje instrukcję, żeby przy wahaniu wybierać `is_lead = true`,
  a odrzucać wyłącznie jednoznaczne nie-leady (sprzedający, konkurencja,
  całkowity off-top).

Skutek uboczny: do modelu trafia znacznie więcej postów i rośnie liczba
fałszywych trafień do ręcznego przejrzenia. Przy obecnym wolumenie
(kilkadziesiąt postów dziennie na grupę) koszt Haiku jest pomijalny, a
przegapiony lead kosztuje realnie — pomiar pokazał, że leadów jest kilka
na miesiąc, więc każdy się liczy.

Wyłączenie: `TOFU_MODE = False` przywraca próg 0.7 i wymóg kontekstu.

## Wersja chmurowa: WhatsApp + GitHub Actions

Pętla:

```
GitHub Actions (4x/dzień)
  └─ fb_browser.harvest()      wyszukiwarka wewnątrz grup, sesja z FB_STORAGE_STATE
  └─ classifier                prefiltr rdzeniowy + Haiku (tryb TOFU)
  └─ responder.generate_variants()   3 warianty, realizacja z listy, link z białej listy
  └─ whatsapp_notifier.send_lead()   "LEAD L7 · grupa · wiek · treść · link · 1) 2) 3)"

Ty odpisujesz na WhatsAppie:  L7 2      (albo L7 0 = pomiń)

GitHub Actions (co 30 min)
  └─ whatsapp_notifier.fetch_replies()   pobiera Twoje odpowiedzi z Twilio
  └─ fb_browser.publish_comment()        wpisuje DOKŁADNIE wybrany wariant pod postem L7
  └─ state/feedback.json                 zapamiętuje wybór -> kolejne warianty uczą się Twojego stylu
```

Pliki: `run.py` (orkiestracja), `fb_browser.py` (Playwright), `whatsapp_notifier.py`
(Twilio REST, bez SDK), `state.py` (trwały stan w `state/*.json`, commitowany do repo),
`make_session.py` (jednorazowe zapisanie sesji FB), `.github/workflows/scheduler.yml`.

### Uruchomienie

1. Lokalnie, raz: `pip install -r requirements.txt && playwright install chromium`,
   potem `python make_session.py` — logujesz się sam w oknie, skrypt zapisuje
   `state/fb_storage_state.json` (jest w `.gitignore`).
2. Repozytorium na GitHubie (publiczne = darmowe minuty; prywatne — patrz
   komentarz w `scheduler.yml`). Sekrety w *Settings → Secrets → Actions*:
   `ANTHROPIC_API_KEY`, `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`,
   `TWILIO_WHATSAPP_NUMBER` (np. `whatsapp:+14155238886`), `WHATSAPP_TO`
   (np. `whatsapp:+48600000000`), `FB_STORAGE_STATE` (zawartość pliku z pkt 1).
3. Twilio: w sandboxie WhatsApp wyślij z telefonu kod dołączenia do numeru sandboxa,
   inaczej nie dostaniesz wiadomości. Produkcyjnie — zatwierdzony nadawca WhatsApp Business.
4. Pierwszy test: *Actions → Elevate FB groups → Run workflow → mode: all, dry_run: true*.
   Logi pokażą, ile postów zebrano i jakie warianty powstały, bez wysyłki.

### Bezpieczniki

- Publikacja tylko po Twojej odpowiedzi, tylko wybrany wariant, raz na lead,
  maks. 3 na przebieg, z odstępem 25 s.
- Link w komentarzu wyłącznie z białej listy (realizacje + landingi). Model, który
  poda inny adres, jest odrzucany, nie poprawiany.
- Grupy z zakazem linków i grupy bez sprawdzonego regulaminu -> warianty bez linku.
- Wygasła sesja FB -> alert na WhatsApp i czerwony przebieg w Actions, żadnych cichych błędów.

### Ryzyko, które przyjmujesz świadomie

Automatyczny dostęp do konta łamie regulamin Facebooka. Sesja w sekrecie GitHuba
to pełny dostęp do Twojego konta dla każdego, kto ma dostęp do repo. Facebook
potrafi zażądać ponownego logowania przy zmianie adresu IP (runner GitHuba jest
w USA) — wtedy dostaniesz alert i trzeba odświeżyć sesję przez `make_session.py`.

## Grupy do monitorowania

`groups.py` — 14 kandydatów (7 PL) z researchu 2026-09-05, plus lista 6 grup
sprawdzonych i odrzuconych. `python groups.py` drukuje ranking.

Ograniczenie, o którym trzeba pamiętać: Facebook zasłania liczbę członków i
regulamin grupy loginem. Potwierdzone są tylko nazwy grup oznaczonych
`name_verified=True`. Priorytety to ocena dopasowania tematycznego, nie
zmierzony zasięg — przed wdrożeniem każdą grupę trzeba otworzyć ręcznie,
przeczytać regulamin i ustawić `rules_checked=True`.
