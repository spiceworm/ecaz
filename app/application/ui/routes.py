from flask import (
    current_app,
    render_template,
)


from . import (
    forms,
    ui_bp,
)


@ui_bp.route("/", methods=['GET', 'POST'])
@ui_bp.route("/login", methods=['GET', 'POST'])
def login():
    form = forms.Login()
    if form.validate_on_submit():
        pw = form.password.data
        un = form.username.data
        current_app.logger.debug(f'username={un}, password={pw}')

    return render_template("login.html", form=form)
