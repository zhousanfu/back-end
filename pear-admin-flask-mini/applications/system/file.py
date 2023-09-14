from flask import request, jsonify
from flask.views import MethodView
from sqlalchemy import desc

from common.utils.http import fail_api, success_api, table_api
from common.utils.upload import upload_one, delete_photo_by_id
from models import PhotoModel


class FilePhotoAPI(MethodView):

    def get(self, photo_id):
        if photo_id is None:
            page = request.args.get('page', type=int, default=1)
            limit = request.args.get('limit', type=int, default=10)
            photo_paginate = PhotoModel.query.order_by(
                desc(PhotoModel.create_at)).paginate(
                page=page, per_page=limit, error_out=False)
            data = [
                {
                    'id': item.id,
                    'name': item.name,
                    'href': item.href,
                    'mime': item.mime,
                    'size': item.size,
                    'ext': item.ext if hasattr(item, 'ext') else "",
                    'create_at': str(item.create_at),
                } for item in photo_paginate.items
            ]
            return table_api(
                result={
                    'items': data,
                    'total': photo_paginate.total,
                },
                code=0)
        else:
            # 显示一张图片
            item = PhotoModel.query.get(photo_id)
            return table_api(
                result={
                    'items': {
                        'id': item.id,
                        'name': item.name,
                        'href': item.href,
                        'mime': item.mime,
                        'size': item.size,
                        'ext': item.ext if hasattr(item, 'ext') else "",
                        'create_at': str(item.create_at),
                    },
                    'total': 1,
                },
                code=0
            )

    def post(self):
        if 'file' in request.files:
            photo = request.files['file']
            mime = request.files['file'].content_type
            file_url = upload_one(photo=photo, mime=mime)

            res = {
                "message": "上传成功",
                "code": 0,
                "success": True,
                "data": {"src": file_url},
            }
            return jsonify(res)
        return fail_api()

    def delete(self, photo_id):
        res = delete_photo_by_id(photo_id)
        if res:
            return success_api(message="删除成功")
        else:
            return fail_api(message="删除失败")

    def put(self, photo_id):
        pass
