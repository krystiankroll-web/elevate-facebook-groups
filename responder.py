"""Generator odpowiedzi na posty z grup FB (Claude Sonnet).

Persona: doradca techniczny ds. nawierzchni sportowych z Elevate Store.
Odpowiedź jest krótka, merytoryczna, a rekomendacja pada dopiero na końcu.

Użycie:
    from classifier import classify_post, is_qualified
    from responder import generate_response

    result = classify_post(post)
    if is_qualified(result):
        print(generate_response(post, result))
"""

from __future__ import annotations

import json
import re

from anthropic import Anthropic

import config

_client: Anthropic | None = None


def _get_client() -> Anthropic:
    global _client
    if _client is None:
        if not config.ANTHROPIC_API_KEY:
            raise RuntimeError(
                "Brak ANTHROPIC_API_KEY w zmiennych środowiskowych. "
                "Ustaw: export ANTHROPIC_API_KEY='sk-ant-...'"
            )
        _client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
    return _client


NO_LINK_BLOCK = """\
TRYB EKSPERCKI — REGULAMIN TEJ GRUPY ZAKAZUJE LINKÓW I AUTOPROMOCJI.
To nie jest ograniczenie, tylko inna metoda sprzedaży: budujesz pozycję
eksperta, a nie kierujesz do sklepu. Zasady:
- Zero adresów stron, zero nazwy sklepu jako zachęty, zero "zapraszam".
- NAZYWASZ PROBLEM, KTÓREGO AUTOR JESZCZE NIE WIDZI: za cienka mata pod
  ciężary, nierówna wylewka pod puzzlami, szpary na łączeniach, hałas
  przenoszony na strop, zapach taniego granulatu. Jedno konkretne ryzyko,
  jedno konkretne rozwiązanie z siatki grubości lub montażu.
- Wolno powiedzieć "zajmuję się tym zawodowo" i zaproponować doprecyzowanie
  na priv, jeśli autor poda parametry. Nic więcej.
- Realizacje możesz przywołać BEZ linku, samym metrażem i tym, jak tam
  rozwiązano problem (np. "na 310 m² na piętrze poszło 43 mm, bo chodziło
  o sąsiadów pod spodem").
Cel: żeby autor sam wszedł w profil, bo dostał najlepszą odpowiedź w wątku."""


def _url_block(market_cfg: dict, link_policy: str = "allowed") -> str:
    """Instrukcja linkowania: dobór URL-a albo twardy zakaz z regulaminu grupy."""
    if link_policy == "banned":
        return NO_LINK_BLOCK

    urls = market_cfg["urls"]
    if len(urls) == 1:
        return f"Link, który podajesz na końcu: {market_cfg['default_url']}"
    lines = "\n".join(f"- {segment}: {url}" for segment, url in urls.items())
    return (
        "Wybierz DOKŁADNIE JEDEN link, najlepiej pasujący do sytuacji autora, "
        "i podaj go na końcu odpowiedzi:\n"
        f"{lines}\n"
        f"Gdy nic nie pasuje jednoznacznie, użyj: {market_cfg['default_url']}"
    )


