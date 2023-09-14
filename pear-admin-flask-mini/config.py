#!python3.10
# coding=utf-8
'''
 Author: Sanfor Chow
 Date: 2023-09-14 21:10:21
 LastEditors: Sanfor Chow
 LastEditTime: 2023-09-14 21:10:22
 FilePath: /back-end/pear-admin-flask-mini/templates/config.py
'''
import logging
import os

# 主题面板的链接列表配置
SYSTEM_NAME = "Pear Admin"
SYSTEM_PANEL_LINKS = [
    {
        "icon": "layui-icon layui-icon-auz",
        "title": "官方网站",
        "href": "http://www.pearadmin.com"
    },
    {
        "icon": "layui-icon layui-icon-auz",
        "title": "开发文档",
        "href": "http://www.pearadmin.com"
    },
    {
        "icon": "layui-icon layui-icon-auz",
        "title": "开源地址",
        "href": "https://gitee.com/Jmysy/Pear-Admin-Layui"
    }
]

SECRET_KEY = os.getenv('SECRET_KEY', 'dev key')

# mysql 配置
MYSQL_USERNAME = "root"
MYSQL_PASSWORD = "123456"
MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3306
MYSQL_DATABASE = "PearAdminFlask"

# redis 配置
REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379

""" Sqlalchemy 配置 """
SQLALCHEMY_DATABASE_URI = r'sqlite:///pear_admin.db'
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_ECHO = False
SQLALCHEMY_POOL_RECYCLE = 8
# SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@\
#                             {MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

LOG_LEVEL = logging.ERROR

# 图片文件存放位置
UPLOADED_PHOTOS_DEST = os.path.join(os.path.dirname(os.path.abspath(__name__)), 'static', 'upload')
UPLOADED_FILES_ALLOW = ['gif', 'jpg']
# JSON配置
JSON_AS_ASCII = False
