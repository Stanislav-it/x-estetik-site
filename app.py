from __future__ import annotations

import os
import re
import sqlite3
from html import escape as html_escape
from urllib.parse import quote
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from flask import Flask, abort, flash, redirect, render_template, request, send_from_directory, url_for

APP_DIR = Path(__file__).resolve().parent


# ----------------------------- Helpers -----------------------------

def get_env(name: str, default: str = "") -> str:
    v = os.environ.get(name, "").strip()
    return v if v else default


# ----------------------------- Data model -----------------------------

@dataclass(frozen=True)
class Product:
    slug: str
    name: str
    category: str  # lasers | hi-tech | accessories
    tag: str
    short: str
    bullets: List[str]
    price: str = ""
    rental: str = ""
    badge: str = ""
    pages: Optional[List[int]] = None  # for reference (images are pre-rendered)

    # Optional: before/after effects gallery (static/efekty/<effects_folder>/...)
    effects_folder: str = ""
    effects_url: str = ""




# Product photo overrides (drop files into static/photos/ with these base names)
PRODUCT_PHOTO_BASE = {
    'depimax': 'DepiMax',
    'ems-formax': 'EMS FormaX',
    'estetik-frax': 'Estetik Frax',
    'lumera-estetik': 'Lumera Estetik',
    'regen-lift': 'Regen Lift',
    'x-blue-pen': 'X-Pen',
    'x-boss': 'X-BOSS',
    'x-contour-krio': 'X-Contour KRIO',
    'x-derma': 'X-Derma',
    'x-fraxel-premium': 'X-FRAXEL PRO',
    'x-fraxel': 'X-FRAXEL',
    'x-hair': 'X-Hair',
    'x-levage-erbo': 'X-Levage Erbo',
    'x-levage': 'X-Levage Pro',
    'x-shape': 'X-Shape',
    'x-v980': 'X-V980',
}

