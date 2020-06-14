# url+视图函数
import json
import os
import random
import time
from PIL import Image
from flask import Blueprint, render_template, jsonify, request, redirect, url_for, session
from sqlalchemy import and_, desc

from App.exts import cache
from App.logic import make_vcode, get_info, user_auth, admin_auth
from .models import *

sd = Blueprint('shudong', __name__)
admin = Blueprint('admin', __name__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# 首页
@sd.route('/', endpoint='index')
def index():
    user = session.get('user', '')
    data = {
        'user': user,
    }
    return render_template('shudong/index.html', **data)


# 用户注册
@sd.route('/register', endpoint='user_register', methods=['post', 'get'])
def user_register():
    if request.method == 'POST':
        phone = request.form.get('phone')
        email = request.form.get('email')
        password = request.form.get('password')
        username = request.form.get('username')
        vcode = request.form.get('vcode')

        # 验证手机号是否存在
        if phone:
            active_user = list(User.query.filter_by(phone=phone))
            if active_user:
                return jsonify({'code': 201, 'msg': '手机号已存在'})
        # 检测验证码是否正确
        cache_vcode = cache.get('vcode')
        if cache_vcode:
            cache_vcode = cache_vcode.lower()
        if vcode:
            vcode = vcode.lower()
        if vcode == cache_vcode:
            user = User()
            user.phone = phone
            user.username = username
            user.password = password
            user.email = email

            try:
                db.session.add(user)
                db.session.commit()
                user = User.query.filter_by(phone=phone).first()
                session_data = {
                    'user_id': user.id,
                    'user_name': user.username
                }
                session['user'] = session_data
                return jsonify({'code': 200, 'msg': '注册成功'})
            except:
                db.session.rollback()
                db.session.flush()
                return jsonify({'code': 201, 'msg': '注册失败'})
        else:
            return jsonify({'code': 203, 'msg': '验证码错误'})
    if request.method == 'GET':
        vcode = make_vcode()
        return render_template('shudong/register.html', image=vcode)


# 获取验证码
@sd.route('/get_captcha', endpoint='user_captcha', methods=['post'])
def get_captcha():
    vcode = make_vcode()
    print(cache.get('vcode'))
    return jsonify({'vcode': vcode})


# 用户登录
@sd.route('/login', endpoint='user_login', methods=['post', 'get'])
def user_login():
    if request.method == 'POST':
        phone = request.form.get('phone')
        password = request.form.get('password')

        user = User.query.filter_by(phone=phone).first()
        if not user:
            return jsonify({'code': 201, 'msg': '无此用户,请注册'})
        if user.password != password:
            return jsonify({'code': 201, 'msg': '密码输入错误'})
        session_data = {
            'user_id': user.id,
            'user_name': user.username
        }
        session['user'] = session_data
        return jsonify({'code': 200, 'msg': '登陆成功'})
    if request.method == 'GET':
        return render_template('shudong/login.html')


# 用户登出
@sd.route('/logout', endpoint='user_logout')
def user_logout():
    session.pop('user')
    return redirect(url_for('shudong.index'))


# 中心简介
@sd.route('/center_info/<string:id>', endpoint='center_info')
def center_info(id):
    try:
        user = session['user']
    except:
        user = ''
    if int(id) > 3 or int(id) < 0:
        return redirect(url_for('shudong.index'))
    article = Article.query.filter(Article.id == int(id)).first()
    article = {
        'user': user,
        'article': article
    }
    return render_template('shudong/center_info.html', **article)


# 树洞能量 - 主页
@sd.route('/article_list', endpoint='article_list')
def article_list():
    try:
        user = session['user']
    except:
        user = ''
    try:
        current_type_id = session.get('article_type_id')
    except:
        current_type_id = 0
    # 获取所有文章
    article = Article.query
    # 获取分类不是"公告"的文章
    article_ = article.filter(Article.type_id != 1)
    # 获取分类不是"公告"的分类
    types = Type.query.filter(Type.id != 1)
    # 分页
    page = 1
    per_page = 1  # 设置每页的文章数量
    articles = article_.paginate(page=page, per_page=per_page, error_out=False)

    data = {
        'user': user,
        'types': types,
        'pages': articles.pages,
        'article': article_.all(),
        'current_type_id': current_type_id
    }
    return render_template('shudong/article_list.html', **data)


# 树洞能量 - 主页 - 分页
@sd.route('/get_all_article', endpoint='get_all_article')
def get_all_article():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 1))
    # 获取分类不是"公告"的文章
    article = Article.query.filter(Article.type_id != 1)

    # 分页
    # per_page = 2  # 设置每页的文章数量
    articles = article.paginate(page=page, per_page=per_page, error_out=False)
    article_list = []
    for i in articles.items:
        article_list.append(
            [i.id, i.article_name]
        )

    data = {
        'articles': article_list
    }
    return jsonify(data)


# 树洞能量 - 分类
@sd.route('/article_select/<string:type_id>', endpoint='article_select')
def article_select(type_id):
    try:
        user = session['user']
    except:
        user = ''
    # 获取所有文章
    article = Article.query
    # 获取分类不是"公告"的文章
    article_ = article.filter(Article.type_id != 1)
    # 判断分类是否为 全部
    if int(type_id) == 0:
        article_fenlei = article.filter(Article.type_id != 1)
    else:
        # 获取分类不是"公告"的文章
        article_fenlei = article.filter(Article.type_id == int(type_id))
    # 获取分类不是"公告"的分类
    types = Type.query.filter(Type.id != 1)

    session['article_type_id'] = type_id
    # 分页
    page = 1
    per_page = 1  # 设置每页的文章数量
    articles = article_fenlei.paginate(page=page, per_page=per_page, error_out=False)
    data = {
        'user': user,
        'types': types,
        'pages': articles.pages,
        'article': article_.all(),
        'current_type_id': int(type_id)
    }
    return render_template('shudong/article_select.html', **data)


