# 模型

import datetime

from .exts import db


# 用户
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(25))
    phone = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(25))
    email = db.Column(db.String(25))
    commands = db.relationship('User_message', backref='user', lazy='dynamic')

# 心理辅导师表 - 普通管理员
class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(25))
    phone = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(25))
    email = db.Column(db.String(25))
    content = db.Column(db.String(255))
    image = db.Column(db.String(50))
    is_use = db.Column(db.Integer)
    message = db.relationship('User_message', backref='teacher', lazy=True)
    reservation = db.relationship('Reservation', backref='teacher', lazy=True)


# 管理员表
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(25))
    phone = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(25))
    email = db.Column(db.String(25))
    is_use = db.Column(db.Integer)

# 用户留言表
class User_message(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(50))
    message = db.Column(db.String(255))
    create_time = db.Column(db.DateTime)
    is_show = db.Column(db.Integer)
    is_replay = db.Column(db.Integer)
    replay = db.Column(db.String(255))
    replay_teacher = db.Column(db.Integer, db.ForeignKey(Teacher.id))
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))



# 预约表
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(25))
    birthday = db.Column(db.Date, unique=True)
    QQ = db.Column(db.BigInteger)
    Wechat = db.Column(db.String(25))
    phone = db.Column(db.String(20))
    content = db.Column(db.String(255))
    process = db.Column(db.String(50))
    create_time = db.Column(db.DateTime)
    work_teacher = db.Column(db.Integer, db.ForeignKey(Teacher.id))

# 文章类型
class Type(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type_name = db.Column(db.String(20))
    articles = db.relationship('Article', backref='types', lazy=True)


# 文章表
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    article_name = db.Column(db.String(255))
    article_content = db.Column(db.TEXT)
    article_time = db.Column(db.Date, default=datetime.datetime.now())
    type_id = db.Column(db.Integer, db.ForeignKey(Type.id))


# 心理测试表
class Test_question(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    test_title = db.Column(db.String(255))
    test_content = db.Column(db.TEXT)
    test_time = db.Column(db.Date, default=datetime.datetime.now())