PRODUCTS: List[Product] = [
    # --- LASERY (6) ---
    Product(
        slug="x-levage",
        name="X‑Levage Pro (laser tulowy 1927 nm)",
        category="lasers",
        tag="Laser tulowy",
        short="Długość fali 1927 nm — ukierunkowana praca w warstwach naskórka i skóry właściwej, wspiera odnowę skóry i redukcję przebarwień.",
        bullets=[
            "Długość fali: 1927 nm (laser tulowy).",
            "Zastosowania: przebarwienia, fotostarzenie, poprawa struktury skóry.",
            "Technologia wspiera stymulację kolagenu i regenerację.",
        ],
        price="105 000 zł",
        pages=list(range(8, 16)),
        effects_folder="x-levage",
        effects_url="https://lasertulowyxlevage.pl/",
    ),
    Product(
        slug="x-levage-erbo",
        name="X‑Levage Erbo (1550 nm + 1927 nm)",
        category="lasers",
        tag="Laser frakcyjny nieablacyjny",
        short="Podwójna długość fali: 1550 nm (erbowo‑szklany) + 1927 nm (tulowy). Resurfacing i przebudowa skóry z szybkim powrotem do formy.",
        bullets=[
            "Podwójna długość fali: 1550 nm + 1927 nm.",
            "Nieablacyjny resurfacing — poprawa tekstury, kolorytu i elastyczności.",
            "Zastosowania: zmarszczki, blizny potrądzikowe, rozstępy, fotostarzenie.",
        ],
        price="129 000 zł",
        pages=list(range(2, 8)),
        effects_folder="x-levage-erbo",
        effects_url="https://lasertulowyxlevage.pl/",
    ),
    Product(
        slug="depimax",
        name="DepiMax™ (laser diodowy do epilacji)",
        category="lasers",
        tag="Laser diodowy 4‑wiązki",
        short="Laser diodowy o czterech długościach fali: 755 / 808 / 940 / 1064 nm. Szybkie, komfortowe zabiegi depilacji dla szerokiego spektrum fototypów.",
        bullets=[
            "Cztery długości fal: 755 / 808 / 940 / 1064 nm.",
            "Wysoka moc i system chłodzenia dla większego komfortu.",
            "Zastosowanie: trwała redukcja owłosienia (różne fototypy).",
        ],
        price="55 000 zł",
        pages=list(range(21, 28)),
    ),
    Product(
        slug="x-hair",
        name="X‑Hair (X‑HairOn)",
        category="lasers",
        tag="Laser diodowy do epilacji",
        short="Diodowy laser do epilacji łączący skuteczne długości fal dla wysokiej skuteczności i bezpieczeństwa w zabiegach depilacji profesjonalnej.",
        bullets=[
            "Wielofalowe podejście — dopasowanie do różnych fototypów skóry.",
            "Nowoczesny system chłodzenia (komfort zabiegowy).",
            "Stabilna praca i wysoka wydajność w gabinecie.",
        ],
        price="65 000 zł",
        pages=list(range(16, 21)),
    ),
    Product(
        slug="x-fraxel",
        name="X‑FRAXEL (laser frakcyjny CO₂)",
        category="lasers",
        tag="Laser ablacyjny CO₂",
        short="Laser frakcyjny CO₂ o długości fali 10 600 nm. Resurfacing, odmładzanie skóry i redukcja blizn z kontrolowanym czasem gojenia.",
        bullets=[
            "Długość fali: 10 600 nm (CO₂).",
            "Zastosowania: blizny, rozstępy, zmarszczki, resurfacing.",
            "Tryby skanowania dla różnych obszarów zabiegowych.",
        ],
        price="35 000 zł",
        rental="2 200 zł",
        pages=list(range(34, 37)),
    ),
    Product(
        slug="x-fraxel-premium",
        name="X‑FRAXEL PRO (Premium)",
        category="lasers",
        tag="Laser ablacyjny CO₂ — PRO",
        short="Wersja PRO z rozbudowanym skanowaniem i konfiguracją głowic. Zaprojektowana do intensywnej pracy w gabinecie i szerokiego spektrum wskazań.",
        bullets=[
            "Długość fali: 10 600 nm (CO₂).",
            "7 trybów skanowania + regulacja gęstości mikrostref.",
            "Zestaw głowic dopasowanych do różnych wskazań.",
        ],
        price="70 000 zł",
        pages=list(range(28, 34)),
        badge="Premium",
    ),

    # --- HI‑TECH ---
    Product(
        slug="x-v980",
        name="X‑V980 (laser diodowy naczyniowy 980 nm)",
        category="lasers",
        tag="Laser diodowy 980 nm",
        short="Laser diodowy 980 nm do pracy z naczynkami — precyzyjna aplikacja i szybkie rezultaty w zamykaniu zmian naczyniowych.",
        bullets=[
            "Długość fali: 980 nm.",
            "Zastosowania: teleangiektazje, rubiniaki, wybrane naczyniaki.",
            "Mała głowica do precyzyjnych obszarów.",
        ],
        price="22 500 zł",
        rental="1 500 zł",
        pages=list(range(37, 40)),
    ),
    Product(
        slug="x-boss",
        name="X‑BOSS (Q‑Switch) / X‑Boss Pro™",
        category="lasers",
        tag="Q‑Switch",
        short="Laser Q‑Switch do usuwania tatuaży i przebarwień — konfiguracje wielowiązkowe oraz funkcje peelingu węglowego (w zależności od wersji).",
        bullets=[
            "Zastosowania: tatuaże, makijaż permanentny, przebarwienia.",
            "Wersje z wieloma długościami fal (katalog).",
            "System chłodzenia i ergonomiczne głowice.",
        ],
        price="27 000 zł",
        rental="2 000 zł",
        pages=[40, 41, 42],
    ),
    Product(
        slug="lumera-estetik",
        name="Luméra Estetik™ (DPL & NIR)",
        category="hi-tech",
        tag="DPL + NIR",
        short="Urządzenie łączące DPL (pulsacyjne światło) i NIR — szeroki zakres terapii skóry i wsparcie protokołów zabiegowych.",
        bullets=[
            "Moduły DPL & NIR.",
            "Rozwiązanie do terapii skóry i przebudowy.",
            "Nowoczesny interfejs i szybka praca.",
        ],
        price="39 000 zł",
        pages=list(range(43, 49)),
    ),
    Product(
        slug="estetik-frax",
        name="Estetik Frax™ (RF mikroigłowy)",
        category="hi-tech",
        tag="RF mikroigłowy",
        short="Radiofrekwencja mikroigłowa — kontrolowana stymulacja skóry z możliwością personalizacji protokołów w zależności od obszaru i wskazania.",
        bullets=[
            "RF mikroigłowy — praca na strukturach skóry.",
            "Personalizacja parametrów zabiegowych.",
            "Zastosowania: tekstura skóry, blizny, odmładzanie (w zależności od protokołu).",
        ],
        price="25 000 zł",
        rental="1 500 zł",
        pages=list(range(49, 55)),
    ),
    Product(
        slug="regen-lift",
        name="Regen Lift (fala radiowa 448 kHz)",
        category="hi-tech",
        tag="RF 448 kHz",
        short="Technologia fali radiowej 448 kHz — wsparcie terapii, zabiegów ujędrniających i protokołów regeneracyjnych.",
        bullets=[
            "Fala radiowa 448 kHz.",
            "Zastosowania: ujędrnianie, regeneracja, wsparcie protokołów (katalog).",
            "Tryby pracy dostosowane do potrzeb gabinetu.",
        ],
        price="49 000 zł",
        rental="3 000 zł",
        pages=list(range(55, 64)),
    ),
    Product(
        slug="x-contour-krio",
        name="X‑Contour KRIO",
        category="hi-tech",
        tag="Kriolipoliza bezpróżniowa + EMS",
        short="Bezpróżniowa kriolipoliza połączona z elektroporacją i EMS. 8 padów może pracować niezależnie lub jednocześnie, co pozwala wykonywać zabiegi na dużych obszarach ciała.",
        bullets=[
            "Do 8 padów działających jednocześnie — duże obszary zabiegowe.",
            "Komfort bez użycia próżni: bez krwiaków i obrzęków spowodowanych zasysaniem.",
            "Parametry: EMS 4000 Hz, temperatura 45°C do −10°C, 3 rodzaje kształtu fali.",
            "35 minut zabiegu: 30 min padów E‑CRYO + 5 min aplikatora O‑Shock.",
            "Deklarowane rezultaty: do 6,8 cm redukcji obwodu; 40–60% redukcji tłuszczu na zabieg (wg katalogu).",
        ],
        price="55 000 zł",
        rental="2600 zł",
        pages=list(range(64, 69)),
        badge="Body shaping",
    ),
    Product(
        slug="x-shape",
        name="X‑Shape",
        category="hi-tech",
        tag="Modelowanie sylwetki",
        short="Urządzenie do zabiegów modelowania — podejście łączące technologie dla maksymalizacji efektu i komfortu.",
        bullets=[
            "Zabiegi ukierunkowane na modelowanie sylwetki.",
            "Tryby i programy dobrane do protokołów gabinetowych.",
            "Nowoczesny panel i ergonomia.",
        ],
        price="50 000 zł",
        pages=list(range(69, 73)),
    ),
    Product(
        slug="ems-formax",
        name="EMS FormaX",
        category="hi-tech",
        tag="EMS / HIFEM",
        short="Urządzenie EMS/HIFEM do intensywnej stymulacji mięśni — protokoły na różne obszary ciała i praca w trybie gabinetowym.",
        bullets=[
            "Technologia HIFEM/EMS (katalog).",
            "Programy na różne partie ciała.",
            "Wysoka moc i duży ekran sterowania.",
        ],
        price="55 000 zł",
        pages=list(range(73, 82)),
    ),
    Product(
        slug="x-derma",
        name="X‑Derma (hydradermabrazja)",
        category="hi-tech",
        tag="Oczyszczanie + nawilżanie",
        short="Platforma do oczyszczania, ekstrakcji i nawilżania (hydradermabrazja). Świetna jako zabieg samodzielny oraz jako przygotowanie skóry do dalszych terapii.",
        bullets=[
            "3‑etapowy proces: złuszczanie, oczyszczanie/ekstrakcja, nawilżanie.",
            "Obrotowa końcówka 360° + ssanie dla skutecznej ekstrakcji.",
            "Minimalny dyskomfort i szybki efekt zabiegowy.",
        ],
        price="15 000 zł",
        pages=[91, 92, 93, 94, 97, 98, 99],
    ),

    # --- AKCESORIA ---
    Product(
        slug="x-blue-pen",
        name="X‑Pen (mikronakłuwanie)",
        category="hi-tech",
        tag="Micro‑needling",
        short="Urządzenie do mikroigłowego nakłuwania z jednorazowymi kartridżami. Szybka praca i ergonomia dla gabinetu.",
        bullets=[
            "Do 1920 kanałów na sekundę (katalog).",
            "Głębokość nakłuć do 2,5 mm.",
            "System ograniczający ryzyko zakażeń krzyżowych (jednorazowe elementy).",
        ],
        price="5 500 zł",
        rental="500 zł",
        pages=list(range(82, 86)),
    ),
    Product(
        slug="biopen-q2",
        name="Bio Pen Q2",
        category="hi-tech",
        tag="Micro‑needling + EMS + LED",
        short="Urządzenie łączące mikronakłuwanie, elektroporację EMS i światło LED. Wielofunkcyjne podejście do pielęgnacji i wsparcia regeneracji skóry.",
        bullets=[
            "3 technologie w jednym: micro‑needling + EMS + LED.",
            "Wspiera teksturę skóry, jędrność i redukcję drobnych zmarszczek.",
            "Kartridże jednorazowe — higiena i bezpieczeństwo.",
        ],
        price="800 zł",
        rental="150 zł",
        pages=list(range(86, 91)),
        badge="Top value",
    ),
]

