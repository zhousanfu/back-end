#!python3.10
# coding=utf-8
'''
 Author: Sanfor Chow
 Date: 2023-09-17 19:35:55
 LastEditors: Sanfor Chow
 LastEditTime: 2023-09-17 20:22:01
 FilePath: /back-end/flask-orm/app.py
'''
from flask import Flask
from .model import db
from .view import docqc_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://SA:Admin@123@119.91.217.225/master'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)
app.register_blueprint(docqc_bp, url_prefix='/v1')



if __name__ == '__main__':
    app.run()