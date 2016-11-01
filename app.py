import os

import conjur
from flask import Flask, request, jsonify

from auth import basic_auth_required
from tokens import Token

app = Flask(__name__)


def get_allowed_actions(roleid, typ, name, actions):
    if typ == 'repository':
        actions = []
        host_id = os.environ['CONJUR_REGISTRY_HOST_NAME']

        api = conjur.new_from_key(
            'host/{}'.format(host_id),
            os.environ['CONJUR_REGISTRY_HOST_API_KEY']
        )

        if roleid.startswith('host/'):
            hostid = '/'.join(roleid.split('/')[1:])  # remove leading 'host/'
            role = api.host(hostid)
        else:
            role = api.user(roleid)

        if api.resource('host', host_id).permitted('push', role):
            actions.extend(['push', 'pull'])  # pushing requires pull privilege as well
        elif api.resource('host', host_id).permitted('pull', role):
            actions.append('pull')

    return actions


@app.route('/tokens')
@basic_auth_required
def tokens():
    service = request.args.get('service')
    scope = request.args.get('scope')
    if not scope:
        typ = ''
        name = ''
        actions = []
    else:
        params = scope.split(':')
        if len(params) != 3:
            return jsonify(error='Invalid scope parameter'), 400
        typ = params[0]
        name = params[1]
        actions = params[2].split(',')

    authorized_actions = get_allowed_actions(request.user, typ, name, actions)

    token = Token(service, typ, name, authorized_actions)
    encoded_token = token.encode_token()

    return jsonify(token=encoded_token)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=bool(os.environ.get('DEBUG', 0)))
