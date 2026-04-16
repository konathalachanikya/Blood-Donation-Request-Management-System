from flask_mail import Message
from flask import current_app
from extensions import mail

def send_email(subject, recipients, body):
    try:
        msg = Message(
            subject=subject,
            recipients=recipients,
            body=body,
            sender=current_app.config["MAIL_USERNAME"]
        )
        mail.send(msg)
        return True
    except Exception as e:
        print("❌ Email Error:", e)
        return False
