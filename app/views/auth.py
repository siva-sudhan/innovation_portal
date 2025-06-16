from flask import Blueprint, session, redirect, url_for, render_template
from app.auth import is_admin
from app.forms import LoginForm

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Display a simple login form that stores the username in the session."""
    form = LoginForm()
    if form.validate_on_submit():
        user = form.username.data.strip()
        session['username'] = user
        session['role'] = 'admin' if is_admin(user) else 'user'
        return redirect(url_for('views.settings'))

    return render_template('login.html', form=form)

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
