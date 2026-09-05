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

# Existing source/grammar regression gates.
RUN python smoke_prod.py
RUN python smoke_contract_v716.py
RUN python smoke_golden_v728.py
# New invariant: ZTM is styling only. The complete Golden slide is rendered first,
# then skinned; protected source/chart panels must remain pixel-identical.
RUN python smoke_ztm_skin_v730.py

RUN useradd --create-home --uid 10001 iscarb \
    && mkdir -p /app/data \
    && chown -R iscarb:iscarb /app
USER iscarb

EXPOSE 8000
CMD ["python", "run_v730_candidate.py"]
