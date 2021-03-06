# -*- coding: utf-8 -*-
from functools import wraps
from flask import g, request, redirect, url_for,abort
import hashlib, time
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('manage.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return "You are not login, man."
        if not g.user.is_admin :
            return "You are not admin, man."
        return f(*args, **kwargs)
    return decorated_function


def require_issue_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        sid = kwargs.get("sid", None)
        if sid is None:
            return "Unknown Issue"
        if g.user is None:
            return redirect(url_for('manage.login', next=request.url))

        if g.user.is_admin:
            return f(*args, **kwargs)

        from model.issue.issue import Issue,Team
        issue = Issue.query.filter_by(id=sid).first()
        if not issue:
            return "Unknown Issue"
        team = Team.query.filter_by(id=issue.team_id).first()

        if team in g.user.teams:
            return f(*args, **kwargs)
        else:
            abort(401)

    return wrapper

def get_encrypt_passwd(p):
    md5 = hashlib.md5()
    md5.update(p)
    e1 = md5.hexdigest()
    md5.update("/")
    md5.update(e1)
    return md5.hexdigest()


def data_format(data):
    formats = ["%Y/%m/%d", "%Y-%m-%d",u"%Y年%m月%d"]
    st = None

    for format in formats:
        try:
            st = time.strptime(data,format)
        except:
            continue

        if st:
            break;

    return st
