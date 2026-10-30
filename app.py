import os
from functools import wraps

from flask import Flask, render_template, request, redirect, session, flash, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# FIX 1: secret key comes from an environment variable, not hardcoded in the code
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)

STATUSES = ["Applied", "Accepted", "Rejected"]


# ======================
# DATABASE MODELS
# ======================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    # FIX 2: longer column because it now stores a password HASH, not the password
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # jobseeker / recruiter


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100))
    location = db.Column(db.String(100))
    salary = db.Column(db.String(50))
    description = db.Column(db.Text)
    # FIX 3: real foreign key + relationships
    posted_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    recruiter = db.relationship("User", backref="jobs")
    applications = db.relationship(
        "Application", backref="job", cascade="all, delete-orphan"
    )


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("job.id"), nullable=False)
    status = db.Column(db.String(50), default="Applied")
    applicant = db.relationship("User", backref="applications")
    # FIX 4: the database itself stops a double application
    __table_args__ = (
        db.UniqueConstraint("user_id", "job_id", name="one_application_per_job"),
    )


# ======================
# HELPERS (decorators)
# ======================

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return wrapper


def role_required(role):
    """Allow the route only for one role (FIX 5: reusable role check)."""
    def decorator(f):
        @wraps(f)
        @login_required
        def wrapper(*args, **kwargs):
            if session.get("role") != role:
                abort(403)
            return f(*args, **kwargs)
        return wrapper
    return decorator


def get_own_job_or_404(job_id):
    """Recruiter can only touch jobs they posted."""
    job = db.session.get(Job, job_id)
    if job is None:
        abort(404)
    if job.posted_by != session["user_id"]:
        abort(403)
    return job


# ======================
# ROUTES
# ======================

@app.route("/")
def home():
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        role = request.form["role"]

        if not name or not email or len(password) < 6:
            flash("Fill all fields. Password must be at least 6 characters.")
            return redirect("/register")
        if role not in ("jobseeker", "recruiter"):
            flash("Invalid role.")
            return redirect("/register")
        if User.query.filter_by(email=email).first():
            flash("Email already registered.")
            return redirect("/register")

        user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),  # hashed, never plain text
            role=role,
        )
        db.session.add(user)
        db.session.commit()
        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["role"] = user.role
            return redirect("/dashboard")

        flash("Invalid email or password.")
        return redirect("/login")

    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():
    user = db.session.get(User, session["user_id"])
    return render_template("dashboard.html", user=user)


# ---------- Recruiter: create, read, update, delete jobs ----------

@app.route("/post_job", methods=["GET", "POST"])
@role_required("recruiter")
def post_job():
    if request.method == "POST":
        job = Job(
            title=request.form["title"],
            company=request.form["company"],
            location=request.form["location"],
            salary=request.form["salary"],
            description=request.form["description"],
            posted_by=session["user_id"],
        )
        db.session.add(job)
        db.session.commit()
        return redirect("/my_jobs")
    return render_template("post_job.html")


@app.route("/my_jobs")
@role_required("recruiter")
def my_jobs():
    jobs = Job.query.filter_by(posted_by=session["user_id"]).all()
    return render_template("my_jobs.html", jobs=jobs)


@app.route("/edit_job/<int:job_id>", methods=["GET", "POST"])
@role_required("recruiter")
def edit_job(job_id):
    job = get_own_job_or_404(job_id)
    if request.method == "POST":
        job.title = request.form["title"]
        job.company = request.form["company"]
        job.location = request.form["location"]
        job.salary = request.form["salary"]
        job.description = request.form["description"]
        db.session.commit()
        return redirect("/my_jobs")
    return render_template("edit_job.html", job=job)


@app.route("/delete_job/<int:job_id>", methods=["POST"])
@role_required("recruiter")
def delete_job(job_id):
    job = get_own_job_or_404(job_id)
    db.session.delete(job)  # its applications are deleted too (cascade)
    db.session.commit()
    return redirect("/my_jobs")


# ---------- Recruiter: see applicants and update status ----------

@app.route("/job/<int:job_id>/applicants")
@role_required("recruiter")
def applicants(job_id):
    job = get_own_job_or_404(job_id)
    return render_template(
        "applicants.html", job=job, apps=job.applications, statuses=STATUSES
    )


@app.route("/application/<int:app_id>/status", methods=["POST"])
@role_required("recruiter")
def update_status(app_id):
    application = db.session.get(Application, app_id)
    if application is None:
        abort(404)
    if application.job.posted_by != session["user_id"]:
        abort(403)
    new_status = request.form.get("status")
    if new_status not in STATUSES:
        abort(400)
    application.status = new_status
    db.session.commit()
    return redirect(f"/job/{application.job_id}/applicants")


# ---------- Job seeker ----------

@app.route("/jobs")
@login_required
def jobs():
    q = request.args.get("q", "").strip()
    query = Job.query
    if q:
        like = f"%{q}%"
        query = query.filter(Job.title.ilike(like) | Job.location.ilike(like))
    applied_ids = set()
    if session.get("role") == "jobseeker":
        applied_ids = {
            a.job_id for a in Application.query.filter_by(user_id=session["user_id"])
        }
    return render_template(
        "jobs.html", jobs=query.order_by(Job.id.desc()).all(), q=q, applied_ids=applied_ids
    )


@app.route("/apply/<int:job_id>")
@role_required("jobseeker")
def apply(job_id):
    job = db.session.get(Job, job_id)
    if job is None:
        abort(404)

    existing = Application.query.filter_by(
        user_id=session["user_id"], job_id=job_id
    ).first()
    if existing:
        flash("You already applied for this job.")
        return redirect("/jobs")

    db.session.add(Application(user_id=session["user_id"], job_id=job_id))
    db.session.commit()
    flash("Application submitted.")
    return redirect("/my_applications")


@app.route("/my_applications")
@role_required("jobseeker")
def my_applications():
    apps = Application.query.filter_by(user_id=session["user_id"]).all()
    return render_template("my_applications.html", apps=apps)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
