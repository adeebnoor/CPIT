from app import learning_experience as le


def test_v736_keeps_exact_20_unit_journey():
    flattened = [u for station in le.STATIONS for u in station["units"]]
    assert flattened == list(range(1, 21))
    assert le.TRANSITIONS[2].startswith("BECAUSE")
    assert le.TRANSITIONS[20].startswith("FINALLY")


def test_v736_structural_rubric_does_not_invent_semantic_grade():
    empty = le._rubric({})
    assert empty["level"] == "Emerging"
    assert empty["score"] == 1.0
    assert set(empty["dimensions"]) == {
        "prediction", "falsification", "quantification", "accountability",
        "risk", "evidence", "verdict", "completion",
    }


def test_v736_quantification_rewards_source_basis_not_fake_number():
    payload = {"tradeoffs": {"U8": {"measure": "unmeasured", "source_basis": "P1 page 4"}}}
    score = le._rubric(payload)["dimensions"]["quantification"]
    assert score == 4


def test_v736_instructor_keys_are_one_way_hashed(tmp_path, monkeypatch):
    db = tmp_path / "learning.sqlite3"
    monkeypatch.setattr(le, "_DB_PATH", db)
    le._init_db()
    le._settings("job-test")
    key = "a" * 48
    assert le._claim_instructor_key("job-test", key) is True
    with le._connect() as con:
        stored = con.execute(
            "SELECT instructor_key_hash FROM learning_settings WHERE job_id=?", ("job-test",)
        ).fetchone()["instructor_key_hash"]
    assert stored != key
    assert len(stored) == 64
    le._require_instructor_key("job-test", key)
