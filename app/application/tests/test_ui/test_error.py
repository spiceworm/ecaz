from flask import url_for


def test_error(client):
    url = url_for("ui_bp.error")
    resp = client.get(url)
    assert resp.request.base_url == url
