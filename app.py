from flask import Flask,render_template,request
import sqlite3
app = Flask(__name__)

@app.route("/", methods=["GET","POST"])
def home():
    if request.method == "GET":
        return render_template("index.html")
    else:
      f = open("login.txt", "r")
      un = f.readline().strip()
      pw = f.readline().strip()
      f.close()
      if un == request.form["un"] and pw == request.form["pw"]:
        return "Hello " + un
      else:
        return "user not recognised"
     
@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "GET":
       return render_template ("signup.html")
    else:
       con = sqlite3.connect("database.db")
       cur = con.cursor()
       cur.execute(""" INSET INTO user (username,password)
                   VALUES (?,?)""",
                   (request.form["un"],request.form["pw"]))
       con.commit()
       con.close()
       return "signup successful"