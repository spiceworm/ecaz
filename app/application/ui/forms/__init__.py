import flask
import flask_wtf


class BaseForm(flask_wtf.FlaskForm):
    def validate_on_submit(self, extra_validators=None):
        result = super().validate_on_submit(extra_validators=extra_validators)

        for field, errors in self.errors.items():
            flask.flash(f"{field}: {', '.join(errors)}", category="error")

        return result


from .access import *
from .profile import *
from .settings import *
