import os
from PIL import Image, ImageDraw

import run  # installs production patch chain
from app import start_v440 as base
from app import start_v670_prod as prod
from app import patch_v730_ztm_skin_only as skin

assert os.getenv("ISCARB_BUILD_ID") == "7.3.0-golden-v660-ztm-skin-only"
health = dict(base._health_v440())
assert health.get("ztm_theme_version") == "v7.3.0-skin-only", health
assert health.get("ztm_content_rewrite") is False
assert health.get("ztm_slide_reflow") is False
assert "Golden lecture first" in health.get("ztm_pipeline", "")
assert base.export_presenter_pdf is skin.export_presenter_pdf_skin
assert base.export_presenter_pptx is skin.export_presenter_pptx_skin
assert base.render_presenter_preview is skin.render_presenter_preview_skin

# Exact ZTM tokens remain public.
t = prod.chapter_design_tokens("Dependable systems")
css = t.css_variables()
assert css["--bg-base"] == "#FFFFFF"
assert css["--bg-surface"] == "#F8FAFC"
assert css["--text-heading"] == "#0F172A"
assert css["--text-body"] == "#475569"
assert css["--accent-primary"] == "#4F46E5"
assert css["--accent-cyan"] == "#06B6D4"
assert css["--alert-urgent"] == "#F43F5E"
assert all(t.contrast_checks().values()), t.contrast_checks()

# Synthetic regression: dark Golden UI must become white, but a large white
# source panel and its internal black diagram line must remain pixel-identical.
img = Image.new("RGB", (960, 540), (5, 7, 13))
d = ImageDraw.Draw(img)
d.rectangle((90, 120, 560, 410), fill=(250, 250, 250))
d.line((150, 250, 500, 250), fill=(20, 20, 20), width=8)
d.rectangle((20, 470, 250, 520), outline=(255, 37, 140), width=4)
rects = skin._protected_bright_rects(img)
assert rects, rects
out = skin._skin_image(img, 7)
assert out.getpixel((20,20))[0] > 235, out.getpixel((20,20))
assert out.getpixel((200,200)) == img.getpixel((200,200)), (out.getpixel((200,200)), img.getpixel((200,200)))
assert out.getpixel((300,250)) == img.getpixel((300,250)), (out.getpixel((300,250)), img.getpixel((300,250)))

# Fresh Golden renderer isolation must load during build, not fail later live.
golden = skin._load_golden_renderer()
assert hasattr(golden, "export_presenter_pdf")
assert hasattr(golden, "export_presenter_pptx")

print("PASS: v7.3.0 Golden-first ZTM-skin-only; source/chart panels protected intact")
