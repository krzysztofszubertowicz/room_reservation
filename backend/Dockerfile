# Backend: FastAPI + Uvicorn + Microsoft ODBC Driver 18 (dla SQL Server)
# Obraz przypiety do Debian 12 (bookworm) - dla niego Microsoft udostepnia sterownik ODBC 18.
FROM python:3.11-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# 1) Narzędzia systemowe + sterownik ODBC 18 Microsoftu (wymagany przez pyodbc)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl gnupg2 apt-transport-https ca-certificates \
        gcc g++ unixodbc-dev \
    && mkdir -p /usr/share/keyrings \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
        | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && curl -fsSL https://packages.microsoft.com/config/debian/12/prod.list \
        -o /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2) Zależności Pythona (instalowane osobno, by lepiej korzystać z cache Dockera)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 3) Kod aplikacji
COPY . .

# 4) Skrypt startowy: czeka na bazę, tworzy ją jeśli nie istnieje, potem startuje API
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
