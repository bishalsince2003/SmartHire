from flask import Flask, render_template, request, redirect, session ,flash
import os
from database import get_connection
from werkzeug.security import generate_password_hash, check_password_hash
from config import SECRET_KEY, DEBUG

app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads/resumes"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = SECRET_KEY

@app.route("/")
def home():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            jobs.*,
            companies.company_name
        FROM jobs
        JOIN companies
            ON jobs.company_id = companies.id
        WHERE jobs.status='Active'
        ORDER BY jobs.id DESC
        LIMIT 6
    """)

    featured_jobs = cursor.fetchall()

    applied_jobs = []

    if "user_id" in session:

        cursor.execute("""
            SELECT job_id
            FROM applications
            WHERE user_id=%s
        """, (session["user_id"],))

        applied_jobs = [
            row["job_id"]
            for row in cursor.fetchall()
        ]

    cursor.close()
    conn.close()

    return render_template(
        "index.html",
        featured_jobs=featured_jobs,
        applied_jobs=applied_jobs
    )

@app.route("/users")
def users():

    try:

        conn = get_connection()

        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users")

        users = cursor.fetchall()
        applied_jobs = []

        if "user_id" in session:

            cursor.execute(
                """
                SELECT job_id
                FROM applications
                WHERE user_id=%s
                """,
                (session["user_id"],)
            )

            applied_jobs = [
                row["job_id"]
                for row in cursor.fetchall()
            ]

        cursor.close()
        conn.close()

        return users

    except Exception as e:

        return str(e)

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "GET":
        return render_template("signup.html")

    full_name = request.form["full_name"]
    email = request.form["email"]
    phone = request.form["phone"]
    password = generate_password_hash(request.form["password"])

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users
        (full_name, email, phone, password)
        VALUES (%s, %s, %s, %s)
    """, (full_name, email, phone, password))

    conn.commit()

    cursor.close()
    conn.close()

    flash("Account created successfully. Please login.", "success")
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("login.html")

    email = request.form["email"]
    password = request.form["password"]

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM users WHERE email=%s",
        (email,)
    )

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user and check_password_hash(user["password"], password):

        session["user_id"] = user["id"]
        session["user_name"] = user["full_name"]
        session["role"] = user["role"]

        return redirect("/dashboard")

    flash("Invalid Email or Password", "danger")
    return redirect("/login")

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM jobs")
    total_jobs = cursor.fetchone()["total"]

    cursor.execute(
        "SELECT COUNT(*) AS total FROM applications WHERE user_id=%s",
        (session["user_id"],)
    )
    applied_jobs = cursor.fetchone()["total"]

    cursor.execute(
        "SELECT COUNT(*) AS total FROM saved_jobs WHERE user_id=%s",
        (session["user_id"],)
    )
    saved_jobs = cursor.fetchone()["total"]
        # Pending Applications
    cursor.execute("""
    SELECT COUNT(*) AS total
    FROM applications
    WHERE user_id=%s
    AND application_status='Pending'
    """, (session["user_id"],))

    pending_jobs = cursor.fetchone()["total"]


    # Shortlisted Applications
    cursor.execute("""
    SELECT COUNT(*) AS total
    FROM applications
    WHERE user_id=%s
    AND application_status='Shortlisted'
    """, (session["user_id"],))

    shortlisted_jobs = cursor.fetchone()["total"]


    # Rejected Applications
    cursor.execute("""
    SELECT COUNT(*) AS total
    FROM applications
    WHERE user_id=%s
    AND application_status='Rejected'
    """, (session["user_id"],))

    rejected_jobs = cursor.fetchone()["total"]


    # Recent Applications
    cursor.execute("""

    SELECT

    jobs.job_title,
    companies.company_name,
    applications.application_status,
    applications.applied_at

    FROM applications

    JOIN jobs
    ON applications.job_id = jobs.id

    JOIN companies
    ON jobs.company_id = companies.id

    WHERE applications.user_id=%s

    ORDER BY applications.applied_at DESC

    LIMIT 5

    """, (session["user_id"],))

    recent_applications = cursor.fetchall()
    

    cursor.close()
    conn.close()

    return render_template(
        "user/dashboard.html",

        name=session["user_name"],

        total_jobs=total_jobs,

        applied_jobs=applied_jobs,

        saved_jobs=saved_jobs,

        pending_jobs=pending_jobs,

        shortlisted_jobs=shortlisted_jobs,

        rejected_jobs=rejected_jobs,

        recent_applications=recent_applications
    )

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

