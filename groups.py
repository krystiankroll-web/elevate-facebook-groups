"""Baza grup FB — dane zmierzone 2026-09-05 na stronach /about każdej grupy.

Wszystkie nazwy, liczby członków, aktywność i regulaminy pochodzą z zakładki
"Informacje" konkretnej grupy, odczytanej bez logowania. To są liczby podane
przez Facebooka, nie szacunki.

Czego NADAL nie ma: odsetka postów z realną intencją zakupową. Facebook bez
logowania pokazuje jeden post i blokuje przewijanie, więc próbki treści nie
udało się zebrać. `posts_month` to SUFIT — górna granica tego, ile leadów
grupa może dać, gdyby każdy post był leadem. Nie jest.

link_policy — wynika wprost z regulaminu grupy:
    "allowed" - regulamin dopuszcza linki do sklepów/producentów
    "limited" - dopuszcza, ale z limitem dla firm
    "banned"  - zakaz autopromocji i nieistotnych linków
    "unknown" - regulamin niewidoczny bez członkostwa
Przy "banned" responder NIE wstawia linku. To nie jest sugestia — to jedyny
sposób, żeby nie stracić konta w największych grupach.
"""

from __future__ import annotations

MEASURED_AT = "2026-09-05"

# Pomiar treści na żywej próbce (zalogowana sesja, feed chronologiczny).
# To jest liczba, której brakowało w pierwszym podejściu do fazy 0.
SAMPLES = {
    "233349823542539": {
        "grupa": "Sprzedam, kupię, oddam - sprzęt sportowy, fitness, siłownia",
        "blokow": 126,
        "zakres": "ok. 1 doba",
        "leady": 0,
        "wniosek": "Zero pytań o nawierzchnię. Cała doba to ogłoszenia "
                   "'sprzedam/kupię' sprzęt: hantle, atlasy, racki, bieżnie. "
                   "766 postów/mies. przy zerowej intencji na podłogę.",
    },
    "1391595044727481": {
        "grupa": "Siłownia w Domu",
        "blokow": 102,
        "zakres": "ok. 6 dni",
        "leady": 1,
        "wniosek": "Jeden wzorcowy lead na 6 dni: pytanie o podłogę 15-20 mm "
                   "pod rzucanie ciężarów, z wymaganiami co do gęstości gumy "
                   "i szczelin. Skala: ok. 5 leadów miesięcznie.",
    },
}