# 树洞能量 - 分类 - 分页
@sd.route('/article_select_page', endpoint='article_select_page')
def article_select_page():
    type_id = session.get('article_type_id')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 1))
    # 获取所有文章
    article = Article.query
    # 判断分类是否为 全部
    if int(type_id) == 0:
        article_fenlei = article.filter(Article.type_id != 1)
    else:
        # 获取分类不是"公告"的文章
        article_fenlei = article.filter(Article.type_id == int(type_id))

    # 分页
    articles = article_fenlei.paginate(page=page, per_page=per_page, error_out=False)
    article_list = []
    for i in articles.items:
        article_list.append(
            [i.id, i.article_name]
        )

    data = {
        'articles': article_list
    }
    return jsonify(data)


# 树洞能量 - 文章详情
@sd.route('/article_detail/<string:article_id>', endpoint='article_detail')
def article_detail(article_id):
    try:
        user = session['user']
    except:
        user = ''
    # 获取分类不是"公告"的分类
    types = Type.query.filter(Type.id != 1)
    # 查不是分类的文章数量
    article = Article.query.filter(Article.type_id != 1)
    article_detail = Article.query.filter(Article.id == int(article_id)).first()
    type_id = article_detail.types.id

    data = {
        'user': user,
        'types': types,
        'article': article.all(),
        'article_detail': article_detail,
        'current_type_id': int(type_id)
    }
    return render_template('shudong/article_detail.html', **data)


# 树洞测试
@sd.route('/sd_test', endpoint='sd_test')
def sd_test():
    data = {}
    try:
        user = session['user']
    except:
        user = ''
    data['user'] = user
    test_number = len(Test_question.query.all())
    data['test_number'] = test_number
    return render_template('shudong/sdtest.html', **data)


# 树洞测试 - 测试列表 - 接口
@sd.route('/sd_test_list_port', endpoint='sd_test_list_port')
def sd_test_list_port():
    data = {}
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 1))

    tests = Test_question.query.paginate(page=page, per_page=per_page, error_out=False)
    test_list = []
    for i in tests.items:
        temp = {}
        temp['id'] = i.id
        temp['name'] = i.test_title
        test_list.append(temp)
    data["tests"] = test_list
    return jsonify(data)

# 树洞测试 - 测试内容
@sd.route('/sd_test_detail/<string:test_id>', endpoint='sd_test_detail',methods=['GET','POST'])
def sd_test_detail(test_id):
    data = {}
    if request.method == 'GET':
        try:
            user = session['user']
        except:
            user = ''
        data['user'] = user
        test_detail = Test_question.query.get(test_id)
        test_list = Test_question.query.all()
        data['test_detail'] = test_detail
        data['test_list'] = test_list
        return render_template('shudong/test_detail.html',**data)
    elif request.method == 'POST':
        test_id = request.form.get('test_id')
        test = Test_question.query.get(test_id)
        data['title'] = test.test_title
        data['content'] = test.test_content
        data['time'] = str(test.test_time)
        return jsonify(data)

# 求助留言
@sd.route('/sd_message_show', endpoint='sd_message_show')
def sd_message_show():
    # 所有留言
    messages = User_message.query.filter(User_message.is_show == 1).order_by(desc('create_time'))
    # 当前登陆用户的留言
    try:
        user = session['user']
        my_messages = User_message.query.filter(User_message.user_id == user['user_id']).order_by(desc('create_time'))
    except:
        my_messages = []
        user = ''
    data = {
        'user': user,
        'messages': messages,
        'my_messages': my_messages
    }
    return render_template('shudong/sdmessage.html', **data)


# 保存留言
@sd.route('/sd_message_save', endpoint='sd_message_save', methods=['POST'])
def sd_message_save():
    title = request.form.get('title')
    message = request.form.get('message')
    niming = request.form.get('niming')
    try:
        user = session['user']
    except:
        return jsonify({'code': 201, 'msg': '请登录'})
    user_message = User_message()
    user_message.title = title
    user_message.message = message
    user_message.create_time = datetime.datetime.now()

    if niming:
        user_message.is_show = 0
    else:
        user_message.is_show = 1
    user_message.user_id = user['user_id']

    try:
        db.session.add(user_message)
        db.session.commit()
        return jsonify({'code': 200, 'msg': '留言成功'})
    except:
        db.session.rollback()
        db.session.flush()
        return jsonify({'code': 201, 'msg': '留言失败,请稍后重试'})


# 联系导师
@sd.route('/sd_contact_teacher', endpoint='sd_contact_teacher')
def sd_contact_teacher():
    try:
        user = session['user']
    except:
        user = ''
    teachers = Teacher.query.filter_by(is_use=1)
    data = {
        'user': user,
        'teachers': teachers,
    }
    return render_template('shudong/sdcontact.html', **data)


