from functools import wraps

import conjur
from flask import request, jsonify

from util import send_audit_event


def check_auth(username, password):
    """
    This function is called to check if a username/password combination is valid.
    """
    request.user = username

    api = conjur.new_from_key(username, password)
    try:
        api.authenticate()
    except conjur.ConjurException:
        return False

    send_audit_event(username, 'login', True)
    return True


def authenticate():
    """
    Sends a 401 response that enables basic auth
    """
    return jsonify(error='Authentication required'), 401, {'WWW-Authenticate': 'Basic realm="Login Required"'}


def basic_auth_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return func(*args, **kwargs)
    return decorated
