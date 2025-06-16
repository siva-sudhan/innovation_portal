import re
import xlsxwriter
import io
from collections import Counter

# 🔖 Generate keyword tags from title + description
def generate_tags(text, top_n=5):
    words = re.findall(r'\b\w+\b', text.lower())
    stopwords = set([
        'the', 'and', 'is', 'in', 'to', 'of', 'for', 'a', 'an', 'with', 'on',
        'this', 'that', 'it', 'as', 'are', 'was', 'by', 'be', 'or', 'from'
    ])
    filtered = [w for w in words if w not in stopwords and len(w) > 2]
    most_common = Counter(filtered).most_common(top_n)
    return [word for word, _ in most_common]

# 📦 Export list of ideas to Excel
def export_ideas_to_excel(ideas):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    sheet = workbook.add_worksheet('Ideas')

    headers = ['ID', 'Title', 'Description', 'Tags', 'Anonymous', 'Timestamp', 'Votes']
    for col, header in enumerate(headers):
        sheet.write(0, col, header)

    for row, idea in enumerate(ideas, start=1):
        sheet.write(row, 0, idea.id)
        sheet.write(row, 1, idea.title)
        sheet.write(row, 2, idea.description)
        sheet.write(row, 3, idea.tags)
        sheet.write(row, 4, 'Yes' if idea.is_anonymous else 'No')
        sheet.write(row, 5, idea.timestamp.strftime('%Y-%m-%d %H:%M'))
        sheet.write(row, 6, idea.votes)

    workbook.close()
    output.seek(0)
    return output
