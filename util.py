import os

import conjur


def send_audit_event(username, action, allowed, message=''):
    hostapi = conjur.new_from_key(
        'host/{}'.format(os.environ['CONJUR_REGISTRY_HOST_NAME']),
        os.environ['CONJUR_REGISTRY_HOST_API_KEY']
    )
    json = {
        'facility': 'docker',
        'action': action,
        'allowed': allowed,
        'resource_id': '{}:host:{}'.format(hostapi.config.account, os.environ['CONJUR_REGISTRY_HOST_NAME']),
        'role': '{}:user:{}'.format(hostapi.config.account, username)
    }
    if message != '':
        json['audit_message'] = message

    hostapi.post('{}/authz/audit'.format(hostapi.config.core_url), json=json)