GROUPS = [
    # ================= POLSKA =================
    {
        "name": "Sprzedam, kupię, oddam - sprzęt sportowy, fitness, siłownia",
        "url": "https://www.facebook.com/groups/233349823542539/",
        "market": "PL", "type": "marketplace", "priority": 1,
        "privacy": "publiczna", "members": 112389,
        "posts_month": 766, "posts_today": 34,
        "link_policy": "unknown",
        "rules_note": "Regulamin to trzy razy wklejona ta sama reguła o zakazie "
                      "nękania. Zakazu promocji NIE MA — ale to bałagan "
                      "administracyjny, nie zielone światło. Moderacja może być "
                      "uznaniowa.",
        "why": "Największy wolumen w całej bazie: 766 postów miesięcznie, 34 dziś. "
               "Jeśli gdziekolwiek jest masa krytyczna, to tutaj.",
        "risk": "ZMIERZONE: 126 bloków z całej doby, ZERO pytań o nawierzchnię. "
                "Sam handel sprzętem. Wolumen jest pozorny — to nie jest kanał "
                "dla podłóg, mimo 112 tys. członków.",
    },
    {
        "name": "Siłownia w Domu",
        "url": "https://www.facebook.com/groups/1391595044727481/",
        "market": "PL", "type": "community", "priority": 1,
        "privacy": "prywatna", "members": 19023,
        "posts_month": 277, "posts_today": 14,
        "link_policy": "unknown",
        "rules_note": "Grupa prywatna — regulamin widoczny dopiero po dołączeniu. "
                      "Sprawdzić przed pierwszą odpowiedzią.",
        "why": "Druga co do wolumenu (277/mies.) i JEDYNA duża polska grupa "
               "dyskusyjna, a nie ogłoszeniowa. Tu pytają, a nie sprzedają — "
               "czyli tu odpowiedź eksperta ma sens.",
        "risk": "ZMIERZONE: 102 bloki z ok. 6 dni, 1 realny lead. To ok. 5 "
                "leadów miesięcznie. Mało, ale to jedyne miejsce, gdzie "
                "cokolwiek realnego padło.",
    },
    {
        "name": "GIEŁDA URZĄDZEŃ FITNESS",
        "url": "https://www.facebook.com/groups/915333785188247/",
        "market": "PL", "type": "trade", "priority": 2,
        "privacy": "publiczna", "members": 28924,
        "posts_month": 191, "posts_today": 9,
        "link_policy": "banned",
        "rules_note": "Reguła 3: 'Autopromocja, spam i nieistotne linki są "
                      "niedozwolone'. Link w komentarzu = złamanie regulaminu.",
        "why": "Obrót sprzętem komercyjnym — najbliżej właściciela obiektu "
               "po polskiej stronie.",
        "risk": "Zakaz linków. Model pracy: merytoryczny komentarz bez linku, "
                "dalej DM. Inaczej ban.",
    },
    {
        "name": "Giełda Sprzętu Sportowego",
        "url": "https://www.facebook.com/groups/216299371910280/",
        "market": "PL", "type": "marketplace", "priority": 2,
        "privacy": "publiczna", "members": 3576,
        "posts_month": 117, "posts_today": 6,
        "link_policy": "limited",
        "rules_note": "Reguła 1 dopuszcza link w ogłoszeniu. Reguła 3: "
                      "'Firmy - 1 na 7 dni'. Czyli firma MOŻE publikować, "
                      "ale raz w tygodniu.",
        "why": "Mała (3,6 tys.), ale jedyna polska grupa, która wprost dopuszcza "
               "obecność firm. 117 postów/mies. przy 3,6 tys. członków to "
               "najlepszy stosunek aktywności do wielkości w całej bazie.",
        "risk": "Limit 1 post na 7 dni. Wykorzystać na poradnik, nie na ofertę.",
    },
    {
        "name": "Obciążenie, hantle, ciezarki na siłownię",
        "url": "https://www.facebook.com/groups/880506396090559/",
        "market": "PL", "type": "marketplace", "priority": 3,
        "privacy": "publiczna", "members": 32626,
        "posts_month": 98, "posts_today": 7,
        "link_policy": "unknown",
        "rules_note": "Brak opublikowanego regulaminu.",
        "why": "Same obciążenia = strefa wolnych ciężarów = najgrubsze maty.",
        "risk": "98 postów/mies. przy 32 tys. członków — grupa uśpiona.",
    },
    {
        "name": "Praca w branży fitness",
        "url": "https://www.facebook.com/groups/473528603537767/",
        "market": "PL", "type": "industry", "priority": 4,
        "privacy": "publiczna", "members": 4202,
        "posts_month": 14, "posts_today": 1,
        "link_policy": "unknown",
        "rules_note": "Brak opublikowanego regulaminu.",
        "why": "Radar otwarć: nabór kadry = obiekt w budowie. Nie odpowiadasz — "
               "notujesz nazwę klubu.",
        "risk": "14 postów/mies. — z tego może 1-2 dotyczy nowego obiektu. "
                "Do przejrzenia raz w tygodniu ręcznie, nie do automatu.",
    },

    {
        "name": "Giełda sprzętu siłowego i fitness",
        "url": "https://www.facebook.com/groups/2106445906400441/",
        "market": "PL", "type": "trade", "priority": 1,
        "privacy": "publiczna", "members": 51739,
        "posts_month": 561, "posts_today": 15,
        "link_policy": "limited",
        "rules_note": "Reguła 3: 'Dopuszczalne jest wstawianie postów "
                      "sprzedażowych tylko w tematyce branży fitness' — czyli "
                      "firma MOŻE publikować, o ile na temat. Jedna z dwóch "
                      "polskich grup, gdzie link jest legalny.",
        "why": "ZNALEZIONA PÓŹNO: byłeś w niej od dawna, a nie było jej w bazie. "
               "51,7 tys. członków, 561 postów miesięcznie, 15 dziś, opis wprost "
               "mówi 'wszystko do klubów fitness i siłowni domowych'. Druga co "
               "do wolumenu polska grupa i jedyna duża, która dopuszcza posty "
               "sprzedażowe. Rośnie: +355 członków w tydzień.",
        "risk": "Gęstości leadów jeszcze nie mierzyłem — to następny krok.",
    },

    # ================= NIEMCY (elevatestore.de) =================
    {
        "name": "HomeGym / GarageGym (deutsch)",
        "url": "https://www.facebook.com/groups/498373407499636/",
        "market": "DE", "type": "community", "priority": 1,
        "privacy": "prywatna", "members": 20374,
        "posts_month": 61, "posts_today": 1,
        "link_policy": "allowed",
        "rules_note": "Reguła 3 WPROST dopuszcza: 'Gerne darfst du "
                      "HOMEGYM-relevante Shops, Aktionen, Produkte etc. ALLER "
                      "Hersteller teilen' — zakazana jest tylko czysta "
                      "autopromocja. Reguła 7 wymienia 'Welchen Boden?' jako "
                      "pytanie zadane w grupie ok. 30 razy.",
        "why": "Najlepsza pozycja w całej bazie i jedyna z twardym dowodem, że "
               "nasz temat wraca regularnie — administracja wpisała pytanie "
               "o podłogę do regulaminu, bo padało 30 razy. Do tego jedyna "
               "grupa, która jawnie pozwala linkować producentów.",
        "risk": "61 postów/mies. — niski wolumen. Reguła 7 każe najpierw szukać "
                "w archiwum, więc część pytań o podłogę nigdy nie powstanie.",
    },
    {
        "name": "Fitnessstudio Inhaber",
        "url": "https://www.facebook.com/groups/fitnessstudioinhaber",
        "market": "DE", "type": "industry", "priority": 2,
        "privacy": "prywatna", "members": 1460,
        "posts_month": 21, "posts_today": 0,
        "link_policy": "unknown",
        "rules_note": "Reguły: bez polityki, bez postów o własnych kursach/"
                      "akcjach, bez MLM. Ogólnego zakazu linków NIE MA, ale "
                      "reguła 3 pokazuje, że autopromocja jest źle widziana.",
        "why": "Sama śmietanka: wyłącznie właściciele i menedżerowie klubów. "
               "Jeden kontakt = potencjalnie kilkaset m².",
        "risk": "21 postów miesięcznie, dziś zero. To nie jest kanał "
                "wolumenowy — to miejsce na obecność, nie na odpowiadanie.",
    },
    {
        "name": "Fitness An- und Verkauf Deutschland",
        "url": "https://www.facebook.com/groups/2062121947259447/",
        "market": "DE", "type": "marketplace", "priority": 3,
        "privacy": "publiczna", "members": 15106,
        "posts_month": 92, "posts_today": 7,
        "link_policy": "banned",
        "rules_note": "Reguła 2: 'Eigenwerbung, Spam und nicht relevante Links "
                      "sind untersagt'.",
        "why": "Najaktywniejsza niemiecka giełda sprzętu (92/mies.).",
        "risk": "Zakaz linków — tylko komentarz merytoryczny i DM.",
    },
    {
        "name": "Fitnessgeräte gebraucht - An- und Verkauf",
        "url": "https://www.facebook.com/groups/275255396650801/",
        "market": "DE", "type": "marketplace", "priority": 3,
        "privacy": "prywatna", "members": 30490,
        "posts_month": 56, "posts_today": 0,
        "link_policy": "banned",
        "rules_note": "Reguła 2 zakazuje autopromocji i nieistotnych linków. "
                      "Reguła 3 wprost zabrania linkowania blogów i podcastów.",
        "why": "30 tys. członków, ale tylko 56 postów/mies.",
        "risk": "Zakaz linków plus ostra moderacja treści niehandlowych.",
    },
    {
        "name": "Bodybuilding und Fitness Deutschland",
        "url": "https://www.facebook.com/groups/bodyfit.deutschland/",
        "market": "DE", "type": "community", "priority": 4,
        "privacy": "publiczna", "members": 8246,
        "posts_month": 43, "posts_today": 1,
        "link_policy": "unknown",
        "rules_note": "Standardowy zestaw reguł o kulturze dyskusji.",
        "why": "Ogólna społeczność, sporadyczne wątki o home gymie.",
        "risk": "Temat szeroki, trafienia rzadkie.",
    },
]