# 预约
@sd.route('/sd_reservation', endpoint='sd_reservation', methods=['POST', 'GET'])
def sd_reservation():
    if request.method == 'POST':
        name = request.form.get('name')
        birthday = request.form.get('birthday')
        QQ = request.form.get('QQ')
        Wechat = request.form.get('Wechat')
        phone = request.form.get('phone')
        content = request.form.get('content')

        reservation = Reservation()
        reservation.name = name
        reservation.birthday = birthday
        reservation.QQ = QQ
        reservation.Wechat = Wechat
        reservation.phone = phone
        reservation.content = content
        reservation.process = '未处理'
        reservation.create_time = datetime.datetime.now()
        try:
            db.session.add(reservation)
            db.session.commit()
            return jsonify({'code': 200, 'msg': '预约成功,导师将在24小时内与你取得联系'})
        except:
            db.session.rollback()
            db.session.flush()
            return jsonify({'code': 201, 'msg': '预约失败,请稍后重试'})
    elif request.method == 'GET':
        data = {}
        try:
            data['user'] = session['user']
        except:
            data['user'] = ''
        return render_template('shudong/sdreservation.html', **data)


# 修改个人信息
@sd.route('/sd_update_user', endpoint='sd_update_user', methods=['POST', 'GET'])
@user_auth
def sd_update_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        user = User()
        user.username = username
        user.password = password
        user.email = email

        try:
            db.session.add(user)
            db.session.commit()
            return jsonify({'code': 200, 'msg': '修改成功'})
        except:
            db.session.rollback()
            db.session.flush()
            return jsonify({'code': 201, 'msg': '修改失败'})
    elif request.method == 'GET':
        data = {}

        data['user'] = session['user']
        data['user_detail'] = User.query.get(session['user']['user_id'])

        return render_template('shudong/sdupdateuser.html', **data)


# 管理员 - 登录
@admin.route('/admin', endpoint='sd_admin_login', methods=['GET', 'POST'])
def sd_admin_login():
    if request.method == 'POST':
        # admin_type -> 0是心理老师, 1是超级管理员
        admin_type = request.form.get('admin')
        phone = request.form.get('phone')
        password = request.form.get('password')

        if not admin_type:
            return jsonify({'code': 201, 'msg': '请选择管理员类型'})
        if int(admin_type) == 0:
            admin = Teacher.query.filter_by(phone=phone).first()
        else:
            admin = Admin.query.filter_by(phone=phone).first()

        if not admin:
            return jsonify({'code': 201, 'msg': '无此用户,请联系管理员'})
        else:
            if admin.password != password:
                return jsonify({'code': 201, 'msg': '密码输入错误'})
            elif admin.is_use != 1:
                return jsonify({'code': 201, 'msg': '账号被停用,请联系管理员'})
            try:
                is_use = session['is_use']
                session.pop('is_use')
                if is_use:
                    return jsonify({'code': 201, 'msg': '账号被停用,请联系管理员'})
            except:
                pass

        session_data = {
            'id': admin.id,
            'name': admin.name,
            'type': admin_type
        }
        print(session_data)
        session['admin'] = session_data
        return jsonify({'code': 200, 'msg': '登陆成功'})
    elif request.method == 'GET':
        return render_template('admin/login.html')


# 管理员 - 退出
@admin.route('/sd_admin_logout', endpoint='sd_admin_logout')
@admin_auth
def sd_admin_logout():
    session.pop('admin')
    return redirect(url_for('admin.sd_admin_login'))


# 管理员 - 主页
@admin.route('/sd_admin_index', endpoint='sd_admin_index')
@admin_auth
def sd_admin_index():
    data = get_info()
    return render_template('admin/index.html',**data)
    # return redirect(url_for('admin.sd_admin_article_list'))


# 管理员 - 展示 - 文章列表
@admin.route('/sd_admin_article_list', endpoint='sd_admin_article_list')
@admin_auth
def sd_admin_article_list():
    data = get_info()
    data['type'] = '文章'
    return render_template('admin/article_list.html', **data)


# 管理员  - 文章列表 - 接口
@admin.route('/sd_admin_art_port', endpoint='sd_admin_art_port')
@admin_auth
def sd_admin_art_port():
    try:
        limit = request.args.get('limit')
        page = request.args.get('page')
    except:
        page = 1
        limit = 10
    articles = Article.query.filter(Article.type_id != 1).paginate(int(page), int(limit), False).items
    all_articles = len(list(Article.query.filter(Article.type_id != 1)))
    article_list = []
    for i in articles:
        temp = {}
        temp['id'] = i.id
        temp['name'] = i.article_name
        temp['content'] = i.article_content
        temp['time'] = str(i.article_time)
        temp['type'] = i.types.type_name
        article_list.append(temp)
    data = {
        "code": 0,
        "msg": "",
        "count": all_articles,
        "data": article_list,
        "totalRow": {
            "score": "666"
            , "experience": "999"
        }
    }
    return jsonify(data)


# 管理员 - 删除文章 - 接口
@admin.route('/sd_admin_artdel_port', endpoint='sd_admin_artdel_port', methods=['POST'])
@admin_auth
def sd_admin_artdel_port():
    article_id = request.form.get('id')
    id_list = json.loads(article_id).get('id')
    data = {}
    try:
        Article.query.filter(Article.id.in_(id_list)).delete(synchronize_session=False)
        db.session.commit()
        data['code'] = 200
        data['msg'] = '删除成功'
        return jsonify(data)
    except:
        data['code'] = 201
        data['msg'] = '删除失败'
        return jsonify(data)