PRODUCTS_BY_SLUG: Dict[str, Product] = {p.slug: p for p in PRODUCTS}

# Order of products on the homepage (manual business order).
# Any products not listed here fall back to alphabetical order after listed items.
HOME_PAGE_ORDER: List[str] = [
    "x-levage-erbo",
    "x-levage",
    "x-fraxel-premium",
    "x-fraxel",
    "depimax",
    "x-hair",
    "x-boss",
    "x-v980",
    "regen-lift",
    "x-contour-krio",
    "x-shape",
    "ems-formax",
    "estetik-frax",
    "lumera-estetik",
    "x-derma",
    "x-blue-pen",
    "biopen-q2",
]

HOME_PAGE_ORDER_MAP: Dict[str, int] = {slug: i for i, slug in enumerate(HOME_PAGE_ORDER)}


CATEGORY_META = {
    "lasers": {
        "label": "Lasery",
        "route": "lasers",
        "description": "Wszystkie lasery . Kliknij urządzenie, aby otworzyć kartę z galerią stron katalogowych.",
        "grid_classes": "grid-cols-2 lg:grid-cols-3 gap-2 sm:gap-4",
        "img_class": "h-44 sm:h-60",
        "section_px": "px-0 sm:px-6 lg:px-10",
        "card_round": "rounded-none sm:rounded-3xl",
    },
    "hi-tech": {
        "label": "Urządzenia Hi‑Tech",
        "route": "hi_tech",
        "description": "Pozostałe urządzenia  — RF, DPL/NIR, EMS, hydradermabrazja i inne technologie.",
    },
    "accessories": {
        "label": "Akcesoria",
        "route": "accessories",
        "description": "Akcesoria i urządzenia uzupełniające ofertę gabinetu.",
    },
}


