from flask import Blueprint, session, redirect, url_for
from app.auth import get_system_user, is_admin

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    user = get_system_user()
    session['username'] = user
    session['role'] = 'admin' if is_admin(user) else 'user'
    return redirect(url_for('views.dashboard'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('views.submit_idea'))
