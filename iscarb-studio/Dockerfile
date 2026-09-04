FROM python:3.12-slim

# Never buffer logs behind a crash, and never ship .pyc noise into the image.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Embed a real Unicode font in PDFs instead of relying on viewer-specific
# Helvetica substitution (which distorted spacing and mathematical symbols).
RUN apt-get update && apt-get install -y --no-install-recommends fonts-dejavu-core \
    && apt-get clean

# Dependencies resolve in their own layer so application edits do not force a
# full reinstall on every deploy.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Production must not deploy if the active patch chain cannot render the current
# LectureUnit schema, or if the source-native/public-web/hero invariants regress.
# This exercises the live presenter payload and HTML/PPTX/PDF exporters.
RUN python smoke_prod.py

# The service only ever reads its own source and writes under data/. Running it
# unprivileged means a defect in source parsing cannot rewrite the application.
RUN useradd --create-home --uid 10001 iscarb \
    && mkdir -p /app/data \
    && chown -R iscarb:iscarb /app
USER iscarb

EXPOSE 8000
CMD ["python", "run.py"]
