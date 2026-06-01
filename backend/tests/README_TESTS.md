# Testy backendu

## Zakres

### Testy jednostkowe

- Logowanie poprawnym loginem i haslem
- Logowanie blednym haslem
- Logowanie nieistniejacego uzytkownika
- Dodanie nowej sali
- Edycja danych sali

### Testy integracyjne

- Utworzenie rezerwacji i widocznosc w harmonogramie
- Anulowanie rezerwacji i zwolnienie terminu
- Wyszukiwanie sal i pobranie danych z bazy

## Uruchamianie

1. Przejdz do katalogu backend.
2. Uruchom testy w srodowisku wirtualnym:

```powershell
.\venv\Scripts\python.exe -m pytest tests -q
```

Albo w bashu:

```bash
source venv/Scripts/activate
python -m pytest tests -q
```

3. Tylko testy jednostkowe:

```powershell
.\venv\Scripts\python.exe -m pytest tests\unit -q
```

W bashu:

```bash
python -m pytest tests/unit -q
```

4. Tylko testy integracyjne:

```powershell
.\venv\Scripts\python.exe -m pytest tests\integration -q
```

W bashu:

```bash
python -m pytest tests/integration -q
```

5. Pokrycie testami:

```powershell
.\venv\Scripts\python.exe -m pytest tests --cov=. --cov-report=term-missing
```

W bashu:

```bash
python -m pytest tests --cov=. --cov-report=term-missing
```

## Raport z wynikow

Wyniki testow zapisujemy w pliku:

- tests/results/TEST_RESULTS.md

## Uwagi

- Testy korzystaja z lokalnego sqlite i nie dotykaja produkcyjnej bazy MSSQL.
- Dane startowe sa stale, wiec wyniki sa powtarzalne.
