from flask import Flask
from flask import request, jsonify
import mysql.connector
import secrets
import hashlib
import time
import urllib.parse

mydb = mysql.connector.connect(
    host="localhost",
    user="kevin",
    password="wa2wahUs",
    database="bookheroes"
    )

app = Flask(__name__)
app.config["DEBUG"] = True

@app.route('/createUser')
def index():
    mycursor = mydb.cursor()
    sql = "INSERT INTO users (username, salt, password, token) VALUES (%s, %s, %s, %s)"
    salt = secrets.token_urlsafe(128)
    hashedPass = hashlib.sha224(str(request.args.get('password')+salt).encode()).hexdigest()
    val = (request.args.get('username'), salt, hashedPass, secrets.token_urlsafe(128))
    mycursor.execute(sql, val)

    mydb.commit()
    return 'Index Page'

@app.route('/login', methods=['POST'])
def login():
    password = request.values.get("password").replace("%","")
    username = request.values.get("username").replace("%","")
    if(urllib.parse.quote(password) != password or urllib.parse.quote(username) != username):
        return "false"

    mycursor = mydb.cursor()
    sql = ("SELECT * FROM users WHERE username like %s")
    mycursor.execute(sql, (username, ))
    myresult = mycursor.fetchall()
    if(len(myresult) < 1):
        return "false"
    salt = myresult[0][1]
    hashedPass = myresult[0][2]
    testPass = hashlib.sha224(str(password+salt).encode()).hexdigest()
    if(hashedPass == testPass):
        token = secrets.token_urlsafe(128)
        sql = "UPDATE users SET token = %s WHERE username like %s"
        mycursor.execute(sql, (token, username))
        mydb.commit()
        return token
    else:
        time.sleep(0.1)
        return "false"
    return "false"

app.run()
