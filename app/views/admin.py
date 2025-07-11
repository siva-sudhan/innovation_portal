# File: app/views/admin.py

from flask import Blueprint, render_template, session, redirect, url_for, flash, request, send_file
from app.models import db, Idea, Event, Vote, DisplayMessage
from app.auth import is_admin
from app.forms import EventForm, DisplayMessageForm
from app.backup import DB_PATH
import random
import os, json, shutil
from datetime import datetime
from collections import defaultdict
from io import BytesIO

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Helper to read/write restricted users
RESTRICTED_USERS_FILE = os.path.join(os.path.dirname(__file__), '..', 'restricted_users.json')


def load_restricted_users():
    if os.path.exists(RESTRICTED_USERS_FILE):
        with open(RESTRICTED_USERS_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def save_restricted_users(users):
    with open(RESTRICTED_USERS_FILE, 'w') as f:
        json.dump(sorted(users), f)


@admin_bp.before_request
def restrict_to_admin():
    if session.get('role') != 'admin':
        flash("Access denied. Admins only.", "error")
        return redirect(url_for('views.dashboard'))


@admin_bp.route('/')
def admin_dashboard():
    users_data = defaultdict(lambda: {'count': 0, 'ideas': []})
    for idea in Idea.query.all():
        if idea.submitter and not idea.is_anonymous:
            users_data[idea.submitter]['count'] += 1
            users_data[idea.submitter]['ideas'].append(idea)

    # Live stats based on current data
    live_stats = {
        'ideas': Idea.query.count(),
        'users': Idea.query.with_entities(Idea.submitter).distinct().count(),
        'votes': Vote.query.count(),
    }

    return render_template("admin/admin_dashboard.html", user_stats=users_data, live_stats=live_stats)


@admin_bp.route('/users')
def user_dashboard():
    users_data = defaultdict(lambda: {'ideas': [], 'restricted': False})
    restricted_users = load_restricted_users()

    for idea in Idea.query.all():
        if idea.submitter and not idea.is_anonymous:
            users_data[idea.submitter]['ideas'].append(idea)

    for username in users_data:
        users_data[username]['restricted'] = username in restricted_users
        users_data[username]['total_ideas'] = len(users_data[username]['ideas'])

    return render_template("admin/user_dashboard.html", users=[{
        'username': u,
        'ideas': d['ideas'],
        'total_ideas': d['total_ideas'],
        'restricted': d['restricted']
    } for u, d in users_data.items()])


@admin_bp.route('/restrict/<username>', methods=['POST'])
def restrict_user(username):
    if username == session.get('username'):
        flash("You cannot restrict yourself.", "error")
        return redirect(url_for('admin.user_dashboard'))

    restricted_users = load_restricted_users()
    restricted_users.add(username)
    save_restricted_users(restricted_users)
    flash(f"User '{username}' has been restricted.", "warning")
    return redirect(url_for('admin.user_dashboard'))


@admin_bp.route('/toggle-restriction/<username>', methods=['POST'])
def toggle_restriction(username):
    if username == session.get('username'):
        flash("You cannot restrict yourself.", "error")
        return redirect(url_for('admin.user_dashboard'))

    restricted_users = load_restricted_users()
    if username in restricted_users:
        restricted_users.remove(username)
        flash(f"User '{username}' has been unrestricted.", "success")
    else:
        restricted_users.add(username)
        flash(f"User '{username}' has been restricted.", "warning")
    save_restricted_users(restricted_users)
    return redirect(url_for('admin.user_dashboard'))

@admin_bp.route('/export')
def export_all_data():
    ideas = Idea.query.order_by(Idea.timestamp.desc()).all()
    data = [{
        'title': i.title,
        'description': i.description,
        'tags': i.tags,
        'submitter': i.submitter,
        'anonymous': i.is_anonymous,
        'timestamp': i.timestamp.isoformat(),
        'votes': i.votes
    } for i in ideas]

    output = BytesIO()
    output.write(json.dumps(data, indent=2).encode('utf-8'))
    output.seek(0)

    return send_file(output, as_attachment=True, download_name='raw_idea_data.json')


@admin_bp.route('/export-db')
def export_database():
    """Download the raw SQLite database file."""
    db.session.commit()  # ensure latest data written
    db_file = DB_PATH  # database located in instance folder
    return send_file(db_file, as_attachment=True, download_name='innovation.db')


@admin_bp.route('/refresh-votes', methods=['POST'])
def refresh_votes():
    """Recalculate vote totals for all ideas."""
    for idea in Idea.query.all():
        idea.votes = Vote.query.filter_by(idea_id=idea.id).count()
    db.session.commit()
    flash('Vote counts refreshed.', 'success')
    return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/events/new', methods=['GET', 'POST'])
def new_event():
    form = EventForm()
    if form.validate_on_submit():
        color = '#' + ''.join(random.choices('0123456789ABCDEF', k=6))
        event = Event(
            title=form.title.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            color=color,
        )
        db.session.add(event)
        db.session.commit()
        flash('Event added.', 'success')
        return redirect(url_for('admin.new_event'))
    events = Event.query.order_by(Event.start_date.desc()).all()
    return render_template('admin/new_event.html', form=form, events=events)


@admin_bp.route('/message', methods=['GET', 'POST'])
def manage_message():
    form = DisplayMessageForm()
    message = DisplayMessage.query.first()
    if form.validate_on_submit():
        if not message:
            message = DisplayMessage()
        message.text = form.text.data
        message.color = form.color.data or '#FF0000'
        link_input = form.link.data.strip() if form.link.data else None
        if link_input and not link_input.startswith(('http://', 'https://')):
            link_input = 'https://' + link_input
        message.link = link_input
        message.blink = form.blink.data
        message.enabled = form.enabled.data
        message.scroll = form.scroll.data
        db.session.add(message)
        db.session.commit()
        flash('Display message updated.', 'success')
        return redirect(url_for('admin.manage_message'))

    if message:
        form.text.data = message.text
        form.color.data = message.color
        form.link.data = message.link
        form.blink.data = message.blink
        form.enabled.data = message.enabled
        form.scroll.data = message.scroll

    return render_template('admin/manage_message.html', form=form)

@admin_bp.route('/events/<int:event_id>/delete')
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted.', 'success')
    return redirect(request.referrer or url_for('views.events'))

@admin_bp.route('/import', methods=['GET', 'POST'])
def import_raw_data():
    from flask_wtf.csrf import validate_csrf
    from wtforms import ValidationError

    if request.method == 'POST':
        file = request.files.get('file')
        csrf_token = request.form.get('csrf_token')

        try:
            validate_csrf(csrf_token)
        except ValidationError:
            flash('Invalid CSRF token.', 'error')
            return redirect(request.url)

        if not file or not file.filename.endswith('.json'):
            flash('Please upload a valid JSON file.', 'error')
            return redirect(request.url)

        try:
            data = json.load(file)
            count_added = 0
            for entry in data:
                # Avoid inserting if exact title+description already exists
                if Idea.query.filter_by(title=entry['title'], description=entry['description']).first():
                    continue

                idea = Idea(
                    title=entry['title'],
                    description=entry['description'],
                    tags=entry.get('tags', ''),
                    submitter=entry.get('submitter', 'unknown'),
                    is_anonymous=entry.get('anonymous', False),
                    timestamp=datetime.fromisoformat(entry['timestamp']),
                    votes=entry.get('votes', 0)
                )
                db.session.add(idea)
                count_added += 1

            db.session.commit()
            flash(f'Successfully imported {count_added} new ideas.', 'success')

        except Exception as e:
            flash(f'Import failed: {str(e)}', 'error')

        return redirect(url_for('admin.admin_dashboard'))

    return render_template('admin/import_data.html')


@admin_bp.route('/import-db', methods=['GET', 'POST'])
def import_database():
    """Replace the current SQLite database with an uploaded file."""
    from flask_wtf.csrf import validate_csrf
    from wtforms import ValidationError

    if request.method == 'POST':
        file = request.files.get('file')
        csrf_token = request.form.get('csrf_token')

        try:
            validate_csrf(csrf_token)
        except ValidationError:
            flash('Invalid CSRF token.', 'error')
            return redirect(request.url)

        if not file or not file.filename.endswith('.db'):
            flash('Please upload a SQLite database file.', 'error')
            return redirect(request.url)

        try:
            backup_path = DB_PATH + '.bak'
            db_file = DB_PATH  # database located in instance folder
            if os.path.exists(db_file):
                shutil.copy2(db_file, backup_path)
            file.save(db_file)
            db.engine.dispose()
            flash('Database imported successfully.', 'success')
        except Exception as e:
            flash(f'Database import failed: {str(e)}', 'error')

        return redirect(url_for('admin.admin_dashboard'))

    return render_template('admin/import_db.html')

