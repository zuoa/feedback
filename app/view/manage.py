# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request, redirect, url_for, session, g, flash, jsonify
from sqlalchemy.exc import IntegrityError
from app.util import *
from app.model.issue.user import User
from app.model.issue.issue import Team
from app import db
import json


mod = Blueprint('manage', __name__, url_prefix='/manage')


@mod.route('/')
@login_required
def manage():
    if g.user.is_admin:
        return redirect(url_for('manage.super'))
    else:
        return redirect(url_for('issue.index'))


@mod.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        user = User.query.filter_by(number=request.form['number']).filter_by(
            password=get_encrypt_passwd(request.form['password'])).first()
        if not user:
            flash(u"工号或密码错误，请重新输入")
            return redirect(url_for('manage.login'))

        session['number'] = request.form['number']
        g.user = user
        return redirect(url_for('manage.manage'))
    else:
        return render_template('manage/login.html')
@mod.route('/logout')
def logout():
    session.clear()
    g.user = None
    return render_template('manage/login.html')

@mod.route('/user/<uid>', methods=['GET', 'POST'])
@login_required
def user(uid):
    if int(uid) != g.user.id and not g.user.is_admin:
        return "Nop"

    if request.method == 'POST':

        return redirect(url_for('manage.manage'))
    else:
        user = User.query.filter_by(id=uid).first()
        return render_template('manage/user.html', user=user)


@mod.route('/super')
@admin_required
def super():
    users = User.query.all()
    teams = Team.query.all()
    return render_template('manage/super.html', users=users, teams=teams)


@mod.route('/user/add', methods=['POST'])
@login_required
def user_add():
    try:
        user = User(request.form.get("name", ""), request.form.get("number", ""),
                    get_encrypt_passwd(request.form.get("password", "")))
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        return jsonify(code=1, msg=u"该工号已被注册")
    except Exception as e:
        return jsonify(code=1, msg=e.message)

    return jsonify(code=0, msg="")


@mod.route('/user/<uid>/edit', methods=['POST'])
@login_required
def user_edit(uid):
    user = User.query.filter_by(id=uid).first()
    passwd = request.form.get('password', '')
    if passwd:
        user.password = get_encrypt_passwd(passwd)
    user.name = request.form['name']
    db.session.commit()
    return jsonify(code=0, msg="")


@mod.route('/user/<uid>/del')
@login_required
def user_del(uid):
    user = User.query.filter_by(id=uid).first()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('manage.super'))


@mod.route('/team/<tid>')
@admin_required
def team(tid):
    team = Team.query.filter_by(id=tid).first()
    users = User.query.all()
    return render_template('manage/team.html', team=team, users=users)

@mod.route('/team/add', methods=['POST'])
@login_required
def team_add():
    try:
        team = Team(request.form.get("name", ""), request.form.get("manager", 1))
        db.session.add(team)
        db.session.commit()
    except Exception as e:
        return jsonify(code=1, msg=e.message)

    return jsonify(code=0, msg="")


@mod.route('/team/<tid>/edit', methods=['POST'])
@login_required
def team_edit(tid):
    team = Team.query.filter_by(id=tid).first()
    team.name = request.form['name']
    team.manager_id = request.form['manager']
    db.session.commit()
    return jsonify(code=0, msg="")


@mod.route('/team/<tid>/del')
@admin_required
def team_del(tid):
    team = Team.query.filter_by(id=tid).first()
    db.session.delete(team)
    db.session.commit()
    return redirect(url_for('manage.super'))