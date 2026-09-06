"""Klasyfikator postów z grup FB pod kątem intencji zakupowej (Claude Haiku).

Użycie:
    from classifier import classify_post
    result = classify_post("Otwieram siłownię, szukam podłogi pod strefę wolnych ciężarów")
    # {'is_lead': True, 'confidence': 0.93, 'reason': '...'}
"""

from __future__ import annotations

import json
import re

from anthropic import Anthropic

import config

_client: Anthropic | None = None


def _get_client() -> Anthropic:
    """Leniwie tworzy klienta, żeby import modułu nie wymagał klucza API."""
    global _client
    if _client is None:
        if not config.ANTHROPIC_API_KEY:
            raise RuntimeError(
                "Brak ANTHROPIC_API_KEY w zmiennych środowiskowych. "
                "Ustaw: export ANTHROPIC_API_KEY='sk-ant-...'"
            )
        _client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
    return _client


SYSTEM_PROMPT = f"""\
Jesteś analitykiem leadów sprzedażowych dla firmy {config.BRAND_NAME}, która
dostarcza nawierzchnie gumowe (maty, puzzle, rolki) do siłowni, klubów fitness,
stref crossfit i domowych home gymów.

Twoje zadanie: ocenić post z grupy na Facebooku i stwierdzić, czy jego autor ma
realną, aktualną potrzebę zakupu lub doboru takiej nawierzchni.

TO JEST LEAD (is_lead = true), gdy autor:
- pyta o dobór, grubość, rodzaj lub jakość podłogi/mat/puzzli gumowych,
- szuka dostawcy albo prosi o polecenie produktu lub firmy,
- otwiera, remontuje lub wyposaża siłownię, klub fitness, studio, strefę treningową,
- opisuje problem z obecną nawierzchnią (hałas, odkształcenia, zapach, uszkodzona posadzka),
- urządza home gym i zastanawia się, co położyć pod sprzęt lub ciężary.

TO NIE JEST LEAD (is_lead = false), gdy post:
- sprzedaje, oddaje lub reklamuje maty (autor jest podażą, nie popytem),
- to konkurencyjna oferta handlowa lub post firmowy,
- dotyczy treningu, diety, suplementów, karnetów, sprzętu innego niż nawierzchnia,
- wspomina o matach tylko mimochodem, bez potrzeby zakupowej,
- jest pytaniem czysto teoretycznym, żartem albo memem.

Ważne: sam fakt, że post zawiera słowo "mata" czy "siłownia", nie czyni go leadem.
Decyduje intencja autora.

Pole confidence (0.0-1.0) to Twoja pewność co do wartości is_lead:
- 0.9-1.0: jednoznaczne zapytanie zakupowe z konkretem,
- 0.7-0.89: wyraźna potrzeba, ale bez pełnego kontekstu,
- 0.4-0.69: sygnał niepewny, wymaga oceny człowieka,
- 0.0-0.39: prawie na pewno nie lead.

Odpowiadasz WYŁĄCZNIE obiektem JSON, bez komentarza i bez bloku markdown:
{{"is_lead": bool, "confidence": float, "reason": "jedno zdanie po polsku"}}
"""

TOFU_NOTE = """

TRYB SZEROKI (góra lejka). Firma jest na wczesnym etapie budowania obecności
i woli odpowiedzieć za dużo razy niż przegapić okazję.

Dlatego:
- Przy wahaniu wybierasz is_lead = true, nie false.
- Wystarczy, że autor URZĄDZA, REMONTUJE albo WYPOSAŻA jakąkolwiek przestrzeń
  treningową — nie musi pytać o podłogę wprost.
- Pytanie o hałas, wibracje, zniszczoną posadzkę, sąsiadów albo strop to lead,
  nawet jeśli słowo "mata" nie pada.
- Ktoś kupujący ciężką maszynę, sztangi albo pomost też jest leadem: za chwilę
  będzie miał problem z podłożem.

Nadal odrzucasz (is_lead = false) tylko rzeczy jednoznaczne:
- autor SPRZEDAJE nawierzchnię lub jest konkurencyjną firmą,
- post w ogóle nie dotyczy przestrzeni treningowej ani sprzętu
  (dieta, suplementy, plan treningowy, motywacja, memy),
- post jest ogłoszeniem o pracy, wydarzeniu lub karnecie.

W trybie szerokim confidence 0.4-0.6 jest normalne i wystarcza do odpowiedzi.
Nie zaniżaj go tylko dlatego, że kontekst jest niepełny."""


def _language_note(market: str) -> str:
    """Uprzedza model, w jakim języku dostanie post — kryteria zostają te same."""
    lang = config.market(market)["language"]
    return f"\n\nPost może być w języku: {lang}. Odpowiadasz zawsze tym samym JSON-em."


_DIACRITICS = str.maketrans("łąćęńóśźżäöüß", "lacenoszzaous")


def _fold(text: str) -> str:
    """Małe litery bez ogonków — 'podłogę' i 'podloge' mają trafiać tak samo."""
    return text.lower().translate(_DIACRITICS)