# ----------------------------- App factory -----------------------------

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=get_env("SECRET_KEY", "dev-secret-key-change-me"),
        STATIC_VERSION=get_env("STATIC_VERSION", str(int(datetime.utcnow().timestamp()))),
        SITE_NAME=get_env("SITE_NAME", "X‑Estetik"),
        BRAND=get_env("BRAND", "X‑Estetik"),
        CONTACT_EMAIL=get_env("CONTACT_EMAIL", "biuro.x-estetik@op.pl"),
        CONTACT_PHONE=get_env("CONTACT_PHONE", "+48 518 151 673"),
        CONTACT_NOTE=get_env("CONTACT_NOTE", "Odpowiadamy w dni robocze."),
        INSTAGRAM_URL=get_env("INSTAGRAM_URL", "https://www.instagram.com/xestetik/"),
        INSTAGRAM_HANDLE=get_env("INSTAGRAM_HANDLE", "@xestetik"),
        FACEBOOK_URL=get_env("FACEBOOK_URL", "https://www.facebook.com/share/16zqxJveFY/"),
        FACEBOOK_HANDLE=get_env("FACEBOOK_HANDLE", "X‑Estetik"),

        FACEBOOK_EPILACJA_URL=get_env("FACEBOOK_EPILACJA_URL", "https://www.facebook.com/share/17P4zyb7vj/"),
        FACEBOOK_EPILACJA_HANDLE=get_env("FACEBOOK_EPILACJA_HANDLE", "Laser diodowy do epilacji"),

        FACEBOOK_ESTETIK_FRAX_URL=get_env("FACEBOOK_ESTETIK_FRAX_URL", "https://www.facebook.com/share/1DrByjvhom/"),
        FACEBOOK_ESTETIK_FRAX_HANDLE=get_env("FACEBOOK_ESTETIK_FRAX_HANDLE", "Estetik Frax"),

        FACEBOOK_TULOWY_ERBO_URL=get_env("FACEBOOK_TULOWY_ERBO_URL", "https://www.facebook.com/lasertulowyxlevage"),
        FACEBOOK_TULOWY_ERBO_HANDLE=get_env("FACEBOOK_TULOWY_ERBO_HANDLE", "laser tulowy + erbowo szklany"),
        TIKTOK_URL=get_env("TIKTOK_URL", "https://www.tiktok.com/"),
        TIKTOK_HANDLE=get_env("TIKTOK_HANDLE", "TikTok"),
        DB_PATH=get_env("DB_PATH", str(APP_DIR / "instance" / "app.db")),

        # R2 public bucket base URL for /filmy showcase clips.
        # Example: https://<pub-...>.r2.dev
        FILMY_BASE_URL=get_env("FILMY_BASE_URL", "https://pub-6b9f87ec02e04dc88c5b18144e88754a.r2.dev"),

        # Comma-separated list of MP4 object names in the R2 bucket for /filmy.
        FILMY_FILES=get_env(
            "FILMY_FILES",
            "video 5.mp4,video 8.mp4,video 9.mp4,video 10.mp4,video 11.mp4,video 14.mp4,video 15.mp4,video 16.mp4,video 17.mp4,video 18.mp4,video 19.mp4,video 20.mp4,video 21.mp4",
        ),

        # Optional external override for the HERO video ("video 1").
        # If set, the site will use this URL *only when the local file is missing*.
        # You can pass either:
        #   - a Google Drive share URL (e.g. https://drive.google.com/file/d/<id>/view?...)
        #   - or a raw Drive file id.
        # Default: the user-provided Drive file.
        VIDEO_1_URL=get_env(
            "VIDEO_1_URL",
            "https://drive.google.com/file/d/1GeLb0EQsq8bxrajZ74LNE6UvUUkiPBy0/view?usp=sharing",
        ),
    )

    def build_r2_showcase() -> list[dict]:
        """Build a list of showcase clips from the public R2 bucket (used on homepage + /filmy)."""
        base = (app.config.get("FILMY_BASE_URL") or "").strip().rstrip("/")
        files_raw = (app.config.get("FILMY_FILES") or "").strip()

        default_files = [
            "video 5.mp4",
            "video 8.mp4",
            "video 9.mp4",
            "video 10.mp4",
            "video 11.mp4",
            "video 14.mp4",
            "video 15.mp4",
            "video 16.mp4",
            "video 17.mp4",
            "video 18.mp4",
            "video 19.mp4",
            "video 20.mp4",
            "video 21.mp4",
        ]

        files = [s.strip() for s in files_raw.split(",") if s.strip()] if files_raw else default_files

        # Sort naturally by the first number in the name, if present.
        def num_key(name: str) -> int:
            m = re.search(r"(\d+)", name)
            return int(m.group(1)) if m else 10**9

        files = sorted(files, key=lambda s: (num_key(s), s.lower()))

        showcase: list[dict] = []
        for fn in files:
            url = f"{base}/{quote(fn)}" if base else ""
            title = fn.rsplit(".", 1)[0]
            if url:
                showcase.append({"src": url, "srcs": [url], "title": title, "desc": ""})

        return showcase

    (APP_DIR / "instance").mkdir(parents=True, exist_ok=True)
    init_db(app)
    ensure_qr_codes(app)

    def extract_drive_file_id(url_or_id: str) -> str:
        """Extract Google Drive file id from a share URL, or return the id as-is."""
        if not url_or_id:
            return ""
        s = url_or_id.strip()
        # Already looks like a raw Drive file id
        if re.fullmatch(r"[A-Za-z0-9_-]{10,}", s) and "http" not in s.lower():
            return s
        # Common share URL: https://drive.google.com/file/d/<id>/view
        m = re.search(r"/file/d/([A-Za-z0-9_-]+)", s)
        if m:
            return m.group(1)
        # open?id=<id>
        m = re.search(r"[?&]id=([A-Za-z0-9_-]+)", s)
        if m:
            return m.group(1)
        return ""

    def drive_direct_download_candidates(url_or_id: str) -> list[str]:
        """Return a small list of direct-download URLs for a Drive file."""
        fid = extract_drive_file_id(url_or_id)
        if not fid:
            return []
        # NOTE: Public Drive files >100MB sometimes need a confirm flag.
        return [
            f"https://drive.google.com/uc?export=download&confirm=t&id={fid}",
            f"https://drive.usercontent.google.com/download?id={fid}&export=download&confirm=t",
        ]

    def is_external_url(url: str) -> bool:
        return bool(url) and bool(re.match(r"^https?://", url.strip(), flags=re.IGNORECASE))

    @app.context_processor
    def inject_globals():
        def resolve_video_urls(video_base: str) -> list[str]:
            """Return a list of candidate URLs for a given video base name."""
            base = (video_base or "").strip()
            if not base:
                return []

            # Prefer local static file when present.
            local = resolve_static_video(base)
            if local:
                return [local]

            # For HERO video ("video 1"), fall back to an external URL (e.g. Google Drive).
            if base.lower() == "video 1":
                raw = (app.config.get("VIDEO_1_URL") or "").strip()
                if raw:
                    drive_id = extract_drive_file_id(raw)
                    if drive_id:
                        return drive_direct_download_candidates(drive_id)
                    return [raw]

            return []

        def resolve_video(video_base: str) -> str:
            urls = resolve_video_urls(video_base)
            return urls[0] if urls else ""

        return {
            "SITE_NAME": app.config["SITE_NAME"],
            "BRAND": app.config["BRAND"],
            "CONTACT_EMAIL": app.config["CONTACT_EMAIL"],
            "CONTACT_PHONE": app.config["CONTACT_PHONE"],
            "CONTACT_NOTE": app.config.get("CONTACT_NOTE", ""),
            "INSTAGRAM_URL": app.config.get("INSTAGRAM_URL", ""),
            "INSTAGRAM_HANDLE": app.config.get("INSTAGRAM_HANDLE", ""),
            "FACEBOOK_URL": app.config.get("FACEBOOK_URL", ""),
            "FACEBOOK_HANDLE": app.config.get("FACEBOOK_HANDLE", ""),
            "HAS_ACCESSORIES": any(p.category == "accessories" for p in PRODUCTS),
            "STATIC_VERSION": app.config["STATIC_VERSION"],
            "CURRENT_YEAR": datetime.utcnow().year,
            "video_url": resolve_video,
            "video_urls": resolve_video_urls,

            # Public R2 showcase clips (homepage + /filmy)
            "R2_SHOWCASE": build_r2_showcase(),

        }
    @app.get("/")
    def index():
        # Homepage blocks
        home_reviews = sample_reviews()[:6]
        def home_sort_key(p: Product):
            # Sort by the explicit homepage order first; then fall back to name.
            return (HOME_PAGE_ORDER_MAP.get(p.slug, 10**9), p.name.lower())

        lasers_all = sorted([p for p in PRODUCTS if p.category == "lasers"], key=home_sort_key)
        hi_tech_all = sorted([p for p in PRODUCTS if p.category == "hi-tech"], key=home_sort_key)
        accessories_all = sorted([p for p in PRODUCTS if p.category == "accessories"], key=home_sort_key)
        return render_template(
            "index.html",
            lasers_products=[to_view(p) for p in lasers_all],
            hi_tech_products=[to_view(p) for p in hi_tech_all],
            accessories_products=[to_view(p) for p in accessories_all],
            home_reviews=home_reviews,
        )

    @app.get("/o-nas")
    def about():
        about_text = get_env(
            "ABOUT_TEXT",
            "X‑Estetik to partner technologiczny dla gabinetów kosmetologii i klinik medycyny estetycznej. "
            "Selekcjonujemy urządzenia, które realnie budują przewagę: skracają czas pracy, pozwalają tworzyć "
            "powtarzalne protokoły i podnoszą komfort zabiegów."
            "\n\n"
            "Wspieramy Cię w całym procesie: od doboru technologii i konfiguracji, przez szkolenie, aż po materiały "
            "sprzedażowe. Ten serwis działa jak katalog premium — kliknij produkt, pokaż klientowi strony  "
            "i pobierz PDF jednym przyciskiem."
            "\n\n"
            "Jeśli chcesz, przygotujemy rekomendację zestawu urządzeń pod Twoją ofertę i budżet oraz pomożemy ułożyć "
            "plan wdrożenia (marketing, pricing, protokoły).",
        )
        return render_template("about.html", about_text=about_text)

    @app.get("/finansowanie")
    def finansowanie():
        return render_template("finansowanie.html")

    @app.get("/gielda")
    def gielda():
        return render_template("gielda.html")

    @app.get("/lasery")
    def lasers():
        prods = [p for p in PRODUCTS if p.category == "lasers"]
        return render_products_list("lasers", prods)

    @app.get("/urzadzenia-hi-tech")
    def hi_tech():
        prods = [p for p in PRODUCTS if p.category == "hi-tech"]
        return render_products_list("hi-tech", prods)

    @app.get("/akcesoria")
    def accessories():
        prods = [p for p in PRODUCTS if p.category == "accessories"]
        return render_products_list("accessories", prods)

    @app.get("/opinie")
    def reviews():
        return render_template("reviews.html", reviews=sample_reviews())

    @app.get("/media-spolecznosciowe")
    def social():
        socials = [
            {"label": "Instagram", "handle": app.config.get("INSTAGRAM_HANDLE", ""), "url": app.config.get("INSTAGRAM_URL", ""), "qr": url_for("static", filename="img/qr/instagram.png")},

            {"label": "Facebook — fanpage firmowy", "handle": app.config.get("FACEBOOK_HANDLE", ""), "url": app.config.get("FACEBOOK_URL", ""), "qr": url_for("static", filename="img/qr/facebook.png")},
            {"label": "Facebook — laser diodowy do epilacji", "handle": app.config.get("FACEBOOK_EPILACJA_HANDLE", ""), "url": app.config.get("FACEBOOK_EPILACJA_URL", ""), "qr": url_for("static", filename="img/qr/facebook_epilacja.png")},
            {"label": "Facebook — Estetik Frax", "handle": app.config.get("FACEBOOK_ESTETIK_FRAX_HANDLE", ""), "url": app.config.get("FACEBOOK_ESTETIK_FRAX_URL", ""), "qr": url_for("static", filename="img/qr/facebook_estetik_frax.png")},
            {"label": "Facebook — laser tulowy + erbowo szklany", "handle": app.config.get("FACEBOOK_TULOWY_ERBO_HANDLE", ""), "url": app.config.get("FACEBOOK_TULOWY_ERBO_URL", ""), "qr": url_for("static", filename="img/qr/facebook_tulowy_erbo.png")},
        ]
        socials = [s for s in socials if s.get("url")]
        return render_template("social.html", socials=socials)

    @app.get("/filmy")
    def filmy():
        return render_template("filmy.html", filmy_showcase=build_r2_showcase())

    @app.get("/produkt/<slug>")
    def product_detail(slug: str):
        p = PRODUCTS_BY_SLUG.get(slug)
        if not p:
            abort(404)

        meta = CATEGORY_META.get(p.category, {})
        back_label = meta.get("label", "Lista")
        back_route = meta.get("route", "index")
        back_url = url_for(back_route)

        view = to_view(p)
        view["back_label"] = back_label
        view["back_url"] = back_url
        view["hero"] = view["thumb"] if view.get("photo_base") else (first_gallery_image(slug) or view["thumb"])
        view["gallery"] = list_gallery_images(slug)

        # Effects (before/after) — visible for selected devices
        effects_folder = (p.effects_folder or "").strip()
        effects_url = (p.effects_url or "").strip()
        effects_enabled = bool(effects_folder or effects_url)
        folder = effects_folder or p.slug
        effects_images = list_effect_images(folder)
        # Optional fallback: if mapping uses a custom folder but it's empty
        if not effects_images and effects_folder and effects_folder != p.slug:
            effects_images = list_effect_images(p.slug)

        return render_template(
            "product_detail.html",
            product=view,
            effects_enabled=effects_enabled,
            effects_images=effects_images,
            effects_folder=folder,
            effects_tech_url=effects_url,
        )

    @app.get("/katalog")
    def catalog_download():
        return send_from_directory(APP_DIR / "static" / "pdf", "X-Estetik-Katalog-2026.pdf", as_attachment=True)

    @app.post("/lead")
    def lead():
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip()
        phone = (request.form.get("phone") or "").strip()
        message = (request.form.get("message") or "").strip()
        privacy_accept = (request.form.get("privacy_accept") or "").strip() == "1"

        if not name or not email or not message:
            flash("Uzupełnij wymagane pola: imię, e‑mail oraz wiadomość.", "error")
            return redirect(request.referrer or url_for("index") + "#kontakt")

        if not privacy_accept:
            flash("Zaznacz zgodę na Politykę prywatności, aby wysłać formularz.", "error")
            return redirect(request.referrer or url_for("index") + "#kontakt")

        save_lead(app, name=name, email=email, phone=phone, message=message, path=(request.referrer or ""))
        flash("Dziękujemy! Wiadomość została zapisana. Skontaktujemy się najszybciej jak to możliwe.", "success")
        return redirect((request.referrer or url_for("index")) + "#kontakt")

    @app.get("/polityki/<slug>")
    def policy(slug: str):
        policies = policy_content(app)
        if slug not in policies:
            abort(404)
        title, body = policies[slug]
        return render_template("policy.html", page_title=title, page_body=body)

    @app.get("/health")
    def health():
        return {"status": "ok", "products": len(PRODUCTS)}

    @app.errorhandler(404)
    def _404(_e):
        return render_template("404.html"), 404

    return app