@app.route("/jobs")
def jobs():

    search = request.args.get("search", "")
    category = request.args.get("category", "")
    location = request.args.get("location", "")
    sort = request.args.get("sort", "")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """

    SELECT

    jobs.*,
    companies.company_name,
    categories.category_name

    FROM jobs

    JOIN companies
    ON jobs.company_id=companies.id

    JOIN categories
    ON jobs.category_id=categories.id

    WHERE 1=1

    """

    values=[]

    if search:

        query+=" AND jobs.job_title LIKE %s"
        values.append(f"%{search}%")

    if category:

        query+=" AND categories.category_name=%s"
        values.append(category)

    if location:

        query+=" AND jobs.location LIKE %s"
        values.append(f"%{location}%")

    if sort=="salary_high":

        query+=" ORDER BY salary DESC"

    elif sort=="salary_low":

        query+=" ORDER BY salary ASC"

    else:

        query+=" ORDER BY jobs.id DESC"

    cursor.execute(query,tuple(values))

    jobs=cursor.fetchall()
    applied_jobs = []

    if "user_id" in session:

        cursor.execute(
            """
            SELECT job_id
            FROM applications
            WHERE user_id=%s
            """,
            (session["user_id"],)
        )

        applied_jobs = [
            row["job_id"]
            for row in cursor.fetchall()
        ]
    cursor.execute("SELECT * FROM categories")

    categories=cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
    "jobs.html",
    jobs=jobs,
    categories=categories,
    applied_jobs=applied_jobs
)
@app.route("/apply/<int:job_id>")
def apply_job(job_id):

    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Check if already applied
    cursor.execute(
        """
        SELECT id
        FROM applications
        WHERE user_id=%s AND job_id=%s
        """,
        (session["user_id"], job_id)
    )

    application = cursor.fetchone()

    if application:

        cursor.close()
        conn.close()

        flash("You have already applied for this job.", "warning")

        return redirect("/jobs")

    # New Application
    cursor.execute(
        """
        INSERT INTO applications
        (user_id, job_id)

        VALUES(%s,%s)
        """,
        (session["user_id"], job_id)
    )

    conn.commit()

    cursor.close()
    conn.close()

    flash("Job applied successfully.", "success")

    return redirect("/jobs")
@app.route("/applications")
def applications():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute("""

    SELECT

    applications.application_status,
    jobs.job_title,
    companies.company_name

    FROM applications

    JOIN jobs
    ON applications.job_id = jobs.id

    JOIN companies
    ON jobs.company_id = companies.id

    WHERE applications.user_id=%s

    """, (session["user_id"],))

    applications = cursor.fetchall()

    cursor.close()

    conn.close()

    return render_template(
        "applications.html",
        applications=applications
    )
@app.route("/save-job/<int:job_id>")
def save_job(job_id):

    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()

    cursor = conn.cursor()

    try:

        cursor.execute("""

        INSERT INTO saved_jobs
        (user_id, job_id)

        VALUES(%s,%s)

        """, (session["user_id"], job_id))

        conn.commit()

    except:
        pass

    cursor.close()

    conn.close()

    return redirect("/jobs")
@app.route("/saved-jobs")
def saved_jobs():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute("""

    SELECT

    jobs.job_title,
    companies.company_name

    FROM saved_jobs

    JOIN jobs
    ON saved_jobs.job_id = jobs.id

    JOIN companies
    ON jobs.company_id = companies.id

    WHERE saved_jobs.user_id=%s

    """, (session["user_id"],))

    jobs = cursor.fetchall()

    cursor.close()

    conn.close()

    return render_template(
        "saved_jobs.html",
        jobs=jobs
    )
@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM users WHERE id=%s",
        (session["user_id"],)
    )

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        "profile.html",
        user=user
    )
@app.route("/edit-profile", methods=["GET", "POST"])
def edit_profile():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":

        full_name = request.form["full_name"]
        phone = request.form["phone"]

        resume = request.files["resume"]

        if resume.filename != "":

            resume.save(

                os.path.join(

                    app.config["UPLOAD_FOLDER"],

                    resume.filename

                )

            )

        cursor.execute("""

        UPDATE users

        SET full_name=%s,
            phone=%s,
            resume=%s

        WHERE id=%s

        """, (full_name, phone, resume.filename, session["user_id"]))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect("/profile")

    cursor.execute(
        "SELECT * FROM users WHERE id=%s",
        (session["user_id"],)
    )

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        "edit_profile.html",
        user=user
    )