# 管理员 - 文章详情 - 修改 - 接口
@admin.route('/sd_admin_article_detail/<string:id>', endpoint='sd_admin_article_detail', methods=['GET', 'POST'])
@admin_auth
def sd_admin_article_detail(id):
    if request.method == 'POST':
        data = {}
        id = request.form.get('id')
        article_content = request.form.get('article_content')
        article_name = request.form.get('article_name')
        article_type = request.form.get('article_type')

        article = Article.query.get(id)
        article.article_name = article_name
        article.type_id = article_type
        article.article_content = article_content
        try:
            db.session.add(article)
            db.session.commit()
            return jsonify({'code': 200, 'msg': '成功'})
        except:
            db.session.rollback()
            db.session.flush()
            return jsonify({'code': 201, 'msg': '失败'})
    elif request.method == 'GET':
        data = get_info()
        types = Type.query.filter(Type.id != 1)
        article = Article.query.get(int(id))
        data['article'] = article
        data['types'] = types
        data['type'] = '文章'
        return render_template('admin/article_detail.html', **data)


# 管理员 - 文章详情 - 新增
@admin.route('/sd_admin_article_insert', endpoint='sd_admin_article_insert', methods=['GET', 'POST'])
@admin_auth
def sd_admin_article_insert():
    if request.method == 'POST':
        data = {}

        article_content = request.form.get('article_content')
        article_name = request.form.get('article_name')
        article_type = request.form.get('article_type')

        if article_content.replace(' ', '').replace('&nbsp;', '') == '':
            return jsonify({'code': 201, 'msg': '文章不能为空'})

        article = Article()
        article.article_name = article_name
        article.type_id = article_type
        article.article_content = article_content
        try:
            db.session.add(article)
            db.session.commit()
            return jsonify({'code': 200, 'msg': '新增文章成功'})
        except:
            db.session.rollback()
            db.session.flush()
            return jsonify({'code': 201, 'msg': '新增文章失败'})
    elif request.method == 'GET':
        data = get_info()
        types = Type.query.filter(Type.id != 1)
        data['types'] = types
        return render_template('admin/article_insert.html', **data)


# 管理员 - 树洞测试 - 测试列表
@admin.route('/sd_admin_test_list', endpoint='sd_admin_test_list')
@admin_auth
def sd_admin_test_list():
    data = get_info()
    data['type'] = '文章'
    return render_template('admin/test_list.html', **data)


# 管理员 - 树洞测试 - 测试列表 - 接口
@admin.route('/sd_admin_test_port', endpoint='sd_admin_test_port')
@admin_auth
def sd_admin_test_port():
    try:
        limit = request.args.get('limit')
        page = request.args.get('page')
    except:
        page = 1
        limit = 10
    tests = Test_question.query.filter(Article.type_id != 1).paginate(int(page), int(limit), False).items
    all_tests = len(list(Test_question.query.filter(Article.type_id != 1)))
    test_list = []
    for i in tests:
        temp = {}
        temp['id'] = i.id
        temp['name'] = i.test_title
        temp['content'] = i.test_content
        temp['time'] = str(i.test_time)
        test_list.append(temp)
    data = {
        "code": 0,
        "msg": "",
        "count": all_tests,
        "data": test_list,
    }
    return jsonify(data)


# 管理员 - 树洞测试 - 修改 - 接口
@admin.route('/sd_admin_test_detail/<string:id>', endpoint='sd_admin_test_detail', methods=['GET', 'POST'])
@admin_auth
def sd_admin_testdetail(id):
    if request.method == 'POST':
        data = {}
        id = request.form.get('id')
        test_content = request.form.get('test_content')
        test_name = request.form.get('test_name')

        if test_content.replace(' ', '').replace('&nbsp;', '') == '':
            return jsonify({'code': 201, 'msg': '测试内容不能为空'})
        test = Test_question.query.get(int(id))
        test.test_title = test_name
        test.test_content = test_content
        try:
            db.session.add(test)
            db.session.commit()
            return jsonify({'code': 200, 'msg': '成功'})
        except:
            db.session.rollback()
            db.session.flush()
            return jsonify({'code': 201, 'msg': '失败'})
    elif request.method == 'GET':
        data = get_info()
        test = Test_question.query.get(int(id))
        data['test'] = test
        return render_template('admin/test_detail.html', **data)


# 管理员 - 树洞测试 - 测试列表 - 新增
@admin.route('/sd_admin_test_insert', endpoint='sd_admin_test_insert', methods=['GET', 'POST'])
@admin_auth
def sd_admin_test_insert():
    if request.method == 'POST':
        data = {}

        test_content = request.form.get('test_content')
        test_name = request.form.get('test_name')

        if test_content.replace(' ', '').replace('&nbsp;', '') == '':
            return jsonify({'code': 201, 'msg': '测试内容不能为空'})

        test = Test_question()
        test.test_title = test_name
        test.test_content = test_content
        try:
            db.session.add(test)
            db.session.commit()
            return jsonify({'code': 200, 'msg': '新增测试成功'})
        except:
            db.session.rollback()
            db.session.flush()
            return jsonify({'code': 201, 'msg': '新增测试失败'})
    elif request.method == 'GET':
        data = get_info()
        return render_template('admin/test_insert.html', **data)


# 管理员 - 删除测试 - 接口
@admin.route('/sd_admin_testdel_port', endpoint='sd_admin_testdel_port', methods=['POST'])
@admin_auth
def sd_admin_testdel_port():
    test_id = request.form.get('id')
    id_list = json.loads(test_id).get('id')
    data = {}
    try:
        Test_question.query.filter(Test_question.id.in_(id_list)).delete(synchronize_session=False)
        db.session.commit()
        data['code'] = 200
        data['msg'] = '删除成功'
        return jsonify(data)
    except:
        data['code'] = 201
        data['msg'] = '删除失败'
        return jsonify(data)


# 管理员 - 公告列表
@admin.route('/sd_admin_announce_list', endpoint='sd_admin_announce_list')
@admin_auth
def sd_admin_announce_list():
    data = get_info()
    data['type'] = '公告'
    return render_template('admin/article_list.html', **data)


