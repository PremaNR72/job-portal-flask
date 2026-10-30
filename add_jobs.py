from app import app, db, Job, User

with app.app_context():

    # Create database tables if they do not exist
    db.create_all()

    # Find an existing recruiter
    recruiter = User.query.filter_by(role="recruiter").first()

    if recruiter is None:
        print("No recruiter found!")
        print("Please register a recruiter account first.")

    else:
        sample_jobs = [
            {
                "title": "Python Developer",
                "company": "Demo Technologies",
                "location": "Bangalore",
                "salary": "₹4-6 LPA",
                "description": "Python, Flask, SQL and REST API knowledge required."
            },
            {
                "title": "Java Developer",
                "company": "ABC Software",
                "location": "Hyderabad",
                "salary": "₹3-5 LPA",
                "description": "Java, Spring Boot and MySQL knowledge required."
            },
            {
                "title": "Frontend Developer",
                "company": "XYZ Technologies",
                "location": "Bangalore",
                "salary": "₹4-7 LPA",
                "description": "HTML, CSS, JavaScript and React knowledge required."
            },
            {
                "title": "Full Stack Developer",
                "company": "Tech Solutions",
                "location": "Chennai",
                "salary": "₹5-8 LPA",
                "description": "Python, Django and SQL knowledge required."
            },
            {
                "title": "Software Engineer",
                "company": "Demo Software",
                "location": "Pune",
                "salary": "₹4-6 LPA",
                "description": "Fresh graduates with programming skills can apply."
            },
            {
                "title": "Python Backend Developer",
                "company": "TechNova Solutions",
                "location": "Bangalore",
                "salary": "₹5-8 LPA",
                "description": "Develop backend applications using Python, Flask, REST APIs, and SQL databases."
            },
            {
                "title": "Data Analyst",
                "company": "DataVision Analytics",
                "location": "Hyderabad",
                "salary": "₹3-5 LPA",
                "description": "Analyze datasets and prepare reports using Python, SQL, and Excel."
            },
            {
                "title": "Java Backend Developer",
                "company": "CodeCraft Technologies",
                "location": "Chennai",
                "salary": "₹4-7 LPA",
                "description": "Build backend applications using Java, Spring Boot, REST APIs, and MySQL."
            },
            {
                "title": "Frontend Developer",
                "company": "WebSpark Solutions",
                "location": "Pune",
                "salary": "₹3-6 LPA",
                "description": "Create responsive web pages using HTML, CSS, JavaScript, and React."
            },
            {
                "title": "Full Stack Python Developer",
                "company": "BrightTech Systems",
                "location": "Bangalore",
                "salary": "₹5-9 LPA",
                "description": "Develop web applications using Python, Flask, JavaScript, and SQL."
            },
            {
                "title": "Software Testing Engineer",
                "company": "QualityFirst Technologies",
                "location": "Mysore",
                "salary": "₹3-5 LPA",
                "description": "Write test cases, report bugs, and perform functional testing."
            },
            {
                "title": "SQL Developer",
                "company": "DataCore Systems",
                "location": "Hyderabad",
                "salary": "₹4-6 LPA",
                "description": "Write SQL queries and maintain relational databases."
            },
            {
                "title": "Junior DevOps Engineer",
                "company": "CloudBridge Technologies",
                "location": "Chennai",
                "salary": "₹4-7 LPA",
                "description": "Work with Git, Linux, Docker, CI/CD pipelines, and deployment automation."
            },
            {
                "title": "Machine Learning Intern",
                "company": "AI Future Labs",
                "location": "Bangalore",
                "salary": "₹15,000-25,000 per month",
                "description": "Support machine learning projects using Python, pandas, NumPy, and scikit-learn."
            },
            {
                "title": "Junior Software Engineer",
                "company": "NextGen Software",
                "location": "Mumbai",
                "salary": "₹3-6 LPA",
                "description": "Develop, debug, and maintain software applications."
            }
        ]

        added_count = 0

        for data in sample_jobs:

            # Check whether this job already exists for this recruiter
            existing = Job.query.filter_by(
                title=data["title"],
                company=data["company"],
                posted_by=recruiter.id
            ).first()

            if existing is None:
                job = Job(
                    **data,
                    posted_by=recruiter.id
                )

                db.session.add(job)
                added_count += 1

        # Save all new jobs
        db.session.commit()

        print(f"{added_count} new jobs added successfully!")
        print("Total jobs in database:", Job.query.count())