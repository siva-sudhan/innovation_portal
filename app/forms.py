from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    BooleanField,
    SubmitField,
    SelectField,
    DateField,
)
from wtforms.validators import DataRequired, Length, Optional, Regexp

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
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Length(min=1, max=150),
            Regexp(
                r'^[a-z0-9._@]+$',
                message=(
                    'Please use your mail id in small case so that we can link your account to teams.'
                ),
            ),
        ],
    )
    submit = SubmitField('Continue')


class EventForm(FlaskForm):
    title = StringField('Event Title', validators=[DataRequired(), Length(max=150)])
    start_date = DateField('Start Date', validators=[DataRequired()], format='%Y-%m-%d')
    end_date = DateField('End Date', validators=[DataRequired()], format='%Y-%m-%d')
    submit = SubmitField('Add Event')


class DisplayMessageForm(FlaskForm):
    text = StringField('Message Text', validators=[DataRequired(), Length(max=500)])
    color = StringField('Text Color', validators=[Optional(), Length(max=20)], default='#FF0000')
    link = StringField('Link', validators=[Optional(), Length(max=500)])
    blink = BooleanField('Blink Animation')
    enabled = BooleanField('Enable Message', default=True)
    scroll = BooleanField('Scrolling Animation', default=True)
    submit = SubmitField('Save Message')
