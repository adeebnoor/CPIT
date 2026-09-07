from __future__ import annotations

"""Install the distinct-visual mapping guard after the v8 route layer."""


def apply_v800_visual_mapping_guard() -> None:
    from . import patch_v800_hybrid_visual_narrative as runtime
    from .hybrid_visual_mapper_v800 import build_hybrid_visual_map

    runtime.build_hybrid_visual_map = build_hybrid_visual_map