# 管理员 - 公告列表 - 表格接口
@admin.route('/sd_admin_ann_port', endpoint='sd_admin_ann_port')
@admin_auth
def sd_admin_ann_port():
    try:
        limit = request.args.get('limit')
        page = request.args.get('page')
    except:
        page = 1
        limit = 10
    articles = Article.query.filter(Article.type_id == 1).paginate(int(page), int(limit), False).items
    all_articles = len(list(Article.query.filter(Article.type_id == 1)))
    article_list = []
    for i in articles:
        temp = {}
        temp['id'] = i.id
        temp['name'] = i.article_name
        temp['content'] = i.article_content
        temp['time'] = str(i.article_time)
        temp['type'] = i.types.type_name
        article_list.append(temp)
    data = {
        "code": 0,
        "msg": "",
        "count": all_articles,
        "data": article_list,
        "totalRow": {
            "score": "666"
            , "experience": "999"
        }
    }
    return jsonify(data)


# 管理员 - 公告详情 - 修改
@admin.route('/sd_admin_announce_detail/<string:id>', endpoint='sd_admin_announce_detail', methods=['GET', 'POST'])
@admin_auth
def sd_admin_announce_detail(id):
    if request.method == 'POST':
        data = {}
        id = request.form.get('id')
        article_content = request.form.get('article_content')
        article_name = request.form.get('article_name')
        article_type = request.form.get('article_type')

        article = Article.query.get(id)
        article.article_name = article_name
        article.type_id = article_type
        article.article_content = article_content
        try:
            db.session.add(article)
            db.session.commit()
            return jsonify({'code': 200, 'msg': '成功'})
        except:
            db.session.rollback()
            db.session.flush()
            return jsonify({'code': 201, 'msg': '失败'})
    elif request.method == 'GET':
        data = get_info()
        types = Type.query.filter(Type.id == 1)
        article = Article.query.get(int(id))
        data['article'] = article
        data['types'] = types  # 所有文章的分类
        data['type'] = '公告'  # 当前文章的分类
        return render_template('admin/article_detail.html', **data)


# 管理员 - 文章分类
@admin.route('/sd_admin_type_list', endpoint='sd_admin_type_list')
@admin_auth
def sd_admin_type_list():
    data = get_info()
    return render_template('admin/type_list.html', **data)


# 管理员 - 文章分类 - 表格接口
@admin.route('/sd_admin_type_port', endpoint='sd_admin_type_port')
@admin_auth
def sd_admin_type_port():
    try:
        limit = request.args.get('limit')
        page = request.args.get('page')
    except:
        page = 1
        limit = 10
    types = Type.query.filter(Type.id != 1).paginate(int(page), int(limit), False).items
    all_types = len(list(Type.query.filter(Type.id != 1)))
    type_list = []
    for i in types:
        temp = {}
        temp['id'] = i.id
        temp['name'] = i.type_name
        type_list.append(temp)
    data = {
        "code": 0,
        "msg": "",
        "count": all_types,
        "data": type_list,
    }
    return jsonify(data)


# 管理员 - 文章分类 - 修改分类
@admin.route('/sd_admin_update_type', endpoint='sd_admin_update_type', methods=['POST'])
@admin_auth
def sd_admin_update_type():
    name = request.form.get('name')
    id = request.form.get('id')

    type = Type.query.get(id)
    type.type_name = name
    print(type, name, id)
    try:
        db.session.add(type)
        db.session.commit()
        return jsonify({'code': 200, 'msg': '修改成功', 'data': name})
    except:
        db.session.rollback()
        db.session.flush()
        return jsonify({'code': 201, 'msg': '修改失败'})


# 管理员 - 文章分类 - 新增分类 - 接口
@admin.route('/sd_admin_insert_type', endpoint='sd_admin_insert_type', methods=['POST'])
@admin_auth
def sd_admin_insert_type():
    name = request.form.get('name')

    type = Type()
    type.type_name = name
    print(type, name, id)
    try:
        db.session.add(type)
        db.session.commit()
        return jsonify({'code': 200, 'msg': '新增成功'})
    except:
        db.session.rollback()
        db.session.flush()
        return jsonify({'code': 201, 'msg': '新增失败'})


# 管理员 - 文章分类 - 删除 - 检测该分类下是否有文章 - 接口
@admin.route('/sd_admin_del_type', endpoint='sd_admin_del_type', methods=['POST'])
@admin_auth
def sd_admin_del_type():
    type_id = request.form.get('type_id')
    articles = list(Article.query.filter(Article.type_id == type_id))
    if articles:
        return jsonify({'code': 200})
    else:
        return jsonify({'code': 201})


# 管理员 - 文章分类 - 单一删除
@admin.route('/sd_admin_deltype_port', endpoint='sd_admin_deltype_port', methods=['POST'])
@admin_auth
def sd_admin_deltype_port():
    type_id = request.form.get('type_id')
    id = json.loads(type_id)
    data = {}
    try:
        Type.query.filter(Type.id == id).delete(synchronize_session=False)
        db.session.commit()
        data['code'] = 200
        data['msg'] = '删除成功'
        return jsonify(data)
    except:
        data['code'] = 201
        data['msg'] = '删除失败'
        return jsonify(data)


# 管理员 - 文章分类 - 关联删除 - 文章iframe
@admin.route('/sd_admin_del_type_iframe/<string:type_id>', endpoint='sd_admin_del_type_iframe')
@admin_auth
def sd_admin_del_type_iframe(type_id):
    data = {}
    data['id'] = type_id
    return render_template('admin/del_type_iframe.html', **data)