def _system_prompt(market: str, link_policy: str = "allowed") -> str:
    cfg = config.market(market)
    return f"""\
Jesteś doradcą technicznym ds. nawierzchni sportowych w firmie {config.BRAND_NAME}.
Odpowiadasz na posty w grupach na Facebooku dotyczących siłowni i fitnessu.
Rynek: {market}. Język odpowiedzi: {cfg['language']}.

KONTEKST PRODUKTOWY (jedyne fakty, których możesz użyć):
{cfg['product_context']}

ZASADY WYPOWIEDZI:
{cfg['persona_rules']}

STRUKTURA ODPOWIEDZI (2-4 zdania, w tej kolejności):
1. Jedno-dwa zdania konkretnej pomocy: odpowiedz na to, o co autor faktycznie
   pyta. Podaj rzeczową wskazówkę (np. dobór grubości do strefy, znaczenie
   równości podłoża, różnica puzzle vs rolki). Odnieś się do szczegółów z posta.
2. Opcjonalnie jedno zdanie doprecyzowujące lub pytanie o brakujący parametr,
   jeśli bez niego nie da się doradzić sensownie.
3. Ostatnie zdanie: naturalna, miękka rekomendacja rozwiązania z
   {config.BRAND_NAME} wraz z linkiem — o ile linkowanie jest dozwolone
   (patrz blok poniżej).

{_url_block(cfg, link_policy)}

CZEGO NIE ROBISZ:
- nie zaczynasz od nazwy firmy ani od linku,
- nie piszesz "polecam gorąco", "najlepsza oferta", "sprawdź koniecznie",
- nie podajesz cen, promocji, terminów,
- nie wstawiasz emotikon ani hashtagów,
- nie powtarzasz linku więcej niż raz,
- nie mieszasz języków — cała odpowiedź w jednym języku ({cfg['language']}),
- nie podajesz linku do innego rynku niż {market},
- nie przekraczasz 4 zdań.

Zwracasz wyłącznie treść komentarza, gotową do wklejenia. Bez nagłówków,
bez cudzysłowów, bez wyjaśnień.
"""


def _realizacje_block() -> str:
    """Lista realizacji do cytowania — model wybiera z niej, nie wymyśla."""
    lines = []
    for r in sorted(config.REALIZACJE, key=lambda r: r["m2"]):
        prod = f", {r['product']}" if r["product"] else ""
        lines.append(f"- {r['m2']} m² · {r['name']}{prod} · {r['url']}")
    return "\n".join(lines)


def _grubosci_block() -> str:
    return "\n".join(f"- {zone}: {mm}" for zone, mm in config.GRUBOSCI)


def _examples_block(examples: list[dict] | None) -> str:
    """Odpowiedzi, które Krystian wybrał wcześniej — uczymy się jego gustu."""
    if not examples:
        return ""
    lines = ["\nPRZYKŁADY ODPOWIEDZI, KTÓRE WŁAŚCICIEL WYBRAŁ DO PUBLIKACJI "
             "(trzymaj się tego stylu i długości):"]
    for ex in examples[-5:]:
        lines.append(f"- Zapytanie: {ex.get('post', '')[:140]}")
        lines.append(f"  Wybrana odpowiedź: {ex.get('chosen', '')}")
    return "\n".join(lines)


def _variants_prompt(market: str, link_policy: str, examples: list[dict] | None) -> str:
    cfg = config.market(market)
    if link_policy == "banned":
        link_rule = NO_LINK_BLOCK
    else:
        link_rule = (
            "Każdy wariant kończy się DOKŁADNIE JEDNYM linkiem. Link musi być "
            "URL-em realizacji z listy poniżej (dobranej do metrażu i typu "
            "obiektu z zapytania) albo, gdy żadna nie pasuje, tym adresem: "
            f"{cfg['default_url']}. Żadnych innych adresów."
        )
    return f"""\
Jesteś doradcą technicznym ds. nawierzchni sportowych w {config.BRAND_NAME}.
Piszesz KOMENTARZ pod cudzym postem w grupie na Facebooku. Rynek: {market}.
Język odpowiedzi: {cfg['language']}.

ZASADY STYLU (bezwzględne):
- 2-3 zdania. Prosto, jak człowiek z branży piszący z telefonu.
- Najpierw konkret odpowiadający na pytanie autora, na końcu realizacja i link.
- Zero cen, terminów, rabatów, emotikon, wykrzykników, "zapraszam", "polecam gorąco".
- Nie wymyślasz niczego, czego nie ma w danych poniżej. Jeśli nie wiesz — pytasz autora.
- Nie obiecujesz braku zapachu: maty są z granulatu SBR z recyklingu opon
  i lepiszcza poliuretanowego; różnicę robi wykonanie (seria PRO cięta na zimno z bloku).

SIATKA GRUBOŚCI (cytuj tylko te liczby):
{_grubosci_block()}

MONTAŻ:
{config.MONTAZ}

REALIZACJE (jedyne, które wolno przywołać; podawaj metraż i URL dosłownie):
{_realizacje_block()}

LINKOWANIE:
{link_rule}
{_examples_block(examples)}

ZADANIE: napisz TRZY RÓŻNE warianty komentarza. Różnią się kątem, nie słowami:
1. "grubość" — dobór grubości do stref pod sprzęt z zapytania, pytanie o brakujący parametr.
2. "podłoże i montaż" — co sprawdzić w posadzce/łączeniach, jak wygląda montaż ekipą.
3. "realizacja" — zaczynasz od najbliższej metrażem realizacji i tego, jak tam to rozwiązano.

Odpowiadasz WYŁĄCZNIE tablicą JSON z trzema stringami, bez komentarza:
["wariant 1", "wariant 2", "wariant 3"]
"""


