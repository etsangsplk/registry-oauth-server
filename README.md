# registry-oauth-server

This is a forked version of OpenDNS's [registry-oauth-server](https://github.com/opendns/registry-oauth-server). 
View the upstream README for configuration defaults.

The purpose of this fork is to authenticate and authorize Docker registry users with
Conjur.

## Quickstart

This assumes you have Docker running (docker-machine on OSX) and available.

Start the `registry` and `oauth_server` containers:

```
$ ./build.sh
```

After installation is finished, you should have a local registry running on `:5000`,
and a local oauth server running on `:8080`. These instructions assume docker-machine; if you're running Docker natively use `localhost` instead of `docker-machine ip`.

## authn

By default, the oauth server is configured to talk to conjurops: the public SSL cert is checked into the *certs* directory and `CONJUR_URL` specifies the Conjur endpoint in *docker-compose.yml*. Log into the registry using your Conjur username and password:

```
$ docker login $(docker-machine ip):5000
Username: dustin
Password: <REDACTED>
Login Succeeded
```

## authz

TODO

The `get_allowed_actions` in [app.py](app.py) is a stub for looking up what actions a user is allowed to perform. We need to do a Conjur lookup here. For example, when a user tries to push an image (alpine in this example), this scope request is `repository:alpine:push,pull`, which maps to `type:name:actions`. Given a username, `get_allowed_actions` needs to return a list of actions that the user is authorized to perform.

Spec details here: https://docs.docker.com/registry/spec/auth/token/
