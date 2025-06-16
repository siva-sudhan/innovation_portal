import os
import getpass

def get_system_user():
    try:
        return os.getlogin()
    except OSError:
        return getpass.getuser()  # safer fallback for Linux/Mac

def is_admin(username):
    try:
        with open('instance/admins.txt') as f:
            admins = [line.strip() for line in f if line.strip()]
        return username in admins
    except FileNotFoundError:
        return False
