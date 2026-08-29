"""ISCARB Faculty Studio application package."""

# Patch the shared prompt module during package initialization so any later
# `from .prompts import MASTER_PROMPT` receives the learner-facing CIMT copy
# contract before GeminiService is imported.
from .presenter_prompt_patch_v431 import install_prompt_patch as _install_prompt_patch

_install_prompt_patch()
