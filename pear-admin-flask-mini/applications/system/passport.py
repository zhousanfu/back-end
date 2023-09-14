from flask import render_template, make_response
from flask import session, redirect, url_for
from flask.views import MethodView
from flask_login import current_user, login_user
from flask_pydantic import validate
from pydantic import BaseModel

from common.gen_captcha import add_auth_session
from common.utils.http import fail_api, success_api
from common.utils.rights import record_logging
from models import UserModel


class LoginModel(BaseModel):
    username: str
    password: str
    captcha: str


class LoginAPI(MethodView):

    def get(self):
        if current_user.is_authenticated:
            return redirect(url_for('admin.index'))
        return make_response(render_template('index/login.html'))

    @validate()
    def post(self, body: LoginModel):
        s_code = session.get("code", None)
        session["code"] = None

        if body.captcha != s_code:
            return fail_api(message="验证码错误")
        user = UserModel.query.filter_by(username=body.username).first()

        if user is None:
            return fail_api(message="不存在的用户")

        if user.enable == 0:
            return fail_api(message="用户被暂停使用")

        if user.validate_password(body.password):
            # 登录
            login_user(user)
            # 记录登录日志
            record_logging()

            # 存入权限
            add_auth_session()
            return success_api(message="登录成功")
        record_logging()
        return fail_api(message="用户名或密码错误")
