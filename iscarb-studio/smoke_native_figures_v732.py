import os

import run  # installs production patch chain
from app import start_v440 as base
from app import source_visuals as sv
from app import source_visuals_v42 as sv42
from app import patch_v731_projection_legibility as leg

assert os.getenv("ISCARB_BUILD_ID") == "7.3.2-golden-v660-native-figures", os.getenv("ISCARB_BUILD_ID")
health = dict(base._health_v440())
assert health.get("native_figure_prominence_version") == "v7.3.2", health
assert "genuine cropped P1" in health.get("native_figure_policy", ""), health
assert "AI MOMENT" in health.get("visual_transition_cues", ""), health
assert "READINESS CHECK" in health.get("visual_transition_cues", ""), health
assert sv.PDF_RENDER_ZOOM >= 3.4, sv.PDF_RENDER_ZOOM
assert sv.MAX_FIGURE_ZOOM >= 8.0, sv.MAX_FIGURE_ZOOM
assert sv.MIN_PRESENTABLE_ASSET_WIDTH >= 1400, sv.MIN_PRESENTABLE_ASSET_WIDTH
assert sv42.PICTURE_PREFERENCE_SHARE <= .35, sv42.PICTURE_PREFERENCE_SHARE
assert leg._split_timebox("TIMEBOX: 5-7 min - defend the decision") == ("5-7 min", "defend the decision")
assert leg._split_timebox("TIMEBOX: 60-90 sec - predict first") == ("60-90 sec", "predict first")
print("PASS: v7.3.2 native source-figure prominence + AI/readiness visual cues")
