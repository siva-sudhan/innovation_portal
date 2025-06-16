from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from datetime import datetime
from app.forms import IdeaForm
from app.models import db, Idea
from app.utils import generate_tags, export_ideas_to_excel, get_current_username
from io import BytesIO

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
    return render_template('dashboard.html', ideas=ideas, unique_user_count=unique_user_count)

@views_bp.route('/idea/<int:idea_id>')
def idea_detail(idea_id):
    idea = Idea.query.get_or_404(idea_id)
    return render_template('idea_detail.html', idea=idea)

@views_bp.route('/export')
def export_ideas():
    ideas = Idea.query.order_by(Idea.timestamp.desc()).all()
    output = export_ideas_to_excel(ideas)
    return send_file(output, as_attachment=True, download_name='ideas.xlsx')
