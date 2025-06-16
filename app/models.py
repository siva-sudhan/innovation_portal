from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from . import db

class Idea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(300))
    submitter = db.Column(db.String(150))
    is_anonymous = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    votes = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Idea {self.id} - {self.title}>'
