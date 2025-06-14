A vibe coding project for splitting expenses within a friend group / family

## Usage
Python script to run app:
```
python FairFare/runner.py
```

Start the server with Flask web app (dev only):
```
python -m FairFare.web.app
```

Or Gunicorn Production WSGI Server
```
gunicorn --bind 0.0.0.0:8000 FairFare.web.app:app
```

## Dev quick start
Setup project:
```
source setup.sh
```

Linters before commit:
```
poetry run all
```
