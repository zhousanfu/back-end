#!python3.10
# coding=utf-8
'''
 Author: Sanfor Chow
 Date: 2023-09-17 19:54:02
 LastEditors: Sanfor Chow
 LastEditTime: 2023-09-17 20:07:57
 FilePath: /back-end/flask-orm/views/view.py
'''
from flask import Blueprint, request, jsonify
from models.model import db, DocQcDocumen, DocQcSentence



docqc_bp = Blueprint('docqc', __name__)

@docqc_bp.route('/docqc', methods=['POST'])
def create_doc():
    '''
    description: 创建
    return {json}
    '''
    data = request.get_json()
    name = data.get('name')
    age = data.get('age')

    new_user = User(name=name, age=age)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'})

@docqc_bp.route('/docqc', methods=['GET'])
def get_all_docqc():
    docqc = User.query.all()
    result = []
    for user in docqc:
        user_data = {
            'id': user.id,
            'name': user.name,
            'age': user.age
        }
        result.append(user_data)

    return jsonify(result)

@docqc_bp.route('/docqc/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'})

    user_data = {
        'id': user.id,
        'name': user.name,
        'age': user.age
    }

    return jsonify(user_data)

@docqc_bp.route('/docqc/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'})

    data = request.get_json()
    name = data.get('name')
    age = data.get('age')

    user.name = name
    user.age = age
    db.session.commit()

    return jsonify({'message': 'User updated successfully'})

@docqc_bp.route('/docqc/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'})

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'User deleted successfully'})