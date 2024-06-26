import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verif_password = request.form['verif_password']
        email = request.form['email']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif verif_password != password:
            error = 'No coinciden las contraseñas'  
        elif not email:
            error = 'Necesito email.'      

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password, verif_password, email) VALUES (?, ?, ?, ?)",
                    (username, generate_password_hash(password), verif_password, email),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Usuario Incorrecto.'
        elif not check_password_hash(user['password'], password):
            error = 'Contraseña Incorrecta.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))        

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

@bp.route('/<int:id>/modEmail', methods=('GET', 'POST'))
@login_required
def modEmail():
    email = request.form['email']

    if request.method == 'POST':
        email = request.form['email']
        error = None

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                """"UPDATE user
                        SET email = ?
                        WHERE id = ?;
                        """,
                (email)
            )
            db.commit()
            return redirect(url_for('auth.modEmail'))

    return render_template('auth/modEmail.html', email = email)