# ============================================================================
# STAN CZŁONKOSTWA po akcji dołączania z 2026-09-05 (zweryfikowany klikając
# w każdą grupę i odczytując stan przycisku, nie z listy /joins/).
# ============================================================================

MEMBERSHIP = {
    "dolaczone": [
        # PL
        "Właściciele, menadżerowie, trenerzy, kluby fitness i siłowni",
        "Domowa Siłownia",
        "Sprzęt na siłownie, fitness, Obciążenie, Hantle, Maszyny",
        "SIŁOWNIA / TRENING / DIETA",
        "Kulturystyka, Siłownia, Cykle, Diety, Pomoc",
        "Siłownia dla początkujących",
        "Kupno Sprzedaż Serwis Sprzęt Siłowy & Cardio",
        # DE
        "Fitness Flohmarkt",
        "Bodybuilding und Fitness Kleinanzeigen",
        "Fitness / Bodybuilding / Beauty Kaufen-Verkaufen",
        "Fitnessgeräte-Set und Fitnessstudio Verkauf",
    ],
    "oczekuje_na_admina": [
        "SPORT SIŁOWNIA FITNES SPRZĘT... KUP SPRZEDAJ POMÓŻ (PL)",
        "Sprzęt fitness poleasingowy / powindykacyjny (PL)",
        "Giełda Sprzętu (Trójbój i Wyciskanie) (PL) — pytania wypełnione",
        "HomeGym (deutsch) / Trainingsgespräche (DE)",
        "Sport-Fitnessgeräte verkaufen (DE)",
        "Kraftsport und Ernährung (DE) — pytania wypełnione",
        "Fitnessstudio Inhaber (DE) — pytania wypełnione, odpowiedź szczera",
    ],
    "nieudane": [
        "Die Muskelwerkstatt (DE) — przycisk przechwytywany przez panel "
        "powiadomień Facebooka, do kliknięcia ręcznie",
    ],
}

