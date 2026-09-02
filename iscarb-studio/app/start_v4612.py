from __future__ import annotations
from .patch_v4612 import install
install()
from .start_v4611 import app
from . import start_v440 as base
PUBLIC_VERSION = "4.6.12"
PIPELINE_ID = "faculty-studio-v4.6.12-source-first-visual"
base.PUBLIC_VERSION = PUBLIC_VERSION
base.PIPELINE_ID = PIPELINE_ID
