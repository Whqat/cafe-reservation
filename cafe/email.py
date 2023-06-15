from flask_mail import Message
from flask import redirect, flash, url_for
from cafe import app, mail, db
from smtplib import SMTPServerDisconnected, SMTPAuthenticationError


def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=app.config["MAIL_DEFAULT_SENDER"],
    )
    print(app.config["MAIL_DEFAULT_SENDER"])
    try:
        mail.send(msg)
    except SMTPAuthenticationError:
        db.session.rollback()
        flash("Error connecting to server, please check your conncetion and try again.", "danger")
        return redirect(url_for('register'))