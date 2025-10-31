# Proxy Generator Tool (Basic)

Simple Flask web app that fetches public proxy lists from configurable sources, tests them concurrently, and presents working proxies in a UI with an export button.

## Setup
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
export FLASK_APP=app.py    # Windows: set FLASK_APP=app.py
flask run
```

Open http://127.0.0.1:5000