# 管理员 - 文章分类 - 关联删除 - 文章iframe - 接口
@admin.route('/sd_admin_deltype_iframe_port/<string:type_id>', endpoint='sd_admin_deltype_iframe_port')
@admin_auth
def sd_admin_deltype_iframe_port(type_id):
    try:
        limit = request.args.get('limit')
        page = request.args.get('page')
    except:
        page = 1
        limit = 10

    articles = Article.query.filter(Article.type_id == type_id).paginate(int(page), int(limit), False).items
    all_articles = len(list(Article.query.filter(Article.type_id == type_id)))
    article_list = []
    for i in articles:
        temp = {}
        temp['id'] = i.id
        temp['name'] = i.article_name
        temp['content'] = i.article_content
        temp['time'] = str(i.article_time)
        temp['type'] = i.types.type_name
        article_list.append(temp)
    data = {
        "code": 0,
        "msg": "",
        "count": all_articles,
        "data": article_list,
    }
    return jsonify(data)


# 管理员 - 留言 - 展示
@admin.route('/sd_admin_message', endpoint='sd_admin_message')
@admin_auth
def sd_admin_message():
    data = get_info()
    return render_template('admin/user_message.html', **data)


# 管理员 - 留言 - 表格接口
@admin.route('/sd_admin_message_port', endpoint='sd_admin_message_port')
@admin_auth
def sd_admin_message_port():
    try:
        limit = request.args.get('limit')
        page = request.args.get('page')
    except:
        page = 1
        limit = 10
    messages = User_message.query.paginate(int(page), int(limit), False).items
    all_messages = len(list(User_message.query.all()))
    message_list = []
    for i in messages:
        temp = {}
        temp['id'] = i.id
        temp['title'] = i.title
        temp['message'] = i.message
        temp['user_name'] = i.user.username
        temp['create_time'] = str(i.create_time)
        temp['is_replay'] = '已回复' if i.is_replay else '未回复'
        message_list.append(temp)
    data = {
        "code": 0,
        "msg": "",
        "count": all_messages,
        "data": message_list,
    }
    return jsonify(data)


# 管理员 - 留言 - 留言接口
@admin.route('/sd_admin_addmessage_port', endpoint='sd_admin_addmessage_port', methods=['GET', 'POST'])
@admin_auth
def sd_admin_addmessage_port():
    data = {}
    if request.method == 'GET':
        message_id = request.args.get('message_id')
        replay_content = User_message.query.get(message_id).replay
        return jsonify({'replay': replay_content})

    elif request.method == 'POST':
        replay = request.form.get('replay')
        message_id = request.form.get('message_id')
        mes = User_message.query.get(message_id)
        mes.replay = replay
        mes.is_replay = 1
        mes.replay_teacher = session.get('admin').get('id')

        try:
            db.session.add(mes)
            db.session.commit()
            return jsonify({'code': 200, 'msg': '回复成功'})
        except:
            db.session.rollback()
            db.session.flush()
            return jsonify({'code': 201, 'msg': '回复失败'})

# 管理员  - 留言 - 删除
@admin.route('/sd_admin_delmessage_port', endpoint='sd_admin_delmessage_port',methods=['POST'])
@admin_auth
def sd_admin_delmessage_port():
    article_id = request.form.get('id')
    id_list = json.loads(article_id).get('id')
    data = {}
    try:
        User_message.query.filter(User_message.id.in_(id_list)).delete(synchronize_session=False)
        db.session.commit()
        data['code'] = 200
        data['msg'] = '删除成功'
        return jsonify(data)
    except:
        data['code'] = 201
        data['msg'] = '删除失败'
        return jsonify(data)

# 管理员 - 预约 - 展示
@admin.route('/sd_admin_reservation_list', endpoint='sd_admin_reservation_list')
@admin_auth
def sd_admin_reservation_list():
    data = get_info()
    return render_template('admin/reservation_list.html', **data)


# 管理员 - 预约 - 表格接口
@admin.route('/sd_admin_reservation_port', endpoint='sd_admin_reservation_port')
@admin_auth
def sd_admin_reservation_port():
    try:
        limit = request.args.get('limit')
        page = request.args.get('page')
    except:
        page = 1
        limit = 10
    reservations = Reservation.query.paginate(int(page), int(limit), False).items
    all_reservations = len(list(Reservation.query.all()))
    reservation_list = []
    for i in reservations:
        temp = {}
        temp['id'] = i.id
        temp['name'] = i.name
        temp['phone'] = i.phone
        temp['content'] = i.content
        temp['birthday'] = str(i.birthday)
        temp['process'] = i.process
        temp['wechat'] = i.Wechat
        temp['QQ'] = i.QQ
        temp['time'] = str(i.create_time)
        temp['teacher'] = i.teacher.name  if i.work_teacher else '无'
        reservation_list.append(temp)
    print(reservation_list)
    data = {
        "code": 0,
        "msg": "",
        "count": all_reservations,
        "data": reservation_list,
    }
    return jsonify(data)


# 管理员 - 预约 - 处理预约 - 接口
@admin.route('/sd_admin_reverpro_port', endpoint='sd_admin_reverpro_port',methods=['POST'])
@admin_auth
def sd_admin_reverpro_port():
    id = request.form.get('id')
    teacher_id = request.form.get('teacher_id')

    reservation = Reservation.query.get(id)
    if reservation.process == '处理完成':
        return jsonify({'code':201,'msg':'该预约已经处理完成'})
    teacher = reservation.work_teacher
    if teacher:
        return jsonify({'code':201,'msg':'该预约已在处理中'})
    reservation.work_teacher = teacher_id
    reservation.process = '处理中'
    try:
        db.session.add(reservation)
        db.session.commit()
        return jsonify({'code':200,'msg':'确认成功'})
    except:
        db.session.rollback()
        db.session.flush()
        return jsonify({'code':201,'msg':'确认失败'})



