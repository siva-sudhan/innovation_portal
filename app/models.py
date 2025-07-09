from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import UniqueConstraint
from . import db

class Idea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(300))
    teammates = db.Column(db.String(200))  # 🧑‍🤝‍🧑 New field
    intent = db.Column(db.String(50))      # 🎯 New field
    submitter = db.Column(db.String(150))
    is_anonymous = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    votes = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Idea {self.id} - {self.title}>'

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idea_id = db.Column(db.Integer, db.ForeignKey('idea.id'), nullable=False)
    voter_id = db.Column(db.String(150), nullable=False)

    __table_args__ = (UniqueConstraint('idea_id', 'voter_id', name='unique_vote'),)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    color = db.Column(db.String(20), default="#FFCD00")

    def __repr__(self):
        return f"<Event {self.title} {self.start_date} - {self.end_date}>"


class DisplayMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    color = db.Column(db.String(20), default="#FF0000")
    link = db.Column(db.String(500))
    blink = db.Column(db.Boolean, default=False)
    enabled = db.Column(db.Boolean, default=True)
    scroll = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<DisplayMessage {self.text[:20]}>"
