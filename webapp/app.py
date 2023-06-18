from flask import Flask, render_template, flash, jsonify, request, session, redirect, url_for
from scripts.forms import LoginForm, SignupForm
from flask_session import Session
import sqlite3 as sql

DATABASE = "test.db"

app = Flask(__name__)
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
@app.route('/')
def index():
    return redirect("/browse")

@app.route("/browse")
def browse(): 
    films = get_films() 
    if 'id' in session:
        return render_template('browse.html', id = session['id'], films = films)
    else:
        return render_template('browse.html', films = films)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        con = sql.connect(DATABASE)
        cur = con.cursor()
        email = form.email.data
        password = form.password.data
        cur.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cur.fetchone()
        if user and user[2] == password:
            session['id'] = user[0]
            return redirect('/')
        else:
            flash("Password or email is incorrect. Please try again", "error")
    return render_template('login.html', form = form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        confirmPassword = form.confirmPassword.data
        if password == confirmPassword:
            session['id'] = create_user(email, password)[0]
            return redirect("/")
        else:
            flash("Passwords do not match", "error")
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{error}", 'error')
    return render_template('signup.html', form = form)

@app.route("/account")
def account():
    user = get_user(session['id'])
    return render_template("account.html", user=user)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route('/<string:title>')
def film_details(title):
    con = sql.connect(DATABASE)
    cur = con.cursor()
    cur.execute("SELECT * FROM films WHERE title = ?", (title,))
    film = cur.fetchone()
    return render_template("film_details.html", film = film)

@app.route('/search', methods=['GET', 'POST'])
def search():
    query = request.args.get('query')
    return render_template("search.html", query = query)
    
@app.route('/search-results', methods=['GET', 'POST'])
def search_results():
    query = request.args.get('query')
    con = sql.connect(DATABASE)
    cur = con.cursor()
    cur.execute("SELECT * FROM films WHERE title LIKE ? OR genre LIKE ? OR dir LIKE ?", (('%' + query + '%'), ('%' + query + '%'), ('%' + query + '%')))
    results = cur.fetchall()
    return render_template("search_results.html", results = results)

def get_user(id):
    con = sql.connect(DATABASE)
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (id,))
    user = cur.fetchone()
    con.close()
    return user

def create_user(email, password):
    con = sql.connect(DATABASE)
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, password TEXT)")
    cur.execute("INSERT INTO users(email, password) VALUES(?, ?)", (email, password))
    con.commit()
    cur.execute("SELECT id FROM users WHERE email = ?", (email,))
    user = cur.fetchone()
    con.close()
    return user

def get_films():
    con = sql.connect(DATABASE)
    cur = con.cursor()
    cur.execute("SELECT * FROM films")
    films = cur.fetchall()
    return films

if __name__ == '__main__':
        app.secret_key = "app.secret_key"
        app.run(debug = True)