# 管理员 - 预约 - 删除预约 - 接口
@admin.route('/sd_admin_reverdel_port', endpoint='sd_admin_reverdel_port',methods=['POST'])
@admin_auth
def sd_admin_reverdel_port():
    id = request.form.get('id')

    reservation = Reservation.query.get(id)
    try:
        db.session.delete(reservation)
        db.session.commit()
        return jsonify({'code':200,'msg':'删除成功'})
    except:
        return jsonify({'code':200,'msg':'删除失败'})


# 管理员 - 预约 - 处理完成预约 - 接口
@admin.route('/sd_admin_reverfin_port', endpoint='sd_admin_reverfin_port',methods=['POST'])
@admin_auth
def sd_admin_reverfin_port():
    id = request.form.get('id')
    teacher_id = request.form.get('teacher_id')

    reservation = Reservation.query.get(id)
    if reservation.process == '未处理':
        return jsonify({'code':201,'msg':'未处理的预约不能完成'})
    if reservation.process == '处理完成':
        return jsonify({'code': 201, 'msg': '该预约已处理'})
    if reservation.work_teacher != teacher_id:
        return jsonify({'code': 201, 'msg': '您不能完成其他导师的预约'})

    reservation.process = '处理完成'
    try:
        db.session.add(reservation)
        db.session.commit()
        return jsonify({'code':200,'msg':'确认成功'})
    except:
        db.session.rollback()
        db.session.flush()
        return jsonify({'code':201,'msg':'确认失败'})

# 管理员 - 权限管理 - 用户
@admin.route('/sd_admin_user', endpoint='sd_admin_user', methods=['GET', 'POST'])
@admin_auth
def sd_admin_user():
    data = get_info()
    data['type'] = '用户'
    return render_template('admin/people_list.html', **data)


# 管理员 - 权限管理 - 用户 - 表格接口
@admin.route('/sd_admin_Tuser_port', endpoint='sd_admin_Tuser_port')
@admin_auth
def sd_admin_Tuser_port():
    try:
        limit = request.args.get('limit')
        page = request.args.get('page')
    except:
        page = 1
        limit = 10
    users = User.query.paginate(int(page), int(limit), False).items
    all_users = len(list(User.query.all()))
    user_list = []
    for i in users:
        temp = {}
        temp['id'] = i.id
        temp['name'] = i.username
        temp['phone'] = i.phone
        temp['email'] = i.email
        # temp['is_use'] = '已启用' if i.is_use else '已停用'
        user_list.append(temp)
    data = {
        "code": 0,
        "msg": "",
        "count": all_users,
        "data": user_list,

    }
    return jsonify(data)


# 管理员 - 权限管理 - 修改用户 - 模态框
@admin.route('/sd_admin_Tuser_iframe/<string:id>', endpoint='sd_admin_Tuser_iframe')
@admin_auth
def sd_admin_Tuser_iframe(id):
    data = {}
    user = User.query.get(id)
    data['user'] = user
    return render_template('admin/people_detail_iframe.html', **data)


# 管理员 - 权限管理 - 修改用户 - 接口
@admin.route('/sd_admin_Tuser_update_port', endpoint='sd_admin_Tuser_update_port', methods=['POST'])
@admin_auth
def sd_admin_Tuser_update_port():
    name = request.form.get('name')
    id = request.form.get('id')
    phone = request.form.get('phone')
    password = request.form.get('password')
    email = request.form.get('email')

    user = User.query.get(id)
    user.username = name
    user.phone = phone
    user.password = password
    user.email = email

    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({'code': 200, 'msg': '修改成功'})
    except:
        db.session.rollback()
        db.session.flush()
        return jsonify({'code': 201, 'msg': '修改失败'})


# 管理员 - 权限管理 - 指导老师
@admin.route('/sd_admin_teacher', endpoint='sd_admin_teacher')
@admin_auth
def sd_admin_teacher():
    data = get_info()
    data['type'] = '导师'
    return render_template('admin/people_list.html', **data)


# 管理员 - 权限管理 - 指导老师 - 表格接口
@admin.route('/sd_admin_Tteacher_port', endpoint='sd_admin_Tteacher_port')
@admin_auth
def sd_admin_Tteacher_port():
    try:
        limit = request.args.get('limit')
        page = request.args.get('page')
    except:
        page = 1
        limit = 10
    teachers = Teacher.query.paginate(int(page), int(limit), False).items
    all_teachers = len(list(Teacher.query.all()))
    teacher_list = []
    for i in teachers:
        temp = {}
        temp['id'] = i.id
        temp['name'] = i.name
        temp['phone'] = i.phone
        temp['email'] = i.email
        temp['is_use'] = '已启用' if i.is_use else '已停用'
        teacher_list.append(temp)
    data = {
        "code": 0,
        "msg": "",
        "count": all_teachers,
        "data": teacher_list,

    }
    return jsonify(data)


# 管理员 - 权限管理 - 修改指导老师 - 模态框
@admin.route('/sd_admin_Tteacher_iframe/<string:id>', endpoint='sd_admin_Tteacher_iframe')
@admin_auth
def sd_admin_Tteacher_iframe(id):
    data = {}
    teacher = Teacher.query.get(id)
    data['user'] = teacher
    data['type'] = '导师'
    return render_template('admin/teacher_detail_iframe.html', **data)