@app.route("/change-password", methods=["GET", "POST"])
def change_password():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "GET":
        return render_template("change_password.html")

    current_password = request.form["current_password"]
    new_password = request.form["new_password"]

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT password FROM users WHERE id=%s",
        (session["user_id"],)
    )
    print(session["user_id"])
    print(session["user_name"])

    user = cursor.fetchone()

    # print(user["password"])
    # print(current_password)

    # print(check_password_hash(user["password"], current_password))

    if not check_password_hash(user["password"], current_password):

        cursor.close()
        conn.close()

        return "Current Password Incorrect"

    new_hash = generate_password_hash(new_password)

    cursor.execute(
        "UPDATE users SET password=%s WHERE id=%s",
        (new_hash, session["user_id"])
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/profile")


@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    if request.method == "GET":
        return render_template("admin_login.html")

    email = request.form["email"]
    password = request.form["password"]

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM users WHERE email=%s AND role='admin'",
        (email,)
    )

    admin = cursor.fetchone()

    cursor.close()
    conn.close()

    if admin and check_password_hash(admin["password"], password):

        session["admin_id"] = admin["id"]
        session["admin_name"] = admin["full_name"]

        return redirect("/admin-dashboard")

    return "Invalid Admin Credentials"

@app.route("/admin-dashboard")
def admin_dashboard():

    if "admin_id" not in session:
        return redirect("/admin-login")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM users")
    total_users = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM jobs")
    total_jobs = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM applications")
    total_applications = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM companies")
    total_companies = cursor.fetchone()["total"]

    cursor.close()
    conn.close()

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_jobs=total_jobs,
        total_applications=total_applications,
        total_companies=total_companies
    )

@app.route("/add-company", methods=["GET", "POST"])
def add_company():

    if "admin_id" not in session:
        return redirect("/admin-login")

    if request.method == "GET":
        return render_template("add_company.html")

    company_name = request.form["company_name"]
    location = request.form["location"]

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO companies
        (company_name, location)

        VALUES(%s,%s)
        """,
        (company_name, location)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/admin-dashboard")

@app.route("/companies")
def companies():

    if "admin_id" not in session:
        return redirect("/admin-login")

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM companies")

    companies = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "companies.html",
        companies=companies
    )
@app.route("/add-job", methods=["GET", "POST"])
def add_job():

    if "admin_id" not in session:
        return redirect("/admin-login")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":

        job_title = request.form["job_title"]
        company_id = request.form["company_id"]
        category_id = request.form["category_id"]
        location = request.form["location"]
        salary = request.form["salary"]

        cursor.execute("""

INSERT INTO jobs
(job_title, company_id, category_id, location, salary)

VALUES(%s,%s,%s,%s,%s)

""", (
    job_title,
    company_id,
    category_id,
    location,
    salary
))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect("/admin-dashboard")

    cursor.execute("SELECT id, company_name FROM companies")
    companies = cursor.fetchall()

    cursor.execute("SELECT id, category_name FROM categories")
    categories = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
    "add_job.html",
    companies=companies,
    categories=categories
)
@app.route("/admin-jobs")
def admin_jobs():

    if "admin_id" not in session:
        return redirect("/admin-login")

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute("""

    SELECT

    jobs.*,
    companies.company_name,
    categories.category_name

    FROM jobs

    JOIN companies
    ON jobs.company_id = companies.id

    JOIN categories
    ON jobs.category_id = categories.id

    ORDER BY jobs.id DESC

    """)

    jobs = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "admin_jobs.html",
        jobs=jobs
    )

@app.route("/delete-job/<int:job_id>")
def delete_job(job_id):

    if "admin_id" not in session:
        return redirect("/admin-login")

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM jobs WHERE id=%s",
        (job_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/admin-jobs")
@app.route("/edit-job/<int:job_id>", methods=["GET", "POST"])
def edit_job(job_id):

    if "admin_id" not in session:
        return redirect("/admin-login")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":

        job_title = request.form["job_title"]
        location = request.form["location"]
        salary = request.form["salary"]

        cursor.execute("""

        UPDATE jobs

        SET job_title=%s,
            location=%s,
            salary=%s

        WHERE id=%s

        """, (
            job_title,
            location,
            salary,
            job_id
        ))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect("/admin-jobs")

    cursor.execute(
        "SELECT * FROM jobs WHERE id=%s",
        (job_id,)
    )

    job = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        "edit_job.html",
        job=job
    )
@app.route("/admin-applications")
def admin_applications():

    if "admin_id" not in session:
        return redirect("/admin-login")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""

    SELECT

    applications.id,
    applications.application_status,
    users.full_name,
    jobs.job_title,
    companies.company_name

    FROM applications

    JOIN users
    ON applications.user_id = users.id

    JOIN jobs
    ON applications.job_id = jobs.id

    JOIN companies
    ON jobs.company_id = companies.id

    """)

    applications = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "admin_applications.html",
        applications=applications
    )

