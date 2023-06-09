from flask import Flask, render_template, flash, request, session, redirect, url_for
from static.forms import LoginForm, SignupForm
from flask_session import Session
import sqlite3 as sql, difflib, random, requests

DATABASE = "database.db"
app = Flask(__name__)
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
@app.route('/')
def index():
    return redirect("/browse")

@app.route("/admin")
def admin():
    if 'id' in session and session['id'] == 'admin':
        return render_template('admin.html') 
    return redirect("/")

@app.route("/admin/edit-films")
def edit_films():
    if 'id' in session and session['id'] == 'admin':
        return render_template('edit_films.html')
    return redirect("/")

@app.route("/browse")
def browse(): 
    func = 'browse()'
    if 'id' in session:
        con = sql.connect(DATABASE)
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE user_id = ?", (session['id'],))
        account = cur.fetchone()
        return render_template('index.html', func = func, account = account)
    else:
        return render_template('index.html', func = func)

@app.route("/browse-content", methods = ['GET', 'POST'])
def browse_content():
    return render_template('browse.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        con = sql.connect(DATABASE)
        cur = con.cursor()
        email = form.email.data
        password = form.password.data
        if password == '1234admin' and email == 'admin@admin.com':
            session['id'] = 'admin'
            return redirect('/')
        cur.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cur.fetchone()
        con.close()
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

@app.route("/watchlist")
def watchlist():
    if 'id' in session:
        con = sql.connect(DATABASE)
        cur = con.cursor()
        cur.execute("""
                    SELECT * FROM films 
                    JOIN watchlist ON watchlist.film_id = films.film_id 
                    WHERE watchlist.user_id = ?
                    """, (session['id'],))
        films = cur.fetchall()
        cur.execute("SELECT * FROM users WHERE user_id = ?", (session['id'],))
        account = cur.fetchone()
        return render_template("watchlist.html", films = films, account=account)
    
@app.route('/<string:title>')
def film_details(title):
    con = sql.connect(DATABASE)
    cur = con.cursor()
    cur.execute("SELECT * FROM films WHERE title = ?", (title,))
    film = cur.fetchone()
    film_id = film[0]
    if 'id' in session:
        user_id = session['id']
        cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        account = cur.fetchone()
        cur.execute("""
                    SELECT * FROM films 
                    JOIN watchlist ON watchlist.film_id = films.film_id 
                    JOIN users ON watchlist.user_id = users.user_id 
                    WHERE users.user_id = ? AND watchlist.film_id = ?
                    """, (user_id, film_id))
        if cur.fetchone():
            return render_template("film_details.html", film = film, account = account, onwishlist = True)
        con.close()
        return render_template("film_details.html", film = film, account = account)
    con.close()
    return render_template("film_details.html", film = film)

@app.route('/search', methods=['GET', 'POST'])
def search():
    query = request.args.get('q')
    func = 'search(\'' + query + '\')'
    return render_template("index.html", func = func)

@app.route('/genre', methods=['GET', 'POST'])
def genre():
    genre = request.args.get('q')
    func = 'genre(\'' + genre + '\')'
    return render_template("index.html", func = func)
    
@app.route('/search-results', methods=['GET', 'POST'])
def search_results():
    query = request.args.get('q')
    con = sql.connect(DATABASE)
    cur = con.cursor()
    cur.execute("SELECT * FROM films WHERE title LIKE ? OR dir LIKE ?", (('%' + query + '%'), ('%' + query + '%')))
    results = cur.fetchall()
    con.close()
    results = sorted(results, key=lambda x: difflib.SequenceMatcher(None, x[1], query).ratio(), reverse=True)
    return render_template("search_results.html", results = results)

@app.route('/add-to-watchlist', methods=['GET', 'POST'])
def add_to_watchlist():
    if 'id' in session:
        film_id = request.args.get('film_id')
        con = sql.connect(DATABASE)
        cur = con.cursor()
        user_id = session['id']
        cur.execute("INSERT INTO watchlist(user_id, film_id) VALUES(?, ?)", (user_id, film_id))
        con.commit()
        cur.execute("SELECT title FROM films WHERE film_id = ?", (film_id,))
        title = cur.fetchone()[0]
        con.close()
        return redirect(url_for("film_details", title = title))
    return redirect("/signup")

@app.route('/remove-from-watchlist', methods=['GET', 'POST'])
def remove_from_watchlist():
    if 'id' in session:
        film_id = request.args.get('film_id')
        page = request.args.get('page')
        con = sql.connect(DATABASE)
        cur = con.cursor()
        user_id = session['id']
        cur.execute("DELETE FROM watchlist WHERE user_id = ? AND film_id = ?", (user_id, film_id))
        con.commit()
        cur.execute("SELECT title FROM films WHERE film_id = ?", (film_id,))
        title = cur.fetchone()[0]
        con.close()
        if (page == 'film_details'):
            return redirect(url_for(page, title = title))
        return redirect(url_for(page))
    return redirect("/signup")  

@app.route('/collections', methods=['GET', 'POST'])
def collections():
    collection = request.args.get('collection')
    con = sql.connect(DATABASE)
    cur = con.cursor()
    if (collection == 'features'):
        cur.execute("SELECT * FROM films JOIN features ON films.film_id = features.film_id")
    if (collection == 'new_releases'):
        cur.execute("SELECT films.* FROM films JOIN new_releases ON films.film_id = new_releases.film_id")
    if (collection == 'short_films'):
        cur.execute("SELECT * FROM films JOIN short_films ON films.film_id = short_films.film_id")
    if (collection == 'student_films'):
        cur.execute("SELECT films.* FROM films JOIN student_films ON films.film_id = student_films.film_id")
    results = cur.fetchall()
    if 'id' in session:
        cur.execute("SELECT * FROM users WHERE user_id = ?", (session['id'],))
        account = cur.fetchone()
        con.close()
        return render_template('collection.html', collection = collection, results = results, account = account)
    con.close
    return render_template('collection.html', collection = collection, results = results)

@app.route('/genre-results', methods=['GET', 'POST'])
def genre_results():
    query = request.args.get('q')
    con = sql.connect(DATABASE)
    cur = con.cursor()
    cur.execute("SELECT * FROM films WHERE genre = ?", (query,))
    results = cur.fetchall()
    con.close()
    random.shuffle(results)
    return render_template("search_results.html", results = results)

def get_user(id):
    con = sql.connect(DATABASE)
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE user_id = ?", (id,))
    user = cur.fetchone()
    con.close()
    return user


def create_user(email, password):
    con = sql.connect(DATABASE)
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, password TEXT)")
    cur.execute("INSERT INTO users(email, password) VALUES(?, ?)", (email, password))
    con.commit()
    cur.execute("SELECT user_id FROM users WHERE email = ?", (email,))
    user = cur.fetchone()
    con.close()
    return user

def get_films():
    con = sql.connect(DATABASE)
    cur = con.cursor()
    cur.execute("SELECT * FROM films")
    films = cur.fetchall()
    con.close()
    return films

if __name__ == '__main__':
        app.secret_key = "app.secret_key"
        app.run(debug = True)