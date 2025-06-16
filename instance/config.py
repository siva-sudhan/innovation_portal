import os

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
SQLALCHEMY_DATABASE_URI = 'sqlite:///innovation.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
