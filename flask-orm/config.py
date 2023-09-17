#!python3.10
# coding=utf-8
'''
 Author: Sanfor Chow
 Date: 2023-09-17 20:39:45
 LastEditors: Sanfor Chow
 LastEditTime: 2023-09-17 20:39:46
 FilePath: /back-end/flask-orm/config.py
'''
from datetime import timedelta


class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = ''

    APP_NAME = 'ApplicationName'
    SECRET_KEY = 'add_secret'
    JWT_EXPIRATION_DELTA = timedelta(days=30)
    JWT_AUTH_URL_RULE = '/api/v1/auth'
    SECURITY_REGISTERABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_TRACKABLE = True
    SECURITY_PASSWORD_HASH = 'sha512_crypt'
    SECURITY_PASSWORD_SALT = 'add_salt'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://username:password@localhost/db'


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data.sqlite'
    DEBUG = True


class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    TESTING = True