@app.route("/update-status/<int:application_id>/<status>")
def update_status(application_id, status):

    if "admin_id" not in session:
        return redirect("/admin-login")

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE applications

        SET application_status=%s

        WHERE id=%s
        """,
        (status, application_id)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/admin-applications")

@app.route("/admin-users")
def admin_users():

    if "admin_id" not in session:
        return redirect("/admin-login")

    search=request.args.get("search","")

    conn=get_connection()

    cursor=conn.cursor(dictionary=True)

    if search:

        cursor.execute("""

        SELECT *

        FROM users

        WHERE full_name LIKE %s

        OR email LIKE %s

        ORDER BY id DESC

        """,(f"%{search}%",f"%{search}%"))

    else:

        cursor.execute("""

        SELECT *

        FROM users

        ORDER BY id DESC

        """)

    users=cursor.fetchall()

    cursor.close()

    conn.close()

    return render_template(
        "admin_users.html",
        users=users
    )

@app.route("/delete-user/<int:user_id>")
def delete_user(user_id):

    if "admin_id" not in session:
        return redirect("/admin-login")

    conn=get_connection()

    cursor=conn.cursor()

    cursor.execute(
        "DELETE FROM users WHERE id=%s",
        (user_id,)
    )

    conn.commit()

    cursor.close()

    conn.close()

    return redirect("/admin-users")


@app.route("/edit-company/<int:company_id>", methods=["GET","POST"])
def edit_company(company_id):

    if "admin_id" not in session:
        return redirect("/admin-login")

    conn=get_connection()
    cursor=conn.cursor(dictionary=True)

    if request.method=="POST":

        company_name=request.form["company_name"]
        location=request.form["location"]

        cursor.execute("""

        UPDATE companies

        SET company_name=%s,
            location=%s

        WHERE id=%s

        """,(company_name,location,company_id))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect("/companies")

    cursor.execute(
        "SELECT * FROM companies WHERE id=%s",
        (company_id,)
    )

    company=cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        "edit_company.html",
        company=company
    )


@app.route("/delete-company/<int:company_id>")
def delete_company(company_id):

    if "admin_id" not in session:
        return redirect("/admin-login")

    conn=get_connection()

    cursor=conn.cursor()

    cursor.execute(
        "DELETE FROM companies WHERE id=%s",
        (company_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/companies")

@app.route("/post-job", methods=["GET", "POST"])
def post_job():

    if request.method == "GET":
        return render_template("post_job_request.html")

    company_name = request.form["company_name"]
    hr_name = request.form["hr_name"]
    email = request.form["email"]
    phone = request.form["phone"]
    job_title = request.form["job_title"]
    location = request.form["location"]
    salary = request.form["salary"]
    experience = request.form["experience"]
    job_type = request.form["job_type"]
    description = request.form["description"]
    deadline = request.form["deadline"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

    INSERT INTO job_requests

    (
        company_name,
        hr_name,
        email,
        phone,
        job_title,
        location,
        salary,
        experience,
        job_type,
        description,
        deadline
    )

    VALUES
    (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)

    """, (

        company_name,
        hr_name,
        email,
        phone,
        job_title,
        location,
        salary,
        experience,
        job_type,
        description,
        deadline

    ))

    conn.commit()

    cursor.close()
    conn.close()

    flash(
        "Job request submitted successfully. Waiting for Admin Approval.",
        "success"
    )

    return redirect("/company-dashboard")

