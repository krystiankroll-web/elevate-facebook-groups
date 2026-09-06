"""Konfiguracja agenta monitorującego grupy FB dla Elevate Store."""

import os


def _load_dotenv(path: str = ".env") -> None:
    """Wczytuje KLUCZ=wartość z .env do środowiska, jeśli plik istnieje.

    Bez zależności. Zmienne już ustawione w środowisku mają pierwszeństwo,
    więc w GitHub Actions (sekrety) plik jest ignorowany, a lokalnie wystarczy
    wkleić wartości do .env zamiast eksportować je w terminalu.
    """
    here = os.path.join(os.path.dirname(os.path.abspath(__file__)), path)
    if not os.path.isfile(here):
        return
    with open(here, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            key, val = key.strip(), val.strip().strip("'\"")
            if key and val and key not in os.environ:
                os.environ[key] = val


_load_dotenv()

# --- Marka i cel ---------------------------------------------------------

BRAND_NAME = "Elevate Store"

TARGET_URL = "https://elevatestore.pl/podloga-na-silownie-otwarcie-nowego-klubu-fitness"

KEYWORDS = [
    "maty gumowe",
    "puzzle gumowe",
    "podłoga na siłownię",
    "nawierzchnia gumowa",
    "guma do strefy ciężarów",
    "szukam podłogi",
    "polecicie maty",
    "otwieram siłownię",
    "studio fitness",
]

# Rozszerzenie wynikające z researchu grup (2026-09-05): w grupach handlowych
# i home-gymowych ludzie prawie nigdy nie piszą "nawierzchnia gumowa" — piszą
# "co pod sztangę" albo "sąsiedzi się skarżą". Bez tych fraz prefiltr wycinał
# większość realnych leadów, zanim dotarły do modelu.
# Wyłącz przez USE_MARKETPLACE_KEYWORDS = False, jeśli chcesz wrócić do
# pierwotnej, wąskiej listy.
KEYWORDS_MARKETPLACE = [
    "co pod sztangę",
    "pod sztangę",
    "co położyć",
    "jaka podłoga",
    "podłoga do garażu",
    "siłownia w garażu",
    "home gym",
    "urządzam siłownię",
    "remont siłowni",
    "wykładzina sportowa",
    "mata pod",
    "kupię maty",
    "hałas",
    "wygłuszenie",
    "sąsiedzi",
    "chronić podłogę",
    "niszczy podłogę",
    "wylewka",
    "strefa wolnych ciężarów",
    "platforma do podnoszenia",
    "box crossfit",
]

USE_MARKETPLACE_KEYWORDS = True

# Lista faktycznie używana przez prefiltr.
ACTIVE_KEYWORDS = KEYWORDS + (KEYWORDS_MARKETPLACE if USE_MARKETPLACE_KEYWORDS else [])

# --- Modele --------------------------------------------------------------

MODEL_CLASSIFIER = "claude-haiku-4-5-20251001"  # tanio i szybko: filtr wstępny
MODEL_RESPONDER = "claude-sonnet-5"             # jakość językowa: odpowiedź publiczna

MAX_TOKENS_CLASSIFIER = 300
MAX_TOKENS_RESPONDER = 400

# --- Progi decyzyjne -----------------------------------------------------

# TRYB TOFU (top of funnel) — decyzja biznesowa, nie techniczna.
# Włączony: łapiemy szeroko i odpowiadamy na wszystko, co daje jakąkolwiek
# szansę. Kosztem jest więcej fałszywych trafień do ręcznego przejrzenia.
# Wyłączony: wąsko i precyzyjnie, dla kanału o dużym wolumenie.
TOFU_MODE = True

# Poniżej tego progu post trafia do kolejki "do ręcznej oceny", nie do odpowiedzi.
# W TOFU celowo nisko: wolimy obejrzeć dziesięć niepewnych niż przegapić jeden
# realny. Pomiar z 2026-09-05 pokazał, że realnych leadów jest kilka na miesiąc
# — przy takiej rzadkości każdy przegapiony boli bardziej niż fałszywy alarm.
CONFIDENCE_THRESHOLD = 0.35 if TOFU_MODE else 0.7

# Jeśli True, posty bez żadnego słowa kluczowego są odrzucane bez wywołania API.
# Oszczędza koszt na grupach z dużym ruchem, ale gubi nietypowe sformułowania.
USE_KEYWORD_PREFILTER = True

# --- Kontekst produktowy dla respondera -----------------------------------

# Tylko fakty, które można publicznie powtórzyć. Nie wpisuj tu cen ani obietnic
# terminów — model potraktuje to jako prawdę i użyje w odpowiedzi.
PRODUCT_CONTEXT = """\
Elevate Store dostarcza nawierzchnie gumowe do siłowni, klubów fitness i stref
crossfit. Asortyment: maty gumowe i puzzle gumowe (typowe grubości 10-15 mm pod
cardio i strefę ogólną, 20-30 mm i więcej pod strefę wolnych ciężarów oraz
platformy do podnoszenia), rolki gumowe, wykładziny sportowe.

Kluczowe zasady doboru, o których warto mówić merytorycznie:
- grubość dobiera się do obciążenia strefy, nie do całej sali naraz,
- pod ciężary olimpijskie i deadlift potrzebna jest większa grubość lub
  dedykowana platforma, żeby chronić posadzkę i ograniczyć hałas,
- podłoże musi być równe i suche; nierówności przenoszą się na matę,
- puzzle są szybkie w montażu i łatwe do wymiany pojedynczego elementu,
  rolki dają mniej łączeń na dużych powierzchniach,
- gęstość i jakość granulatu wpływa na trwałość i zapach bardziej niż sama cena.
"""

# --- Zasady wypowiedzi (persona) -----------------------------------------

PERSONA_RULES = """\
- Piszesz jako doradca techniczny ds. nawierzchni sportowych z Elevate Store.
- Nie ukrywasz, skąd jesteś, ale nie zaczynasz od autopromocji.
- Najpierw realna pomoc: konkretna wskazówka techniczna odpowiadająca na pytanie.
- Dopiero na końcu jedno naturalne zdanie z rekomendacją i linkiem.
- 2-4 zdania. Bez emotikon, bez wykrzykników, bez sloganów marketingowych.
- Nie podajesz cen, terminów dostaw ani rabatów.
- Nie wymyślasz parametrów produktów, których nie masz w kontekście.
- Ton: spokojny, rzeczowy, jak człowiek z branży piszący z telefonu.
"""

# --- Prefiltr: dopasowanie po rdzeniach, nie po pełnych frazach -------------
#
# Pomiar na żywej próbce (102 posty z grupy "Siłownia w Domu", 2026-09-05)
# pokazał, że dopasowanie po pełnych frazach nie działa w polskim. Realny lead
# brzmiał "Polecicie jakąś solidną podłogę do siłowni grubości 15-20mm" i nie
# trafiło w niego ŻADNE z 30 skonfigurowanych słów kluczowych, bo mamy
# "podłoga na siłownię", a człowiek odmienił: "podłogę do siłowni".
#
# Dlatego dopasowujemy rdzenie z granicą słowa, na tekście pozbawionym
# ogonków. Dwa poziomy:
#   STRONG  - sam w sobie wystarcza (podłoga, nawierzchnia, wygłuszenie)
#   WEAK    - łapie tylko w parze z CONTEXT, bo osobno generuje śmieci
#             ("gumy oporowe", "guma mu pękła" - oba były w próbce)

PREFILTER = {
    "PL": {
        "strong": [
            r"\bpodlog\w*", r"\bpodloz\w*", r"\bnawierzchn\w*",
            r"\bwykladzin\w*", r"\bwyglusz\w*",
            r"\bmat\w*\s+gumow\w*", r"\bgumow\w*\s+mat\w*",
            r"\bpuzzl\w*\s+gum\w*",
            r"\bpomost\w*\s+do\s+podnosz\w*",
            r"\bplatform\w*\s+do\s+podnosz\w*",
            r"\bstref\w*\s+wolnych\s+ciezar\w*",
        ],
        "weak": [
            r"\bgum\w*", r"\bmat[ay]\w*", r"\bhalas\w*",
            r"\bsasiad\w*", r"\bsasiedz\w*", r"\bsasiedzk\w*",
            r"\bwylewk\w*", r"\bkafelk\w*", r"\bstyropian\w*",
            r"\bwibracj\w*", r"\bdudni\w*",
        ],
        "context": [
            r"\bsilown\w*", r"\bgym\w*", r"\bgaraz\w*", r"\bpiwnic\w*",
            r"\bstrop\w*", r"\bsztang\w*", r"\bciezar\w*", r"\bhantl\w*",
            r"\bpodlog\w*", r"\bklub\w*", r"\bbox\w*", r"\bcrossfit\w*",
            r"\bbiezn\w*", r"\batlas\w*", r"\brack\w*", r"\bstojak\w*",
            r"\bmieszkan\w*", r"\bstref\w*",
            r"\bmartw\w*\s+ciag\w*", r"\bprzysiad\w*", r"\bwyciskan\w*",
            r"\bpomost\w*", r"\bmaszyn\w*", r"\bwyposaz\w*", r"\bremont\w*",
        ],
    },
    "DE": {
        "strong": [
            r"\bboden\w*", r"\bbodenbelag\w*", r"\bbodenschutzmatt\w*",
            r"\bgummimatt\w*", r"\bgummibod\w*", r"\bfitnessbod\w*",
            r"\bsportbod\w*", r"\btrittschall\w*", r"\bschallisolier\w*",
            r"\bschallschutz\w*", r"\bkreuzheb\w*\s+matt\w*",
        ],
        "weak": [
            r"\bgummi\w*", r"\bmatt\w*", r"\blarm\w*", r"\bnachbarn\w*",
            r"\bestrich\w*", r"\blaut\b",
        ],
        "context": [
            r"\bgym\w*", r"\bhomegym\w*", r"\bgarage\w*", r"\bkeller\w*",
            r"\bstudio\w*", r"\bhantel\w*", r"\bkreuzheb\w*",
            r"\bfreihantel\w*", r"\bbox\w*", r"\bfitnessstudio\w*",
            r"\brack\w*", r"\bmaschine\w*", r"\beroffn\w*", r"\bumbau\w*",
            r"\brenovier\w*", r"\btrainingsraum\w*", r"\blanghantel\w*",
        ],
    },
}

# --- Rynek niemiecki (elevatestore.de) --------------------------------------

# Wszystkie URL-e poniżej to linki dosłownie obecne w nawigacji elevatestore.de
# (sprawdzone 2026-09-05). Sklep DE jest osobnym serwisem — landing z
# TARGET_URL (.pl) nie ma wersji niemieckiej, więc nie wolno go podawać Niemcom.
TARGET_URL_DE = "https://elevatestore.de/fitnessboeden-fuer-fitnessstudios-und-fitnessclubs"

# Niemiecki odpowiednik landingu "otwarcie nowego klubu" jeszcze nie istnieje.
# Do czasu publikacji duże zapytania z DE (otwarcie klubu, cały obiekt) idą na
# kategorię dla klubów powyżej. Gdy landing wejdzie, wpisz go tutaj i dopisz do
# TARGET_URLS_DE pod kluczem "club" — nic więcej nie trzeba zmieniać.
TARGET_URL_DE_LANDING = None  # TODO: podmienić po publikacji wersji DE

TARGET_URLS_DE = {
    "club": "https://elevatestore.de/fitnessboeden-fuer-fitnessstudios-und-fitnessclubs",
    "homegym": "https://elevatestore.de/fitnessboeden-fuers-homegym",
    "crossfit": "https://elevatestore.de/crossfit-boeden",
    "deadlift": "https://elevatestore.de/kreuzheben-matten",
    "plates": "https://elevatestore.de/olympia-hantelscheiben",
}

KEYWORDS_DE = [
    "gummimatten",
    "gummiboden",
    "bodenschutzmatten",
    "fitnessboden",
    "sportboden",
    "bodenbelag",
    "matten fürs homegym",
    "homegym boden",
    "garage gym boden",
    "was für einen boden",
    "welcher boden",
    "boden für",
    "kreuzheben matte",
    "hantelscheiben schutz",
    "estrich",
    "schallschutz",
    "schallisolierung",
    "trittschall",
    "nachbarn beschweren",
    "zu laut",
    "lärm",
    "studio eröffnen",
    "fitnessstudio eröffnen",
    "box eröffnen",
    "freihantelbereich",
    "hantelbereich",
]

PRODUCT_CONTEXT_DE = """\
Elevate Store (elevatestore.de) ist ein polnischer Hersteller von Gummiböden
für Fitnessstudios, Fitnessclubs, CrossFit-Boxen und Homegyms und liefert nach
Deutschland.

Sortimentskategorien (so heißen sie im Shop):
- Fitnessböden für Fitnessstudios und Fitnessclubs
- Matten für das Homegym
- CrossFit-Böden
- Kreuzheben-Matten
- Olympia-Hantelscheiben

Fachliche Grundsätze, die du frei erklären darfst:
- Die Stärke richtet sich nach der Zone, nicht nach der ganzen Fläche.
- Für Freihantelbereich und Kreuzheben braucht es mehr Stärke oder eine eigene
  Plattform, um Estrich und Nachbarn zu schützen.
- Der Untergrund muss eben und trocken sein; Unebenheiten drücken durch.
- Puzzlematten sind schnell verlegt und einzeln austauschbar, Rollenware hat
  auf großen Flächen weniger Fugen.
- Für Obergeschosse ist Trittschall das eigentliche Thema — hier zählt der
  Aufbau, nicht nur die Mattenstärke. Referenz: 310 m² Studio-Schallisolierung
  mit Antishock-Matten 43 mm (Case Study auf elevatestore.de).
"""

PERSONA_RULES_DE = """\
- Du schreibst als technischer Berater für Sportböden von Elevate Store.
- Du antwortest auf Deutsch, sachlich und knapp, wie jemand aus der Branche.
- Zuerst echte Hilfe: eine konkrete fachliche Antwort auf die gestellte Frage.
- Erst am Ende ein natürlicher Hinweis auf die Lösung mit Link.
- 2-4 Sätze. Keine Emojis, keine Ausrufezeichen, keine Werbefloskeln.
- Keine Preise, keine Lieferzeiten, keine Rabatte.
- Keine erfundenen Produktdaten.
"""

# --- Rejestr rynków --------------------------------------------------------

MARKETS = {
    "PL": {
        "language": "polski",
        "default_url": TARGET_URL,
        "urls": {"default": TARGET_URL},
        "keywords": ACTIVE_KEYWORDS,
        "prefilter": PREFILTER["PL"],
        "product_context": PRODUCT_CONTEXT,
        "persona_rules": PERSONA_RULES,
    },
    "DE": {
        "language": "niemiecki",
        "default_url": TARGET_URL_DE,
        "urls": TARGET_URLS_DE,
        "keywords": KEYWORDS_DE,
        "prefilter": PREFILTER["DE"],
        "product_context": PRODUCT_CONTEXT_DE,
        "persona_rules": PERSONA_RULES_DE,
    },
}


def market(code: str = "PL") -> dict:
    """Zwraca konfigurację rynku. Nieznany kod = błąd, nie cichy fallback na PL."""
    try:
        return MARKETS[code.upper()]
    except KeyError:
        raise ValueError(
            f"Nieznany rynek: {code!r}. Dostępne: {', '.join(MARKETS)}"
        ) from None


# --- Realizacje (źródło: elevatestore.pl/realizacje, odczyt 2026-09-05) -----
#
# To jest jedyna lista, z której responder może cytować realizacje. Model
# dostaje ją w prompcie i ma obowiązek podać URL DOSŁOWNIE z tej listy albo
# nie podawać wcale. Pola product=None oznaczają, że strona nie podaje serii —
# wtedy w odpowiedzi wolno wspomnieć tylko metraż i nazwę.
REALIZACJE = [
    {"name": "AURA w Zakliczynie", "m2": 63, "product": "Fitness Puzzle 15 mm",
     "kind": "klub", "url": "https://elevatestore.pl/realizacje/AURA-w-Zakliczynie-63-m2-czarnej-maty-Fitness-Puzzle-15-mm"},
    {"name": "Mind Your Body, Warszawa", "m2": 65, "product": "Puzzle PRO 15 mm",
     "kind": "studio", "url": "https://elevatestore.pl/realizacje/montaz-podlogi-studio-mind-your-body-warszawa-puzzel-pro-15mm"},
    {"name": "Workout Athlete, Kraków (kalistenika)", "m2": 90, "product": None,
     "kind": "studio", "url": "https://elevatestore.pl/realizacje/nowe-studio-kalisteniki-krakow-workout-athlete-case-study"},
    {"name": "Domowa siłownia na strychu pod martwy ciąg", "m2": 41, "product": "Antishock 30 mm",
     "kind": "dom", "url": "https://elevatestore.pl/realizacje/domowa-silownia-strych-martwy-ciag-antishock-30mm-case-study"},
    {"name": "Siłownia i strefa rozrywki na strychu, Dobrzyniewo Duże", "m2": 130, "product": None,
     "kind": "dom", "url": "https://elevatestore.pl/realizacje/domowa-silownia-strefa-rozrywki-na-strychu-130m2"},
    {"name": "Strefa treningowa na Gym Square Pro", "m2": 16, "product": "Gym Square Pro 20 mm",
     "kind": "dom", "url": "https://elevatestore.pl/realizacje/elegancka-strefa-treningowa-16m2-najazd-gym-square-pro"},
    {"name": "Mosaic Pro na trudnym podłożu (montaż 5-6 h)", "m2": 70, "product": "Square Pro Mosaic 15 mm",
     "kind": "klub", "url": "https://elevatestore.pl/realizacje/montaz-podlogi-gumowej-mosaic-pro-15mm-trudne-podloze"},
    {"name": "MoveSpace, Poznań", "m2": 75, "product": "Gym Square 20 mm",
     "kind": "klub", "url": "https://elevatestore.pl/realizacje/nowoczesna-strefa-treningowa-movespace-mosina-case-study-75m"},
    {"name": "Brzykcy Trening, studio 25 m²", "m2": 25, "product": "Fitness Puzzle Mini",
     "kind": "studio", "url": "https://elevatestore.pl/jak-urzadzic-studio-treningowe-25m2-brzykcy-trening"},
    {"name": "TeamZuzannkov, pod Krakowem", "m2": 50, "product": None,
     "kind": "studio", "url": "https://elevatestore.pl/realizacje/podloga-na-silownie-50m2-teamzuzannkov-case-study"},
    {"name": "Wyciszenie siłowni na piętrze, Ełk", "m2": 310, "product": "Antishock 43 mm",
     "kind": "klub", "url": "https://elevatestore.pl/realizacje/wygluszenie-silowni-na-pietrze-maty-antishock-43mm-elk"},
    {"name": "AWF Warszawa, hala", "m2": 400, "product": None,
     "kind": "klub", "url": "https://elevatestore.pl/realizacja-awf-warszawa"},
    {"name": "Studio treningowe na piętrze, amortyzacja", "m2": 110, "product": "Antishock 43 mm",
     "kind": "studio", "url": "https://elevatestore.pl/realizacje/amortyzujace-maty-gumowe-na-pietrze-realizacja-110m2"},
    {"name": "Domowa siłownia w Stęszewku", "m2": 16, "product": "Fitness Premium 15 mm (puzzle)",
     "kind": "dom", "url": "https://elevatestore.pl/realizacje/silownia-domowa-16m2-puzzle-premium"},
    {"name": "Minisiłownia na strychu", "m2": 6, "product": None,
     "kind": "dom", "url": "https://elevatestore.pl/realizacje/ministrefa-treningowa-6m2-na-strychu"},
    {"name": "Studio 12 m² Gabriela Piotrowskiego", "m2": 12, "product": None,
     "kind": "dom", "url": "https://elevatestore.pl/realizacje/domowa-silownia-gabriel-piotrowski-12m2"},
    {"name": "Domowa siłownia w pokoju, Bełchatów", "m2": 16, "product": None,
     "kind": "dom", "url": "https://elevatestore.pl/realizacje/domowa-silownia-w-pokoju-16-m2-belchatow"},
    {"name": "Baza treningowa Karola Zalewskiego", "m2": 20, "product": None,
     "kind": "dom", "url": "https://elevatestore.pl/realizacje/domowa-silownia-20-m2-karol-zalewski"},
    {"name": "Siłownia komercyjna, Szczecin", "m2": 600, "product": None,
     "kind": "klub", "url": "https://elevatestore.pl/realizacje/podloga-do-silowni-komercyjnej-szczecin-600m2"},
    {"name": "Siłownia w garażu, Warszawa", "m2": 38, "product": None,
     "kind": "dom", "url": "https://elevatestore.pl/realizacje/domowa-silownia-w-garazu-warszawa"},
]

# Siatka grubości — dosłownie z landingu PL. Responder cytuje TYLKO te liczby.
GRUBOSCI = [
    ("Cardio — bieżnie, orbitreki, rowery", "6–10 mm"),
    ("Trening funkcjonalny i strefa maszyn", "15 mm"),
    ("Wolne ciężary i hantle", "20 mm"),
    ("Martwy ciąg i platformy olimpijskie", "25–30 mm"),
    ("Lokal na piętrze, sąsiedzi pod spodem", "25–43 mm (Antishock)"),
]

# Montaż — dosłownie z landingu PL.
MONTAZ = (
    "Montaż wykonuje własna ekipa Elevate: przyjeżdża, układa, docina "
    "niestandardowe elementy przy słupach, skosach i zaokrągleniach, sprząta po "
    "sobie; opcjonalnie demontuje starą podłogę i oddaje ją do recyklingu. "
    "Realizacja 70 m² na trudnym podłożu: montaż w 5–6 godzin."
)

# --- Harvester: kwerendy wyszukiwarki wewnątrz grup ---------------------------
# Mniej kwerend = krótszy przebieg. Pierwszy test w chmurze: 21 grup × 6 kwerend
# przekroczyło 25 min. Trzy kwerendy PL i dwie DE łapią to samo, co sześć:
# wyszukiwarka FB i tak dopasowuje odmiany.
SEARCH_QUERIES = {
    "PL": ["podłogę", "puzzle", "maty"],
    "DE": ["Boden", "Matten"],
}
MAX_POST_AGE_DAYS = 7
MAX_POSTS_PER_QUERY = 8
HARVEST_TIME_BUDGET_SEC = int(os.environ.get("HARVEST_TIME_BUDGET_SEC", "900"))
# Do testów: ogranicz liczbę grup w przebiegu (0 = wszystkie).
GROUPS_LIMIT = int(os.environ.get("GROUPS_LIMIT", "0") or 0)

# --- WhatsApp / Twilio ------------------------------------------------------
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.environ.get("TWILIO_WHATSAPP_NUMBER")  # np. whatsapp:+14155238886
WHATSAPP_TO = os.environ.get("WHATSAPP_TO")                        # np. whatsapp:+48600000000

# --- Sesja Facebooka dla harvestera ----------------------------------------
# JSON storage_state z Playwright (patrz make_session.py). W GitHub Actions
# trafia tu z sekretu FB_STORAGE_STATE. Lokalnie może wskazywać na plik.
FB_STORAGE_STATE = os.environ.get("FB_STORAGE_STATE")
FB_STORAGE_STATE_FILE = os.environ.get("FB_STORAGE_STATE_FILE", "state/fb_storage_state.json")

# --- API -----------------------------------------------------------------

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
