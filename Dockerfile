# Stage 1: Install dependencies
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Production
FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /install /usr/local
COPY . .

EXPOSE 5000

CMD ["newrelic-admin", "run-program", "gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--timeout", "120", "application:application"]