def _parse_variants(raw: str) -> list[str]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\[.*\]", raw, re.DOTALL)
        if not m:
            raise ValueError(f"Brak tablicy JSON w odpowiedzi modelu: {raw[:200]!r}")
        data = json.loads(m.group(0))
    variants = [str(v).strip() for v in data if str(v).strip()]
    if len(variants) < 3:
        raise ValueError(f"Model zwrócił {len(variants)} wariantów zamiast 3.")
    return variants[:3]


def _check_links(variants: list[str], market: str, link_policy: str) -> list[str]:
    """Twardy bezpiecznik: link tylko z listy realizacji albo default rynku."""
    allowed = {r["url"] for r in config.REALIZACJE} | set(config.market(market)["urls"].values())
    allowed.add(config.market(market)["default_url"])
    out = []
    for v in variants:
        urls = re.findall(r"https?://\S+", v)
        if link_policy == "banned" and urls:
            for u in urls:
                v = v.replace(u, "").strip()
        else:
            for u in urls:
                if u.rstrip(".,;)") not in allowed:
                    raise ValueError(f"Model podał link spoza listy: {u}")
        out.append(v)
    return out


def generate_variants(
    post_text: str,
    classification: dict | None = None,
    group: dict | None = None,
    examples: list[dict] | None = None,
) -> list[str]:
    """Trzy różne warianty komentarza pod post. Do wyboru przez człowieka.

    `group` z groups.py ustala rynek (domenę linku) i politykę linkowania.
    `examples` to wcześniej wybrane odpowiedzi — few-shot, żeby styl dryfował
    w stronę tego, co właściciel faktycznie publikuje.
    """
    market = _resolve_market(None, group)
    link_policy = (group or {}).get("link_policy", "allowed")
    if link_policy == "unknown":
        link_policy = "banned"

    text = (post_text or "").strip()
    if not text:
        raise ValueError("Pusty post — nie ma na co odpowiadać.")
    if classification is not None and not classification.get("is_lead"):
        raise ValueError(
            f"Post nie jest leadem: {classification.get('reason', 'brak uzasadnienia')}"
        )

    hint = f"\n\nCo wykryto w poście: {classification['reason']}" if classification and classification.get("reason") else ""
    response = _get_client().messages.create(
        model=config.MODEL_RESPONDER,
        max_tokens=900,
        system=_variants_prompt(market, link_policy, examples),
        messages=[
            {"role": "user", "content": f"Post z grupy FB:\n{text}{hint}\n\nNapisz trzy warianty."},
            {"role": "assistant", "content": "["},
        ],
    )
    raw = "[" + response.content[0].text
    return _check_links(_parse_variants(raw), market, link_policy)


