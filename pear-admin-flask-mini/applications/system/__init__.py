from flask import Blueprint

from common import register_api
from .file import FilePhotoAPI
from .passport import LoginAPI


def register_sys_api(api_bp):
    register_api(LoginAPI, 'login_api', '/passport/login', pk='_id', app=api_bp)
    register_api(FilePhotoAPI, 'photo_api', '/file/photo/', pk='photo_id', app=api_bp)