# Odpowiedzi wysłane administratorom (do Twojej wiadomości — to poszło w Twoim imieniu):
ANKIETY = {
    "Giełda Sprzętu (Trójbój i Wyciskanie)":
        "Opis tematyki grupy + przykłady sprzętu (gryf olimpijski, talerze "
        "kalibrowane, ławka, pas trójbojowy, buty, owijki) i potwierdzenie "
        "znajomości zasad.",
    "Fitnessstudio Inhaber":
        "Pytanie brzmiało: jakiego obiektu jesteś właścicielem. Odpowiedź "
        "SZCZERA: nie prowadzisz studia, jesteś właścicielem Elevate Store, "
        "producenta nawierzchni; chcesz czytać i pomagać merytorycznie, "
        "bez postów reklamowych. Ryzyko odrzucenia realne.",
    "Kraftsport und Ernährung":
        "Trzy potwierdzenia: konto na prawdziwe nazwisko, zaproszę znajomych, "
        "nie publikuję reklam. Plus akceptacja regulaminu.",
}

# ============================================================================
# KOLEJKA DO DOŁĄCZENIA — znalezione wyszukiwarką Facebooka 2026-09-05.
# Liczby członków i "postów dziennie" pochodzą z kart wyników FB, nie z moich
# szacunków. Nazwy potwierdzone. Regulaminów jeszcze nie czytałem — widać je
# dopiero po wejściu do grupy, więc każda pozycja startuje z link_policy
# "unknown", czyli responder nie wstawi tam linku, dopóki nie sprawdzimy.
#
# Kolejność = kolejność dołączania. Wchodź po kilka dziennie, nie wszystkie
# naraz — seria zgłoszeń z jednego konta wygląda dla Facebooka jak bot.
# ============================================================================