# ----------------------------- Views -----------------------------

def resolve_static_photo(photo_base: str) -> str:
    """Resolve a product photo URL from static/photos by base name.

    - Matches the base name (stem) case-insensitively.
    - Accepts .jpg/.jpeg/.png/.webp/.jfif (any extension case, e.g. .JPEG).
    - Returns the real filename so the URL matches the filesystem exactly.
    """
    if not photo_base:
        return ""

    folder = APP_DIR / "static" / "photos"
    if not folder.exists():
        return ""

    # Normalize to survive Windows/Explorer copy-paste of “fancy” dashes/spaces
    # (e.g. X‑Levage uses U+2011 non‑breaking hyphen, not ASCII '-').
    def _norm(s: str) -> str:
        if not s:
            return ""
        s = s.replace("\u00A0", " ")  # NBSP
        dash_chars = "\u2010\u2011\u2012\u2013\u2014\u2212\uFE58\uFE63\uFF0D"
        for ch in dash_chars:
            s = s.replace(ch, "-")
        s = s.strip().lower()
        s = re.sub(r"\s+", " ", s)
        return s

    wanted = _norm(photo_base)
    allowed = {".jpg", ".jpeg", ".png", ".webp", ".jfif"}

    try:
        for fp in folder.iterdir():
            if not fp.is_file():
                continue
            if fp.suffix.lower() not in allowed:
                continue
            if _norm(fp.stem) == wanted:
                return url_for("static", filename=f"photos/{fp.name}")
    except Exception:
        return ""

    return ""


