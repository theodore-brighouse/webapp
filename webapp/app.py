from flask import Flask, render_template, flash, request, session, redirect, url_for
from forms import LoginForm, SignupForm
from flask_session import Session
import sqlite3 as sql

DATABASE = "test.db"

app = Flask(__name__)
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
@app.route('/')
def index():
    if 'id' in session:
        return render_template('index.html', id = session['id'])
    else:
        return render_template('index.html')

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
    cur.execute(("SELECT id FROM users WHERE email = ?"), (email,))
    user = cur.fetchone()
    con.close()
    return user


if __name__ == '__main__':
        app.secret_key = "app.secret_key"
        app.run(debug = True)