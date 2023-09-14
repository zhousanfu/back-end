#!python3.10
# coding=utf-8
'''
 Author: Sanfor Chow
 Date: 2023-09-14 20:32:22
 LastEditors: Sanfor Chow
 LastEditTime: 2023-09-14 20:34:28
 FilePath: /back-end/app.py
'''
# -*- coding: utf-8 -*-
# @Author  : Liqiju
# @Time    : 2022/5/1 2:45
# @File    : app.py
# @Software: PyCharm
import pymysql
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import make_response,request
from flask_cors import CORS
pymysql.install_as_MySQLdb()
 
app = Flask(__name__)
# ------------------database----------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost:3306/books'
# 指定数据库文件
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# 允许修改跟踪数据库
db = SQLAlchemy(app)
# 解决浏览器浏览器访问输出乱码问题
app.config['JSON_AS_ASCII'] = False
CORS(app, resources=r'/*', supports_credentials=True)

@app.after_request
def after(resp):
    resp = make_response(resp)
    resp.headers['Access-Control-Allow-Origin'] = '*'  # 允许跨域地址
    resp.headers['Access-Control-Allow-Methods'] = '*'  # 请求 ‘*’ 就是全部
    resp.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'  # 头部
    resp.headers['Access-Control-Allow-Credentials'] = 'True'
    return resp

class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True, comment='自动递增id，唯一键')
    title = db.Column(db.String(80), nullable=False, comment='书名')
    author = db.Column(db.String(120), nullable=False, comment='作者')
    read_status = db.Column(db.Boolean, comment='阅读状态，0未读，1已读') # bool的True和False是数值1和0

# 增加数据
def insert_data(title, author, read_status):
    book = Books(title=title, author=author, read_status=read_status)
    db.session.add_all([book])
    db.session.commit()

# 查询所有
def select_data_all():
    book_list = []
    books = Books.query.all()
    # 类似于 select * from Books
 
    for s in books:
        dic = {}
        dic['id'] = s.id
        dic['title'] = s.title
        dic['author'] = s.author
        dic['read_status'] = s.read_status
        book_list.append(dic)
    return book_list

# 通过id查询
def select_data_by_id(id):
    book_list = []
    book = Books.query.get(id)
    if not book:
        return False
    dic = {}
    dic['id'] = book.id
    dic['title'] = book.title
    dic['author'] = book.author
    dic['read_status'] = book.read_status
    book_list.append(dic)
    return book_list

# 通过id删除数据
def delete_data(id):
    # 类似于 select * from Books where id = id
    delete_id = Books.query.get(id)
    if not delete_id:
        return False
    db.session.delete(delete_id)
    db.session.commit()
    # 提交操作到数据库

# 修改数据
def update_data(id, title='', author='', read_status=''):
    book = Books.query.get(id)
    if not title == '':
        book.title = title
    if not author == '':
        book.author = author
    if not read_status == '':
        book.read_status = read_status
    db.session.commit()


# 前端通过传参title、author、read_status增加书籍
@app.route('/add', methods=['POST'])
def add():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        print('调用add方传过来的参数是', post_data)
        book_list = select_data_all()
        for i in range(len(book_list)):
            title_list = book_list[i]['title']
        if post_data.get('title') in title_list:
            response_object['message'] = '书名（title）重复!'
            response_object["status"]= 'fail'
            return response_object
        if post_data.get('title') is None:
            response_object['message'] = 'title是必传参数!'
            response_object["status"]= 'fail'
            return response_object
        if post_data.get('author') is None:
            response_object['message'] = 'author是必传参数!'
            response_object["status"]= 'fail'
            return response_object
        if post_data.get('read_status') is None:
            response_object['message'] = 'read_status是必传参数!'
            response_object["status"]= 'fail'
            return response_object
        title = str(post_data.get('title')).strip(),
        author = str(post_data.get('author')).strip(),
        read_status = int(str(post_data.get('read_status')))# 前端传过来字符串处理为int
 
        if title[0] is None or title[0] is '':
            response_object['message'] = 'title不能为空!'
            response_object["status"] = 'fail'
            return response_object
        if author[0] is None or author[0] is '':
            response_object['message'] = '作者不能为空!'
            response_object["status"] = 'fail'
            return response_object
        if read_status != 0 and read_status != 1:
            response_object['message'] = '阅读状态只能为0和1!'
            response_object["status"] = 'fail'
            return response_object
        insert_data(title=title[0], author=author[0], read_status=read_status)
        response_object['message'] = '图书添加成功!'
    return response_object
 
