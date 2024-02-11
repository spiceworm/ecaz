import functools

from flask_jwt_extended import create_access_token
import flask_login
import flask_mailman
import pytest

from application import create_app
from application.models import (
    AuthToken,
    db,
    Topic,
    User,
)
from application.util.misc import generate_unique_username


DEFAULT_COMMENT_BODY = "default-comment"
DEFAULT_EMAIL = "default-email@test.com"
DEFAULT_PASSWORD = "default-password"
DEFAULT_THREAD_BODY = "thread-body"
DEFAULT_THREAD_TITLE = "thread-title"
DEFAULT_TOPIC_DESCRIPTION = "Topic description"
DEFAULT_TOPIC_NAME = "Topic-name"


class _UiUser:
    def __init__(self, app, email=DEFAULT_EMAIL, password=DEFAULT_PASSWORD, username=None, **kwargs):
        _user = User(
            email=email,
            password=password,
            username=username or generate_unique_username(),
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
    def __init__(self, app, email=DEFAULT_EMAIL, password=DEFAULT_PASSWORD, username=None, **kwargs):
        super().__init__(app, email=email, password=password, username=username, **kwargs)

        self._client = app.test_client()
        self._token = AuthToken(
            name="test-token",
            value=create_access_token(
                expires_delta=False,
                identity=self._user.id,
            ),
            user=self._user,
        )
        db.session.add(self._token)
        db.session.commit()

    @property
    def _headers(self):
        return {
            "headers": {
                "Authorization": f"Bearer {self._token.value}",
                "Content-Type": "application/json",
            }
        }


class _BadAuthTokenApiUser(_ApiUser):
    @property
    def _headers(self):
        # identity is normally `User.id` so setting it to -1 here makes it intentionally invalid
        # for testing purposes.
        token_belonging_to_nonexistent_user = create_access_token(identity=-1)
        return {
            "headers": {
                "Authorization": f"Bearer {token_belonging_to_nonexistent_user}",
                "Content-Type": "application/json",
            }
        }


@pytest.fixture(autouse=True)
def _cleanup_and_teardown():
    db.drop_all()
    db.create_all()
    yield  # this is where the test runs


@pytest.fixture(autouse=True)
def _app():
    _a = create_app()
    _a.test_client_class = flask_login.FlaskLoginClient
    with _a.app_context():
        yield _a


@pytest.fixture()
def api_user(_app):
    return functools.partial(_ApiUser, _app)


@pytest.fixture
def cli_runner(_app):
    return _app.test_cli_runner()


@pytest.fixture()
def client(_app):
    return _app.test_client()


@pytest.fixture
def comment(thread):
    def func(discussion, body=DEFAULT_COMMENT_BODY, **kwargs):
        _thread = thread(discussion=discussion)
        return _thread.create_comment(
            body=body,
            discussion=discussion,
            **kwargs,
        )

    return func


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
def bad_auth_token_api_user(_app):
    return functools.partial(_BadAuthTokenApiUser, _app)


@pytest.fixture
def thread(topic):
    def func(discussion, body=DEFAULT_THREAD_BODY, title=DEFAULT_THREAD_TITLE, **kwargs):
        _topic = topic()
        return _topic.create_thread(body=body, title=title, discussion=discussion, **kwargs)

    return func


@pytest.fixture
def topic():
    def func(name=DEFAULT_TOPIC_NAME, description=DEFAULT_TOPIC_DESCRIPTION, **kwargs):
        _topic = Topic(
            name=name,
            description=description,
            **kwargs,
        )
        db.session.add(_topic)
        db.session.commit()
        return _topic

    return func


@pytest.fixture()
def ui_user(_app):
    return functools.partial(_UiUser, _app)


@pytest.fixture
def user():
    def func(email=DEFAULT_EMAIL, password=DEFAULT_PASSWORD, username=None, **kwargs):
        _user = User(
            email=email,
            password=password,
            username=username or generate_unique_username(),
            **kwargs,
        )
        db.session.add(_user)
        db.session.commit()
        return _user

    return func
