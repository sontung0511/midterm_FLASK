from ssl import HAS_TLSv1_1
from flask_api import FlaskAPI
from flask import request, jsonify
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
import time
import math
import random
import smtplib
import MySQLdb.cursors
from dotenv import load_dotenv
from pathlib import Path  # Python 3.6+ only
import os

#load var in file .env
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = FlaskAPI(__name__)

# app.url_map.strict_slashes = False
# Thiet lap ket noi MySQL
app.config['MYSQL_Host'] = os.getenv("MYSQL_HOST")
app.config['MYSQL_USER'] = os.getenv("MYSQL_USER")
app.config['MYSQL_PASSWORD'] = os.getenv("MYSQL_PASS")
app.config['MYSQL_DB'] = os.getenv("DATABASE_NAME")
mysql = MySQL(app)

# Mail config
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
sender = "Hoc phi TDT"
mail = Mail(app)


@app.route("/login", methods=["POST"])
def login():
    loggedin = 0
    user = []
    data = request.get_json(force=True)
    if request.method == "POST":

        username = data["username"]
        password = data["password"]

        # ket noi database
        cursor = mysql.connection.cursor()
        cursor.execute(
            'SELECT * FROM accounts WHERE username = % s AND password = % s', (
                username, password, )
        )
        account = cursor.fetchone()
        mysql.connection.commit()
        cursor.close()

        # neu dung tai khoan trong DB
        if account:
            loggedin = 1
            user = account
    return jsonify(code=loggedin,
                   user=user)

@app.route('/user', methods=['POST'])
def user():
    data = request.get_json(force=True)
    iduser = data['id_user']
    cursor = mysql.connection.cursor()
    cursor.execute(
        'SELECT * FROM accounts WHERE id = %s', (
            iduser, )
    )
    account = cursor.fetchone()
    mysql.connection.commit()
    cursor.close()
    return jsonify(user=account)

@app.route('/checking', methods=['POST'])
def check():
    data = request.get_json(force=True)
    idfee = data['id_fee']
    otp = []

    cursor = mysql.connection.cursor()

    sql = 'DELETE FROM otp WHERE time < %s'
    val = (int(time.time()),)
    cursor.execute(sql, val)
    mysql.connection.commit()

    cursor.execute(
        'SELECT * FROM otp WHERE id_fee = %s', (
            idfee, )
    )
    result = cursor.fetchone()
    if result:
        otp = result
    
    return jsonify(data=otp)


@app.route("/fee", methods=["POST"])
def fee():
    available = 0
    student = []
    data = request.get_json(force=True)
    message = "Không có MSSV trong hệ thống"
    if request.method == "POST":
        ID = data["ID"]

        cursor = mysql.connection.cursor()
        cursor.execute(
            'SELECT * FROM fee WHERE ID = % s', (ID,)
        )

        account = cursor.fetchone()
        cursor.close()

        if account:
            available = 1
            student = account
            message = "OK"
            if account[2] < 1:
                available = 0
                message = "MSSV này đã được thanh toán học phí"
    return jsonify(available=available,
                   student=student,
                   message=message)

@app.route('/otp', methods=['POST'])
def otp():
    data = request.get_json(force=True)
    iduser = data['id_user']
    idfee = data['id_fee']
    email = data['email']
    time_start = int(time.time())
    time_expired = time_start + 300
    digits = "0123456789"
    OTP = ""
    for i in range(6):
        OTP += digits[math.floor(random.random()*9)]
    
    #sql
    sql = "INSERT INTO otp(id_user, id_fee, otp, time) VALUES (%s, %s, %s, %s)"
    val = (iduser, idfee, OTP, time_expired)
    cur = mysql.connection.cursor()
    cur.execute(sql, val)
    mysql.connection.commit()
    cur.close()

    #send otp
    msg = Message('OTP Thanh toán học phí TDT', sender = sender, recipients = [email])
    msg.body = OTP
    mail.send(msg)
    return jsonify({
        "code" : 1
    })

@app.route('/transaction', methods=['POST'])
def transaction():
    code = 0
    message = "Mã OTP không hợp lệ vui lòng kiểm tra lại"
    data = request.get_json(force=True)
    otp = data['otp']
    reba = data['reba']

    #sql
    sql = "SELECT * FROM otp WHERE otp = %s"
    val = (otp,)
    cur = mysql.connection.cursor()
    cur.execute(sql, val)
    result = cur.fetchone()
    
    if result:
        if(int(result[3]) >= int(time.time())):

            sql = 'UPDATE fee SET total_fee = 0 WHERE ID = %s'
            val = (result[1],)
            cur.execute(sql, val)
            mysql.connection.commit()

            sql = 'UPDATE accounts SET amount = %s WHERE id = %s'
            val = (reba, result[0])
            cur.execute(sql, val)
            mysql.connection.commit()

            sql = 'DELETE FROM otp WHERE id_fee = %s'
            val = (result[1],)
            cur.execute(sql, val)
            mysql.connection.commit()
            
            cur.close()
            
            code = 1 
            message = "Giao dịch thành công SDTK của bạn: " + str(reba)

    return jsonify(code=code,message=message)


if __name__ == "__main__":
    app.run(host=os.getenv("SERVER_HOST"),debug=True)