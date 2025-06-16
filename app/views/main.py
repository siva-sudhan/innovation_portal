from flask import Blueprint, render_template, redirect, url_for
from ..forms import IdeaForm
from ..models import Idea
from ..utils import format_idea_title

bp = Blueprint('main', __name__)

# In-memory idea list for demonstration purposes
IDEAS = []

@bp.route('/')
def dashboard():
    """Show the dashboard with submitted ideas."""
    return render_template('dashboard.html', ideas=IDEAS)

@bp.route('/submit', methods=['GET', 'POST'])
def submit():
    """Submit a new idea."""
    form = IdeaForm()
    if form.validate_on_submit():
        idea = Idea(format_idea_title(form.title.data), form.description.data)
        IDEAS.append(idea)
        return redirect(url_for('main.dashboard'))
    return render_template('submit.html', form=form)

@bp.route('/idea/<int:idea_id>')
def idea_detail(idea_id: int):
    """View details for a single idea."""
    if 0 <= idea_id < len(IDEAS):
        idea = IDEAS[idea_id]
    else:
        idea = Idea('Unknown', 'Idea not found.')
    return render_template('idea_detail.html', idea=idea)
