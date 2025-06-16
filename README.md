# innovation_portal

This Flask application collects innovation ideas from teammates in a corporate organisation.

## Setup
Install dependencies with `pip install -r requirements.txt`.

Create a virtual environment first if desired:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running
Start the development server with:

```bash
export FLASK_APP=run.py
flask run
```

Then visit <http://localhost:5000/> to view the app.

The `instance/config.py` file holds configuration values such as `SECRET_KEY`.
Create your own local override if needed.

## Testing

Verify Python files compile without syntax errors:

```bash
python -m py_compile $(git ls-files '*.py')
```
