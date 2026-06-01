# Wyniki testow

Testy odpalone lokalnie na Python 3.12 i pytest 9.0.3.

## Szybkie podsumowanie

- Wynik: 8/8 testow zaliczone
- Niezaliczone: 0
- Pominiete: 0
- Czas wykonania: 13.59 s

## Co sprawdzilismy

### Testy jednostkowe

- Logowanie poprawnym loginem i haslem: API zwraca 200, token i dane uzytkownika.
- Logowanie blednym haslem: API zwraca 401 i komunikat Invalid login credentials.
- Logowanie nieistniejacego uzytkownika: API zwraca 401 i ten sam komunikat bledu.
- Dodanie nowej sali: rekord jest tworzony i odczytywalny z bazy testowej.
- Edycja danych sali: zmiany zapisuja sie poprawnie dla uzytkownika z rola admin.

### Testy integracyjne

- Utworzenie rezerwacji -> zapis do bazy -> aktualizacja harmonogramu:
  po POST /reservations nowy wpis widac na liscie GET /reservations.
- Anulowanie rezerwacji:
  po usunięciu rezerwacji można ją ponownie zarezerwować DELETE /reservations/{id} .
- Wyszukiwanie sal -> pobranie danych z bazy:
  GET /rooms/filter zwraca tylko sale, ktore spelniaja podane filtry.

## Komentarz po uruchomieniu

- W testach nie ma żadnych błędów krytycznych.
