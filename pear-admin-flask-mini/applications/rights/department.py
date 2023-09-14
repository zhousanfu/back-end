import typing as t

from flask import jsonify
from flask.views import MethodView
from flask_pydantic import validate
from pydantic import BaseModel, Field

from common.utils.http import success_api, fail_api
from extensions import db
from models import DepartmentModel, UserModel


class DeptModel(BaseModel):
    address: t.Optional[str]
    dept_name: t.Optional[str] = Field(alias='deptName')
    email: t.Optional[str]
    leader: t.Optional[str]
    parent_id: t.Optional[str] = Field(alias='parentId')
    phone: t.Optional[str]
    sort: t.Optional[int]
    status: t.Optional[int]


class DepartmentsApi(MethodView):

    def get(self, _id):
        if _id:
            dept = DepartmentModel.query.filter_by(id=_id).first()
            dept_data = {
                'id': dept.id,
                'dept_name': dept.dept_name,
                'leader': dept.leader,
                'email': dept.email,
                'phone': dept.phone,
                'status': dept.status,
                'sort': dept.sort,
                'address': dept.address,
            }
            return dict(success=True, message='ok', dept=dept_data)

        dept_data = DepartmentModel.query.order_by(DepartmentModel.sort).all()
        # TODO dtree 需要返回状态信息
        res = {
            "status": {"code": 200, "message": "默认"},
            "data": [
                {
                    'deptId': item.id,
                    'parentId': item.parent_id,
                    'deptName': item.dept_name,
                    'sort': item.sort,
                    'leader': item.leader,
                    'phone': item.phone,
                    'email': item.email,
                    'status': item.status,
                    'comment': item.comment,
                    'address': item.address,
                    'create_at': item.create_at.strftime('%Y-%m-%d %H:%M:%S')
                } for item in dept_data
            ]
        }
        return jsonify(res)

    @validate()
    def post(self, body: DeptModel):
        dept = DepartmentModel(
            parent_id=body.parent_id,
            dept_name=body.dept_name,
            sort=body.sort,
            leader=body.leader,
            phone=body.phone,
            email=body.email,
            status=body.status,
            address=body.address
        )
        db.session.add(dept)
        db.session.commit()

        return success_api(message="成功")

    @validate()
    def put(self, _id, body: DeptModel):
        data = {
            "dept_name": body.dept_name,
            "sort": body.sort,
            "leader": body.leader,
            "phone": body.phone,
            "email": body.email,
            "status": body.status,
            "address": body.address
        }
        body = DepartmentModel.query.filter_by(id=_id).update(data)
        if not body:
            return fail_api(message="更新失败")
        db.session.commit()
        return success_api(message="更新成功")

    def delete(self, _id):
        ret = DepartmentModel.query.filter_by(id=_id).delete()
        UserModel.query.filter_by(dept_id=_id).update({"dept_id": None})
        db.session.commit()
        if ret:
            return success_api(message="删除成功")
        return fail_api(message="删除失败")


class DeptEnableAPI(MethodView):
    def put(self, _id):
        d = DepartmentModel.query.get(_id)
        if d:
            d.status = not d.status
            db.session.commit()
            message = '修改成功'
            return success_api(message=message)
        return fail_api(message="出错啦")
