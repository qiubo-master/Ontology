FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOST=0.0.0.0 \
    APP_PORT=8000

WORKDIR /app

RUN groupadd --system --gid 1001 ontology \
    && useradd --system --uid 1001 --gid ontology --home-dir /app ontology

COPY --chown=ontology:ontology app.py ./
COPY --chown=ontology:ontology ontology ./ontology
COPY --chown=ontology:ontology web ./web

USER ontology
EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --retries=12 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=2)" || exit 1

CMD ["python", "app.py"]

