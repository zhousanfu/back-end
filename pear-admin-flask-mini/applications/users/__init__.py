from common import register_api
from .user import UserApi, user_role_resource, user_info


def register_users_api(api_bp):
    api_bp.add_url_rule('/users/user/<int:_id>/<action>',
                        view_func=user_info,
                        methods=['PUT'])

    register_api(UserApi, 'users_api', '/users/user/', pk='_id', app=api_bp)

    api_bp.add_url_rule('/users/user/<int:_id>/role',
                        view_func=user_role_resource,
                        methods=['PUT'])
