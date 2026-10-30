# Job Portal (Flask)

A two-sided job portal. Recruiters post and manage jobs and review applicants. Job seekers browse, search and apply, and track their application status.

## Tech
Python, Flask, Flask-SQLAlchemy (SQLAlchemy), SQLite, Jinja2 templates, HTML/CSS

## Features
- Registration and login with hashed passwords and sessions
- Role-based access (recruiter / job seeker)
- Recruiter: post, edit, delete jobs; view applicants; accept or reject
- Job seeker: browse and search jobs, apply once per job, see application status
- 3 tables with foreign keys: User, Job, Application

## Run
```
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000
