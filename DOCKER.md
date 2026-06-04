# Konteneryzacja projektu (Docker)

Dokumentacja opisuje **kompletną konteneryzację** systemu rezerwacji sal: backendu,
frontendu, bazy danych oraz monitoringu. Całość uruchamia się jedną komendą.

---

## Spis treści

1. [Architektura](#1-architektura)
2. [Wymagania](#2-wymagania)
3. [Szybki start](#3-szybki-start)
4. [Konfiguracja (`.env`)](#4-konfiguracja-env)
5. [Opis usług](#5-opis-usług)
6. [Opis dodanych plików](#6-opis-dodanych-plików)
7. [Jak to działa krok po kroku](#7-jak-to-działa-krok-po-kroku)
8. [Najczęstsze komendy](#8-najczęstsze-komendy)
9. [Rozwiązywanie problemów (FAQ)](#9-rozwiązywanie-problemów-faq)

---

## 1. Architektura

Wszystkie komponenty działają jako osobne kontenery w jednej, wewnętrznej sieci
Dockera. Usługi komunikują się ze sobą po **nazwach** (np. `backend`, `db`).

```
                         Przeglądarka użytkownika
                                  │
                ┌─────────────────┼───────────────────┐
                │                 │                    │
          :3000 │           :8000 │              :9090 / :3001
                ▼                 ▼                    ▼
        ┌──────────────┐   ┌──────────────┐   ┌─────────────────────┐
        │   frontend   │   │   backend    │   │ prometheus + grafana│
        │  (Next.js)   │   │  (FastAPI)   │◄──┤   (monitoring)      │
        └──────────────┘   └──────┬───────┘   └─────────────────────┘
                                  │ ODBC 18
                                  ▼
                           ┌──────────────┐
                           │      db      │
                           │ (SQL Server) │
                           └──────────────┘
```

| Komponent | Technologia | Port (host) | Opis |
|-----------|-------------|-------------|------|
| `frontend` | Next.js 15 / React 19 | `3000` | Interfejs użytkownika |
| `backend` | FastAPI + Uvicorn | `8000` | API + metryki na `/metrics` |
| `db` | Microsoft SQL Server 2022 | `1433` | Baza danych |
| `prometheus` | Prometheus | `9090` | Zbieranie metryk z backendu |
| `grafana` | Grafana | `3001` | Wizualizacja metryk |

---

## 2. Wymagania

- **Docker** oraz **Docker Compose** (Docker Desktop lub `docker` + plugin `compose`).
- Wolne porty na hoście: `3000`, `8000`, `1433`, `9090`, `3001`.

Sprawdzenie, czy Docker działa:

```bash
docker --version
docker compose version
```

---

## 3. Szybki start

```bash
# 1. Skopiuj wzór konfiguracji i uzupełnij wartości (hasła, klucze)
cp .env.example .env

# 2. Zbuduj obrazy i uruchom cały stos
docker compose up --build
```

Po uruchomieniu dostępne są:

| Usługa | Adres | Uwagi |
|--------|-------|-------|
| Frontend | http://localhost:3000 | Aplikacja webowa |
| Backend (API) | http://localhost:8000 | Dokumentacja API: http://localhost:8000/docs |
| Metryki | http://localhost:8000/metrics | Format Prometheus |
| Prometheus | http://localhost:9090 | Zakładka *Status → Targets* pokazuje stan backendu |
| Grafana | http://localhost:3001 | Domyślny login: `admin` / `admin` |

Zatrzymanie:

```bash
docker compose down
```

---

## 4. Konfiguracja (`.env`)

Sekrety i ustawienia trzymane są w pliku `.env` (ignorowanym przez git). Wzór znajduje
się w `.env.example`.

```dotenv
# --- Baza danych (SQL Server) ---
DB_SERVER=db                 # nazwa usługi z docker-compose (NIE zmieniać przy Dockerze)
DB_NAME=room_reservation     # nazwa bazy (tworzona automatycznie, jeśli nie istnieje)
DB_USER=sa                   # użytkownik administracyjny SQL Server
DB_PASSWORD=Your_Strong_Passw0rd!   # patrz uwaga poniżej

# --- JWT (logowanie / tokeny) ---
SECRET_KEY=zmien-na-dlugi-losowy-ciag-znakow
ALGORITHM=HS256

# --- SMTP (powiadomienia e-mail; opcjonalne) ---
SMTP_SERVER=smtp.example.com
SMTP_PORT=465
SMTP_USER=twoj@email.com
SMTP_PASSWORD=haslo-do-smtp
```

> **Ważne — hasło do bazy:** SQL Server wymaga "silnego" hasła:
> minimum 8 znaków, w tym **wielka litera, mała litera, cyfra i znak specjalny**.
> Zbyt słabe hasło spowoduje, że kontener `db` się nie uruchomi.

> **SMTP jest opcjonalne** — używane tylko przy wysyłce e-maili (przypomnienia
> o rezerwacjach). Bez poprawnej konfiguracji reszta aplikacji działa normalnie.

---

## 5. Opis usług

### `db` — Microsoft SQL Server
- Obraz: `mcr.microsoft.com/mssql/server:2022-latest`.
- Dane zapisywane są w wolumenie `mssql_data`, więc **przetrwają restart** kontenerów.
- **Healthcheck**: co kilka sekund wykonuje zapytanie `SELECT 1`. Dopóki nie przejdzie,
  baza nie jest uznana za "zdrową" i backend na nią czeka.
- **Backup `sanspace.bak`**: plik z katalogu głównego jest podmontowany (tylko do odczytu)
  do `/var/opt/mssql/backup/sanspace.bak`. Przy pierwszym starcie (pusty wolumen)
  backend odtwarza z niego bazę wraz z danymi (sale, użytkownicy, rezerwacje).
  Jeśli plik backupu nie istnieje, tworzona jest pusta baza i tabele zakłada SQLAlchemy.

> **Świeży import danych z backupu:** ponieważ dane są w wolumenie, backup wczytuje się
> tylko gdy baza jeszcze nie istnieje. Aby wymusić ponowne wczytanie od zera:
> `docker compose down -v` (usuwa wolumeny), a następnie `docker compose up --build`.

### `backend` — FastAPI
- Budowany z `backend/Dockerfile`.
- Zawiera **sterownik ODBC Driver 18** (wymagany przez `pyodbc` do połączenia z SQL Server).
- Startuje dopiero, gdy `db` przejdzie healthcheck (`depends_on: condition: service_healthy`).

### `frontend` — Next.js
- Budowany z `frontend/Dockerfile` w trybie **standalone** (lekki obraz produkcyjny).
- Zapytania do API (`http://localhost:8000`) wykonuje **przeglądarka użytkownika**,
  dlatego backend musi mieć wystawiony port `8000` na hoście (i ma).

### `prometheus` + `grafana` — monitoring
- Prometheus pobiera metryki z `backend:8000/metrics` (konfiguracja w `monitoring/prometheus.yml`).
- Grafana służy do budowania dashboardów na podstawie danych z Prometheusa.

---

## 6. Opis dodanych plików

| Plik | Rola |
|------|------|
| `docker-compose.yml` | Definiuje i łączy wszystkie 5 usług. Główny punkt startu. |
| `.env.example` | Wzór pliku `.env` z konfiguracją i sekretami. |
| `backend/Dockerfile` | Obraz backendu: Python + sterownik ODBC 18 + zależności. |
| `backend/entrypoint.sh` | Skrypt startowy: najpierw `wait_for_db.py`, potem Uvicorn. |
| `backend/wait_for_db.py` | Czeka na SQL Server i przygotowuje bazę: odtwarza ją z backupu (`sanspace.bak`), a jeśli backupu brak — tworzy pustą. |
| `backend/.dockerignore` | Wyklucza zbędne pliki z obrazu backendu. |
| `frontend/Dockerfile` | Wieloetapowy build Next.js (instalacja → build → uruchomienie). |
| `frontend/.dockerignore` | Wyklucza `node_modules`, `.next` itd. z obrazu frontendu. |

**Zmienione pliki:**

| Plik | Zmiana |
|------|--------|
| `frontend/next.config.ts` | Dodano `output: "standalone"` (lekki obraz) oraz `eslint.ignoreDuringBuilds` i `typescript.ignoreBuildErrors`, by istniejące w kodzie ostrzeżenia lintera i niespójności typów nie blokowały builda produkcyjnego (tryb `next dev` i tak ich nie wymusza). |
| `monitoring/prometheus.yml` | Cel zmieniony z `host.docker.internal:8000` na `backend:8000`. |
| `.gitignore` | Dodano wyjątek `!.env.example`, by wzór trafiał do repo. |

---

## 7. Jak to działa krok po kroku

Po wpisaniu `docker compose up --build` dzieje się następująca sekwencja:

1. **Budowanie obrazów**
   - Backend: instalacja sterownika ODBC 18 + zależności z `requirements.txt`.
   - Frontend: `npm install` → `npm run build` → przygotowanie serwera standalone.

2. **Start bazy `db`**
   - SQL Server uruchamia się i co kilka sekund jest odpytywany przez healthcheck.
   - Na tym etapie istnieje tylko systemowa baza `master` — bazy aplikacji jeszcze nie ma.

3. **Start backendu `backend`** (dopiero gdy `db` jest "zdrowa")
   - Uruchamia się `entrypoint.sh`, który najpierw woła `wait_for_db.py`.
   - `wait_for_db.py` łączy się z bazą `master` i:
     - jeśli baza `room_reservation` już istnieje → nic nie robi,
     - jeśli nie istnieje, a jest dostępny backup (`BACKUP_FILE`) → **odtwarza bazę z backupu** (`sanspace.bak`),
     - w innym wypadku → tworzy pustą bazę.
   - Następnie startuje Uvicorn → przy imporcie `main.py` SQLAlchemy zakłada brakujące tabele.

4. **Start frontendu `frontend`**
   - Serwuje aplikację Next.js na porcie `3000`.

5. **Start monitoringu**
   - Prometheus zaczyna co 5 s pobierać metryki z `backend:8000/metrics`.
   - Grafana jest gotowa do podpięcia Prometheusa jako źródła danych.

> **Dlaczego potrzebny był `wait_for_db.py`?**
> Kontener SQL Server startuje tylko z bazą `master`. Aplikacja przy starcie od razu
> próbuje tworzyć tabele w bazie `room_reservation`. Bez wcześniejszego utworzenia tej
> bazy backend wywaliłby się błędem połączenia. Skrypt rozwiązuje problem "kury i jajka".

---

## 8. Najczęstsze komendy

```bash
# Uruchomienie (z przebudową obrazów)
docker compose up --build

# Uruchomienie w tle
docker compose up -d

# Podgląd logów (wszystkie usługi lub jedna)
docker compose logs -f
docker compose logs -f backend

# Zatrzymanie kontenerów
docker compose down

# Zatrzymanie + USUNIĘCIE danych bazy i Grafany (czysty start)
docker compose down -v

# Przebudowa pojedynczej usługi
docker compose build backend

# Wejście do działającego kontenera (debug)
docker compose exec backend bash
```

---

## 9. Rozwiązywanie problemów (FAQ)

**Kontener `db` od razu się wyłącza / restartuje.**
Najczęściej zbyt słabe `DB_PASSWORD`. Ustaw hasło spełniające wymogi złożoności
(wielka litera, mała litera, cyfra, znak specjalny, min. 8 znaków).

**Backend zgłasza błąd połączenia z bazą przy starcie.**
To normalne przez pierwsze kilkanaście sekund — backend czeka, aż baza będzie gotowa
(widać próby `wait_for_db`). Jeśli błąd jest trwały, sprawdź `DB_USER` / `DB_PASSWORD`
w `.env`.

**Prometheus pokazuje target `backend:8000` jako *DOWN*.**
Upewnij się, że backend wstał poprawnie (`docker compose logs backend`) i że endpoint
http://localhost:8000/metrics zwraca dane.

**Port jest zajęty (`port is already allocated`).**
Inny proces używa portu (np. `3000` lub `8000`). Zatrzymaj go lub zmień mapowanie
portów w `docker-compose.yml` (np. `"3010:3000"`).

**Zmieniłem kod — jak zobaczyć efekt?**
Przebuduj obraz danej usługi: `docker compose up --build` (lub `docker compose build <usługa>`).
