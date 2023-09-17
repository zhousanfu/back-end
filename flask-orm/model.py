#!python3.10
# coding=utf-8
'''
 Author: Sanfor Chow
 Date: 2023-09-17 19:52:55
 LastEditors: Sanfor Chow
 LastEditTime: 2023-09-17 20:23:52
 FilePath: /back-end/flask-orm/model.py
'''
import os
import sys
from flask_sqlalchemy import SQLAlchemy
from .app import app



db = SQLAlchemy(app)


class DocQcDocumen(db.Model):
    __tablename__ = 'doc_qc_documen'
    doc_id = db.Column(db.Integer, primary_key=True)
    doc_title = db.Column(db.String(64), nullable=False)


class DocQcSentence(db.Model):
    __tablename__ = 'doc_qc_sentence'
    sen_id = db.Column(db.Integer, primary_key=True)
    doc_id = db.Column(db.Integer, db.ForeignKey('doc_qc_documen.id'), nullable=False)
    sen_txt = db.Column(db.Text, nullable=False)
