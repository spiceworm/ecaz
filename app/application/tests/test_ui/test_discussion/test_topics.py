from flask import url_for


def test_view_topics(client):
    url = url_for("ui_bp.view_topics")
    resp = client.get(url)
    assert resp.request.base_url == url
