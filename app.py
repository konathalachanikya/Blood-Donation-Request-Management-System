from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message

from config import Config
from extensions import db, login_manager, mail
from models import User, Donor, Volunteer, BloodRequest, Assignment

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager.init_app(app)
mail.init_app(app)

login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ============================================================
# ✅ EMAIL HELPER FUNCTION
# ============================================================
def send_email(to_email, subject, body):
    try:
        if not to_email:
            return

        msg = Message(
            subject=subject,
            recipients=[to_email],
            body=body
        )
        mail.send(msg)
        print(f"✅ Email sent to {to_email}")

    except Exception as e:
        print("❌ Email sending failed:", str(e))


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")  # donor/volunteer/requester

        if not name or not email or not password or not role:
            flash("All fields are required!", "danger")
            return redirect(url_for("register"))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please login.", "warning")
            return redirect(url_for("login"))

        hashed_password = generate_password_hash(password)

        new_user = User(
            name=name,
            email=email,
            password_hash=hashed_password,
            role=role
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password!", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")


# ---------------- DASHBOARD REDIRECT ----------------
@app.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "admin":
        return redirect(url_for("admin_dashboard"))
    elif current_user.role == "donor":
        return redirect(url_for("donor_dashboard"))
    elif current_user.role == "volunteer":
        return redirect(url_for("volunteer_dashboard"))
    elif current_user.role == "requester":
        return redirect(url_for("requester_dashboard"))
    else:
        flash("Invalid role detected!", "danger")
        return redirect(url_for("logout"))


# ============================================================
# ROLE DASHBOARDS
# ============================================================

@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        flash("Access denied!", "danger")
        return redirect(url_for("dashboard"))

    total_users = User.query.count()
    total_donors = Donor.query.count()
    total_volunteers = Volunteer.query.count()
    total_requests = BloodRequest.query.count()

    pending_requests = BloodRequest.query.filter_by(status="Pending").count()
    approved_requests = BloodRequest.query.filter_by(status="Approved").count()
    waiting_requests = BloodRequest.query.filter_by(status="Waiting").count()
    completed_requests = BloodRequest.query.filter_by(status="Completed").count()

    recent_requests = BloodRequest.query.order_by(BloodRequest.requested_at.desc()).limit(5).all()

    return render_template(
        "admin/admin_dashboard.html",
        total_users=total_users,
        total_donors=total_donors,
        total_volunteers=total_volunteers,
        total_requests=total_requests,
        pending_requests=pending_requests,
        approved_requests=approved_requests,
        waiting_requests=waiting_requests,
        completed_requests=completed_requests,
        recent_requests=recent_requests
    )


@app.route("/donor/dashboard")
@login_required
def donor_dashboard():
    return render_template("donor/donor_dashboard.html")


@app.route("/volunteer/dashboard")
@login_required
def volunteer_dashboard():
    return render_template("volunteer/volunteer_dashboard.html")


@app.route("/requester/dashboard")
@login_required
def requester_dashboard():
    return render_template("requester/requester_dashboard.html")


# ============================================================
# DONOR PROFILE
# ============================================================
@app.route("/donor/profile", methods=["GET", "POST"])
@login_required
def donor_profile():
    if current_user.role != "donor":
        flash("Access denied!", "danger")
        return redirect(url_for("dashboard"))

    donor = Donor.query.filter_by(user_id=current_user.id).first()

    if request.method == "POST":
        blood_group = request.form.get("blood_group")
        phone = request.form.get("phone")
        city = request.form.get("city")
        pincode = request.form.get("pincode")
        availability = request.form.get("availability")  # Active / Inactive

        availability_status = True if availability == "Active" else False

        if donor:
            donor.blood_group = blood_group
            donor.phone = phone
            donor.city = city
            donor.pincode = pincode
            donor.availability = availability_status
        else:
            donor = Donor(
                user_id=current_user.id,
                blood_group=blood_group,
                phone=phone,
                city=city,
                pincode=pincode,
                availability=availability_status
            )
            db.session.add(donor)

        db.session.commit()
        flash("Donor profile updated successfully!", "success")
        return redirect(url_for("donor_dashboard"))

    return render_template("donor/donor_profile.html", donor=donor)


# ============================================================
# VOLUNTEER PROFILE
# ============================================================
@app.route("/volunteer/profile", methods=["GET", "POST"])
@login_required
def volunteer_profile():
    if current_user.role != "volunteer":
        flash("Access denied!", "danger")
        return redirect(url_for("dashboard"))

    volunteer = Volunteer.query.filter_by(user_id=current_user.id).first()

    if request.method == "POST":
        phone = request.form.get("phone")
        city = request.form.get("city")
        status = request.form.get("status")  # Active / Inactive

        if volunteer:
            volunteer.phone = phone
            volunteer.city = city
            volunteer.status = status
        else:
            volunteer = Volunteer(
                user_id=current_user.id,
                phone=phone,
                city=city,
                status=status
            )
            db.session.add(volunteer)

        db.session.commit()
        flash("Volunteer profile updated successfully!", "success")
        return redirect(url_for("volunteer_dashboard"))

    return render_template("volunteer/volunteer_profile.html", volunteer=volunteer)