JOIN_QUEUE = [
    # ---- PL ----
    {"name": "Właściciele, menadżerowie, trenerzy, kluby fitness i siłowni",
     "url": "https://www.facebook.com/groups/232812574798746/",
     "market": "PL", "members": 2500, "posts_day": 2, "privacy": "publiczna",
     "priority": 1,
     "why": "Decydenci B2B po polskiej stronie — dokładnie to, czego nie było "
            "w poprzedniej bazie. Właściciele i menadżerowie klubów. Jeden "
            "obiekt to setki metrów, więc 2 posty dziennie wystarczą."},
    {"name": "Domowa Siłownia",
     "url": "https://www.facebook.com/groups/2844126572521135/",
     "market": "PL", "members": 15000, "posts_day": 7, "privacy": "publiczna",
     "priority": 1,
     "why": "Druga duża polska grupa home gymowa obok 'Siłowni w Domu' — "
            "a to właśnie tam padł jedyny zmierzony lead. Ten sam typ ruchu, "
            "prawie dwa razy większa."},
    {"name": "Sprzęt na siłownie, fitness, Obciążenie, Hantle, Maszyny, Kupię, Sprzedam",
     "url": "https://www.facebook.com/groups/1140924534609835/",
     "market": "PL", "members": 5700, "posts_day": 10, "privacy": "publiczna",
     "priority": 2,
     "why": "10 postów dziennie przy 5,7 tys. członków — najlepszy stosunek "
            "aktywności do wielkości wśród polskich giełd."},
    {"name": "SPORT SIŁOWNIA FITNES SPRZĘT ODZIEZ SUPLEMENTY PORADY KUP SPRZEDAJ POMÓŻ",
     "url": "https://www.facebook.com/groups/1683417358589442/",
     "market": "PL", "members": 6600, "posts_day": 6, "privacy": "prywatna",
     "priority": 2,
     "why": "Giełda z wątkiem poradowym w nazwie — miesza handel z pytaniami, "
            "więc jest gdzie odpowiadać."},
    {"name": "Giełda Sprzętu (Trójbój i Wyciskanie)",
     "url": "https://www.facebook.com/groups/197934937042063/",
     "market": "PL", "members": 5100, "posts_day": None, "privacy": "prywatna",
     "priority": 2,
     "why": "Trójbój to najcięższe obciążenia i pomosty — najgrubsze maty "
            "w ofercie. Wąska, ale idealnie dopasowana."},
    {"name": "Sprzęt fitness / do siłowni — poleasingowy, powindykacyjny",
     "url": "https://www.facebook.com/groups/poleasingowe.fitness/",
     "market": "PL", "members": 587, "posts_day": None, "privacy": "prywatna",
     "priority": 3,
     "why": "Mała, ale kto kupuje sprzęt poleasingowy, ten wyposaża obiekt "
            "od zera. Sygnał otwarcia."},
    {"name": "Kupno Sprzedaż Serwis Sprzęt Siłowy & Cardio",
     "url": "https://www.facebook.com/groups/480522267617361/",
     "market": "PL", "members": 726, "posts_day": 4, "privacy": "publiczna",
     "priority": 3,
     "why": "Mała, ale 4 posty dziennie. Serwis w nazwie = ludzie z obiektami."},
    {"name": "SIŁOWNIA / TRENING / DIETA - porady i wsparcie dla każdego!",
     "url": "https://www.facebook.com/groups/silownia.trening.dieta/",
     "market": "PL", "members": 23000, "posts_day": None, "privacy": "publiczna",
     "priority": 3,
     "why": "Duża grupa poradowa. TOFU: pytania o home gym padają tu "
            "przypadkiem, ale przy 23 tys. członków to i tak coś."},
    {"name": "Kulturystyka, Siłownia, Cykle, Diety, Pomoc",
     "url": "https://www.facebook.com/groups/26549665951365757/",
     "market": "PL", "members": 5900, "posts_day": 10, "privacy": "publiczna",
     "priority": 4,
     "why": "Ogólna, ale 10+ postów dziennie. Czysty TOFU."},
    {"name": "Siłownia dla początkujących - diety, treningi, porady",
     "url": "https://www.facebook.com/groups/470504228839618/",
     "market": "PL", "members": 13000, "posts_day": 4, "privacy": "publiczna",
     "priority": 4,
     "why": "Początkujący budujący pierwszy kąt do ćwiczeń w domu."},

    # ---- DE ----
    {"name": "Fitness Flohmarkt",
     "url": "https://www.facebook.com/groups/829554940473103/",
     "market": "DE", "members": 86000, "posts_day": 9, "privacy": "prywatna",
     "priority": 1,
     "why": "Największa niemiecka giełda fitness — 86 tys. członków, 9 postów "
            "dziennie. Największy pojedynczy zbiornik ruchu na rynku, na "
            "którym mamy sklep."},
    {"name": "Bodybuilding und Fitness Kleinanzeigen",
     "url": "https://www.facebook.com/groups/800758306653473/",
     "market": "DE", "members": 9600, "posts_day": None, "privacy": "publiczna",
     "priority": 2,
     "why": "Publiczna giełda ogłoszeniowa, drugi co do wielkości zbiornik DE."},
    {"name": "HomeGym (deutsch) / Trainingsgespräche",
     "url": "https://www.facebook.com/groups/754956568751142/",
     "market": "DE", "members": 1800, "posts_day": None, "privacy": "prywatna",
     "priority": 2,
     "why": "Grupa siostrzana do HomeGym/GarageGym — ta jest od rozmów, nie "
            "od handlu. Czyli od pytań, na które się odpowiada."},
    {"name": "Sport-Fitnessgeräte verkaufen",
     "url": "https://www.facebook.com/groups/927126413977394/",
     "market": "DE", "members": 3900, "posts_day": 2, "privacy": "prywatna",
     "priority": 2,
     "why": "Giełda sprzętu, stały ruch."},
    {"name": "Fitnessgeräte-Set und Fitnessstudio Verkauf",
     "url": "https://www.facebook.com/groups/395459855478001/",
     "market": "DE", "members": 282, "posts_day": None, "privacy": "publiczna",
     "priority": 3,
     "why": "Malutka, ale handluje CAŁYMI siłowniami. Kto kupuje wyposażenie "
            "studia, ten za chwilę kładzie podłogę."},
    {"name": "Fitness / Bodybuilding / Beauty etc... Kaufen-Verkaufen",
     "url": "https://www.facebook.com/groups/1589160791399674/",
     "market": "DE", "members": 2700, "posts_day": None, "privacy": "publiczna",
     "priority": 3,
     "why": "Kolejna giełda DE."},
    {"name": "Die Muskelwerkstatt - Fitness, Ernährung & Leidenschaft",
     "url": "https://www.facebook.com/groups/274449101347419/",
     "market": "DE", "members": 213000, "posts_day": 90, "privacy": "publiczna",
     "priority": 3,
     "why": "213 tys. członków, 90+ postów dziennie. Ogólna, ale to "
            "największy strumień niemieckojęzyczny, jaki znalazłem. "
            "Czysty TOFU — łowimy rzadkie pytania w dużej rzece."},
    {"name": "Kraftsport und Ernährung",
     "url": "https://www.facebook.com/groups/581879655286396/",
     "market": "DE", "members": 74000, "posts_day": None, "privacy": "prywatna",
     "priority": 4,
     "why": "74 tys. członków, temat siłowy. TOFU."},
]


