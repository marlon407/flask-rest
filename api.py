#!/usr/bin/env python
import os
import json
from flask import Flask, abort, request, jsonify, g, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from database import db_session, init_db
from config import config

from models.user import User
from models.category import Category
from models.page import Page

# initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = config['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = config['SQLALCHEMY_DATABASE_URI']
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

# extensions
auth = HTTPBasicAuth()

#@app.teardown_appcontext
#def shutdown_session(exception=None):
    #db_session.remove()

@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.route('/api/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)    # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        abort(400)    # existing user
    user = User(username=username)
    user.hash_password(password)
    db_session.add(user)
    db_session.commit()
    return (jsonify({'username': user.username}), 201,
            {'Location': url_for('get_user', id=user.id, _external=True)})


@app.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})


@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 3600})


@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.username})

@app.route('/api/categories', methods=['POST'])
@auth.login_required
def new_category():
	print request
	name = request.json.get('name')
	if Category.query.filter_by(name=name).first() is not None:
		abort(400)    # existing user
	cat = Category(name=name)
	cat.likes = 0
	cat.views = 0
	cat.user = g.user.id
	db_session.add(cat)
	db_session.commit()
	return (jsonify({'name': cat.name}), 201,
		{'Location': url_for('get_category', id=cat.id, _external=True)})

@app.route('/api/categories/<int:id>')
def get_category(id):
    cat = Category.query.get(id)
    pages = Page.query.filter_by(category=cat.id)
    if not cat:
        abort(400)
    return jsonify({"category":cat.serialize,"pages":[i.serialize for i in pages] })

@app.route('/api/categories')
@auth.login_required
def get_categories():
	#categories = Category.query.all()
    categories = Category.query.filter_by(user=g.user.id)
    return jsonify(json_list=[i.serialize for i in categories])

@app.route('/api/pages', methods=['POST'])
@auth.login_required
def new_page():
	title = request.json.get('title')
	if Page.query.filter_by(title=title).first() is not None:
		abort(400)    # existing user
	page = Page(title=title)
	page.views = request.json.get('views')
	page.category = request.json.get('category')
	page.user = g.user.id
	page.url = request.json.get('url')
	db_session.add(page)
	db_session.commit()
	return (jsonify({'title': page.title}), 201,
		{'Location': url_for('get_page', id=page.id, _external=True)})

@app.route('/api/pages/<int:id>')
def get_page(id):
    page = Page.query.get(id)
    if not page:
        abort(400)
    return jsonify({'title': page.title, 'views': page.views, 'url': page.url})

@app.route('/api/pages')
@auth.login_required
def get_pages():
	pages = Page.query.filter_by(user=g.user.id)
	#pages = Page.query.all()
	return jsonify(json_list=[i.serialize for i in pages])

@app.route('/api/pages/<int:id>', methods=['DELETE'])
def delete_page(id):
    page = Page.query.get(id)
    if not page:
        abort(400)
	page.delete()
	db_session.delete(page)
	db_session.commit()
    return jsonify({'deleted': "true"})


if __name__ == '__main__':
	init_db()
	app.run(debug=True)
