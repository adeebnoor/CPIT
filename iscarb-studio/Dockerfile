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
# Boot the exact v8.0 surface for inherited regression contracts, then boot v8.1
# separately below. This avoids weakening historical assertions just to accept a
# new build identifier.
RUN ISCARB_BUILD_ID=8.0.0-hybrid-visual-narrative ISCARB_DISABLE_V810_PATCH=1 python smoke_golden_v728.py
RUN ISCARB_BUILD_ID=8.0.0-hybrid-visual-narrative ISCARB_DISABLE_V810_PATCH=1 python smoke_editor_gates_v729.py
RUN ISCARB_BUILD_ID=8.0.0-hybrid-visual-narrative ISCARB_DISABLE_V810_PATCH=1 python smoke_universal_meta_v730.py
RUN ISCARB_BUILD_ID=8.0.0-hybrid-visual-narrative ISCARB_DISABLE_V810_PATCH=1 python smoke_projection_v731.py
RUN ISCARB_BUILD_ID=8.0.0-hybrid-visual-narrative ISCARB_DISABLE_V810_PATCH=1 python smoke_native_figures_v732.py
RUN ISCARB_BUILD_ID=8.0.0-hybrid-visual-narrative ISCARB_DISABLE_V810_PATCH=1 python smoke_final_readability_v733.py
RUN ISCARB_BUILD_ID=8.0.0-hybrid-visual-narrative ISCARB_DISABLE_V810_PATCH=1 python smoke_instructional_director_v737.py
RUN ISCARB_BUILD_ID=8.0.0-hybrid-visual-narrative ISCARB_DISABLE_V810_PATCH=1 python smoke_hybrid_visual_v800.py
# v8.1 Public Visual Intelligence: semantic brief/search/ranking/licensing/UI/evidence.
RUN python smoke_public_visual_v810.py

RUN useradd --create-home --uid 10001 iscarb \
    && mkdir -p /app/data \
    && chown -R iscarb:iscarb /app
USER iscarb

EXPOSE 8000
CMD ["python", "run.py"]