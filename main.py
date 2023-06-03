from flask import Flask, render_template, request, session, redirect
import sqlite3
import hashlib
import os
import secrets

app = Flask(__name__)
app.secret_key = os.getenv("secret")

@app.route("/")
def index():
    try:
        tried = session['logged']
    except KeyError:
        return render_template("index.html")
    else:
        return render_template("index.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        res = cur.execute("SELECT name FROM users WHERE name=?", (request.form['username'], ))
        if res.fetchone() is None:
            error = 'Invalid Credentials. Please try again'
        else:
            res = cur.execute(f"SELECT password FROM users WHERE name=?", (request.form['username'], ))
            if hashlib.sha512(request.form['password'].encode()).hexdigest() != res.fetchone()[0]:
                error = 'Invalid Credentials. Please try again'
            else:
                session['username'] = request.form['username']
                session['logged'] = True
                return redirect("http://localhost:5000")
    return render_template('login.html', error=error)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        cur.execute("INSERT INTO users VALUES(?, ?)", (request.form['username'], hashlib.sha512(request.form['password'].encode()).hexdigest(), ))
        con.commit()
        con.close()
        return redirect("http://localhost:5000")
    return render_template("register.html")



app.run()

