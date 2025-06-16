import os
import getpass
from flask import current_app

def get_system_user():
    try:
        return os.getlogin()
    except OSError:
        return getpass.getuser()  # safer fallback for Linux/Mac

def is_admin(username):
    try:
        path = os.path.join(current_app.instance_path, 'admins.txt')
        with open(path) as f:
            admins = [line.strip() for line in f if line.strip()]
        return username in admins
    except FileNotFoundError:
        return False
