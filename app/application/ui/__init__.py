from flask import (
    Blueprint,
    render_template,
)
from . import forms

ui_bp = Blueprint(
    "ui_bp",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static",
)


@ui_bp.route("/", methods=['GET', 'POST'])
@ui_bp.route("/login", methods=['GET', 'POST'])
def login():
    form = forms.Login()
    if form.validate_on_submit():
        pw = form.password.data
        un = form.username.data
        print(f'username={un}, password={pw}')

    return render_template("login.html", form=form)