def _resolve_market(market: str | None, group: dict | None) -> str:
    """Ustala rynek. Grupa ma pierwszeństwo — link musi pasować do grupy.

    Podanie rynku sprzecznego z grupą jest błędem, nie preferencją: to jedyny
    sposób, w jaki polski link mógłby trafić do niemieckiej grupy.
    """
    if group is None:
        return market or "PL"

    group_market = group["market"]
    if group_market not in config.MARKETS:
        raise ValueError(
            f"Grupa {group['name']!r} należy do rynku {group_market}, dla którego "
            "nie ma sklepu ani persony. Nie publikuj tam odpowiedzi — "
            f"obsługiwane rynki: {', '.join(config.MARKETS)}."
        )
    if market and market.upper() != group_market:
        raise ValueError(
            f"Konflikt rynków: grupa {group['name']!r} to {group_market}, "
            f"a zażądano {market.upper()}. Link trafiłby na złą domenę."
        )
    return group_market


def generate_response(
    post_text: str,
    classification: dict | None = None,
    market: str | None = None,
    group: dict | None = None,
) -> str:
    """Generuje treść komentarza pod postem.

    `market` steruje językiem, kontekstem produktowym i pulą linków
    ("PL" -> elevatestore.pl, "DE" -> elevatestore.de).

    Zalecane użycie: zamiast `market` podaj `group` z groups.py — wtedy domena
    linku wynika z grupy i nie da się jej pomylić.

    Jeśli `classification` jest podana i post nie kwalifikuje się jako lead,
    funkcja podnosi ValueError — odpowiadanie na przypadkowe posty szkodzi marce.
    """
    market = _resolve_market(market, group)
    link_policy = (group or {}).get("link_policy", "allowed")
    if link_policy == "unknown":
        # Regulaminu nie widzieliśmy — traktujemy jak zakaz. Taniej niż ban.
        link_policy = "banned"

    text = (post_text or "").strip()
    if not text:
        raise ValueError("Pusty post — nie ma na co odpowiadać.")

    if classification is not None:
        if not classification.get("is_lead"):
            raise ValueError(
                "Post nie został zakwalifikowany jako lead: "
                f"{classification.get('reason', 'brak uzasadnienia')}"
            )
        if classification.get("confidence", 0.0) < config.CONFIDENCE_THRESHOLD:
            raise ValueError(
                f"Zbyt niska pewność klasyfikacji "
                f"({classification.get('confidence'):.2f} < {config.CONFIDENCE_THRESHOLD}) "
                "— post do ręcznej oceny."
            )

    hint = ""
    if classification and classification.get("reason"):
        hint = f"\n\nCo wykryto w poście: {classification['reason']}"

    response = _get_client().messages.create(
        model=config.MODEL_RESPONDER,
        max_tokens=config.MAX_TOKENS_RESPONDER,
        system=_system_prompt(market, link_policy),
        messages=[
            {
                "role": "user",
                "content": f"Post z grupy FB:\n{text}{hint}\n\nNapisz komentarz zgodnie z zasadami.",
            }
        ],
    )
    return response.content[0].text.strip()


if __name__ == "__main__":
    from classifier import classify_post, is_qualified

    SAMPLES = [
        ("PL", "Cześć, otwieram siłownię w Poznaniu i szukam podłogi pod strefę "
               "wolnych ciężarów. Polecicie maty, które wytrzymają rzucanie sztangą?"),
        ("PL", "Robię home gym w garażu, mam wylewkę betonową. Puzzle gumowe "
               "wystarczą pod stojak i ławkę czy trzeba coś grubszego?"),
        ("DE", "Ich baue mir ein Homegym in der Garage. Welcher Boden hält "
               "Kreuzheben aus, ohne dass der Estrich kaputtgeht?"),
        ("DE", "Wir eröffnen ein Studio im ersten Stock, die Nachbarn "
               "beschweren sich schon jetzt über Lärm. Was für einen Boden "
               "braucht der Freihantelbereich?"),
    ]

    for i, (market, post) in enumerate(SAMPLES, 1):
        result = classify_post(post, market=market)
        print(f"--- Post {i} [{market}] ---")
        print(post)
        print(f"\nKlasyfikacja: lead={result['is_lead']} conf={result['confidence']:.2f}")
        if is_qualified(result):
            print(f"\nOdpowiedź:\n{generate_response(post, result, market=market)}\n")
        else:
            print(f"\nPomijam: {result['reason']}\n")
