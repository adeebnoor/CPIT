from __future__ import annotations

from app.deterministic_blueprint_fallback import build_deterministic_blueprint
from app.models import CoverageItem, SourceProfile, TopicFamily
from app.source_profile_fallback import _declared_topic_families


def test_in_scope_family_inventory_is_not_silently_truncated_at_twenty():
    names = [f"Family {i}" for i in range(1, 26)]
    profile = SourceProfile(
        lecture_title="Dense chapter",
        weekly_focus="Dense chapter",
        topic_families=[TopicFamily(name=n) for n in names],
        in_scope_families=names,
    )
    assert profile.in_scope_families == names


def test_explicit_topics_covered_slide_defines_broad_pptx_families():
    chunks = [
        (1, "Chapter 10 - Dependable systems", "Chapter 10 Dependable Systems · 30/10/2014"),
        (
            2,
            "Topics covered",
            "Topics covered · Dependability properties · Sociotechnical systems · "
            "Redundancy and diversity · Dependable processes · Formal methods and dependability · "
            "Chapter 10 Dependable Systems · 30/10/2014",
        ),
    ]
    recurring = {"chapter 10 dependable systems", "30 10 2014"}
    declared = _declared_topic_families(chunks, recurring)
    assert declared is not None
    slide, names = declared
    assert slide == 2
    assert names == [
        "Dependability properties",
        "Sociotechnical systems",
        "Redundancy and diversity",
        "Dependable processes",
        "Formal methods and dependability",
    ]


def test_unit7_requires_trace_and_application_even_for_behavior_checkpoint():
    families = [TopicFamily(name=f"Family {i}", source_anchor=f"[P1] SLIDE {i}") for i in range(1, 6)]
    rows = [
        CoverageItem(
            id=f"P1-S{i:02d}",
            label=f"Checkpoint {i}",
            knowledge_type="SYSTEM_BEHAVIOR",
            importance="major",
            source_anchor=f"[P1] SLIDE {i}",
            why_important=(
                f"Checkpoint {i} describes a source-supported system behavior with enough detail "
                "to trace prerequisites, consequences, observable failures, and engineering decisions."
            ),
        )
        for i in range(1, 13)
    ]
    profile = SourceProfile(
        lecture_title="Reliability Engineering",
        weekly_focus="Reliability Engineering",
        topic_families=families,
        coverage_items=rows,
        in_scope_families=[f.name for f in families],
    )
    bp = build_deterministic_blueprint(profile)
    action = bp.units[6].student_action.lower()
    assert "trace" in action
    assert "apply" in action