def resolve_static_video(video_base: str) -> str:
    """Resolve a video URL from static/video by base name (stem), extension-agnostic.

    - Matches the base name (stem) case-insensitively.
    - Accepts .mp4/.mov/.m4v/.webm (any extension case).
    - Normalizes “fancy” dashes/spaces (e.g. U+2011) to survive Windows Explorer names.
    - Returns the real filename so the URL matches the filesystem exactly.
    """
    if not video_base:
        return ""

    folder = APP_DIR / "static" / "video"
    if not folder.exists():
        return ""

    def _norm(s: str) -> str:
        if not s:
            return ""
        s = s.replace("\u00A0", " ")  # NBSP
        dash_chars = "\u2010\u2011\u2012\u2013\u2014\u2212\uFE58\uFE63\uFF0D"
        for ch in dash_chars:
            s = s.replace(ch, "-")
        s = s.strip().lower()
        s = re.sub(r"\s+", " ", s)
        return s

    wanted = _norm(video_base)
    allowed = {".mp4", ".mov", ".m4v", ".webm"}

    # Prefer mp4 then mov then m4v/webm
    ext_priority = {".mp4": 0, ".mov": 1, ".m4v": 2, ".webm": 3}

    best_fp = None
    best_prio = 999

    try:
        for fp in folder.iterdir():
            if not fp.is_file():
                continue
            if fp.suffix.lower() not in allowed:
                continue
            if _norm(fp.stem) != wanted:
                continue
            prio = ext_priority.get(fp.suffix.lower(), 999)
            if prio < best_prio:
                best_prio = prio
                best_fp = fp
    except Exception:
        return ""

    if best_fp is None:
        return ""

    return url_for("static", filename=f"video/{best_fp.name}")


def render_products_list(category: str, prods: List[Product]):
    meta = CATEGORY_META.get(category, {})
    return render_template(
        "products_list.html",
        page_title=f"{meta.get('label', category)} — X‑Estetik",
        page_heading=meta.get("label", category),
        page_description=meta.get("description", ""),
        products=[to_view(p) for p in prods],
        grid_classes=meta.get("grid_classes", "grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"),
        img_class=meta.get("img_class", "h-56"),
        section_px=meta.get("section_px", "px-4"),
        card_round=meta.get("card_round", "rounded-3xl"),
    )


def to_view(p: Product) -> Dict:
    category_meta = CATEGORY_META.get(p.category, {})

    photo_base = PRODUCT_PHOTO_BASE.get(p.slug, "")
    thumb_fallback = url_for("static", filename=f"img/thumbs/{p.slug}.jpg")
    thumb = resolve_static_photo(photo_base) or thumb_fallback

    return {
        "slug": p.slug,
        "name": p.name,
        "category": p.category,
        "category_label": category_meta.get("label", p.category),
        "tag": p.tag,
        "short": p.short,
        "bullets": p.bullets,
        "price": p.price,
        "rental": p.rental,
        "badge": p.badge,
        "thumb": thumb,
        "photo_base": photo_base,
        "effects_folder": p.effects_folder,
        "effects_url": p.effects_url,
    }


def list_gallery_images(slug: str) -> List[str]:
    folder = APP_DIR / "static" / "img" / "catalog" / slug
    if not folder.exists():
        return []
    imgs = sorted([p for p in folder.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}])
    return [url_for("static", filename=f"img/catalog/{slug}/{p.name}") for p in imgs]




def list_effect_images(folder_name: str) -> List[str]:
    """List before/after effect images from static/efekty/<folder_name>/.

    The folder is optional and must be a single path segment (no traversal).
    Supported formats: .jpg/.jpeg/.png/.webp
    """
    folder_name = (folder_name or "").strip().strip("/\\")
    if not folder_name:
        return []

    # Prevent path traversal
    if "/" in folder_name or "\\" in folder_name or ".." in folder_name:
        return []

    folder = APP_DIR / "static" / "efekty" / folder_name
    if not folder.exists():
        return []

    imgs = sorted(
        [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}]
    )
    return [url_for("static", filename=f"efekty/{folder_name}/{p.name}") for p in imgs]

def first_gallery_image(slug: str) -> str:
    imgs = list_gallery_images(slug)
    return imgs[0] if imgs else ""


# ----------------------------- Content -----------------------------

