"""Form definitions for the application."""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired


class IdeaForm(FlaskForm):
    """Simple form for submitting an innovation idea."""

    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
