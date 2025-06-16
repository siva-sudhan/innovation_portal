from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, session
from datetime import datetime
from app.forms import IdeaForm
from app.models import db, Idea, Vote
from app.utils import generate_tags, export_ideas_to_excel, get_current_username, get_voter_id
from io import BytesIO
from datetime import datetime

views_bp = Blueprint('views', __name__)

@views_bp.route('/', methods=['GET', 'POST'])
def submit_idea():
    form = IdeaForm()
    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        is_anonymous = form.is_anonymous.data
        tags = ','.join(generate_tags(f"{title} {description}"))

        idea = Idea(
            title=title,
            description=description,
            tags=tags,
            submitter=get_current_username(),
            is_anonymous=is_anonymous,
            timestamp=datetime.utcnow()
        )
        db.session.add(idea)
        db.session.commit()
        flash('Idea submitted successfully!', 'success')
        return redirect(url_for('views.dashboard'))

    return render_template('submit.html', form=form)

@views_bp.route('/dashboard')
def dashboard():
    ideas = Idea.query.order_by(Idea.timestamp.desc()).all()
    unique_user_count = db.session.query(Idea.submitter).filter(Idea.submitter != None).distinct().count()

    voter_id = get_voter_id()
    voted = Vote.query.filter_by(voter_id=voter_id).all()
    voted_ideas = {v.idea_id for v in voted}

    return render_template(
        'dashboard.html',
        ideas=ideas,
        unique_user_count=unique_user_count,
        voted_ideas=voted_ideas,
    )

@views_bp.route('/idea/<int:idea_id>')
def idea_detail(idea_id):
    idea = Idea.query.get_or_404(idea_id)
    voter_id = get_voter_id()
    voted = Vote.query.filter_by(idea_id=idea.id, voter_id=voter_id).first() is not None
    return render_template('idea_detail.html', idea=idea, voted=voted)

@views_bp.route('/idea/<int:idea_id>/edit', methods=['GET', 'POST'])
def edit_idea(idea_id):
    if session.get('role') != 'admin':
        flash("Access denied.", "error")
        return redirect(url_for('views.dashboard'))

    idea = Idea.query.get_or_404(idea_id)
    form = IdeaForm(obj=idea)

    if form.validate_on_submit():
        idea.title = form.title.data
        idea.description = form.description.data
        idea.is_anonymous = form.is_anonymous.data
        idea.timestamp = datetime.utcnow()
        db.session.commit()
        flash("Idea updated successfully!", "success")
        return redirect(url_for('views.dashboard'))

    return render_template("edit_idea.html", form=form, idea=idea)


# --- Delete Idea ---
@views_bp.route('/idea/<int:idea_id>/delete')
def delete_idea(idea_id):
    if session.get('role') != 'admin':
        flash("Access denied.", "error")
        return redirect(url_for('views.dashboard'))

    idea = Idea.query.get_or_404(idea_id)
    db.session.delete(idea)
    db.session.commit()
    flash("Idea deleted.", "success")
    return redirect(url_for('views.dashboard'))


# --- Vote on Idea ---
@views_bp.route('/vote/<int:idea_id>', methods=['POST'])
def vote(idea_id):
    voter_id = get_voter_id()
    existing = Vote.query.filter_by(idea_id=idea_id, voter_id=voter_id).first()
    if existing:
        flash('You already voted for this idea.', 'info')
        return redirect(url_for('views.dashboard'))

    idea = Idea.query.get_or_404(idea_id)
    idea.votes += 1
    vote = Vote(idea_id=idea_id, voter_id=voter_id)
    db.session.add(vote)
    db.session.commit()
    flash('Thanks for voting!', 'success')
    return redirect(url_for('views.dashboard'))

@views_bp.route('/export')
def export_ideas():
    ideas = Idea.query.order_by(Idea.timestamp.desc()).all()
    output = export_ideas_to_excel(ideas)
    return send_file(output, as_attachment=True, download_name='ideas.xlsx')
