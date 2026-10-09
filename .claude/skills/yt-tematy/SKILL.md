---
name: yt-tematy
description: >-
  Znajduje tematy odcinków YouTube na podstawie tego, czego ludzie naprawdę szukają: pobiera
  podpowiedzi YouTube dla fraz z banku kanału, sprawdza konkurencję i świeżość wyników oraz to,
  gdzie kanał już jest, i zwraca 3 rekomendacje tematów na miesiąc plus frazy do dopisania do
  banku. Używaj przy „co nagrać", „tematy na odcinki", „research fraz", „SEO tematy",
  „aktualizacja banku fraz", „czego ludzie szukają", przed /yt-plan i /yt-script.
---

# yt-tematy

Odpowiada na pytanie „co nagrać", zanim powstanie scenariusz. Nie pisze tytułów ani opisów —
to robi `youtube-seo-tytuly-opisy` na podstawie banku fraz.

```bash
python3 tematy.py                    # frazy bazowe z seeds.txt
python3 tematy.py --seed "fraza"     # jedna lub kilka fraz zamiast pliku
python3 tematy.py --json wynik.json  # pełne dane do dalszej pracy
```

Wymaga sesji z dostępem do youtube.com i *.youtube.com. Bez tego skrypt zgłosi błędy
połączenia — wtedy powiedz to wprost i nie zastępuj danych zgadywaniem.

## Zanim zaczniesz

1. Przeczytaj `.claude/youtube/voice.md` (persony, zasady kanału, czego nie twierdzimy,
   listę opublikowanych odcinków).
2. Sprawdź, czy `seeds.txt` odpowiada aktualnemu bankowi fraz w `youtube-seo-tytuly-opisy`
   (data wersji banku jest w nagłówku pliku). Jeśli bank jest nowszy — zaktualizuj `seeds.txt`.

## Co robisz

1. Uruchom `tematy.py` (domyślnie 60 fraz sprawdzanych w wyszukiwarce, ok. 3–5 min).
2. **Odsiej śmieci.** Podpowiedzi YouTube zawierają frazy z innej bajki (np. „mata gumowa
   podeszwa", „siłownia w garażu doc") i błędne dokończenia. Zostaw tylko te, przy których widz
   kupujący podłogę lub urządzający siłownię dostałby od kanału uczciwą odpowiedź.
3. **Przypisz personę** z `voice.md`: dom / inwestor klubu / sieć fitness / firma handlowa.
4. **Sprawdź zasady kanału.** Odrzuć tematy, których nie da się zrobić bez łamania zasad:
   obietnice akustyczne bez badania, liczby o cudzych firmach, kraj pochodzenia jako teza.
5. **Porównaj z kanałem.** Kolumna „TY" mówi, gdzie kanał już jest w wynikach. Fraza, na której
   kanał jest w top 3, nie potrzebuje nowego odcinka — chyba że odcinek jest słaby (zapytaj).
6. **Wybierz 3 tematy na miesiąc.** Kryteria w tej kolejności: fraza istnieje w podpowiedziach,
   kanału nie ma w wynikach albo jest nisko, konkurencja słaba lub średnia, są świeże wyniki
   (YouTube podsuwa nowe filmy pod frazę), kanał ma o tym uczciwą wiedzę i materiał.

## Co oddajesz

- **Tabela** (maks. 15 wierszy, po odsianiu): fraza (dokładna forma) | persona | konkurencja |
  świeże | pozycja kanału | pomysł na odcinek w jednym zdaniu.
- **3 rekomendacje na miesiąc**, każda: fraza główna w dokładnej formie, persona, jedno zdanie
  obietnicy odcinka, dlaczego teraz (na faktach z tabeli), co kanał już ma (rekwizyty, historie,
  realizacje).
- **Do banku fraz:** nowe frazy z podpowiedzi, w dokładnej formie, ze statusem pogrubienia „?" —
  pogrubienie i świeżość sprawdza człowiek w przeglądarce (karta incognito, polski IP), bo
  maszyna tego nie widzi.
- **Czego nie sprawdzono:** frazy pominięte przez limit albo blokadę — wprost, bez zgadywania.

## Uczciwie o ograniczeniach (powiedz je, gdy pytają o skuteczność)

- YouTube nie podaje liczby wyszukiwań. Podpowiedź znaczy „ktoś tego szuka", nie „ilu".
- Etykieta konkurencji to mediana wyświetleń pierwszych wyników (<1 tys. słaba, <10 tys.
  średnia, wyżej silna) — reguła kciuka, nie prognoza. Duży film na pierwszym miejscu może
  pochodzić z reklamy.
- Nie formatuj podpowiedzi: zapisuj frazy znak w znak, tak jak zwrócił je YouTube — bank fraz
  i metoda `youtube-seo-tytuly-opisy` wymagają dokładnej formy.

## Bramka

Nic tu nie publikuje. Wynik kończy się blokiem do skopiowania, a ostatnia linia to pytanie:
**nagrywamy, czy zmieniamy?**
