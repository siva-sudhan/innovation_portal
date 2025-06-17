import os
import getpass
import re
import xlsxwriter
import io
import uuid
from flask import session
from sqlalchemy import or_
from urllib.parse import quote_plus
from sklearn.feature_extraction.text import TfidfVectorizer

# Manually defined lightweight stopwords list
STATIC_STOPWORDS = set([
    'the', 'and', 'is', 'in', 'to', 'of', 'for', 'a', 'an', 'with', 'on', 'this',
    'that', 'it', 'as', 'are', 'was', 'by', 'be', 'or', 'from', 'you', 'your',
    'our', 'at', 'will', 'can', 'more', 'such', 'if', 'should'
])

def generate_tags(text: str, top_n: int = 5) -> list[str]:
    """Return the top ``top_n`` keyword tags for ``text``.

    The input text is cleaned of lightweight stopwords and analyzed
    using ``TfidfVectorizer`` to surface the most relevant single or
    bi-gram terms.
    """
    # Clean and filter words
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())
    filtered_text = ' '.join(w for w in words if w not in STATIC_STOPWORDS)

    # Use TF-IDF to extract keywords
    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform([filtered_text])
    feature_array = vectorizer.get_feature_names_out()
    scores = tfidf_matrix.toarray()[0]

    # Get top terms
    scored = list(zip(feature_array, scores))
    scored.sort(key=lambda x: x[1], reverse=True)
    return [term for term, _ in scored[:top_n]]

# 🔑 Determine the current system username
def get_current_username() -> str:
    """Return the current system username in a robust way."""
    try:
        return os.getlogin()
    except OSError:
        return getpass.getuser()


def get_device_id() -> str:
    """Return a persistent device identifier stored in the session."""
    device_id = session.get('device_id')
    if not device_id:
        device_id = uuid.uuid4().hex
        session['device_id'] = device_id
    return device_id

# 👤 Determine a stable identifier for voting
def get_voter_id() -> str:
    """Return an identifier for the current voter."""
    if 'username' in session:
        return session['username']
    return get_device_id()


# 🔍 Find similar ideas in the portal by matching tags
def find_similar_ideas(new_idea_tags, exclude_id=None, max_results=5):
    from app.models import Idea
    if not new_idea_tags:
        return []

    filters = [Idea.tags.like(f"%{tag}%") for tag in new_idea_tags]
    query = Idea.query.filter(or_(*filters))

    if exclude_id:
        query = query.filter(Idea.id != exclude_id)

    return query.order_by(Idea.timestamp.desc()).limit(max_results).all()

# 🌐 Generate Google Patents search URL
def generate_patent_search_url(title, tags):
    query_terms = title + " " + " ".join(tags)
    query_string = quote_plus(query_terms.strip())
    return f"https://patents.google.com/?q={query_string}"

# 📦 Export list of ideas to Excel
def export_ideas_to_excel(ideas):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    sheet = workbook.add_worksheet('Ideas')

    headers = ['ID', 'Title', 'Description', 'Tags', 'Submitter', 'Anonymous', 'Timestamp', 'Votes']
    for col, header in enumerate(headers):
        sheet.write(0, col, header)

    for row, idea in enumerate(ideas, start=1):
        sheet.write(row, 0, idea.id)
        sheet.write(row, 1, idea.title)
        sheet.write(row, 2, idea.description)
        sheet.write(row, 3, idea.tags)
        sheet.write(row, 4, idea.submitter or '')
        sheet.write(row, 5, 'Yes' if idea.is_anonymous else 'No')
        sheet.write(row, 6, idea.timestamp.strftime('%Y-%m-%d %H:%M'))
        sheet.write(row, 7, idea.votes)

    workbook.close()
    output.seek(0)
    return output

def generate_teams_link(username: str, message: str | None = None) -> str:
    """Return a Microsoft Teams chat link with an optional custom message."""
    base = "https://teams.microsoft.com/l/chat/0/0"
    if message is None:
        message = (
            "Hi! I found your idea on the Innovation Hub and would love to collaborate."
        )
    encoded = quote_plus(message)
    return f"{base}?users={username}@caterpillar.com&message={encoded}"
