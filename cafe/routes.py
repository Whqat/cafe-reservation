from flask import render_template, session, redirect, url_for, flash, current_app
from cafe import app, db
from cafe.models import User, Reservation
from cafe.forms import RegisterForm, LoginForm, ReserveForm
from sqlalchemy.exc import OperationalError
from cafe.token import generate_token, confirm_token
from cafe.email import send_email
import functools
from smtplib import SMTPServerDisconnected, SMTPAuthenticationError

@app.before_first_request
def create_tables():
    try:
        db.create_all()
    except OperationalError:
        return '<h1>Connection to database failed, please check your connection and try again</h1>'

        


def login_required(route):
    @functools.wraps(route)
    def route_wrapper(*args, **kwargs):
        if session.get("email") is None:
            flash("You need to log-in before accessing this page", category="success")
            return redirect(url_for("login"))
        return route(*args, **kwargs)

    return route_wrapper

@app.route('/')
def index():
    if session.get("email"):
        user = User.query.filter_by(email=session.get("email")).first()
    else:
        user = False
    return render_template('index.html', user=user)

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/reserve', methods=['GET', 'POST'])
@login_required
def reserve():
    user = User.query.filter_by(email=session.get("email")).first()
    if user.confirmed == False:
        flash("Please confirm your email before accessing this page", category="success")
        return redirect(url_for('index'))
    user = User.query.filter_by(email=session.get("email")).first()
    form = ReserveForm()
    if form.validate_on_submit():
        try:
            db.create_all()
            reservation = Reservation(date=form.date.data, time=form.time.data, owner=user.id)
            db.session.add(reservation)
            db.session.commit()
            print(reservation.owner, reservation.reserved_user)
            flash(f"Reservation successful for {user.name} on {reservation.date} at {reservation.time}", category="success")
            return redirect(url_for('index'))
        except OperationalError:
            db.session.rollback()
            return '<h1>Connection to database failed, please check your connection and try again</h1>'
    return render_template('reserve.html', form=form)
    

@app.route('/register', methods=['GET', 'POST'])
def register():
    resend = 0
    form = RegisterForm()
    if form.validate_on_submit():
        db.create_all()
        exists = User.query.filter_by(email=form.email.data).first()
        if exists:
            flash("Email address is in-use, please use another one.", category="success")
            redirect(url_for('register'))
        else:
            try:
                db.create_all()
                user = User(name=form.name.data, email=form.email.data, password=form.password.data)
                db.session.add(user)
                db.session.commit()
                token = generate_token(user.email)
                confirm_url = url_for('confirm_email', token=token, _external=True)
                html = render_template("confirm_email.html", confirm_url=confirm_url)
                subject = "Please confirm your email"
                try:
                    send_email(user.email, subject, html)
                except SMTPServerDisconnected or SMTPAuthenticationError:
                    db.session.rollback()
                    flash("Error connecting to server, please check your conncetion and try again.", "success")
                    return redirect(url_for('register'))
                session["user_id"] = user.id
                session['email'] = user.email
                resend = 1
                flash("A confirmation email has been sent to your address.", category="danger")
                return redirect(url_for('index'))
            except OperationalError:
                db.session.rollback()
                return "<h1>Connection to database failed, please check your connection and try again.</h1>"
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():

    if session.get('email'):
        return redirect(url_for('index'))

    form = LoginForm()

    
    if form.validate_on_submit():
        try:
            user= User.query.filter_by(email=form.email.data).first()
        except OperationalError:
            return "<h1>Connection to database failed, please check your connection and try again.</h1>"

        if not user:
            flash("Login credentials incorrect", category="success")
            return redirect(url_for('login'))

        if user.check_password_correction(attempted_password=form.password.data):
            session["user_id"] = user.id
            session["email"] = user.email
            flash("Log-in successful", category="success")
            return redirect(url_for('index'))
        else:
            flash("Login credentials incorrect", category='success')
            return redirect(url_for('login'))
    return render_template('login.html', form=form)

@app.get('/logout')
def logout():
    session.clear()
    flash("Log-out successful", category="success")
    return redirect(url_for('index'))

@app.route('/confirm/<token>', methods=["GET", "POST"])
@login_required
def confirm_email(token):
    try:
        user = User.query.filter_by(email=session.get("email")).first_or_404()
    except OperationalError:
        return "<h1>Connection to database failed, please check your connection and try again.</h1>"

    if user.confirmed:
        resend = 0
        flash("Account is already confirmed", "success")
        return redirect(url_for("index", resend=resend))
    email = confirm_token(token)
    if user.email == email:
        try:
            user.confirmed = True
            db.session.commit()
        except OperationalError:
            db.session.rollback()
            return "<h1>Connection to database failed, please check your connection and try again.</h1>"
        resend = 0
        flash("Your email has been confirmed!", "success")
        return redirect(url_for('index'))
    else:
        flash("The confirmation link is invalid or has expired", "success")
    return redirect(url_for('index'))

@app.route("/resend")
@login_required
def resend_confirmation():
    try:
        user = User.query.filter_by(email=session.get("email")).first()
        print(user.email)
    except OperationalError:
        return "<h1>Connection to database failed, please check your connection and try again.</h1>"

    if user.confirmed:
        flash("Your account has already been confirmed.", "success")
        return redirect(url_for("home"))
    token = generate_token(user.email)
    confirm_url = url_for("confirm_email", token=token, _external=True)
    html = render_template("confirm_email.html", confirm_url=confirm_url)
    subject = "Please confirm your email"
    send_email(user.email, subject, html)
    flash("A new confirmation email has been sent.", "success")
    return redirect(url_for("index"))

with app.app_context():
    db.create_all()
    