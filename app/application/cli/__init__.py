import random
import secrets

import click
import flask
import flask_mailman
import IPython
from sqlalchemy.sql.expression import func

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

    click.echo("Creating admin account")
    admin = User(email="admin@test.com", password="qqqqqqqq", username="admin")
    db.session.add(admin)
    db.session.commit()

    topic_count = 5 * object_multiplier
    with click.progressbar(range(topic_count), label=f"Creating {topic_count} topics") as count:
        for i in count:
            topic = Topic(name=f"Topic-{i}", description=f"Topic {i} description")
            topic.add_moderator(admin.discussion)
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

    private_topic_count = 5 * object_multiplier
    with click.progressbar(range(private_topic_count), label=f"Creating {private_topic_count} private topics") as count:
        for i in count:
            topic = Topic(name=f"Private-topic-{i}", description=f"Private topic {i} description", is_private=True)
            topic.add_moderator(admin.discussion)
            db.session.add(topic)
            db.session.commit()

            topic_subscribe_request_count = 5 * object_multiplier
            query = User.query.order_by(func.random()).limit(topic_subscribe_request_count)
            with click.progressbar(query, label=f"Creating {topic_subscribe_request_count} private topic subscribe requests") as users:
                for user in users:
                    user.discussion.create_subscribe_request(topic)

            ban_count = 5 * object_multiplier
            query = User.query.order_by(func.random()).limit(ban_count)
            with click.progressbar(query, label=f"Creating {ban_count} bans") as users:
                for idx, user in enumerate(users):
                    topic.create_ban(created_by=admin.discussion, discussion=user.discussion, reason=f"test {idx}")


@cli_bp.cli.command("mark-admin")
@click.option(
    "--username",
    prompt="Username",
    type=click.UNPROCESSED,
)
def mark_admin(username):
    """
    Update an existing `User` such that `User.admin == True`
    """
    if user := User.query.filter_by(username=username).one_or_none():
        user.is_admin = True
        db.session.add(user)
        db.session.commit()
    else:
        raise click.UsageError(messages.NO_USER_FOR_PROVIDED_USERNAME)


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


@cli_bp.cli.command("shell")  # pragma: no cover
def shell():
    IPython.embed()
