from flask import render_template, Blueprint, request, redirect, url_for, flash
from flask_login import logout_user, login_user, current_user
from models import authenticate, get_user_by_username, add_user, create_welcome_note

auth_blueprint = Blueprint('auth', __name__,
                           template_folder='templates',
                           url_prefix='/authentication')


@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        form = request.form
        username = form['username']
        password = form['password'].encode('utf-8')
        user = get_user_by_username(username)
        if user is not None:
            if authenticate(user, password):
                user = get_user_by_username(username)
                login_user(user)
                flash(f'Logged in successfully for {current_user.username}.', category='success')
                return redirect(url_for('home'))
            flash(f'Username or Password are incorrect.', category='error')
        else:
            flash(f'"{username}" is not registered, try signing up.', category='error')

    return render_template('login.j2')


@auth_blueprint.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        form = request.form
        user = add_user(username=form['username'],
                        password=form['password'].encode('utf-8'),
                        email=form['email'])
        if user is not None:
            create_welcome_note(user)
            return redirect(url_for('auth.login'))
        flash(f'Username and email needs to be unique.', category='error')
    return render_template('signup.j2')


@auth_blueprint.route('/logout')
def logout():
    flash(f'successfully logged out for {current_user.username}.', category='success')
    logout_user()
    return redirect(url_for('auth.login'))
