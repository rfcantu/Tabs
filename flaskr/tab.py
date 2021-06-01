from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('tab', __name__)

@bp.route('/')
def index():
    db = get_db()
    tabs = db.execute(
        'SELECT p.id, title, body, created, artist_id, username'
        ' FROM tabs p JOIN user u ON p.artist_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('tab/index.html', tabs=tabs)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO tabs (title, body, artist_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('tab.index'))
    return render_template('tab/create.html')

def get_tab(id, check_artist=True):
    tab = get_db().execute(
        'SELECT p.id, title, body, created, artist_id, username'
        ' FROM tabs p JOIN user u ON p.artist_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if tab is None:
        abort(404, f"Tab id {id} does not exist")
    if check_artist and tab['artist_id'] != g.user['id']:
        abort(403)
    return tab

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    tab = get_tab(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE tabs SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('tab.index'))
    return render_template('tab/update.html', tab=tab)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_tab(id)
    db = get_db()
    db.execute('DELETE FROM tabs WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('tab.index'))