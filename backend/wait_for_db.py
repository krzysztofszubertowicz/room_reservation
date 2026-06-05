"""
Przygotowuje baze danych zanim wystartuje aplikacja FastAPI.

Logika (uruchamiane przez entrypoint.sh PRZED importem main.py):
  1. Czeka, az serwer SQL Server zacznie odpowiadac.
  2. Jesli baza (DB_NAME) juz istnieje  -> nic nie robi.
  3. Jesli istnieje plik backupu (BACKUP_FILE) -> odtwarza z niego baze.
  4. W przeciwnym razie -> tworzy pusta baze (tabele zalozy potem SQLAlchemy).

Dzieki temu przy pierwszym `docker compose up` baza zostaje automatycznie
zaladowana danymi z backupu kolegi (sanspace.bak).
"""
import os
import sys
import time

import pyodbc

server = os.getenv("DB_SERVER", "db")
database = os.getenv("DB_NAME", "room_reservation")
username = os.getenv("DB_USER", "sa")
password = os.getenv("DB_PASSWORD", "")
# Sciezka pliku .bak WIDZIANA z poziomu kontenera bazy danych (podmontowana w compose).
backup_file = os.getenv("BACKUP_FILE", "")
# Katalog na pliki danych wewnatrz kontenera SQL Server (Linux).
data_dir = os.getenv("MSSQL_DATA_DIR", "/var/opt/mssql/data")

MASTER_CONNECTION = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={server};DATABASE=master;UID={username};PWD={password};"
    "Encrypt=no;TrustServerCertificate=yes;"
)


def _database_exists(cursor) -> bool:
    cursor.execute("SELECT DB_ID(?)", database)
    return cursor.fetchone()[0] is not None


def _restore_from_backup(cursor) -> None:
    # 1) Odczytaj logiczne nazwy plikow z backupu, by zbudowac klauzule MOVE.
    cursor.execute(f"RESTORE FILELISTONLY FROM DISK = N'{backup_file}'")
    files = cursor.fetchall()

    move_clauses = []
    data_index = 0
    for row in files:
        logical_name = row[0]
        file_type = (row[2] or "").upper()  # 'D' = dane, 'L' = log
        if file_type == "L":
            physical = f"{data_dir}/{database}_log.ldf"
        else:
            suffix = "" if data_index == 0 else f"_{data_index}"
            physical = f"{data_dir}/{database}{suffix}.mdf"
            data_index += 1
        move_clauses.append(f"MOVE N'{logical_name}' TO N'{physical}'")

    # 2) Odtworz baze pod nazwa DB_NAME (RESTORE pozwala zmienic nazwe bazy).
    restore_sql = (
        f"RESTORE DATABASE [{database}] FROM DISK = N'{backup_file}' "
        f"WITH {', '.join(move_clauses)}, REPLACE"
    )
    print(f"[wait_for_db] Odtwarzam baze '{database}' z backupu '{backup_file}'...", flush=True)
    cursor.execute(restore_sql)
    while cursor.nextset():  # skonsumuj komunikaty RESTORE ("Processed N pages...")
        pass
    print(f"[wait_for_db] Backup odtworzony do bazy '{database}'.", flush=True)


def wait_and_prepare(max_attempts: int = 60, delay_seconds: int = 3) -> None:
    for attempt in range(1, max_attempts + 1):
        try:
            # autocommit=True jest wymagane: CREATE/RESTORE DATABASE nie dzialaja w transakcji.
            connection = pyodbc.connect(MASTER_CONNECTION, autocommit=True, timeout=5)
            cursor = connection.cursor()

            if _database_exists(cursor):
                print(f"[wait_for_db] Baza '{database}' juz istnieje - pomijam.", flush=True)
            elif backup_file:
                _restore_from_backup(cursor)
            else:
                cursor.execute(f"CREATE DATABASE [{database}]")
                print(f"[wait_for_db] Utworzono pusta baze '{database}'.", flush=True)

            cursor.close()
            connection.close()
            return
        except pyodbc.Error as error:
            print(
                f"[wait_for_db] Proba {attempt}/{max_attempts}: SQL Server jeszcze nie gotowy "
                f"({error}). Ponawiam za {delay_seconds}s...",
                flush=True,
            )
            time.sleep(delay_seconds)

    print("[wait_for_db] Nie udalo sie przygotowac bazy danych. Koncze.", flush=True)
    sys.exit(1)


if __name__ == "__main__":
    wait_and_prepare()
