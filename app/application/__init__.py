import decouple
import flask
import flask_admin
import flask_jwt_extended
import flask_login
import flask_mailman


def create_app():
    from application.admin import views as admin_views
    from application.api import api_bp
    from application.cli import cli_bp
    from application.models import (
        ApiToken,
        db,
        migrate,
        User,
    )
    from application.ui import ui_bp

    class Config:
        APP_NAME = decouple.config("APP_NAME")
        BASE_URL = decouple.config("BASE_URL")

        DEBUG = decouple.config("DEBUG", cast=bool, default=False)
        FLASK_ADMIN_SWATCH = decouple.config("FLASK_ADMIN_SWATCH", default="cerulean")

        PROD = decouple.config("PROD", cast=bool, default=False)
        SECRET_KEY = decouple.config("SECRET_KEY")
        TESTING = decouple.config("TESTING", cast=bool, default=False)
        WTF_CSRF_ENABLED = decouple.config("WTF_CSRF_ENABLED", cast=bool, default=True)

        MAIL_DEFAULT_SENDER = decouple.config("MAIL_DEFAULT_SENDER")
        MAIL_PASSWORD = decouple.config("MAIL_PASSWORD")
        MAIL_PORT = decouple.config("MAIL_PORT", cast=int, default=587)
        MAIL_SERVER = decouple.config("MAIL_SERVER")
        MAIL_TIMEOUT = decouple.config("MAIL_TIMEOUT", cast=int, default=10)
        MAIL_USE_TLS = MAIL_PORT == 587
        MAIL_USE_SSL = MAIL_PORT == 465
        MAIL_USERNAME = decouple.config("MAIL_USERNAME")

        POSTGRES_DB = decouple.config("POSTGRES_DB")
        POSTGRES_HOST = decouple.config("POSTGRES_HOST")
        POSTGRES_PASSWORD = decouple.config("POSTGRES_PASSWORD")
        POSTGRES_PORT = decouple.config("POSTGRES_PORT")
        POSTGRES_SSL = decouple.config("POSTGRES_SSL", cast=bool, default=True)
        POSTGRES_USER = decouple.config("POSTGRES_USER")

        # Magic flask-sqlalchemy environment variable
        SQLALCHEMY_DATABASE_URI = (
            f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
            f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        ) + ("?sslmode=require" if POSTGRES_SSL else "")

        # Magic flask-sqlalchemy environment variable
        SQLALCHEMY_ENGINE_OPTIONS = {
            # Each time the connection is used, send a SELECT 1 query to check the connection.
            # If it fails, then the connection is recycled and checked again.
            # Upon success, the query is then executed.
            "pool_pre_ping": True,
        }

        def json(self):
            return {attr: getattr(self, attr) for attr in dir(self) if attr.isupper()}

    app = flask.Flask(
        __name__,
        static_folder=None,
        template_folder=None,
    )
    app.register_blueprint(api_bp)
    app.register_blueprint(cli_bp)
    app.register_blueprint(ui_bp)

    config = Config()
    app.config.from_object(config)
    app.logger.debug(config.json())

    flask_jwt_extended.JWTManager(app)
    flask_mailman.Mail(app)

    login_manager = flask_login.LoginManager()
    login_manager.login_view = "ui_bp.login"
    login_manager.init_app(app)

    admin = flask_admin.Admin(
        app,
        index_view=admin_views.RestrictedIndexView(name="CLI"),
        template_mode="bootstrap4",
    )
    admin.add_link(flask_admin.base.MenuLink(name="Site", url="/"))
    admin.add_view(admin_views.ApiTokenModelView(ApiToken, db.session))
    admin.add_view(admin_views.UserModelView(User, db.session))

    db.init_app(app)
    migrate.init_app(app, db)
    with app.app_context():
        db.create_all()

    @app.before_request
    def define_globals():
        """No custom attributes will be available on `flask.g` unless
        they are set on the `flask.g` object here."""
        flask.g.config = config

    @app.errorhandler(Exception)
    def handle_exception(e):
        flask.flash(str(e), category="error")
        return flask.redirect(flask.url_for("ui_bp.login"))

    @login_manager.user_loader
    def load_user(user_id):
        """Callback function that tells flask-login how to reload
        an object for a user that has already been authenticated,
        such as when someone reconnects to a "remember me" session"""
        return db.session.get(User, user_id)

    return app
