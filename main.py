from flask import Flask, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user, login_required

from auth.auth import auth_blueprint
from config import SECRET_KEY, db
from edit.edit import edit_blueprint
from models import (add_note, get_all_colors, get_all_user_notes,
                    get_color_by_id, get_user_by_id)


main = Flask(__name__)

main.secret_key = SECRET_KEY
main.register_blueprint(auth_blueprint)
main.register_blueprint(edit_blueprint)

login_manager = LoginManager()
login_manager.init_app(main)


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('auth.login'))


@login_manager.user_loader
def load_user(user_id: str):
    return get_user_by_id(int(user_id))


@main.before_request
def before_request():
    db.close()
    db.connect()


@main.teardown_request
def close_connection(_):
    return db.close()


@main.route('/', methods=['POST', 'GET'])
@login_required
def home():
    notes = get_all_user_notes(current_user.id)
    if request.method == 'POST':
        form = request.form
        add_note(user_id=current_user.id, **form)

    return render_template(
        'index.j2',
        notes=notes,
        colors=get_all_colors(),
        color_by_id=get_color_by_id
    )