@app.route("/job-requests")
def job_requests():

    if "admin_id" not in session:
        return redirect("/admin-login")

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute("""

    SELECT *

    FROM job_requests

    ORDER BY id DESC

    """)

    jobs = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "job_requests.html",
        jobs=jobs
    )
@app.route("/approve-job/<int:request_id>")
def approve_job(request_id):

    if "admin_id" not in session:
        return redirect("/admin-login")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM job_requests WHERE id=%s",
        (request_id,)
    )

    job = cursor.fetchone()

    # Company exists?
    cursor.execute(
        "SELECT id FROM companies WHERE company_name=%s",
        (job["company_name"],)
    )

    company = cursor.fetchone()

    if company:
        company_id = company["id"]
    else:
        cursor.execute(
            """
            INSERT INTO companies
            (company_name, email, location, description)
            VALUES (%s,%s,%s,%s)
            """,
            (
                job["company_name"],
                job["email"],
                job["location"],
                "Recruiter Submitted Company"
            )
        )

        conn.commit()
        company_id = cursor.lastrowid

    # Default category = 1
    category_id = 1

    cursor.execute(
        """
        INSERT INTO jobs
        (
            company_id,
            category_id,
            job_title,
            location,
            salary,
            experience,
            job_type,
            description,
            deadline
        )

        VALUES
        (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            company_id,
            category_id,
            job["job_title"],
            job["location"],
            job["salary"],
            job["experience"],
            job["job_type"],
            job["description"],
            job["deadline"]
        )
    )

    cursor.execute(
        """
        UPDATE job_requests
        SET status='Approved'
        WHERE id=%s
        """,
        (request_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/job-requests")
@app.route("/reject-job/<int:request_id>")
def reject_job(request_id):

    if "admin_id" not in session:
        return redirect("/admin-login")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE job_requests
        SET status='Rejected'
        WHERE id=%s
        """,
        (request_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/job-requests")

@app.route("/explore-companies")
def explore_companies():

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM companies
        ORDER BY company_name
    """)

    companies = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "explore_companies.html",
        companies=companies
    )

@app.route("/company/<int:company_id>")
def company_jobs(company_id):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM companies WHERE id=%s",
        (company_id,)
    )

    company = cursor.fetchone()

    cursor.execute(
        """
        SELECT jobs.*, categories.category_name

        FROM jobs

        JOIN categories
        ON jobs.category_id = categories.id

        WHERE company_id=%s

        ORDER BY jobs.id DESC
        """,
        (company_id,)
    )

    jobs = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "company_jobs.html",
        company=company,
        jobs=jobs
    )

@app.route("/career-tips")
def career_tips():

    return render_template("career_tips.html")

@app.route("/about")
def about():

    return render_template("about.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():

    if request.method == "GET":
        return render_template("contact.html")

    name = request.form["name"]
    email = request.form["email"]
    subject = request.form["subject"]
    message = request.form["message"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO contact_messages
        (name, email, subject, message)

        VALUES (%s,%s,%s,%s)
        """,
        (name, email, subject, message)
    )

    conn.commit()

    cursor.close()
    conn.close()

    flash("Your message has been sent successfully.", "success")
    return redirect("/contact")     

@app.route("/job/<int:job_id>")
def job_details(job_id):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            jobs.*,
            companies.company_name,
            companies.website,
            companies.description AS company_description,
            categories.category_name

        FROM jobs

        JOIN companies
        ON jobs.company_id = companies.id

        JOIN categories
        ON jobs.category_id = categories.id

        WHERE jobs.id=%s
        """,
        (job_id,)
    )

    job = cursor.fetchone()

    cursor.close()
    conn.close()

    if not job:
        return "Job Not Found"

    return render_template(
        "job_details.html",
        job=job
    )

@app.route("/admin-contact-messages")
def admin_contact_messages():

    if "admin_id" not in session:
        return redirect("/admin-login")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM contact_messages
        ORDER BY created_at DESC
    """)

    messages = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "admin_contact_messages.html",
        messages=messages
    )

