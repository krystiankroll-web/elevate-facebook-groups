#!/usr/bin/env python3
"""tematy.py - czego ludzie szukają na YouTube i czy da się tam wygrać.

Dla każdej frazy bazowej pobiera podpowiedzi YouTube (autouzupełnianie), rozwija je o słowa
pytające i łączniki, a potem dla każdej znalezionej frazy sprawdza pierwsze wyniki wyszukiwania:
ile ich jest, jak są świeże, ile mają wyświetleń i czy jest wśród nich Twój kanał.

    python3 tematy.py                         # frazy z seeds.txt obok skryptu
    python3 tematy.py --seed "mata gumowa" --seed "siłownia w garażu"
    python3 tematy.py --litery                # dodatkowo rozwija o litery a-ż (dużo zapytań)
    python3 tematy.py --json wynik.json       # zapisz pełne dane

CZEGO TO NIE MÓWI. YouTube nie udostępnia liczby wyszukiwań. Fraza w podpowiedziach znaczy
tylko, że ktoś jej szuka. Pogrubienia w podpowiedziach maszyna nie widzi - to dalej sprawdza
człowiek w przeglądarce. Etykiety konkurencji to prosta reguła na medianie wyświetleń
pierwszych wyników, nie prognoza.

Bez zależności: czysty Python 3. Pyta wolno (przerwy między zapytaniami), bo YouTube
blokuje szybkie serie jako bota. Każdej frazy, której nie dało się sprawdzić, nie zgaduje -
oznacza ją jako niesprawdzoną.
"""
import argparse, json, os, re, statistics, sys, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
UA = {"User-Agent": "Mozilla/5.0", "Accept-Language": "pl-PL,pl;q=0.9"}
PYTAJNIKI = ["jak", "jaka", "jaki", "ile", "czy", "dlaczego", "co"]
LACZNIKI = ["na", "do", "pod", "w", "z", "czy", "jak"]
LITERY = list("abcdefghijklmnoprstuwyz") + ["ł", "ś", "ż"]
STOP = {"na", "do", "pod", "w", "z", "i", "czy", "jak", "jaka", "jaki", "ile", "co", "dla", "od",
        "po", "się", "to", "vs", "o", "a"}


def get(url, timeout=20):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")


def podpowiedzi(q):
    u = "https://suggestqueries-clients6.youtube.com/complete/search?" + urllib.parse.urlencode(
        {"client": "youtube", "ds": "yt", "hl": "pl", "gl": "PL", "q": q})
    t = get(u, 15)
    m = re.search(r"\((\[.*\])\)\s*$", t, re.S)
    if not m:
        return []
    return [x[0] for x in json.loads(m.group(1))[1]]


def rdzenie(fraza):
    return {w[:5] for w in re.findall(r"\w+", fraza.lower()) if w not in STOP and len(w) >= 4}


def zbierz(seeds, litery, pauza):
    znalezione = {}
    for s in seeds:
        # pytania tak, jak ludzie je wpisują: „jaka mata…", a nie „jaka mata gumowa…" - YouTube
        # dokańcza wtedy realne zapytania, a filtr niżej zostawia tylko te z całą frazą bazową
        pierwsze = s.split()[0]
        zapytania = [s] + [f"{s} {w}" for w in LACZNIKI] + [f"{p} {pierwsze}" for p in PYTAJNIKI]
        if litery:
            zapytania += [f"{s} {l}" for l in LITERY]
        r_seed = rdzenie(s)
        for q in zapytania:
            try:
                wyniki = podpowiedzi(q)
            except Exception as e:  # noqa: BLE001 - jedna fraza nie zatrzymuje całości
                print(f"  ! podpowiedzi dla „{q}\": {e}", file=sys.stderr)
                wyniki = []
            for f in wyniki:
                f = f.strip()
                # zostają tylko frazy, które zawierają wszystkie znaczące słowa frazy bazowej
                # (inaczej „mata gumowa" ściąga „matę szklaną" i „matę chłodzącą na fotel")
                if f and r_seed <= rdzenie(f) and f not in znalezione:
                    znalezione[f] = s
            time.sleep(pauza)
    return znalezione


def liczba(tekst):
    d = re.sub(r"\D", "", tekst or "")
    return int(d) if d else 0


def swieze(tekst):
    t = (tekst or "").lower()
    return not re.search(r"\b(rok|lat|lata)\b", t) and bool(t)


def wyniki_wyszukiwania(q, ile):
    h = get("https://www.youtube.com/results?" + urllib.parse.urlencode(
        {"search_query": q, "hl": "pl", "gl": "PL"}))
    m = re.search(r"var ytInitialData = (\{.*?\});</script>", h, re.S)
    if not m:
        raise RuntimeError("brak danych wyszukiwania (możliwa blokada)")
    d = json.loads(m.group(1))
    out = []

    def walk(o):
        if len(out) >= ile:
            return
        if isinstance(o, dict):
            v = o.get("videoRenderer")
            if v:
                out.append({
                    "id": v.get("videoId"),
                    "tytul": "".join(r.get("text", "") for r in v.get("title", {}).get("runs", [])),
                    "kanal": "".join(r.get("text", "") for r in v.get("ownerText", {}).get("runs", [])),
                    "wyswietlenia": liczba(v.get("viewCountText", {}).get("simpleText")),
                    "opublikowano": v.get("publishedTimeText", {}).get("simpleText", ""),
                })
                return
            for x in o.values():
                walk(x)
        elif isinstance(o, list):
            for x in o:
                walk(x)

    walk(d)
    return out


