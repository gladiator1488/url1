from flask import Flask, request, render_template, redirect
import sqlite3 as sq
import random
import string
import requests
from flask.helpers import send_file, url_for




class Short_url:
    def create_short(self):
        self.db = sq.connect("short_url.db")
        self.cur = self.db.cursor()
        a = False
        letters = string.ascii_letters + string.digits
        q = "SELECT * FROM links"
        self.cur.execute(q)
        b = [i[1] for i in self.cur.fetchall()]
        self.token = "".join(random.choice(letters) for _ in range(5))
        while not a:
            if self.token not in b:
                a = True
                self.db.commit()
                return self.token
            else:
                a = False
                self.token = "".join(random.choice(letters) for _ in range(5))
        

    def get_new_url(self, link):
        self.link = link
        try:
            self.db = sq.connect("short_url.db")
            self.cur = self.db.cursor()
            q = "SELECT * FROM links WHERE long_url=?"
            self.cur.execute(q, (self.link,))
            a = self.cur.fetchall() # ВОЗВРАЩАЕТ КОРТЕЖ (ССЫЛКА, ТОКЕН)
            if not len(a):
                self.token = self.create_short()
                data = (self.link, self.token)
                q = "INSERT INTO links(long_url,token) VALUES (?,?)"
                self.cur.execute(q, data)
                a = self.cur.fetchall()

        except Exception as err:
            print(f"\n\n\n{err}\n\n")
        else:
            self.db.commit()
            return a

    def get_long_url(self, token):
        try:
            self.db = sq.connect("short_url.db")
            self.cur = self.db.cursor()
            q = "SELECT * FROM links WHERE token=?"
            self.cur.execute(q, (token,))
            a = self.cur.fetchall() # ВОЗВРАЩАЕТ КОРТЕЖ (ССЫЛКА, ТОКЕН)
            if not len(a):
                return "Ссылка не существует"

        except Exception as err:
            print(f"\n\n\n{err}\n\n")
        else:
            self.db.commit()
            return a
            


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route("/shorten", methods=["GET","POST"])
def shorten():
    if request.method == 'POST':
        url = request.form['long_url']
    try:
        print(requests.get(url))
    except Exception:
        return render_template("error.html", link=f"{request.host}/")
    else:
        q = Short_url()
        short_url = q.get_new_url(url)
        short_url1 = q.get_new_url(url)
        print("\n\nКороткая:  ", short_url1)
        short_url = (f"{request.host}/{short_url1[0][1]}", short_url1[0][0])
        return render_template("short.html", short_url=short_url)

@app.route('/<token>')
def redir(token):
    q = Short_url()
    url = q.get_long_url(token)[0][0]
    return redirect(url)

@app.route("/error")
def back():
    return redirect(url_for("index"), 301) 

@app.route("/open")
def open_link():
    return redirect(url_for("redir"), 301)

if __name__ == "__main__":
    app.run(port=5500)

