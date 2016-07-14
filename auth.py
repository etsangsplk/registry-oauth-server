import os
from functools import wraps

import requests
from flask import request, jsonify
from requests.auth import HTTPBasicAuth


def check_auth(username, password):
    """
    This function is called to check if a username/password combination is valid.
    """
    request.user = username

    resp = requests.get(
        '{}/api/authn/users/login'.format(os.environ.get('CONJUR_URL')),
        verify=os.environ.get('CONJUR_SSL_CERT'),
        auth=HTTPBasicAuth(username, password))
    return resp.status_code == 200


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