# ============================================================
# REQUESTER: NEW BLOOD REQUEST
# ============================================================
@app.route("/requester/new-request", methods=["GET", "POST"])
@login_required
def new_request():
    if current_user.role != "requester":
        flash("Access denied!", "danger")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        patient_name = request.form.get("patient_name")
        contact_number = request.form.get("contact_number")
        blood_group_needed = request.form.get("blood_group_needed")
        city = request.form.get("city")
        pincode = request.form.get("pincode")

        new_req = BloodRequest(
            requester_user_id=current_user.id,
            patient_name=patient_name,
            contact_number=contact_number,
            blood_group_needed=blood_group_needed,
            city=city,
            pincode=pincode,
            status="Pending"
        )

        db.session.add(new_req)
        db.session.commit()

        flash("Blood request submitted successfully!", "success")
        return redirect(url_for("requester_dashboard"))

    return render_template("requester/new_request.html")


# ============================================================
# ✅ REQUESTER TRACKING PAGE (MY REQUESTS)
# ============================================================
@app.route("/requester/my-requests")
@login_required
def requester_my_requests():
    if current_user.role != "requester":
        flash("Access denied!", "danger")
        return redirect(url_for("dashboard"))

    my_requests = BloodRequest.query.filter_by(
        requester_user_id=current_user.id
    ).order_by(BloodRequest.requested_at.desc()).all()

    return render_template("requester/my_requests.html", my_requests=my_requests)


# ============================================================
# STEP 5: ADMIN REQUEST MANAGEMENT + AUTOMATED DONOR MATCHING
# ============================================================
def get_matching_donors(blood_group_needed, city, pincode):
    donors = Donor.query.filter_by(availability=True).all()

    matched = []
    for d in donors:
        if d.blood_group == blood_group_needed:
            score = 0
            if d.city.lower() == city.lower():
                score += 2
            if d.pincode == pincode:
                score += 3
            matched.append((d, score))

    matched.sort(key=lambda x: x[1], reverse=True)
    return [m[0] for m in matched]


@app.route("/admin/requests")
@login_required
def admin_requests():
    if current_user.role != "admin":
        flash("Access denied!", "danger")
        return redirect(url_for("dashboard"))

    requests_list = BloodRequest.query.order_by(BloodRequest.requested_at.desc()).all()
    return render_template("admin/admin_requests.html", requests_list=requests_list)


@app.route("/admin/request/<int:request_id>")
@login_required
def admin_request_details(request_id):
    if current_user.role != "admin":
        flash("Access denied!", "danger")
        return redirect(url_for("dashboard"))

    req = BloodRequest.query.get_or_404(request_id)

    matched_donors = get_matching_donors(req.blood_group_needed, req.city, req.pincode)
    volunteers = Volunteer.query.filter_by(status="Active").all()

    return render_template(
        "admin/request_details.html",
        req=req,
        matched_donors=matched_donors,
        volunteers=volunteers
    )


@app.route("/admin/request/<int:request_id>/approve")
@login_required
def approve_request(request_id):
    if current_user.role != "admin":
        flash("Access denied!", "danger")
        return redirect(url_for("dashboard"))

    req = BloodRequest.query.get_or_404(request_id)
    req.status = "Approved"
    db.session.commit()

    # ✅ Email Notification to matched donors (OPTIONAL)
    matched_donors = get_matching_donors(req.blood_group_needed, req.city, req.pincode)

    for d in matched_donors:
        user = User.query.get(d.user_id)
        if user and user.email:
            send_email(
                to_email=user.email,
                subject="BloodCare+ | Urgent Blood Requirement Match Found",
                body=f"""
Hello {user.name},

A blood request has been approved and matches your blood group ({d.blood_group}).

Patient: {req.patient_name}
City: {req.city}
Pincode: {req.pincode}
Contact: {req.contact_number}

Please login to BloodCare+ for more details.

Thank you,
BloodCare+ Team
"""
            )

    flash("Request approved successfully!", "success")
    return redirect(url_for("admin_request_details", request_id=request_id))