def queue_by_market(code: str) -> list[dict]:
    return sorted(
        (g for g in JOIN_QUEUE if g["market"] == code.upper()),
        key=lambda g: g["priority"],
    )


# Sprawdzone i ODRZUCONE — z powodem. Nie wracać.
REJECTED = [
    ("CrossFit Germany (12,4 tys. członków)",
     "ZERO postów w ostatnim miesiącu. Grupa martwa mimo wielkości."),
    ("CrossFit Athletes Deutschland (1,1 tys.)",
     "1 post w ostatnim miesiącu. Martwa."),
    ("CrossFit Polska (22,4 tys.)",
     "19 postów/mies. przy 22 tys. członków, dziś zero. Praktycznie martwa."),
    ("FitnessGeräte Verkauf+ Kauf (10,6 tys.)",
     "14 postów/mies. plus zakaz reklamy. Nie warto."),
    ("Grupy UK i US (7 sztuk)",
     "Brak sklepu i logistyki. Fracht na gumę zjada marżę."),
    ("Home Gym / Home Gym Community (EN)",
     "Poza zasięgiem sprzedażowym. Wartość wyłącznie contentowa — wątki "
     "o doborze podłogi jako materiał na bloga i FAQ."),
    ("Kępno - Ogłoszenia, Świat Licytacji, POZNAŃ Sprzedam/Kupię",
     "Ogólne ogłoszenia lokalne, sprzęt siłowy pojawia się przypadkiem."),
    ("TRENERZY PERSONALNI i grupy regionalne trenerów",
     "Trener nie kupuje nawierzchni — kupuje właściciel obiektu."),
]


