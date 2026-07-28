FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN addgroup --system app \
    && adduser --system --ingroup app app \
    && mkdir /data \
    && chown app:app /data

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=app:app . .

USER app

EXPOSE 5000

CMD ["sh", "-c", "flask --app run.py db upgrade && exec gunicorn --bind 0.0.0.0:5000 --workers 2 --threads 4 --access-logfile - --error-logfile - run:app"]
