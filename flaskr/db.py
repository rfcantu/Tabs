import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    '''
    open_resource(): opens a file relative to the flaskr package
    get_db(): returns a database connection, which is used to execute the commands read from the file
    '''
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf-8'))


# Defines a command line command called init-db that calls the init_db function and shows a success message
@click.command('init-db')
@with_appcontext
def init_db_command():
    ''' Clear the existing data and create new tables '''
    init_db()
    click.echo('Initialized the database.')


'''
Register close_db and init_db_command functions with the app

app.teardown_appcontext(): tells Flask to call that function when cleaning up after returning response
app.cli.add_command(): adds a new command that can be called with the flask command
'''
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)