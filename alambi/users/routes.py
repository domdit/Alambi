from flask import render_template, request, flash, redirect, url_for, Blueprint
from flask_login import logout_user, current_user, login_user
from flask_mail import Message
from alambi import bcrypt, db, mail
from alambi.models import User, GeneralSettings, Theme
from alambi.users.forms import InitializationForm, Login, RequestResetForm, ResetPassword


users = Blueprint('users', __name__)


@users.route("/initialize", methods=['GET', 'POST'])
def init():

    form = InitializationForm()

    if request.method == 'POST':
        if form.validate_on_submit:

            admin = User.query.first()
            admin.email = form.email.data
            admin.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

            settings = GeneralSettings.query.first()
            settings.name = form.blog_name.data
            settings.author = form.author_name.data
            settings.post_count = 3
            settings.excerpt = True
            settings.comments = True
            settings.init = True

            db.session.commit()
            return redirect(url_for('main.index'))

    return render_template('initialize.html', title="Welcome to Alambi", form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():
    theme_settings = Theme.query.filter_by(selected=True).first()

    form = Login()
    if current_user.is_authenticated:
        return redirect(url_for('admin.settings'))
    if request.method == 'POST':
        if form.validate_on_submit:
            user = User.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('admin.settings'))
            else:
                flash('Login Unsuccessful. Please check your email and password', 'danger')
                return redirect(url_for('users.login'))

    return render_template('login.html', form=form, title='Alambi - Admin Login', theme_settings=theme_settings)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('users.login'))


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    theme_settings = Theme.query.filter_by(selected=True).first()

    form = RequestResetForm()
    if current_user.is_authenticated:
        return redirect(url_for('admin.settings'))

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        reset_email(user)
        flash('An email has been sent with instructions to reset your password', 'info')
        return redirect(url_for('users.login'))

    return render_template('reset_request.html', title="Alambi - Reset Password", form=form, theme_settings=theme_settings)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    theme_settings = Theme.query.filter_by(selected=True).first()

    form = ResetPassword()
    if current_user.is_authenticated:
        return redirect(url_for('admin.settings'))

    user = User.verify_reset_token(token)

    if user is None:
        flash('Your verification token has expired or is invalid, Try again.', 'danger')
        return redirect(url_for('users.reset_request'))

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('You have successfully updated your password!', 'success')
        return redirect(url_for('users.login'))

    return render_template('users.reset_token.html', title="Alambi - Reset Password", form=form, theme_settings=theme_settings)


def reset_email(user):
    blog = GeneralSettings.query.first()
    token = user.get_reset_token()
    msg = Message('Reset Password - ' + blog.name, sender='noreply@alambi.com', recipients=[user.email])
    token_link = url_for('users.reset_password', token=token, _external=True)
    msg.body = "To reset your password, click the following link: " + token_link
    mail.send(msg)
