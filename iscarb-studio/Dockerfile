FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends fonts-dejavu-core \
    && apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Production must preserve the authoritative Golden v6.6 curriculum baseline.
RUN python smoke_prod.py
RUN python smoke_contract_v716.py
RUN python smoke_golden_v728.py
# Domain-specific assurance profile remains available only when relevant.
RUN python smoke_editor_gates_v729.py
# Universal cross-course meta-structure + deterministic feedback loop.
RUN python smoke_universal_meta_v730.py

RUN useradd --create-home --uid 10001 iscarb \
    && mkdir -p /app/data \
    && chown -R iscarb:iscarb /app
USER iscarb

EXPOSE 8000
CMD ["python", "run.py"]
