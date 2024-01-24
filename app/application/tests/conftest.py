import functools

from flask_jwt_extended import create_access_token
import flask_login
import pytest

from application import create_app
from application.models import (
    ApiToken,
    db,
    User,
)


@pytest.fixture()
def app():
    _app = create_app()
    _app.test_client_class = flask_login.FlaskLoginClient
    with _app.app_context():
        yield _app


@pytest.fixture()
def client(app):
    yield app.test_client()


@pytest.fixture()
def user(app):
    user = User(email="email@test.com", password="test-password")
    db.session.add(user)
    db.session.commit()
    yield user
    db.session.delete(user)
    db.session.commit()


@pytest.fixture()
def auth_token(app, user):
    token_value = create_access_token(expires_delta=False, identity=user.email)
    token = ApiToken(name="test-token", value=token_value, user=user)
    db.session.add(token)
    db.session.commit()
    yield token
    db.session.delete(token)
    db.session.commit()


@pytest.fixture()
def api_client(app):
    return app.test_client()


@pytest.fixture()
def api_get(auth_token, api_client):
    return api_client.get


@pytest.fixture()
def api_auth_get(auth_token, api_client):
    return functools.partial(
        api_client.get, headers={"Authorization": f"Bearer {auth_token.value}"}
    )


@pytest.fixture()
def ui_client(app, user):
    """Requests sent by `client` are automatically authenticated with the
    email and password of `user`"""
    with app.test_client(user=user) as client:
        yield client


@pytest.fixture()
def ui_auth_get(ui_client):
    return ui_client.get


@pytest.fixture()
def ui_auth_post(ui_client):
    return ui_client.post