# Grupy, które harvester faktycznie przegląda: te, w których Krystian jest
# członkiem (stan po akcji dołączania 2026-09-05). Pozycje z JOIN_QUEUE bez
# przeczytanego regulaminu dostają link_policy "unknown" -> responder nie wstawi
# tam linku, dopóki ktoś nie ustawi polityki po lekturze zasad grupy.
MONITORED_URLS = [
    # PL — baza (zmierzone, regulaminy sprawdzone)
    "https://www.facebook.com/groups/2106445906400441/",   # Giełda sprzętu siłowego i fitness (limited)
    "https://www.facebook.com/groups/233349823542539/",    # Sprzedam, kupię, oddam
    "https://www.facebook.com/groups/1391595044727481/",   # Siłownia w Domu
    "https://www.facebook.com/groups/915333785188247/",    # GIEŁDA URZĄDZEŃ FITNESS (banned)
    "https://www.facebook.com/groups/216299371910280/",    # Giełda Sprzętu Sportowego (limited)
    "https://www.facebook.com/groups/880506396090559/",    # Obciążenie, hantle
    # PL — dołączone 2026-09-05
    "https://www.facebook.com/groups/232812574798746/",    # Właściciele, menadżerowie klubów
    "https://www.facebook.com/groups/2844126572521135/",   # Domowa Siłownia
    "https://www.facebook.com/groups/1140924534609835/",   # Sprzęt na siłownie, Obciążenie, Hantle
    "https://www.facebook.com/groups/silownia.trening.dieta/",
    "https://www.facebook.com/groups/26549665951365757/",  # Kulturystyka, Siłownia
    "https://www.facebook.com/groups/470504228839618/",    # Siłownia dla początkujących
    "https://www.facebook.com/groups/480522267617361/",    # Kupno Sprzedaż Serwis
    # DE — członkostwo potwierdzone
    "https://www.facebook.com/groups/498373407499636/",    # HomeGym / GarageGym (deutsch) (allowed)
    "https://www.facebook.com/groups/2062121947259447/",   # Fitness An- und Verkauf (banned)
    "https://www.facebook.com/groups/275255396650801/",    # Fitnessgeräte gebraucht (banned)
    "https://www.facebook.com/groups/bodyfit.deutschland/",
    "https://www.facebook.com/groups/829554940473103/",    # Fitness Flohmarkt
    "https://www.facebook.com/groups/800758306653473/",    # Bodybuilding und Fitness Kleinanzeigen
    "https://www.facebook.com/groups/1589160791399674/",
    "https://www.facebook.com/groups/395459855478001/",    # Fitnessgeräte-Set und Fitnessstudio Verkauf
]