@app.route("/delete-contact-message/<int:message_id>")
def delete_contact_message(message_id):

    if "admin_id" not in session:
        return redirect("/admin-login")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM contact_messages
        WHERE id=%s
        """,
        (message_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/admin-contact-messages")

@app.route("/company-register", methods=["GET", "POST"])
def company_register():

    if request.method == "GET":
        return render_template("company_register.html")

    company_name = request.form["company_name"]
    email = request.form["email"]
    password = generate_password_hash(request.form["password"])
    website = request.form["website"]
    location = request.form["location"]
    description = request.form["description"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO companies
        (
            company_name,
            email,
            password,
            website,
            location,
            description
        )

        VALUES (%s,%s,%s,%s,%s,%s)

    """, (
        company_name,
        email,
        password,
        website,
        location,
        description
    ))

    conn.commit()

    cursor.close()
    conn.close()

    flash(
        "Company registered successfully. Please login.",
        "success"
    )

    return redirect("/company-login")

@app.route("/company-login", methods=["GET", "POST"])
def company_login():

    if request.method == "GET":
        return render_template("company_login.html")

    email = request.form["email"]
    password = request.form["password"]

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM companies
        WHERE email=%s
        """,
        (email,)
    )

    company = cursor.fetchone()

    cursor.close()
    conn.close()

    if company and check_password_hash(company["password"], password):

        session["company_id"] = company["id"]
        session["company_name"] = company["company_name"]

        flash("Welcome " + company["company_name"], "success")

        return redirect("/company-dashboard")

    flash("Invalid Email or Password", "danger")

    return redirect("/company-login")
@app.route("/company-logout")
def company_logout():

    session.pop("company_id", None)
    session.pop("company_name", None)

    flash("Logged out successfully.", "success")

    return redirect("/")

@app.route("/company-dashboard")
def company_dashboard():

    if "company_id" not in session:
        return redirect("/company-login")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    company_id = session["company_id"]

    # Total Jobs
    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM jobs
        WHERE company_id=%s
        """,
        (company_id,)
    )
    total_jobs = cursor.fetchone()["total"]

    # Pending Jobs
    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM jobs
        WHERE company_id=%s
        AND status='Pending'
        """,
        (company_id,)
    )
    pending_jobs = cursor.fetchone()["total"]

    # Approved Jobs
    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM jobs
        WHERE company_id=%s
        AND status='Active'
        """,
        (company_id,)
    )
    approved_jobs = cursor.fetchone()["total"]

    # Applications
    cursor.execute(
        """
        SELECT COUNT(*) AS total

        FROM applications

        JOIN jobs
        ON applications.job_id = jobs.id

        WHERE jobs.company_id=%s
        """,
        (company_id,)
    )

    total_applications = cursor.fetchone()["total"]

    cursor.close()
    conn.close()

    return render_template(
        "company_dashboard.html",
        total_jobs=total_jobs,
        pending_jobs=pending_jobs,
        approved_jobs=approved_jobs,
        total_applications=total_applications
    )

@app.route("/company-my-jobs")
def company_my_jobs():

    if "company_id" not in session:
        return redirect("/company-login")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM jobs
        WHERE company_id=%s
        ORDER BY id DESC
    """, (session["company_id"],))

    jobs = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "company_my_jobs.html",
        jobs=jobs
    )

@app.route("/company-applications/<int:job_id>")
def company_applications(job_id):

    if "company_id" not in session:
        return redirect("/company-login")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT

            applications.id,
            applications.application_status,
            applications.applied_at,

            users.full_name,
            users.email,
            users.phone,
            users.resume,

            jobs.job_title

        FROM applications

        JOIN users
        ON applications.user_id = users.id

        JOIN jobs
        ON applications.job_id = jobs.id

        WHERE
            applications.job_id=%s
            AND jobs.company_id=%s

        ORDER BY applications.applied_at DESC

    """, (job_id, session["company_id"]))

    applications = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "company_applications.html",
        applications=applications
    )

@app.route("/shortlist-application/<int:application_id>")
def shortlist_application(application_id):

    if "company_id" not in session:
        return redirect("/company-login")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE applications
        SET application_status='Shortlisted'
        WHERE id=%s
    """, (application_id,))

    conn.commit()

    cursor.close()
    conn.close()

    flash("Candidate shortlisted successfully.", "success")

    return redirect(request.referrer)

@app.route("/reject-application/<int:application_id>")
def reject_application(application_id):

    if "company_id" not in session:
        return redirect("/company-login")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE applications
        SET application_status='Rejected'
        WHERE id=%s
    """, (application_id,))

    conn.commit()

    cursor.close()
    conn.close()

    flash("Candidate rejected.", "warning")

    return redirect(request.referrer)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=DEBUG)