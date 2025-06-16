from flask import Blueprint, jsonify
from app.models import Idea, Vote
from sqlalchemy import func

gamification_bp = Blueprint('gamification', __name__)

@gamification_bp.route('/api/stats')
def stats():
    idea_count = Idea.query.count()
    unique_users = Idea.query.with_entities(Idea.submitter).distinct().count()
    total_votes = Vote.query.count()
    return jsonify({
        'ideas': idea_count,
        'users': unique_users,
        'votes': total_votes
    })

@gamification_bp.route('/api/leaderboard')
def leaderboard():
    top_ideas = (
        Idea.query
        .filter(Idea.votes > 0)
        .order_by(Idea.votes.desc())
        .limit(5)
        .all()
    )
    return jsonify([
        {
            'title': idea.title,
            'votes': idea.votes,
            'submitter': idea.submitter if not idea.is_anonymous else "Anonymous"
        }
        for idea in top_ideas
    ])