def _matches_keywords(text: str, market: str = "PL") -> tuple[bool, str]:
    """Prefiltr po rdzeniach. Zwraca (czy_przepuścić, poziom).

    poziom: "strong" - sam rdzeń wystarczy, "weak" - rdzeń słaby w parze
    z kontekstem, "none" - odrzucone bez wywołania API.
    """
    pf = config.market(market)["prefilter"]
    norm = _fold(text)

    if any(re.search(p, norm) for p in pf["strong"]):
        return True, "strong"

    has_weak = any(re.search(p, norm) for p in pf["weak"])
    if has_weak and any(re.search(p, norm) for p in pf["context"]):
        return True, "weak"

    # TOFU: przepuszczamy wszystko, co dotyka tematu z którejkolwiek strony —
    # sam słaby rdzeń ("guma") albo sam kontekst ("kupię atlas do garażu").
    # Prefiltr przestaje być sitem, a staje się tylko odsiewaczem oczywistego
    # off-topu. Właściwą decyzję podejmuje model, bo jest do tego zdolny,
    # a kosztuje grosze przy tym wolumenie.
    if config.TOFU_MODE and (
        has_weak or any(re.search(p, norm) for p in pf["context"])
    ):
        return True, "tofu"

    return False, "none"


def _extract_json(raw: str) -> dict:
    """Wyciąga obiekt JSON z odpowiedzi modelu, tolerując otoczkę tekstową."""
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError(f"Brak JSON w odpowiedzi modelu: {raw!r}")
    return json.loads(match.group(0))


def _normalize(parsed: dict) -> dict:
    """Waliduje i przycina wynik do kontraktu {is_lead, confidence, reason}."""
    is_lead = bool(parsed.get("is_lead", False))

    try:
        confidence = float(parsed.get("confidence", 0.0))
    except (TypeError, ValueError):
        confidence = 0.0
    confidence = max(0.0, min(1.0, confidence))

    reason = str(parsed.get("reason", "")).strip() or "Brak uzasadnienia od modelu."

    return {"is_lead": is_lead, "confidence": round(confidence, 2), "reason": reason}


def classify_post(post_text: str, author: str | None = None, market: str = "PL") -> dict:
    """Ocenia post pod kątem intencji zakupowej.

    `market` wybiera listę słów kluczowych do prefiltru ("PL" albo "DE").

    Zwraca słownik: {"is_lead": bool, "confidence": float, "reason": str}.
    Przy błędzie API lub parsowania zwraca is_lead=False — lepiej zgubić lead
    niż odpowiedzieć na przypadkowy post.
    """
    text = (post_text or "").strip()

    if not text:
        return {"is_lead": False, "confidence": 1.0, "reason": "Pusty post."}

    passed, level = _matches_keywords(text, market)
    if config.USE_KEYWORD_PREFILTER and not passed:
        return {
            "is_lead": False,
            "confidence": 0.6,
            "reason": "Prefiltr: brak rdzeni tematycznych, post nie trafił do modelu.",
        }

    user_content = f"Autor: {author}\n\nTreść posta:\n{text}" if author else f"Treść posta:\n{text}"

    try:
        response = _get_client().messages.create(
            model=config.MODEL_CLASSIFIER,
            max_tokens=config.MAX_TOKENS_CLASSIFIER,
            system=SYSTEM_PROMPT
            + (TOFU_NOTE if config.TOFU_MODE else "")
            + _language_note(market),
            messages=[
                {"role": "user", "content": user_content},
                {"role": "assistant", "content": "{"},  # prefill wymusza czysty JSON
            ],
        )
        raw = "{" + response.content[0].text
        return _normalize(_extract_json(raw))
    except Exception as exc:  # noqa: BLE001 - świadomie łapiemy wszystko
        return {
            "is_lead": False,
            "confidence": 0.0,
            "reason": f"Błąd klasyfikacji: {type(exc).__name__}: {exc}",
        }


def is_qualified(result: dict) -> bool:
    """Czy wynik klasyfikacji kwalifikuje post do wygenerowania odpowiedzi."""
    return result["is_lead"] and result["confidence"] >= config.CONFIDENCE_THRESHOLD


if __name__ == "__main__":
    SAMPLES = [
        "Cześć, otwieram siłownię w Poznaniu i szukam podłogi pod strefę "
        "wolnych ciężarów. Polecicie maty, które wytrzymają rzucanie sztangą?",
        "Sprzedam maty gumowe 15mm, używane pół roku, odbiór osobisty Kraków.",
        "Jaki split treningowy polecacie na masę? 4 czy 5 dni?",
        "Robię home gym w garażu, mam wylewkę betonową. Puzzle gumowe wystarczą "
        "pod stojak i ławkę czy trzeba coś grubszego?",
        "Nasze studio fitness zaprasza na zajęcia od poniedziałku!",
    ]

    for i, post in enumerate(SAMPLES, 1):
        outcome = classify_post(post)
        flag = "LEAD" if is_qualified(outcome) else "----"
        print(f"[{flag}] {i}. conf={outcome['confidence']:.2f}  {outcome['reason']}")
        print(f"       {post[:70]}...\n")