def sample_reviews() -> List[Dict[str, str]]:
    return [
        {
            "source": "Google",
            "title": "Wyniki i komfort pracy",
            "text": "Po wdrożeniu nowego urządzenia skróciliśmy czas zabiegów i poprawiliśmy komfort pacjentów. Duży plus za konkretne wsparcie i materiały.",
            "author": "Klinika Beauty",
        },
        {
            "source": "Instagram",
            "title": "Szkolenie i protokoły",
            "text": "Bardzo klarowne szkolenie, realne podejście do protokołów i ustawień. Sprzęt jest przemyślany pod codzienną pracę w gabinecie.",
            "author": "@gabinet_estetyczny",
        },
        {
            "source": "Facebook",
            "title": "Szybki kontakt, konkret",
            "text": "Dostaliśmy komplet kart i materiałów — w sprzedaży to oszczędza masę czasu. Szybka odpowiedź na pytania, bez lania wody.",
            "author": "Salon w Warszawie",
        },
        {
            "source": "Google",
            "title": "Dobór pod profil klienta",
            "text": "Pomogli nam dobrać konfigurację pod naszą klientelę. Sprzęt pracuje stabilnie, a procedury są powtarzalne. Polecam.",
            "author": "Gabinet kosmetologii",
        },
        {
            "source": "Instagram",
            "title": "Katalog online robi robotę",
            "text": "Karty produktów i strony  pod ręką — klient widzi wszystko od razu. Decyzje zakupowe są dużo szybsze.",
            "author": "@klinika_nowoczesna",
        },
        {
            "source": "Facebook",
            "title": "Estetyka i pierwsze wrażenie",
            "text": "Urządzenia robią świetne pierwsze wrażenie. Dla klientów to sygnał, że pracujemy na nowoczesnej technologii.",
            "author": "Salon",
        },
        {
            "source": "Google",
            "title": "Wsparcie posprzedażowe",
            "text": "Po zakupie nie zostajesz sam. Pomoc w ustawieniach, przypomnienie protokołów i szybkie reakcje — na plus.",
            "author": "Klinika",
        },
        {
            "source": "Instagram",
            "title": "Materiały do konsultacji",
            "text": "Na konsultacji pokazuję klientowi konkretne slajdy/strony  i rozmowa jest dużo prostsza. Świetne narzędzie.",
            "author": "@beauty_consult",
        },
        {
            "source": "Facebook",
            "title": "Porównanie technologii",
            "text": "Wreszcie mamy porządek w ofercie: co jest do jakich wskazań i jak to komunikować. Dobrze ułożone argumenty sprzedażowe.",
            "author": "Gabinet",
        },
        {
            "source": "Google",
            "title": "Szybkie wdrożenie",
            "text": "Od decyzji do startu minęło niewiele czasu. Pomogli nam ułożyć plan wdrożenia i pricing zabiegów.",
            "author": "Klinika",
        },
        {
            "source": "Instagram",
            "title": "Jakość wykonania",
            "text": "Bardzo solidne wykonanie i intuicyjna obsługa. Klientki zwracają uwagę na wygląd sprzętu — tutaj jest premium.",
            "author": "@studio_kosmetologii",
        },
        {
            "source": "Facebook",
            "title": "Polecam do gabinetu",
            "text": "Dobra relacja ceny do możliwości i sensowne wsparcie. Najważniejsze: sprzęt realnie pracuje i zarabia, a nie stoi.",
            "author": "Właściciel gabinetu",
        },
    ]
