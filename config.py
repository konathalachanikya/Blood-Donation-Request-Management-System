import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "blood_donation_secret_key_2026"

    # ✅ Keep your existing DB path
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "database", "blood_donation.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ✅ Email Config (Gmail SMTP)
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False

    #  Enter your Gmail + App Password here
    MAIL_USERNAME = "lallupentakota1112@gmail.com"
    MAIL_PASSWORD = "xuqb mrns vvcj himw"

    #  Recommended Extra Settings
    MAIL_DEFAULT_SENDER = MAIL_USERNAME
