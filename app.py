import os

import conjur
from flask import Flask, request, jsonify

from auth import basic_auth_required
from tokens import Token

app = Flask(__name__)


def get_allowed_actions(user, typ, name, actions):
    api = conjur.new_from_key(
        os.environ['CONJUR_REGISTRY_HOST_NAME'],
        os.environ['CONJUR_REGISTRY_HOST_API_KEY']
    )

    pushers = api.group(os.environ['CONJUR_PUSHERS_GROUP_NAME'])
    pullers = api.group(os.environ['CONJUR_PULLERS_GROUP_NAME'])

    pushers_names = [x['member'].split(':')[-1] for x in pushers.members()]
    pullers_names = [x['member'].split(':')[-1] for x in pullers.members()]

    actions = []

    if user in pushers_names:
        actions.append('push')

    if user in pullers_names:
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
    app.run(host='0.0.0.0', port=8080)  # add debug=True for more verbose logging
