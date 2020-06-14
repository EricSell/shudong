import base64
import random
from functools import wraps

from captcha.image import ImageCaptcha
from flask import session, redirect, url_for

from App.exts import cache


# 生成验证码
from App.models import Admin, Teacher


def make_vcode():
    str_list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
                'v', 'w', 'x', 'y', 'z',
                '', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
                'V', 'W', 'X', 'Y', 'Z']
    chars = ''.join(random.choices(str_list, k=4))
    print(chars)
    cache.set('vcode', chars, timeout=300)
    image = ImageCaptcha().generate_image(chars)
    image.save('vcode.jpg')
    with open('vcode.jpg', 'rb') as f:
        ls_f = base64.b64encode(f.read()).decode()
    return ls_f


# 用户 —— 登录验证
def user_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 参数检查，判断是否用户登录并无停用，如果有，直接执行函数的功能
        sess = session.get('user')
        if sess is None:
            return redirect(url_for('shudong.user_login'))
        return func(*args, **kwargs)

    return wrapper

# 管理员身份
def get_info():
    admin = session.get('admin')
    # admin_type -> 0是心理老师, 1是超级管理员

    admin_type = admin.get('type')
    if int(admin_type) == 1:
        admin_info = Admin.query.get(admin.get('id'))
    else:
        admin_info = Teacher.query.get(admin.get('id'))

    admin_info.admin_type = admin_type
    data = {
        'admin_info':admin_info
    }
    return data

# 管理员，导师 —— 登录验证
def admin_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 参数检查，判断是否用户登录并无停用，如果有，直接执行函数的功能
        sess = session.get('admin')
        if sess is None:
            return redirect(url_for('admin.sd_admin_login'))
        admin_id = sess.get('id')
        is_use = Admin.query.get(admin_id).is_use
        if not is_use:
            session['is_user'] = 0
            return redirect(url_for('admin.sd_admin_login'))

        return func(*args, **kwargs)

    return wrapper
