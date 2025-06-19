from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    BooleanField,
    SubmitField,
    SelectField,
    DateField,
)
from wtforms.validators import DataRequired, Length, Optional

class IdeaForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=5, max=150)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10)])
    teammates = StringField('Teammates', validators=[Optional(), Length(max=250)])
    intent = SelectField('Your Role :', choices=[
        ('owner', 'I want to own and implement this idea'),
        ('mentor', 'I want to mentor others on this idea'),
        ('visionary', 'I just believe this idea should exist')
    ], validators=[DataRequired()])
    is_anonymous = BooleanField('Submit Anonymously')
    submit = SubmitField('Submit Idea')


class VoteForm(FlaskForm):
    submit = SubmitField('\N{THUMBS UP SIGN} Vote')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=1, max=150)])
    submit = SubmitField('Continue')


class EventForm(FlaskForm):
    title = StringField('Event Title', validators=[DataRequired(), Length(max=150)])
    start_date = DateField('Start Date', validators=[DataRequired()], format='%Y-%m-%d')
    end_date = DateField('End Date', validators=[DataRequired()], format='%Y-%m-%d')
    submit = SubmitField('Add Event')
