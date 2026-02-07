FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System deps: psycopg2 build uchun, nc wait-for-it uchun
RUN apt-get update \
  && apt-get install -y --no-install-recommends gcc libpq-dev netcat-openbsd \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app/

EXPOSE 8000

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "main.asgi:application"]
