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


DEFAULT_EMAIL = "default-email@test.com"
DEFAULT_PASSWORD = "default-password"


class UiUser:
    def __init__(self, app, email=DEFAULT_EMAIL, password=DEFAULT_PASSWORD, **kwargs):
        _user = User(
            email=email,
            password=password,
            **kwargs,
        )
        db.session.add(_user)
        db.session.commit()
        self._user = _user
        self._client = app.test_client(user=_user)

    def __getattr__(self, item):
        return getattr(self._user, item)

    @property
    def _headers(self):
        return {}

    def get(self, *args, **kwargs):
        kwargs.update(self._headers)
        return self._client.get(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.update(self._headers)
        return self._client.delete(*args, **kwargs)

    def patch(self, *args, **kwargs):
        kwargs.update(self._headers)
        return self._client.patch(*args, **kwargs)

    def post(self, *args, **kwargs):
        kwargs.update(self._headers)
        return self._client.post(*args, **kwargs)

    def put(self, *args, **kwargs):
        kwargs.update(self._headers)
        return self._client.put(*args, **kwargs)


class ApiUser(UiUser):
    def __init__(self, app, email=DEFAULT_EMAIL, password=DEFAULT_PASSWORD, **kwargs):
        super().__init__(app, email=email, password=password, **kwargs)

        self._client = app.test_client()
        self._token = ApiToken(
            name="test-token",
            value=create_access_token(
                expires_delta=False,
                identity=self._user.email,
            ),
            user=self._user,
        )
        db.session.add(self._token)
        db.session.commit()

    @property
    def _headers(self):
        return {"headers": {"Authorization": f"Bearer {self._token.value}"}}


@pytest.fixture(autouse=True)
def cleanup_and_teardown():
    # Setup code
    yield  # this is where the test runs
    ApiToken.query.delete()
    User.query.delete()
    db.session.commit()


@pytest.fixture(autouse=True)
def app():
    _app = create_app()
    _app.test_client_class = flask_login.FlaskLoginClient
    with _app.app_context():
        yield _app


@pytest.fixture
def api_token(app):
    def func(*args, **kwargs):
        _token = ApiToken(*args, **kwargs)
        db.session.add(_token)
        db.session.commit()
        return _token
    return func


@pytest.fixture()
def api_user(app):
    return functools.partial(ApiUser, app)


@pytest.fixture()
def ui_user(app):
    return functools.partial(UiUser, app)


@pytest.fixture
def user(app):
    def func(email=DEFAULT_EMAIL, password=DEFAULT_PASSWORD, **kwargs):
        _user = User(
            email=email,
            password=password,
            **kwargs,
        )
        db.session.add(_user)
        db.session.commit()
        return _user
    return func


@pytest.fixture()
def client(app):
    return app.test_client()
