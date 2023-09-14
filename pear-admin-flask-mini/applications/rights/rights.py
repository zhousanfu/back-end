import copy
from collections import OrderedDict
from typing import Optional

from flask import request, jsonify, current_app
from flask.views import MethodView
from flask_login import current_user
from flask_pydantic import validate
from pydantic import BaseModel, Field

from common.utils.http import success_api, fail_api
from extensions import db
from models import RightModel, RoleModel


def get_render_config():
    # 网站配置
    config = {
        'logo': {
            # 网站名称
            "title": current_app.config.get("SYSTEM_NAME"),
            # 网站图标
            "image": "/static/admin/admin/images/logo.png"
            # 菜单配置
        },
        'menu': {
            # 菜单数据来源
            "data": "/api/v1/rights/menu",
            "collaspe": True,
            # 是否同时只打开一个菜单目录
            "accordion": True,
            "method": "GET",
            # 是否开启多系统菜单模式
            "control": False,
            # 默认选中的菜单项
            "select": "0",
            # 是否开启异步菜单，false 时 data 属性设置为菜单数据，false 时为 json 文件或后端接口
            "async": True
        },
        'tab': {
            # 是否开启多选项卡
            "muiltTab": True,
            # 切换选项卡时，是否刷新页面状态
            "keepState": True,
            # 是否开启 Tab 记忆
            "session": True,
            # 最大可打开的选项卡数量
            "tabMax": 30,
            "index": {
                # 标识 ID , 建议与菜单项中的 ID 一致
                "id": "10",
                # 页面地址
                "href": "/admin/welcome",
                # 标题
                "title": "首页"
            }
        },
        'theme': {
            # 默认主题色，对应 colors 配置中的 ID 标识
            "defaultColor": "2",
            # 默认的菜单主题 dark-theme 黑 / light-theme 白
            "defaultMenu": "dark-theme",
            # 是否允许用户切换主题，false 时关闭自定义主题面板
            "allowCustom": True
        },
        'colors': [
            {
                "id": "1",
                "color": "#2d8cf0"
            },
            {
                "id": "2",
                "color": "#5FB878"
            },
            {
                "id": "3",
                "color": "#1E9FFF"
            },
            {
                "id": "4",
                "color": "#FFB800"
            },
            {
                "id": "5",
                "color": "darkgray"
            },
        ],
        'links': current_app.config.get("SYSTEM_PANEL_LINKS"),
        'other': {
            # 主页动画时长
            "keepLoad": 1200,
            # 布局顶部主题
            "autoHead": False
        },
        'header': False
    }
    return config


# 生成菜单树
def make_menu_tree():
    role = current_user.role
    powers = []
    for i in role:
        # 如果角色没有被启用就直接跳过
        if i.enable == 0:
            continue
        # 变量角色用户的权限
        for p in i.power:
            # 如果权限关闭了就直接跳过
            if p.enable == 0:
                continue
            # 一二级菜单
            if p.type == 0 or p.type == 1:
                powers.append(p)

    power_dict = [
        {
            'id': item.id,
            'title': item.name,
            'type': item.type,
            'code': item.code,
            'href': item.url,
            'openType': item.open_type,
            'parent_id': item.parent_id,
            'icon': item.icon,
            'sort': item.sort,
            'enable': item.enable,
        } for item in powers
    ]
    power_dict.sort(key=lambda x: x['id'], reverse=True)

    menu_dict = OrderedDict()
    for _dict in power_dict:
        if _dict['id'] in menu_dict:
            # 当前节点添加子节点
            _dict['children'] = copy.deepcopy(menu_dict[_dict['id']])
            _dict['children'].sort(key=lambda item: item['sort'])
            # 删除子节点
            del menu_dict[_dict['id']]

        if _dict['parent_id'] not in menu_dict:
            menu_dict[_dict['parent_id']] = [_dict]
        else:
            menu_dict[_dict['parent_id']].append(_dict)

    return sorted(menu_dict.get(0), key=lambda item: item['sort'])


class PowerModel(BaseModel):
    icon: str
    open_type: Optional[str] = Field(alias='openType')
    parent_id: Optional[str] = Field(alias='parentId')
    power_code: Optional[str] = Field(alias='powerCode')
    power_name: Optional[str] = Field(alias='powerName')
    power_type: Optional[str] = Field(alias='powerType')
    power_url: Optional[str] = Field(alias='powerUrl')
    sort: Optional[int] = Field(alias='sort')


class RightsApi(MethodView):
    def get(self):
        """获取选择父节点"""

        power = RightModel.query.all()
        # power_data = marshal(power, RightModel.fields())
        power_data = [
            {
                'powerId': item.id,
                'powerName': item.name,
                'powerType': item.type,
                'powerUrl': item.url,
                'openType': item.open_type,
                'parentId': item.parent_id,
                'icon': item.icon,
                'sort': item.sort,
                'enable': item.enable,
            } for item in power
        ]
        power_data.append({"powerId": 0, "powerName": "顶级权限", "parentId": -1})
        res = {
            "status": {"code": 200, "message": "默认"},
            "data": power_data
        }
        return res

    def delete(self):
        ids = request.form.getlist('ids[]')
        for id in ids:
            role = RoleModel.query.filter_by(id=id).first()
            # 删除该角色的权限和用户
            role.power = []
            role.user = []

            r = RoleModel.query.filter_by(id=id).delete()
            db.session.commit()
        return success_api(message="批量删除成功")


class PowerApi(MethodView):
    @validate()
    def post(self, body: PowerModel):
        power = RightModel(
            icon=body.icon,
            open_type=body.open_type,
            parent_id=body.parent_id,
            code=body.power_code,
            name=body.power_name,
            type=body.power_type,
            url=body.power_url,
            sort=body.sort,
            enable=1
        )
        try:
            db.session.add(power)
            db.session.commit()
        except Exception as e:
            print(e)
            return fail_api(message='数据提交失败')

        return success_api(message="成功")

    def delete(self, _id):
        # 删除权限（目前没有判断父节点自动删除子节点）
        power = RightModel.query.filter_by(id=_id).first()
        role_id_list = []
        roles = power.role
        for role in roles:
            role_id_list.append(role.id)
        roles = RoleModel.query.filter(RoleModel.id.in_(role_id_list)).all()
        for p in roles:
            power.role.remove(p)
        r = RightModel.query.filter_by(id=_id).delete()
        db.session.commit()

        if r:
            return success_api(message="删除成功")
        else:
            return fail_api(message="删除失败")

    @validate()
    def put(self, _id, body: PowerModel):
        data = {
            "icon": body.icon,
            "open_type": body.open_type,
            "parent_id": body.parent_id,
            "code": body.power_code,
            "name": body.power_name,
            "type": body.power_type,
            "url": body.power_url,
            "sort": body.sort
        }
        power = RightModel.query.filter_by(id=_id).update(data)
        db.session.commit()

        if not power:
            return fail_api(message="更新权限失败")
        return success_api(message="更新权限成功")


def right_power_enable_resource(_id, action):
    power = RightModel.query.get(_id)
    if power:
        power.enable = not power.enable
        db.session.commit()
        message = "修改成功"
        return success_api(message=message)
    else:
        return fail_api(message="出错啦")


def admin_configs_resource():
    return get_render_config()


def admin_menu_resource():
    menu_tree = make_menu_tree()
    return jsonify(menu_tree)
