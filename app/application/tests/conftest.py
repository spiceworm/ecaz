import functools

from flask_jwt_extended import create_access_token
import flask_login
import flask_mailman
import pytest

from application import create_app
from application.models import (
    ApiToken,
    db,
    User,
)


DEFAULT_EMAIL = "default-email@test.com"
DEFAULT_PASSWORD = "default-password"


class _UiUser:
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


class _ApiUser(_UiUser):
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
def _cleanup_and_teardown():
    # Setup code
    yield  # this is where the test runs
    ApiToken.query.delete()
    User.query.delete()
    db.session.commit()


@pytest.fixture(autouse=True)
def _app():
    _a = create_app()
    _a.test_client_class = flask_login.FlaskLoginClient
    with _a.app_context():
        yield _a


@pytest.fixture
def api_token(_app):
    def func(*args, **kwargs):
        _token = ApiToken.create(*args, **kwargs)
        db.session.add(_token)
        db.session.commit()
        return _token
    return func


@pytest.fixture()
def api_user(_app):
    return functools.partial(_ApiUser, _app)


@pytest.fixture
def cli_runner(_app):
    return _app.test_cli_runner()


@pytest.fixture()
def client(_app):
    return _app.test_client()


@pytest.fixture(autouse=True)
def mock_email_send(monkeypatch):
    def patched_send(return_value=True):
        return return_value

    # Patch send to return `True` by default.
    monkeypatch.setattr(flask_mailman.EmailMessage, "send", patched_send)

    def patch_send(patch_func=patched_send):
        # This patch will not be applied unless we explicitly use the `mock_email_send`
        # fixture. Otherwise the default patch will be applied to all test cases.
        monkeypatch.setattr(flask_mailman.EmailMessage, "send", patch_func)

    # Return `patch_send` so we can change the return value of send to something
    # other than `True` if needed.
    return patch_send


@pytest.fixture()
def ui_user(_app):
    return functools.partial(_UiUser, _app)


@pytest.fixture
def user():
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
