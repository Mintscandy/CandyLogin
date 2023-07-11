from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import config
import uuid
import jwt
import time

from hashlib import md5

app = Flask(__name__)

app.config.from_object(config)
db = SQLAlchemy(app)

SECRET_KEY = "SMD-BSW"
offset = 86400


def encrypt_md5(s):
    new_md5 = md5()
    new_md5.update(s.encode(encoding='utf-8'))
    return new_md5.hexdigest()


def getJWT(uid, username):
    d = {
        "exp": int(time.time()) + offset,
        "iat": int(time.time()),
        "iss": "issuer",
        "data": {
            "id": uid,
            "username": username,
            "timestamp": int(time.time())
        }
    }
    jwt_encode = jwt.encode(d, SECRET_KEY, algorithm="HS256")
    return jwt_encode


class loginTable(db.Model):
    __tablename__ = 'login'
    id = db.Column(db.String(40), primary_key=True)
    username = db.Column(db.String(30))
    password = db.Column(db.String)
    token = db.Column(db.String)
    status = db.Column(db.String)


class UserInfoTable(db.Model):
    __tablename__ = 'userinfo'
    id = db.Column(db.String(40), primary_key=True)
    sname = db.Column(db.String(11))
    sex = db.Column(db.String(1))
    saddress = db.Column(db.String(50))


@app.route('/register', methods=['POST'])
def register():
    jd = request.get_json()
    username = jd["username"]
    password = jd["password"]
    data = loginTable.query.filter(loginTable.username == username).first()
    if data:
        back_data = {
            "time": int(time.time()),
            "msg": "该用户名已被注册",
            "code": 202
        }
        return jsonify(back_data)
    else:
        suid = ''.join(str(uuid.uuid4()).split('-'))
        token = getJWT(suid, username)
        d1 = loginTable(id=suid, username=username, password=encrypt_md5(password), token=token, status='0')
        db.session.add(d1)
        db.session.commit()
        back_data = {
            "token": token,
            "time": int(time.time()),
            "msg": "注册成功！",
            "code": 200
        }
        return jsonify(back_data)


@app.route('/login', methods=["POST"])
def fetch_data():
    jd = request.get_json()
    username = jd["username"]
    password = jd["password"]
    data = loginTable.query.filter(loginTable.username == username).first()
    if encrypt_md5(password) == data.password:
        # try:
        #     jwt_decode = jwt.decode(data.token, SECRET_KEY, issuer='issuer', algorithms=['HS256'])
        # except jwt.exceptions.ExpiredSignatureError:
        #     return "jwt失效"
        new_token = getJWT(data.id, data.username)
        data.token = new_token
        data.status = '1'
        db.session.commit()
        back_data = {
            "token": data.token,
            "time": int(time.time()),
            "msg": "登录成功！",
            "code": 200
        }
        return jsonify(back_data)
    else:
        back_data = {
            "time": int(time.time()),
            "msg": "用户名或密码错误！",
            "code": 202
        }
        return jsonify(back_data)


@app.route('/updateInfo', methods=['POST'])
def update_info():
    jd = request.get_json()
    token = jd["token"]
    data = jd['data']
    name = data['name']
    sex = data['sex']
    address = data['address']
    try:
        jwt_decode = jwt.decode(token, SECRET_KEY, issuer='issuer', algorithms=['HS256'])
        uuid = jwt_decode['data']['id']
        data = UserInfoTable.query.filter(UserInfoTable.id == uuid).first()
        if data:
            data.sname = name
            data.sex = sex
            data.saddress = address
            db.session.commit()
        else:
            d1 = UserInfoTable(id=uuid, sname=name, sex=sex, saddress=address)
            db.session.add(d1)
            db.session.commit()
        back_data = {
            "time": int(time.time()),
            "msg": "个人信息修改成功",
            "code": 200
        }
        return jsonify(back_data)
    except jwt.exceptions.PyJWTError:
        back_data = {
            "time": int(time.time()),
            "msg": "token失效，请重新登录",
            "code": 203
        }
        return jsonify(back_data)


@app.route('/getuserInfo', methods=["POST"])
def getInfo():
    jd = request.get_json()
    token = jd["token"]
    try:
        jwt_decode = jwt.decode(token, SECRET_KEY, issuer='issuer', algorithms=['HS256'])
        data = loginTable.query.filter(loginTable.token == token).first()
        uuid = data.id
        userinfo = UserInfoTable.query.filter(UserInfoTable.id == uuid).first()
        back_data = {
            "time": int(time.time()),
            "msg": "获取成功！",
            "data": {
                "name": userinfo.sname,
                "sex": userinfo.sex,
                "address": userinfo.saddress
            },
            "code": 203
        }
        return back_data
    except jwt.exceptions.ExpiredSignatureError:
        back_data = {
            "time": int(time.time()),
            "msg": "token失效，请重新登录",
            "code": 203
        }
        return jsonify(back_data)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="8080")