def policy_content(app: Flask) -> Dict[str, tuple]:
    """Return HTML bodies for legal pages.

    Notes:
    - Content is intentionally practical and generic.
    - Update firm data (adres/NIP) via env vars if needed.
    """
    site = html_escape(app.config.get("SITE_NAME", "X‑Estetik"))
    email = html_escape(app.config.get("CONTACT_EMAIL", ""))
    phone = html_escape(app.config.get("CONTACT_PHONE", ""))

    admin_name = html_escape(get_env("LEGAL_ENTITY_NAME", site))
    admin_address = html_escape(get_env("LEGAL_ENTITY_ADDRESS", ""))
    admin_nip = html_escape(get_env("LEGAL_ENTITY_NIP", ""))

    contact_lines = []
    if email:
        contact_lines.append(f"E‑mail: <a href=\"mailto:{email}\">{email}</a>")
    if phone:
        contact_lines.append(f"Telefon: <a href=\"tel:{phone.replace(' ', '')}\">{phone}</a>")
    contact_html = "<br>".join(contact_lines) if contact_lines else ""

    admin_block = f"<strong>{admin_name}</strong>" + (f"<br>{admin_address}" if admin_address else "") + (f"<br>NIP: {admin_nip}" if admin_nip else "")
    if contact_html:
        admin_block += f"<br>{contact_html}"

    privacy = f"""
    <p>Dokument określa zasady przetwarzania danych osobowych w serwisie <strong>{site}</strong> (dalej: „Serwis”).</p>

    <h2>1. Administrator danych</h2>
    <p>Administratorem danych osobowych jest:</p>
    <p>{admin_block}</p>

    <h2>2. Jakie dane przetwarzamy</h2>
    <ul>
      <li>dane przekazane w formularzu kontaktowym: imię i nazwisko, e‑mail, telefon (opcjonalnie), treść wiadomości,</li>
      <li>dane techniczne: podstawowe logi serwera (np. adres IP, data i godzina zapytania, typ przeglądarki) — wyłącznie w celu bezpieczeństwa i diagnostyki.</li>
    </ul>

    <h2>3. Cele i podstawy prawne</h2>
    <ul>
      <li><strong>Kontakt i obsługa zapytań</strong> — udzielenie odpowiedzi, przygotowanie oferty, umówienie prezentacji (art. 6 ust. 1 lit. b RODO — działania przed zawarciem umowy / art. 6 ust. 1 lit. f RODO — uzasadniony interes Administratora).</li>
      <li><strong>Zapewnienie bezpieczeństwa Serwisu</strong> — wykrywanie nadużyć, utrzymanie i diagnostyka (art. 6 ust. 1 lit. f RODO).</li>
      <li><strong>Obrona lub dochodzenie roszczeń</strong> (art. 6 ust. 1 lit. f RODO).</li>
    </ul>

    <h2>4. Odbiorcy danych</h2>
    <p>Dane mogą być udostępniane podmiotom wspierającym Administratora w utrzymaniu Serwisu (np. hosting/IT) wyłącznie na podstawie umów powierzenia i w zakresie niezbędnym do realizacji usług.</p>

    <h2>5. Okres przechowywania</h2>
    <ul>
      <li>dane z formularza kontaktowego — przez okres niezbędny do obsługi zapytania, a następnie do czasu przedawnienia ewentualnych roszczeń,</li>
      <li>logi techniczne — przez okres niezbędny do zapewnienia bezpieczeństwa i diagnostyki (zwykle do 90 dni, o ile nie zajdzie potrzeba dłuższego przechowywania w związku z incydentem).</li>
    </ul>

    <h2>6. Prawa osób, których dane dotyczą</h2>
    <p>Masz prawo żądać: dostępu do danych, sprostowania, usunięcia, ograniczenia przetwarzania, przenoszenia danych oraz wniesienia sprzeciwu (w przypadkach przewidzianych prawem).</p>
    <p>Jeśli uważasz, że przetwarzanie narusza przepisy, przysługuje Ci prawo wniesienia skargi do Prezesa UODO.</p>

    <h2>7. Dobrowolność podania danych</h2>
    <p>Podanie danych jest dobrowolne, ale niezbędne do udzielenia odpowiedzi na zapytanie (formularz kontaktowy).</p>

    <h2>8. Zautomatyzowane podejmowanie decyzji</h2>
    <p>Administrator nie podejmuje decyzji w sposób zautomatyzowany, w tym nie stosuje profilowania w rozumieniu RODO.</p>
    """

    cookies = f"""
    <p>Niniejsza Polityka opisuje zasady wykorzystywania plików cookies w Serwisie <strong>{site}</strong>.</p>

    <h2>1. Czym są pliki cookies</h2>
    <p>Cookies to niewielkie pliki tekstowe zapisywane na urządzeniu użytkownika. Mogą być wykorzystywane m.in. do prawidłowego działania serwisu, utrzymania preferencji oraz statystyk.</p>

    <h2>2. Jakich cookies używamy</h2>
    <ul>
      <li><strong>Niezbędne</strong> — wymagane do działania Serwisu i jego funkcji (np. mechanizmy bezpieczeństwa, pamięć ustawień).</li>
      <li><strong>Funkcjonalne</strong> — poprawiają wygodę korzystania (np. zapamiętanie akceptacji komunikatu cookies w przeglądarce).</li>
    </ul>

    <p>Serwis nie wykorzystuje cookies marketingowych. Jeśli w przyszłości zostaną dodane narzędzia analityczne lub reklamowe, polityka zostanie zaktualizowana.</p>

    <h2>3. Zarządzanie cookies</h2>
    <p>Możesz zmienić ustawienia cookies w swojej przeglądarce (blokowanie, usuwanie). Ograniczenie cookies niezbędnych może wpłynąć na działanie Serwisu.</p>
    """

    terms = f"""
    <p>Niniejszy regulamin określa zasady korzystania z Serwisu <strong>{site}</strong>.</p>

    <h2>1. Charakter Serwisu</h2>
    <p>Serwis ma charakter informacyjny i prezentacyjny. Nie stanowi sklepu internetowego ani platformy transakcyjnej.</p>

    <h2>2. Prawa autorskie</h2>
    <p>Wszelkie materiały udostępnione w Serwisie (teksty, grafiki, zdjęcia, układ) są chronione prawem autorskim. Zabronione jest ich kopiowanie i rozpowszechnianie bez zgody Administratora, z wyjątkiem dozwolonego użytku wynikającego z przepisów.</p>

    <h2>3. Odpowiedzialność</h2>
    <p>Administrator dokłada starań, aby informacje były aktualne, jednak nie gwarantuje ich kompletności. Parametry urządzeń, wskazania i protokoły należy zawsze weryfikować w dokumentacji oraz zgodnie z obowiązującymi przepisami.</p>

    <h2>4. Kontakt</h2>
    <p>W sprawach dotyczących Serwisu skontaktuj się z Administratorem: {contact_html if contact_html else "(dane kontaktowe w stopce)"}.</p>

    <h2>5. Zmiany regulaminu</h2>
    <p>Administrator może zaktualizować regulamin z ważnych powodów (np. zmiany prawne lub techniczne). Aktualna wersja jest zawsze dostępna w Serwisie.</p>
    """

    disclaimer = f"""
    <p>Materiały w Serwisie <strong>{site}</strong> mają charakter informacyjny. Nie stanowią porady medycznej ani gwarancji efektów zabiegowych.</p>
    <ul>
      <li>Wskazania, przeciwwskazania i parametry należy weryfikować w dokumentacji urządzenia oraz zgodnie z przepisami.</li>
      <li>Ostateczną decyzję o protokole zabiegowym podejmuje wykwalifikowany specjalista.</li>
    </ul>
    """

    return {
        "privacy": ("Polityka prywatności", privacy),
        "cookies": ("Polityka cookies", cookies),
        "terms": ("Regulamin serwisu", terms),
        "disclaimer": ("Zastrzeżenia", disclaimer),
    }


# ----------------------------- Storage (SQLite) -----------------------------

def get_db(app: Flask) -> sqlite3.Connection:
    conn = sqlite3.connect(app.config["DB_PATH"])
    conn.row_factory = sqlite3.Row
    return conn


def init_db(app: Flask) -> None:
    db_path = Path(app.config["DB_PATH"])
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with get_db(app) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS leads (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              created_at TEXT NOT NULL,
              name TEXT NOT NULL,
              email TEXT NOT NULL,
              phone TEXT,
              message TEXT NOT NULL,
              source_path TEXT
            )
            """
        )
        conn.commit()


def save_lead(app: Flask, name: str, email: str, phone: str, message: str, path: str) -> None:
    with get_db(app) as conn:
        conn.execute(
            """
            INSERT INTO leads (created_at, name, email, phone, message, source_path)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (datetime.utcnow().isoformat(timespec="seconds"), name, email, phone, message, path),
        )
        conn.commit()


# ----------------------------- Assets (QR) -----------------------------

def ensure_qr_codes(app: Flask) -> None:
    """Generate QR codes for social links.

    We overwrite QR files on startup so they always match the configured URLs.
    """
    try:
        import qrcode  # type: ignore
    except Exception:
        return

    qr_dir = APP_DIR / "static" / "img" / "qr"
    qr_dir.mkdir(parents=True, exist_ok=True)

    items = [
        ("instagram.png", app.config.get("INSTAGRAM_URL", "")),
        ("facebook.png", app.config.get("FACEBOOK_URL", "")),
        ("facebook_epilacja.png", app.config.get("FACEBOOK_EPILACJA_URL", "")),
        ("facebook_estetik_frax.png", app.config.get("FACEBOOK_ESTETIK_FRAX_URL", "")),
        ("facebook_tulowy_erbo.png", app.config.get("FACEBOOK_TULOWY_ERBO_URL", "")),
    ]

    for filename, url in items:
        if not url:
            continue
        out = qr_dir / filename
        try:
            img = qrcode.make(url)
            img = img.resize((512, 512))
            img.save(out)
        except Exception:
            continue


# ----------------------------- Run -----------------------------

app = create_app()

if __name__ == "__main__":
    # Port 5000 as requested.
    app.run(host="0.0.0.0", port=5000, debug=True)