def monitored() -> list[dict]:
    """Pełne rekordy grup do przeglądania, z polityką linkowania."""
    by_url = {g["url"].rstrip("/"): g for g in GROUPS}
    for q in JOIN_QUEUE:
        by_url.setdefault(
            q["url"].rstrip("/"),
            {**q, "link_policy": q.get("link_policy", "unknown"), "type": q.get("type", "marketplace")},
        )
    out = []
    for u in MONITORED_URLS:
        g = by_url.get(u.rstrip("/"))
        if g is None:
            out.append({"name": u, "url": u, "market": "PL", "link_policy": "unknown"})
        else:
            out.append({**g, "url": u})
    return out


def by_priority(max_priority: int = 2) -> list[dict]:
    return sorted(
        (g for g in GROUPS if g["priority"] <= max_priority),
        key=lambda g: (g["priority"], -g["posts_month"]),
    )


def by_market(code: str) -> list[dict]:
    return sorted(
        (g for g in GROUPS if g["market"] == code.upper()),
        key=lambda g: (g["priority"], -g["posts_month"]),
    )


def linkable() -> list[dict]:
    """Grupy, w których regulamin dopuszcza link. Tylko tu publikujemy URL."""
    return [g for g in GROUPS if g["link_policy"] in ("allowed", "limited")]


def no_link() -> list[dict]:
    """Grupy z zakazem linków — komentarz bez URL-a, kontakt przez DM."""
    return [g for g in GROUPS if g["link_policy"] == "banned"]


def find(needle: str) -> dict:
    n = needle.lower().strip()
    hits = [g for g in GROUPS if n in g["url"].lower() or n in g["name"].lower()]
    if not hits:
        raise ValueError(f"Nie znam grupy: {needle!r}")
    if len(hits) > 1:
        raise ValueError(
            f"{needle!r} pasuje do wielu grup: {', '.join(g['name'] for g in hits)}"
        )
    return hits[0]


def monthly_ceiling(market: str | None = None) -> int:
    """Sufit: suma wszystkich postów miesięcznie. Nie prognoza leadów."""
    pool = by_market(market) if market else GROUPS
    return sum(g["posts_month"] for g in pool)


if __name__ == "__main__":
    print(f"Pomiar: {MEASURED_AT} | grup: {len(GROUPS)} "
          f"(PL {len(by_market('PL'))}, DE {len(by_market('DE'))}) "
          f"| odrzuconych: {len(REJECTED)}\n")

    hdr = f"{'PRIO':<5}{'RYNEK':<7}{'CZŁONKÓW':>10}{'POSTÓW/MIES':>13}  {'LINKI':<9} GRUPA"
    print(hdr)
    print("-" * len(hdr))
    for g in sorted(GROUPS, key=lambda g: (g["priority"], -g["posts_month"])):
        members = f"{g['members']:,}".replace(",", " ")
        print(f"P{g['priority']:<4}{g['market']:<7}{members:>10}"
              f"{g['posts_month']:>13}  {g['link_policy']:<9} {g['name'][:44]}")

    print(f"\nSufit wolumenu: PL {monthly_ceiling('PL')} postów/mies., "
          f"DE {monthly_ceiling('DE')} postów/mies.")

    print(f"\n=== DO DOŁĄCZENIA ({len(JOIN_QUEUE)}) ===")
    for g in sorted(JOIN_QUEUE, key=lambda g: (g["priority"], -g["members"])):
        czl = f"{g['members']:,}".replace(",", " ")
        pd = f"{g['posts_day']}/dzień" if g["posts_day"] else "brak danych"
        print(f"P{g['priority']} {g['market']:<3}{czl:>8} czł.  {pd:<12} {g['name'][:52]}")
    print(f"Linkowanie dozwolone w {len(linkable())} grupach, "
          f"zakazane w {len(no_link())}.")