def konkurencja(mediana):
    if mediana < 1000:
        return "słaba"
    if mediana < 10000:
        return "średnia"
    return "silna"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", action="append", help="fraza bazowa (można wiele razy)")
    ap.add_argument("--seeds", default=os.path.join(HERE, "seeds.txt"), help="plik z frazami bazowymi")
    ap.add_argument("--kanal", default="Krystian Kroll", help="nazwa Twojego kanału w wynikach")
    ap.add_argument("--litery", action="store_true", help="rozwijaj też o litery (dużo zapytań)")
    ap.add_argument("--wyniki", type=int, default=10, help="ile wyników wyszukiwania sprawdzić na frazę")
    ap.add_argument("--max", type=int, default=60, help="maks. liczba fraz do sprawdzenia w wyszukiwarce")
    ap.add_argument("--pauza", type=float, default=0.6, help="przerwa między podpowiedziami (s)")
    ap.add_argument("--json", help="zapisz pełny wynik do pliku JSON")
    a = ap.parse_args()

    seeds = a.seed or [l.strip() for l in open(a.seeds, encoding="utf-8")
                       if l.strip() and not l.startswith("#")]
    print(f"\n  {len(seeds)} fraz bazowych - zbieram podpowiedzi YouTube...", file=sys.stderr)
    frazy = zbierz(seeds, a.litery, a.pauza)
    print(f"  {len(frazy)} fraz z podpowiedzi; sprawdzam wyszukiwarkę dla maks. {a.max}...", file=sys.stderr)

    # limit sprawdzeń dzielony po równo między frazy bazowe: najpierw sama fraza bazowa,
    # potem najkrótsze rozwinięcia, na zmianę - żeby pierwsza baza nie zjadła całego limitu
    kolejki = {}
    for f, s in frazy.items():
        kolejki.setdefault(s, []).append(f)
    for s, lst in kolejki.items():
        lst.sort(key=lambda f: (f.lower() != s.lower(), len(f)))
    kolejnosc = []
    while any(kolejki.values()):
        for s in list(kolejki):
            if kolejki[s]:
                kolejnosc.append((kolejki[s].pop(0), s))
    rows = []
    for i, (f, s) in enumerate(kolejnosc[: a.max]):
        try:
            w = wyniki_wyszukiwania(f, a.wyniki)
            views = [x["wyswietlenia"] for x in w] or [0]
            moje = [n + 1 for n, x in enumerate(w) if x["kanal"].strip().lower() == a.kanal.lower()]
            rows.append({
                "fraza": f, "baza": s, "wynikow": len(w),
                "swiezych": sum(swieze(x["opublikowano"]) for x in w),
                "mediana_wysw": int(statistics.median(views)), "max_wysw": max(views),
                "konkurencja": konkurencja(statistics.median(views)),
                "moja_pozycja": moje[0] if moje else None,
                "top": w[0]["tytul"] if w else "",
                "top_kanal": w[0]["kanal"] if w else "",
                "sprawdzono": True,
            })
        except Exception as e:  # noqa: BLE001
            print(f"  ! wyszukiwarka dla „{f}\": {e}", file=sys.stderr)
            rows.append({"fraza": f, "baza": s, "sprawdzono": False})
        time.sleep(1.5)
    for f, s in kolejnosc[a.max:]:
        rows.append({"fraza": f, "baza": s, "sprawdzono": False})

    rank = {"słaba": 0, "średnia": 1, "silna": 2}
    ok = sorted([r for r in rows if r["sprawdzono"]],
                key=lambda r: (r["moja_pozycja"] is not None, rank[r["konkurencja"]], -r["swiezych"]))
    print(f"\n  {'FRAZA (dokładna forma)':<44} {'KONKUR.':<8} {'ŚWIEŻE':>6} {'MEDIANA':>9}  {'TY':>3}  NAJWYŻEJ")
    for r in ok:
        ty = str(r["moja_pozycja"]) if r["moja_pozycja"] else "-"
        print(f"  {r['fraza'][:44]:<44} {r['konkurencja']:<8} {r['swiezych']:>3}/{r['wynikow']:<2} "
              f"{r['mediana_wysw']:>9,}  {ty:>3}  {r['top'][:50]}")
    nie = [r["fraza"] for r in rows if not r["sprawdzono"]]
    if nie:
        print(f"\n  niesprawdzone w wyszukiwarce ({len(nie)}): " + " · ".join(nie[:30]) + (" …" if len(nie) > 30 else ""))
    print("\n  KONKUR. = mediana wyświetleń pierwszych wyników: <1 tys. słaba, <10 tys. średnia, wyżej silna."
          "\n  ŚWIEŻE = wyniki młodsze niż rok. TY = pozycja Twojego kanału (- = nie ma Cię w wynikach).\n")
    if a.json:
        json.dump(rows, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
