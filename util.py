import os

import conjur


def send_audit_event(username, password, action, allowed, message=''):
    api = conjur.new_from_key(username, password)

    json = {
        'facility': 'docker',
        'action': action,
        'allowed': allowed,
        'resource_id': '{}:webservice:{}'.format(api.config.account, os.environ['CONJUR_REGISTRY_WEBSERVICE']),
    }
    if message != '':
        json['audit_message'] = message

    api.post('{}/authz/audit'.format(api.config.core_url), json=json)
