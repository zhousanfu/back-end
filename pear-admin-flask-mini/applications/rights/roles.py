from flask import request
from flask.views import MethodView

from common.utils.http import table_api, success_api, fail_api
from extensions import db
from models import RightModel, RoleModel


def role_deletes():
    ids = request.form.getlist('ids[]')
    for id in ids:
        role = RoleModel.query.filter_by(id=id).first()
        # 删除该角色的权限和用户
        role.power = []
        role.user = []

        r = RoleModel.query.filter_by(id=id).delete()
        db.session.commit()
    return success_api(message="批量删除成功")


class RoleRoleApi(MethodView):

    def get(self, _id):
        if not _id:
            page = request.args.get('page', default=1, type=int)
            limit = request.args.get('limit', default=10, type=int)
            role_name = request.args.get('roleName', default="", type=str)
            role_code = request.args.get('roleCode', default="", type=str)

            filters = []
            if role_name:
                filters.append(RoleModel.name.like('%' + role_name + '%'))
            if role_code:
                filters.append(RoleModel.code.like('%' + role_code + '%'))

            paginate = RoleModel.query.filter(*filters).paginate(page=page, per_page=limit, error_out=False)

            return table_api(
                result={
                    'items': [{'id': item.id,
                               'roleName': item.name,
                               'roleCode': item.code,
                               'enable': item.enable,
                               'comment': item.comment,
                               'details': item.details,
                               'sort': item.sort,
                               } for item in paginate.items],
                    'total': paginate.total}
                , code=0)

    def post(self):
        # TODO 添加校验
        details = request.json.get('details', '')
        enable = request.json.get('enable', 0)
        role_code = request.json.get('roleCode', '')
        role_name = request.json.get('roleName', '')
        sort = request.json.get('sort', 0)

        role = RoleModel(
            details=details,
            enable=int(enable),
            code=role_code,
            name=role_name,
            sort=int(sort)
        )
        db.session.add(role)
        db.session.commit()
        return success_api(message="成功")

    # 更新角色
    def put(self, _id):
        # TODO 添加校验
        role_code = request.json.get('roleCode', 0)
        role_name = request.json.get('roleName', '')
        sort = request.json.get('sort', 0)  # int
        enable = request.json.get('enable', 0)  # int
        details = request.json.get('details', '')

        data = {
            "code": role_code,
            "name": role_name,
            "sort": sort,
            "enable": enable,
            "details": details
        }

        role = RoleModel.query.filter_by(id=_id).update(data)
        db.session.commit()
        if not role:
            return fail_api(message="更新角色失败")
        return success_api(message="更新角色成功")


def role_enable_resource(_id):
    """启用用户"""
    ret = RoleModel.query.get(_id)
    ret.enable = not ret.enable
    db.session.commit()

    message = "修改成功"
    if not ret:
        return fail_api(message="出错啦")
    return success_api(message=message)


class RolePowerApi(MethodView):

    def get(self, _id):
        # 获取角色权限
        role = RoleModel.query.filter_by(id=_id).first()
        # 获取权限列表的 id
        check_powers_list = [rp.id for rp in role.power]
        powers = RightModel.query.all()  # 获取所有的权限
        powers = [
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
            } for item in powers]
        for i in powers:
            if int(i.get("powerId")) in check_powers_list:
                i["checkArr"] = "1"
            else:
                i["checkArr"] = "0"
        return {
            "data": powers,
            "status": {"code": 200, "message": "默认"}
        }

    # 保存角色权限
    def put(self, _id):
        power_ids = request.json.get('powerIds', '')

        power_list = power_ids.split(',')

        """ 更新角色权限 """
        role = RoleModel.query.filter_by(id=_id).first()
        powers = RightModel.query.filter(RightModel.id.in_(power_list)).all()
        role.power = powers

        db.session.commit()
        return success_api(message="授权成功")

    # 角色删除
    def delete(self, _id):
        role = RoleModel.query.filter_by(id=_id).first()
        # 删除该角色的权限和用户
        role.power = []
        role.user = []

        r = RoleModel.query.filter_by(id=_id).delete()
        db.session.commit()
        if not r:
            return fail_api(message="角色删除失败")
        return success_api(message="角色删除成功")
