# X‑Estetik — Flask katalog (port 5000)

## Uruchomienie lokalne
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Otwórz: http://127.0.0.1:5000

## Struktura
- `app.py` — aplikacja Flask (routes + dane produktów)
- `templates/` — szablony Jinja
- `static/` — CSS/JS, obrazy, QR, katalog PDF

## Konfiguracja (opcjonalnie)
Możesz podmienić dane w `app.py` lub przez zmienne środowiskowe:

- `CONTACT_EMAIL` (domyślnie: kontakt@x-estetik.pl)
- `CONTACT_PHONE` (domyślnie: +48 518 151 673)
- `ABOUT_TEXT` — treść na stronie „O nas”
- `INSTAGRAM_URL`, `FACEBOOK_URL`, `TIKTOK_URL` — linki do profili
- `INSTAGRAM_HANDLE`, `FACEBOOK_HANDLE`, `TIKTOK_HANDLE` — opisy/handle
- `SECRET_KEY` — klucz sesji
- `DB_PATH` — ścieżka do bazy SQLite (domyślnie `instance/app.db`)

## Lead form
Formularz kontaktowy zapisuje zgłoszenia do SQLite: `instance/app.db` (tabela `leads`).

## Katalog PDF
Plik: `static/pdf/X-Estetik-Katalog-2025.pdf`  
Podglądy stron zostały wyrenderowane do: `static/img/catalog/<slug>/`.