# 前端通过传id删除书籍
@app.route('/delete', methods=['POST'])  # 改为post方法
def delete():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        print('调用delete方传过来的参数是：', post_data)
        if post_data.get('id') is None:
            response_object['message'] = 'id是必传参数!'
            response_object["status"]= 'fail'
            return response_object
        id = post_data.get('id')
        result = delete_data(id)  # 删除方法调用
        if result is False:
            response_object['message'] = '需要删除的图书不存在!'
            response_object["status"] = 'fail'
            return response_object
        else:
            response_object['message'] = '图书被删除!'
            return response_object
 
# 前端通过传参title、author、read_status修改书籍
@app.route('/update', methods=['POST'])
def update():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        print('调用update方传过来的参数是', post_data)
        if post_data.get('id') is None:
            response_object['message'] = 'id是必传参数!'
            response_object["status"]= 'fail'
            return response_object
        if post_data.get('title') is None:
            response_object['message'] = 'title是必传参数!'
            response_object["status"]= 'fail'
            return response_object
        if post_data.get('author') is None:
            response_object['message'] = 'author是必传参数!'
            response_object["status"]= 'fail'
            return response_object
        if post_data.get('read_status') is None:
            response_object['message'] = 'read_status是必传参数!'
            response_object["status"]= 'fail'
            return response_object
        # 查询所有数据
        book_list = select_data_all()
        # 拼接所有的id到列表
        print(book_list)
        #  这里的逻辑写错了，有bug，改一下
        book_id = []
        for i in range(len(book_list)):
            book_id.append(book_list[i]['id'])
        print('book_id是', book_id)
        # 判断书籍id在不在列表内
        if post_data.get('id') not in book_id and int(post_data.get('id')) not in book_id: #  这里也有bug，改一下
            response_object['message'] = '需要修改的图书id不存在!'
            response_object["status"]= 'fail'
            return response_object
        title = str(post_data.get('title')).strip(),
        author = str(post_data.get('author')).strip(),
        #print("处理前",post_data.get('read_status'))
        read_status = int(post_data.get('read_status'))  # 前端传过来字符串处理为int
        #print("处理后", read_status)
        if title[0] is None or title[0] is '':
            response_object['message'] = 'title不能为空!'
            response_object["status"] = 'fail'
            return response_object
        if author[0] is None or author[0] is '':
            response_object['message'] = '作者不能为空!'
            response_object["status"] = 'fail'
            return response_object
        if read_status != 0 and read_status != 1:
            response_object['message'] = '阅读状态只能为0和1!'
            response_object["status"] = 'fail'
            return response_object
 
        books_id = post_data.get('id')
        title = post_data.get('title')
        author = post_data.get('author')
        read_status = read_status
        # 这里原来的post_data.get('read_status')改为read_status，上面已经处理了
        update_data(id=books_id, title=title, author=author, read_status=read_status)
        response_object['message'] = '图书已更新!'
        return response_object

# 前端通过不传参默认查询所有书籍，传id查询对应书籍
@app.route('/query', methods=['POST'])
def query():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        print('调用query方传过来的参数是', post_data)
        # if post_data.get('id') is None:
        id = str(post_data.get('id')).strip()
        if id is None or id is '':
            books = select_data_all()
            response_object['message'] = '查询所有图书成功!'
            response_object['data'] = books
            return response_object
        # id = str(post_data.get('id')).strip()
        # if id is None or id is '':
        #     response_object['message'] = 'id不能为空!'
        #     response_object["status"] = 'fail'
        #     return response_object
        book = select_data_by_id(id)
        if book is False:
            response_object['message'] = '需要查询的图书不存在!'
            response_object["status"] = 'fail'
            return response_object
        else:
            response_object['message'] = '图书查询成功!'
            response_object['data'] = book
            return response_object

if __name__ == '__main__':
    app.run(debug=True, port=5001)
