from flask import redirect, render_template, url_for
from flask_login import current_user, login_user, logout_user

from finance import db
from finance.auth import bp
from finance.auth.forms import LoginForm, RegistrationForm
from finance.auth.models import User
from finance.wallet.models import Payday, Wallet


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('wallet.wallet'))

    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)

        wallet = Wallet(user=user, balance=0)
        db.session.add(wallet)

        payday = Payday(date=form.payday.data, wallet=wallet)
        db.session.add(payday)

        db.session.commit()

        return redirect(url_for('auth.login'))

    context = {
        'pagetype': 'register',
        'form': form}

    return render_template('login_or_register.html', **context)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('wallet.wallet'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            return redirect(url_for('auth.login'))

        login_user(user)
        return redirect(url_for('wallet.wallet'))

    context = {
        'pagetype': 'login',
        'form': form}

    return render_template('login_or_register.html', **context)


@bp.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
