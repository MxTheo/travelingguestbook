import json
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import CookieConsentLog

def test_save_cookie_consent_anonymous(client):
    """Test saving cookie consent for an anonymous user."""
    url = reverse("cookie-consent")
    payload = {"consent": True}
    resp = client.post(
        url,
        data=json.dumps(payload),
        content_type="application/json",
        HTTP_USER_AGENT="pytest-agent/1.0",
    )

    assert resp.status_code == 200
    assert resp.json() == {"ok": True}

    assert CookieConsentLog.objects.count() == 1
    log = CookieConsentLog.objects.first()
    assert log.user is None
    assert log.consent == payload
    assert log.ip  # should be set (e.g. "127.0.0.1")
    assert "pytest-agent" in (log.user_agent or "")

    cookie = resp.cookies.get("site_cookie_consent_v1")
    assert cookie is not None
    assert json.loads(cookie.value) == payload
    assert cookie.get("samesite", "").lower() == "lax"


def test_save_cookie_consent_authenticated(client):
    """Test saving cookie consent for an authenticated user."""
    user = User.objects.create_user("tester", "tester@example.com", "pw")
    client.force_login(user)

    payload = {"accepted": ["analytics"]}
    resp = client.post(
        reverse("cookie-consent"),
        data=json.dumps(payload),
        content_type="application/json",
    )

    assert resp.status_code == 200
    assert CookieConsentLog.objects.filter(user=user).exists()
    log = CookieConsentLog.objects.filter(user=user).first()
    assert log.consent == payload


def test_save_cookie_consent_invalid_json_returns_400(client):
    """Test that invalid JSON returns a 400 response."""
    url = reverse("cookie-consent")
    resp = client.post(url, data="not-a-json", content_type="application/json")
    assert resp.status_code == 400
    assert resp.json() == {"ok": False}
    assert CookieConsentLog.objects.count() == 0