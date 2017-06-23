import os
import sqlite3
from flask import Flask, g, render_template, session, abort, request, flash, redirect, url_for

app = Flask(__name__)  #Create application instance
app.config.from_object(__name__)  # load config from this file, flaskr.py

# Load default config and ocerride config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to a specific database"""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is not one already stored
    in the application context
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request"""
    if hasattr(g,'sqlite_db'):
        g.sqlite_db.close()


def init_db():
    """Runs t5he schema creation script"""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Initialises the database"""
    init_db()
    print('Initialised the database.')

@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('SELECT  title, text FROM entries ORDER BY id DESC ')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('INSERT INTO entries (title, text) VALUES (?, ?)', [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was posted sucessfully')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    print(request.method)
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('you were logged out')
    return redirect(url_for('show_entries'))

# to let us run from pyCharm.
if __name__ == '__main__':
    app.run()