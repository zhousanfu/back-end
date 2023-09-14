from common import register_api
from .department import DepartmentsApi, DeptEnableAPI
from .rights import (
    RightsApi, PowerApi, right_power_enable_resource,
    admin_configs_resource, admin_menu_resource
)
from .roles import RoleRoleApi, RolePowerApi, role_deletes, role_enable_resource


def register_rights_api(api_bp):
    register_api(DepartmentsApi, 'rights_dept_api', '/dept/department/', pk='_id', app=api_bp)
    api_bp.add_url_rule('/dept/department/<int:_id>/status',
                        view_func=DeptEnableAPI.as_view('dept_status_api'),
                        methods=['PUT', ])
    api_bp.add_url_rule('/rights/rights',
                        view_func=RightsApi.as_view('dept_rights_api'),
                        methods=['GET', 'DELETE'])

    register_api(PowerApi, 'rights_power_api', '/rights/power/', pk='_id', app=api_bp)
    api_bp.add_url_rule('/rights/configs',
                        endpoint='rights_config_api',
                        view_func=admin_configs_resource,
                        methods=['GET'])
    api_bp.add_url_rule('/rights/menu',
                        endpoint='rights_menu_api',
                        view_func=admin_menu_resource,
                        methods=['GET'])
    api_bp.add_url_rule('/rights/power/<int:_id>/<action>',
                        endpoint='rights_power_action_api',
                        view_func=right_power_enable_resource,
                        methods=['PUT'])
    api_bp.add_url_rule('/roles/role',
                        endpoint='rights_roles_role_api',
                        view_func=role_deletes,
                        methods=['DELETE'])

    register_api(RoleRoleApi, 'rights_role_api', '/roles/role/', pk='_id', app=api_bp)
    register_api(RolePowerApi, 'rights_role_power_api', '/roles/role_power/', pk='_id', app=api_bp)
    api_bp.add_url_rule('/roles/role/<int:_id>/status',
                        endpoint='rights_roles_enable_api',
                        view_func=role_enable_resource,
                        methods=['PUT'])
