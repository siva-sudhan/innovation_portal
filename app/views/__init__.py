from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from app.forms import IdeaForm, VoteForm, LoginForm, EventForm
from app.models import db, Idea, Vote, Event, DisplayMessage
from app.utils import (
    generate_tags,
    export_ideas_to_excel,
    get_current_username,
    get_voter_id,
    find_similar_ideas,
    generate_patent_search_url
)
from app.auth import is_admin
from io import BytesIO

views_bp = Blueprint('views', __name__)

@views_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    form = LoginForm()
    if form.validate_on_submit():
        user = form.username.data.strip()
        session['username'] = user
        session['role'] = 'admin' if is_admin(user) else 'user'
        flash('Username updated.', 'success')
        return redirect(url_for('views.settings'))
    return render_template('settings.html', form=form)

@views_bp.route('/', methods=['GET', 'POST'])
def submit_idea():
    if 'username' not in session:
        flash('Please log in to submit an idea.', 'error')
        return redirect(url_for('auth.login'))

    form = IdeaForm()
    display_message = DisplayMessage.query.filter_by(enabled=True).first()
    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        is_anonymous = form.is_anonymous.data
        teammates = form.teammates.data.strip() if form.teammates.data else ""
        intent = form.intent.data
        tags_list = generate_tags(f"{title} {description}")
        tags = ','.join(tags_list)

        idea = Idea(
            title=title,
            description=description,
            tags=tags,
            teammates=teammates,
            intent=intent,
            submitter=session.get('username', get_current_username()),
            is_anonymous=is_anonymous,
            timestamp=datetime.utcnow()
        )
        db.session.add(idea)
        db.session.commit()

        similar_ideas = find_similar_ideas(tags_list, exclude_id=idea.id)
        patent_url = generate_patent_search_url(title, tags_list)

        flash('Idea submitted successfully!', 'success')
        return render_template(
            'submit_success.html',
            idea=idea,
            similar_ideas=similar_ideas,
            patent_url=patent_url
        )

    return render_template('submit.html', form=form, display_message=display_message)

@views_bp.route('/dashboard')
def dashboard():
    filter_my = request.args.get('mine') == '1'
    query = Idea.query.order_by(Idea.timestamp.desc())
    if filter_my and session.get('username'):
        query = query.filter_by(submitter=session['username'])
    ideas = query.all()
    unique_user_count = db.session.query(Idea.submitter).filter(Idea.submitter.isnot(None)).distinct().count()

    voter_id = get_voter_id()
    voted = Vote.query.filter_by(voter_id=voter_id).all()
    voted_ideas = {v.idea_id for v in voted}
    vote_form = VoteForm()

    return render_template(
        'dashboard.html',
        ideas=ideas,
        unique_user_count=unique_user_count,
        voted_ideas=voted_ideas,
        vote_form=vote_form,
        filter_my=filter_my,
    )

@views_bp.route('/idea/<int:idea_id>')
def idea_detail(idea_id):
    idea = Idea.query.get_or_404(idea_id)
    voter_id = get_voter_id()
    voted = Vote.query.filter_by(idea_id=idea.id, voter_id=voter_id).first() is not None
    vote_form = VoteForm()

    # ✅ Find similar ideas (by tags)
    tags_list = [tag.strip() for tag in idea.tags.split(',')] if idea.tags else []
    similar_ideas = find_similar_ideas(tags_list, exclude_id=idea.id)
    patent_url = generate_patent_search_url(idea.title, tags_list)

    return render_template(
        'idea_detail.html',
        idea=idea,
        voted=voted,
        vote_form=vote_form,
        similar_ideas=similar_ideas,
        patent_url=patent_url
    )

