from fastapi.testclient import TestClient


def test_production_home_uses_exact_user_original_hero():
    from run import app

    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert "/static/hero_user_original.png?v=7.3.4" in response.text
    assert "hero_user_web.jpg" not in response.text
    assert "hero_v671.svg" not in response.text
    assert "hero_desert.jpg" not in response.text
    assert response.headers["x-iscarb-version"] == "7.3.4"
    assert response.headers["x-iscarb-ui"] == "7.3.4"
    assert response.headers["x-iscarb-hero-mode"] == "exact-user-original-png"
    assert response.headers["x-iscarb-hero-asset"] == "hero_user_original.png"
    assert response.headers["x-iscarb-hero-sha256"] == "8967fa14fe910e5831531a6b74c64bcd650c965ad691697dd2d705d450b6e50d"


def test_original_hero_lock_preserves_clean_home_contract():
    from run import app

    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert "7.3.4 · CLEAN · IT-WIDE" in response.text
    assert "IT Lecture Transformation Studio" in response.text
    assert 'background-size:contain!important' in response.text
    assert '.heroArt::after{display:none!important;content:none!important}' in response.text
