FROM python:3.12-slim

# Never buffer logs behind a crash, and never ship .pyc noise into the image.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dependencies resolve in their own layer so application edits do not force a
# full reinstall on every deploy.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# The service only ever reads its own source and writes under data/. Running it
# unprivileged means a defect in source parsing cannot rewrite the application.
RUN useradd --create-home --uid 10001 iscarb \
    && mkdir -p /app/data \
    && chown -R iscarb:iscarb /app
USER iscarb

EXPOSE 8000
CMD ["python", "run.py"]
