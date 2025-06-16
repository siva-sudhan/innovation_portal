from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

class IdeaForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=5, max=150)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10)])
    is_anonymous = BooleanField('Submit Anonymously')
    submit = SubmitField('Submit Idea')


class VoteForm(FlaskForm):
    submit = SubmitField('\N{THUMBS UP SIGN} Vote')


class LoginForm(FlaskForm):
    """Simple form to capture a username for login/rename."""
    username = StringField('Username', validators=[DataRequired(), Length(min=1, max=150)])
    submit = SubmitField('Continue')