# 管理员 - 权限管理 - 修改指导老师 - 接口
@admin.route('/sd_admin_Tteacher_update_port', endpoint='sd_admin_Tteacher_update_port', methods=['POST'])
@admin_auth
def sd_admin_Tteacher_update_port():

    name = request.form.get('name')
    id = request.form.get('id')
    phone = request.form.get('phone')
    password = request.form.get('password')
    email = request.form.get('email')
    is_use = request.form.get('is_use')
    img = request.files.get('img')

    teacher = Teacher.query.get(id)
    # 上传头像
    if img:
        img_name = 'admin_'+id+'.'+img.filename.split('.')[1]
        img_path = 'static/image/teacher/'+img_name
        img.save(img_path)
        teacher.image = 'image/teacher/' + img_name
        try:
            db.session.add(teacher)
            db.session.commit()
            return jsonify({'code': 200, 'msg': '上传成功','filename':img.filename})
        except:
            db.session.rollback()
            db.session.flush()
            return jsonify({'code': 201, 'msg': '上传失败'})

    teacher.name = name
    teacher.phone = phone
    teacher.password = password
    teacher.email = email
    teacher.is_use = is_use
    try:
        db.session.add(teacher)
        db.session.commit()
        return jsonify({'code': 200, 'msg': '修改成功'})
    except:
        db.session.rollback()
        db.session.flush()
        return jsonify({'code': 201, 'msg': '修改失败'})


# 管理员 - 权限管理 - 添加指导老师 - 接口
@admin.route('/sd_admin_Tteacher_add_port', endpoint='sd_admin_Tteacher_add_port', methods=['POST'])
@admin_auth
def sd_admin_Tteacher_add_port():
    name = request.form.get('name')
    phone = request.form.get('phone')
    password = request.form.get('password')
    email = request.form.get('email')
    textarea = request.form.get('textarea')
    img = request.files.get('img')

    teacher = Teacher()
    teacher.name = name
    teacher.phone = phone
    teacher.password = password
    teacher.email = email
    teacher.content = textarea
    teacher.is_use = 1

    try:
        db.session.add(teacher)
        db.session.commit()
        return jsonify({'code': 200, 'msg': '添加成功'})
    except:
        db.session.rollback()
        db.session.flush()
        return jsonify({'code': 201, 'msg': '添加失败'})


# 管理员 - 权限管理 - 管理员
@admin.route('/sd_admin_admin', endpoint='sd_admin_admin')
@admin_auth
def sd_admin_admin():
    data = get_info()
    data['type'] = '管理员'
    return render_template('admin/people_list.html', **data)


# 管理员 - 权限管理 - 管理员 - 表格接口
@admin.route('/sd_admin_Tadmin_port', endpoint='sd_admin_Tadmin_port')
@admin_auth
def sd_admin_Tadmin_port():
    try:
        limit = request.args.get('limit')
        page = request.args.get('page')
    except:
        page = 1
        limit = 10
    admins = Admin.query.paginate(int(page), int(limit), False).items
    all_admins = len(list(Admin.query.all()))
    admin_list = []
    for i in admins:
        temp = {}
        temp['id'] = i.id
        temp['name'] = i.name
        temp['phone'] = i.phone
        temp['email'] = i.email
        temp['is_use'] = '已启用' if i.is_use else '已停用'
        admin_list.append(temp)
    data = {
        "code": 0,
        "msg": "",
        "count": all_admins,
        "data": admin_list,

    }
    return jsonify(data)


# 管理员 - 权限管理 - 管理员 - 模态框
@admin.route('/sd_admin_Tadmin_iframe/<string:id>', endpoint='sd_admin_Tadmin_iframe')
@admin_auth
def sd_admin_Tadmin_iframe(id):
    data = {}
    admin = Admin.query.get(id)
    data['user'] = admin
    data['type'] = '管理员'
    return render_template('admin/admin_detail_iframe.html', **data)


# 管理员 - 权限管理 - 修改管理员 - 接口
@admin.route('/sd_admin_Tadmin_update_port', endpoint='sd_admin_Tadmin_update_port', methods=['POST'])
@admin_auth
def sd_admin_Tadmin_update_port():
    name = request.form.get('name')
    id = request.form.get('id')
    phone = request.form.get('phone')
    password = request.form.get('password')
    email = request.form.get('email')
    is_use = request.form.get('is_use')

    admin = Admin.query.get(id)
    admin.name = name
    admin.phone = phone
    admin.password = password
    admin.email = email
    admin.is_use = is_use

    try:
        db.session.add(admin)
        db.session.commit()
        return jsonify({'code': 200, 'msg': '修改成功'})
    except:
        db.session.rollback()
        db.session.flush()
        return jsonify({'code': 201, 'msg': '修改失败'})


# 管理员 - 权限管理 - 添加管理员 - 接口
@admin.route('/sd_admin_Tadmin_add_port', endpoint='sd_admin_Tadmin_add_port', methods=['POST'])
@admin_auth
def sd_admin_Tadmin_add_port():
    name = request.form.get('name')
    phone = request.form.get('phone')
    password = request.form.get('password')
    email = request.form.get('email')

    admin = Admin()
    admin.name = name
    admin.phone = phone
    admin.password = password
    admin.email = email
    admin.is_use = 1


    try:
        db.session.add(admin)
        db.session.commit()
        return jsonify({'code': 200, 'msg': '添加成功'})
    except:
        db.session.rollback()
        db.session.flush()
        return jsonify({'code': 201, 'msg': '添加失败'})