@views_bp.route('/idea/<int:idea_id>/edit', methods=['GET', 'POST'])
def edit_idea(idea_id):
    idea = Idea.query.get_or_404(idea_id)
    if session.get('role') != 'admin' and session.get('username') != idea.submitter:
        flash("Access denied.", "error")
        return redirect(url_for('views.dashboard'))

    form = IdeaForm(obj=idea)

    if form.validate_on_submit():
        idea.title = form.title.data
        idea.description = form.description.data
        idea.is_anonymous = form.is_anonymous.data
        idea.teammates = form.teammates.data.strip() if form.teammates.data else ""
        idea.intent = form.intent.data
        idea.timestamp = datetime.utcnow()
        db.session.commit()
        flash("Idea updated successfully!", "success")
        return redirect(url_for('views.dashboard'))

    return render_template("edit_idea.html", form=form, idea=idea)

@views_bp.route('/idea/<int:idea_id>/delete')
def delete_idea(idea_id):
    idea = Idea.query.get_or_404(idea_id)
    if session.get('role') != 'admin' and session.get('username') != idea.submitter:
        flash("Access denied.", "error")
        return redirect(url_for('views.dashboard'))

    # Remove votes tied to this idea so stats remain accurate
    Vote.query.filter_by(idea_id=idea.id).delete()

    db.session.delete(idea)
    db.session.commit()
    flash("Idea deleted.", "success")
    return redirect(url_for('views.dashboard'))

@views_bp.route('/vote/<int:idea_id>', methods=['POST'])
def vote(idea_id):
    if 'username' not in session:
        flash('Please log in to vote.', 'error')
        return redirect(url_for('auth.login'))

    form = VoteForm()
    if not form.validate_on_submit():
        flash('Invalid vote submission.', 'error')
        return redirect(url_for('views.dashboard'))

    voter_id = get_voter_id()
    existing = Vote.query.filter_by(idea_id=idea_id, voter_id=voter_id).first()
    if existing:
        flash('You already voted for this idea.', 'info')
        return redirect(url_for('views.dashboard'))

    idea = Idea.query.get_or_404(idea_id)
    idea.votes += 1
    vote = Vote(idea_id=idea_id, voter_id=voter_id)
    db.session.add(vote)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash('You already voted for this idea.', 'info')
        return redirect(url_for('views.dashboard'))

    flash('Thanks for voting!', 'success')
    return redirect(url_for('views.dashboard'))

@views_bp.route('/export')
def export_ideas():
    ideas = Idea.query.order_by(Idea.timestamp.desc()).all()
    output = export_ideas_to_excel(ideas)
    return send_file(output, as_attachment=True, download_name='ideas.xlsx')


@views_bp.route('/events')
def events():
    from calendar import monthrange
    month = request.args.get('month', type=int) or datetime.utcnow().month
    year = request.args.get('year', type=int) or datetime.utcnow().year

    start_month = datetime(year, month, 1).date()
    end_month = datetime(year, month, monthrange(year, month)[1]).date()

    events_query = (
        Event.query
        .filter(Event.start_date <= end_month, Event.end_date >= start_month)
        .all()
    )
    events = [
        {
            'id': ev.id,
            'title': ev.title,
            'start_date': ev.start_date.isoformat(),
            'end_date': ev.end_date.isoformat(),
            'color': ev.color,
            'display_start': ev.start_date.strftime('%d %b %Y').upper(),
            'display_end': ev.end_date.strftime('%d %b %Y').upper(),
        }
        for ev in events_query
    ]

    upcoming_query = (
        Event.query
        .filter(Event.start_date > end_month)
        .order_by(Event.start_date)
        .all()
    )
    upcoming_events = [
        {
            'id': ev.id,
            'title': ev.title,
            'start_date': ev.start_date.isoformat(),
            'end_date': ev.end_date.isoformat(),
            'color': ev.color,
            'display_start': ev.start_date.strftime('%d %b %Y').upper(),
            'display_end': ev.end_date.strftime('%d %b %Y').upper(),
        }
        for ev in upcoming_query
    ]

    month_name = datetime(year, month, 1).strftime('%b %Y').upper()

    return render_template(
        'calendar.html',
        month=month,
        year=year,
        month_name=month_name,
        events=events,
        upcoming_events=upcoming_events,
    )
