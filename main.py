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
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        return render_template("index_acc.html", name=session['username'], bal=cur.execute("SELECT bal FROM wallets WHERE name=?", (session['username'],)))
        con.close()

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
    error = None
    if request.method == 'POST':
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        res = cur.execute("SELECT name FROM users WHERE name=?", (request.form['username'],))
        if res.fetchone() is None:
            cur.execute("INSERT INTO users VALUES(?, ?)", (request.form['username'], hashlib.sha512(request.form['password'].encode()).hexdigest(), ))
            cur.execute("INSERT INTO wallets VALUES(?, ?, ?)", (request.form['username'], secrets.token_hex(), 0))
            con.commit()
            return redirect("http://localhost:5000")
        else:
            error = "That username is already in use."
        con.close()
    return render_template("register.html", error=error)

@app.route("/explorer", methods=['GET', 'POST'])
def explorer():
    if request.method == 'POST':
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        res = cur.execute("SELECT bal FROM wallets WHERE wallet=?", (request.form['wallet'], ))
        return str(res.fetchone()[0])
    return render_template("explorer.html")
        
@app.route("/send", methods=['GET', 'POST'])
def send():
    error = None
    if request.method == 'POST':
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        res = cur.execute("SELECT wallet FROM wallets WHERE wallet=?", (request.form['wallet'], ))
        if res.fetchone() is None:
            error = "This wallet doesn't exist"
        else:
            res = cur.execute("SELECT bal FROM wallets WHERE name=?", (session['username'], ))
            if res.fetchone()[0] < int(request.form['amount']):
                error = "You don't have that much radiana in your wallet"
            else:
                res = cur.execute("SELECT bal FROM wallets WHERE wallet=?", (request.form['wallet'],)).fetchone()[0]
                cur.execute("UPDATE wallets SET bal = ? WHERE wallet = ?", (res+int(request.form['amount']), request.form['wallet'],))
                cur.execute("UPDATE wallets SET bal = ? WHERE name=?", (cur.execute("SELECT bal FROM wallets WHERE name=?", (session='username'), ).fetchone()[0]-int(request.form['amount']), session['username']))
                con.commit()
                return redirect("http://localhost:5000")
        con.close()
    return render_template("send.html", error=error)
                



app.run()

