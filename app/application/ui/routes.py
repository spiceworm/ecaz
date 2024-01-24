from flask import (
    current_app,
    flash,
    render_template,
)


from . import (
    forms,
    ui_bp,
)
from ..models import User


@ui_bp.route("/", methods=["GET", "POST"])
@ui_bp.route("/login", methods=["GET", "POST"])
def login():
    form = forms.Login()
    if form.validate_on_submit():
        matches = User.query.filter_by(
            password=form.password.data,
            username=form.username.data,
        ).all()

        current_app.logger.debug(f"Match count = {len(matches)}")
        current_app.logger.debug(matches)

        if matches:
            if len(matches) == 1:
                user = matches[0]
                flash(f"Logged in as {user.username}")
            else:
                flash("Multiple matches found for log in credentials")
        else:
            flash("Invalid log in credentials")

    return render_template("login.html", form=form)
