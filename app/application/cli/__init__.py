import random
import re
import secrets

import click
import flask
import flask_mailman

from application.constants import messages
from application.models import (
    Comment,
    db,
    Thread,
    Topic,
    User,
)
from application.util.misc import (
    csv_to_list,
    generate_unique_username,
)


cli_bp = flask.Blueprint(
    "cli",
    __name__,
)


EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")


def validate_email(ctx, param, value):
    if not EMAIL_REGEX.match(value):
        raise click.BadParameter(messages.INVALID_EMAIL_ADDRESS)
    return value


@cli_bp.cli.command("get-config")
def get_config():
    """
    Show config for current running app.
    """
    for k, v in sorted(flask.current_app.config.items()):
        click.echo(f"{k}={v}")


@cli_bp.cli.command("get-endpoints")
def get_endpoints():
    """
    Show all URL endpoints and the URL path they map to.
    """
    for obj in flask.current_app.url_map.iter_rules():
        click.echo(f"{obj.endpoint} -> {obj.rule}")


@cli_bp.cli.command("generate-data")  # pragma: no cover
@click.option("-o", "--object-multiplier", count=True, default=1, show_default=True)
@click.option("-w", "--wipe-db", is_flag=True, help="Reset database before generating data")
def generate_data(object_multiplier, wipe_db):
    """
    This command only exists for development purposes
    """
    assert not flask.current_app.config["PROD"]

    if wipe_db:
        db.drop_all()
        db.create_all()

    topic_count = 5 * object_multiplier
    with click.progressbar(range(topic_count), label=f"Creating {topic_count} topics") as count:
        for i in count:
            topic = Topic(name=f"Topic-{i}", description=f"Topic {i} description")
            db.session.add(topic)
            db.session.commit()

    user_count = 100 * object_multiplier
    topics = Topic.query.all()
    with click.progressbar(range(user_count), label=f"Creating {user_count} users and a thread for each user") as count:
        for _ in count:
            username = generate_unique_username()
            u = User(email=f"{username}@test.com", password=secrets.token_hex(), username=username)
            db.session.add(u)
            db.session.commit()
            topic_idx = random.randint(0, len(topics) - 1)
            topic = topics[topic_idx]
            topic.create_thread(body=f"Body {u.username}", title=f"Title {u.username}", discussion=u.discussion)

    comment_count = 5 * object_multiplier
    threads = Thread.query.all()
    with click.progressbar(User.query.all(), label=f"Creating {comment_count} comments for each user") as users:
        for user in users:
            for i in range(comment_count):
                thread_idx = random.randint(0, len(threads) - 1)
                thread = threads[thread_idx]
                thread.create_comment(body=f"Comment {user.username}-{i}", discussion=user.discussion)

    reply_count = 5 * object_multiplier
    comments = Comment.query.all()
    with click.progressbar(User.query.all(), label=f"Creating {reply_count} replies for each user") as users:
        for user in users:
            for i in range(reply_count):
                comment_idx = random.randint(0, len(comments) - 1)
                comment = comments[comment_idx]
                comment.create_comment(body=f"Reply {user.username}-{i}", discussion=user.discussion)


@cli_bp.cli.command("mark-admin")
@click.option(
    "--email",
    callback=validate_email,
    prompt="Email",
    type=click.UNPROCESSED,
)
def mark_admin(email):
    """
    Update an existing `User` such that `User.admin == True`
    """
    if user := User.query.filter(User.email == email).one_or_none():
        user.is_admin = True
        db.session.add(user)
        db.session.commit()
    else:
        raise click.UsageError(messages.NO_USER_FOR_PROVIDED_EMAIL)


@click.option(
    "--subject",
    prompt="Subject",
    type=click.UNPROCESSED,
)
@click.option(
    "--to",
    prompt="Recipient",
    type=click.UNPROCESSED,
)
@click.option(
    "--body",
    prompt="Body",
    type=click.UNPROCESSED,
)
@click.option(
    "--is-html",
    is_flag=True,
)
@cli_bp.cli.command("send-email")
def send_email(subject, to, body, is_html):
    """
    Send an email.
    """
    msg = flask_mailman.EmailMessage(subject=subject, body=body, to=csv_to_list(to))
    if is_html:
        msg.content_subtype = "html"
    status = bool(msg.send())
    click.echo(f"Sent status: {status}")
