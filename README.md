# registry-oauth-server

This is a forked version of OpenDNS's [registry-oauth-server](https://github.com/opendns/registry-oauth-server). 
View the upstream README for configuration defaults.

The purpose of this fork is to authenticate and authorize Docker registry users with
Conjur.

## Quickstart

This assumes you have Docker running and available.

Start the `registry` and `oauth_server` containers:

```
$ ./build.sh
```

After installation is finished, you should have a local registry running on `:5000`,
and a local oauth server running on `:8080`.

## Policy

[policy.yml](policy.yml) defines:

* A host that represents the Docker registry (`registry`)
* A group of users that can push to registry (`pushers`)
* A group of users that can pull from registry (`pullers`)

Group `pushers` is permitted `push` on `registry`. Group `pullers` is permitted `pull` on `registry`.
Host `registry` is a member of both `pushers` and `pullers`. This is because a role needs to be a member of the group
to discover the group's members.

## Configuration

Configuration is applied by passing environment variables to the OAuth container:

* `CONJUR_CERT_FILE`: Path to Conjur public SSL cert (should be mounted into container)
* `CONJUR_APPLIANCE_URL`: Conjur endpoint
* `CONJUR_ACCOUNT`: Conjur account, specified during initial configuration
* `CONJUR_REGISTRY_HOST_NAME`: Name of the host representing the registry
* `CONJUR_REGISTRY_HOST_API_KEY`: API key of the registry host

## authn

By default, the oauth server is configured to talk to conjurops: the public SSL cert is checked into the 
*certs* directory and `CONJUR_URL` specifies the Conjur endpoint in *docker-compose.yml*. Log into the registry 
using your Conjur username and password:

```
$ docker login localhost:5000
Username: dustin
Password: <REDACTED>
Login Succeeded
```

The function `check_auth` in [auth.py](auth.py) calls out to Conjur to verify the user.

## authz

Authorization is performed by checking privilege on the `registry` host, either `push` or `pull`.
Privilege is checked in real-time, when the request is recieved.

More granular permission checking can be implemented by modifying the function `get_allowed_actions` in [app.py](app.py).
`type` is the type of action, most commonly 'repository'. `name` is the name of the repository.

Note that roles must have `pull` and `push` privilege to push images to the registry. This is required because
Docker makes a pull request (to check if image already exists) before pushing images.

OAuth spec details here: https://docs.docker.com/registry/spec/auth/token/

---

TODO:

* Add a webservice to the policy to represent the registry
* Machine authz - current authz implementation assumes user is a User
* Deployment guide (to AWS)
