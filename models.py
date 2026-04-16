from datetime import datetime
from flask_login import UserMixin
from extensions import db

class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    password_hash = db.Column(db.String(255), nullable=False)

    # roles: admin, donor, volunteer, requester
    role = db.Column(db.String(30), nullable=False, default="donor")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Donor(db.Model):
    __tablename__ = "donors"

    donor_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    blood_group = db.Column(db.String(10), nullable=False)
    phone = db.Column(db.String(20), nullable=False)

    city = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)

    availability = db.Column(db.Boolean, default=True)
    last_donated_date = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", backref=db.backref("donor_profile", uselist=False))



class Volunteer(db.Model):
    __tablename__ = "volunteers"

    volunteer_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    phone = db.Column(db.String(20), nullable=False)
    city = db.Column(db.String(100), nullable=False)

    # status: Active / Inactive
    status = db.Column(db.String(20), default="Active")

    user = db.relationship("User", backref=db.backref("volunteer_profile", uselist=False))


class BloodRequest(db.Model):
    __tablename__ = "blood_requests"

    request_id = db.Column(db.Integer, primary_key=True)
    requester_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    patient_name = db.Column(db.String(120), nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)

    blood_group_needed = db.Column(db.String(10), nullable=False)

    city = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)

    # status: Pending / Approved / Waiting / Completed
    status = db.Column(db.String(20), default="Pending")

    requested_at = db.Column(db.DateTime, default=datetime.utcnow)

    requester = db.relationship("User", backref="requests")


class Assignment(db.Model):
    __tablename__ = "assignments"

    assignment_id = db.Column(db.Integer, primary_key=True)

    request_id = db.Column(db.Integer, db.ForeignKey("blood_requests.request_id"), nullable=False)
    volunteer_id = db.Column(db.Integer, db.ForeignKey("volunteers.volunteer_id"), nullable=False)

    task_status = db.Column(db.String(30), default="Assigned")
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)

    request = db.relationship("BloodRequest", backref="assignments")
    volunteer = db.relationship("Volunteer", backref="assignments")