# ============================================================
# STEP 6: VOLUNTEER ASSIGNMENT + TASK MANAGEMENT + EMAIL
# ============================================================
@app.route("/admin/request/<int:request_id>/assign-volunteer", methods=["POST"])
@login_required
def assign_volunteer(request_id):
    if current_user.role != "admin":
        flash("Access denied!", "danger")
        return redirect(url_for("dashboard"))

    volunteer_id = request.form.get("volunteer_id")
    req = BloodRequest.query.get_or_404(request_id)

    if not volunteer_id:
        flash("Please select a volunteer!", "warning")
        return redirect(url_for("admin_request_details", request_id=request_id))

    existing_assignment = Assignment.query.filter_by(request_id=req.request_id).first()
    if existing_assignment:
        flash("Volunteer already assigned for this request!", "warning")
        return redirect(url_for("admin_request_details", request_id=request_id))

    new_assign = Assignment(
        request_id=req.request_id,
        volunteer_id=int(volunteer_id),
        task_status="Assigned"
    )
    db.session.add(new_assign)

    req.status = "Waiting"
    db.session.commit()

    # ✅ Email Notification to Volunteer
    volunteer = Volunteer.query.get(int(volunteer_id))
    if volunteer:
        volunteer_user = User.query.get(volunteer.user_id)
        if volunteer_user and volunteer_user.email:
            send_email(
                to_email=volunteer_user.email,
                subject="BloodCare+ | New Volunteer Task Assigned",
                body=f"""
Hello {volunteer_user.name},

You have been assigned a new blood request task.

Request ID: {req.request_id}
Patient Name: {req.patient_name}
Blood Group Needed: {req.blood_group_needed}
City: {req.city}
Pincode: {req.pincode}
Contact Number: {req.contact_number}

Please login and check your tasks dashboard.

Thank you,
BloodCare+ Team
"""
            )

    flash("Volunteer assigned successfully!", "success")
    return redirect(url_for("admin_request_details", request_id=request_id))


@app.route("/volunteer/tasks")
@login_required
def volunteer_tasks():
    if current_user.role != "volunteer":
        flash("Access denied!", "danger")
        return redirect(url_for("dashboard"))

    volunteer = Volunteer.query.filter_by(user_id=current_user.id).first()

    if not volunteer:
        flash("Please complete your volunteer profile first!", "warning")
        return redirect(url_for("volunteer_profile"))

    tasks = Assignment.query.filter_by(volunteer_id=volunteer.volunteer_id).all()
    return render_template("volunteer/volunteer_tasks.html", tasks=tasks)


@app.route("/volunteer/task/<int:assignment_id>/update", methods=["POST"])
@login_required
def update_task_status(assignment_id):
    if current_user.role != "volunteer":
        flash("Access denied!", "danger")
        return redirect(url_for("dashboard"))

    assignment = Assignment.query.get_or_404(assignment_id)
    new_status = request.form.get("task_status")

    assignment.task_status = new_status

    if new_status == "Completed":
        assignment.request.status = "Completed"

        req = assignment.request
        requester = User.query.get(req.requester_user_id)

        if requester and requester.email:
            send_email(
                to_email=requester.email,
                subject="BloodCare+ | Your Blood Request is Completed",
                body=f"""
Hello {requester.name},

Your blood request has been successfully completed.

Request ID: {req.request_id}
Patient: {req.patient_name}
Blood Group Needed: {req.blood_group_needed}
City: {req.city}

Thank you for using BloodCare+.

Regards,
BloodCare+ Team
"""
            )

    db.session.commit()
    flash("Task status updated!", "success")
    return redirect(url_for("volunteer_tasks"))


# ============================================================
# ✅ ADMIN MANAGE DONORS PAGE
# ============================================================
@app.route("/admin/donors")
@login_required
def admin_donors():
    if current_user.role != "admin":
        flash("Access denied!", "danger")
        return redirect(url_for("dashboard"))

    donors = Donor.query.order_by(Donor.donor_id.desc()).all()
    return render_template("admin/admin_donors.html", donors=donors)


# ============================================================
# ✅ ADMIN MANAGE VOLUNTEERS PAGE
# ============================================================
@app.route("/admin/volunteers")
@login_required
def admin_volunteers():
    if current_user.role != "admin":
        flash("Access denied!", "danger")
        return redirect(url_for("dashboard"))

    volunteers = Volunteer.query.order_by(Volunteer.volunteer_id.desc()).all()
    return render_template("admin/admin_volunteers.html", volunteers=volunteers)


# ---------------- LOGOUT ----------------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "info")
    return redirect(url_for("home"))


# ---------------- ADMIN CREATION ----------------
def create_admin():
    admin_email = "admin@bloodcare.com"
    admin_password = "Admin@123"

    existing_admin = User.query.filter_by(email=admin_email).first()
    if not existing_admin:
        admin_user = User(
            name="Admin",
            email=admin_email,
            password_hash=generate_password_hash(admin_password),
            role="admin"
        )
        db.session.add(admin_user)
        db.session.commit()
        print("✅ Admin account created successfully!")
        print("📧 Email:", admin_email)
        print("🔑 Password:", admin_password)
    else:
        print("ℹ️ Admin account already exists!")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        create_admin()
    app.run(debug=True)
