from __future__ import print_function
from flask import Flask
from flask import request, jsonify
import mysql.connector
import secrets
import hashlib
import time
import urllib.parse
import json
import parameters
import sys

mydb = mysql.connector.connect(
    host="localhost",
    user=parameters.mysql_username,
    password=parameters.mysql_password,
    database=parameters.mysql_database
    )

app = Flask(__name__)
app.config["DEBUG"] = True
mycursor = mydb.cursor()

@app.route('/createUser', methods=['POST'])
def index():
    print('This is standard output', file=sys.stdout)
    username = request.json.get("username")
    sql = "SELECT COUNT(*) FROM users WHERE username like %s"
    mycursor.execute(sql, (username,))
    myresult = mycursor.fetchall()
    if(myresult[0][0] >= 1):
        return json.dumps({"status":"duplicate"})
    sql = "INSERT INTO users (username, salt, password, token, school, email) VALUES (%s, %s, %s, %s, %s, %s)"
    salt = secrets.token_urlsafe(128)
    hashedPass = hashlib.sha224(str(request.json.get('password')+salt).encode()).hexdigest()
    val = (username, salt, hashedPass, secrets.token_urlsafe(128), request.json.get("school"), request.json.get("email"))
    mycursor.execute(sql, val)
    mydb.commit()
    return json.dumps({"status":"success"})

@app.route('/login', methods=['POST'])
def login():
    password = request.json.get("password")
    username = request.json.get("username")

    if(urllib.parse.quote(password) != password or urllib.parse.quote(username) != username):
        return json.dumps({"token":"false"})

    sql = ("SELECT * FROM users WHERE username = %s")
    mycursor.execute(sql, (username, ))
    myresult = mycursor.fetchall()
    if(len(myresult) != 1):
        return json.dumps({"token":"false"})
    salt = myresult[0][1]
    hashedPass = myresult[0][2]
    testPass = hashlib.sha224(str(password+salt).encode()).hexdigest()
    if(hashedPass == testPass):
        token = secrets.token_urlsafe(128)
        sql = "UPDATE users SET token = %s WHERE username = %s"
        mycursor.execute(sql, (token, username))
        mydb.commit()
        return json.dumps({"token":token})
    else:
        time.sleep(0.1)
        return json.dumps({"token":"false"})
    return json.dumps({"token":"false"})

@app.route('/getUserData', methods=['POST'])
def getUserData():
    token = request.json.get("token")
    sql = ('SELECT username, email, school FROM users WHERE token = %s')
    mycursor.execute(sql,(token,))
    result = mycursor.fetchall()
    return(json.dumps({"username":result[0][0], "email":result[0][1], "school":result[0][2]}))
app.run()
