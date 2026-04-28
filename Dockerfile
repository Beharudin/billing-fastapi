FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

RUN useradd --create-home app
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chown -R app:app /app
USER app

# Default to Gunicorn + Uvicorn workers for production; override in compose for dev if needed
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000", "--workers", "4"]