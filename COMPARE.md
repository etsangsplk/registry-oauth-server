# Docker Registry authn/authz

This document is a summary of the state of tooling for authenticating and authorizing use of a Docker registry (v2). 
This is not an exhaustive guide, but covers popular **self-hosted** tooling and approaches right now.


|Project|authn|authz|audit|ease of use|web interface|
|-------|-----|-----|-----|-----------|-------------|
|Registry|static|no|no|*****|DIY|
|Portus|UI/LDAP|UI/LDAP|yes|**|yes|
|Atomic Registry|UI/OAuth/OpenShift|UI/RBAC|no|*|yes|
|cesanta/docker_auth|static/SSO/MongoDB/LDAP|static/MongoDB|no|***|no|
|conjurinc/registry-oauth-server|Conjur|Conjur|yes|****|no|

# 1. [Registry](https://docs.docker.com/registry/)

Docker open-sources their registry as a [Docker image](https://hub.docker.com/_/registry/) (go figure). 
Registry only supports [basic HTTP authentication](https://docs.docker.com/registry/deploying/#/restricting-access). 
This means you have to create a htpasswd file and mount it into the container. This works well for very small teams, 
but the htpasswd file must be edited whenever you need to modify access to the registry. The htpassword file is also 
only base64-encrypted, so anyone with access to that file can decrypt it can get all your passwords.

Docker Cloud (Docker's paid SaaS product) provides authn/authz functionality, so there's not much incentive for 
them to develop an open source solution. Instead, for Docker Registry v2 (v1 is deprecated), they shared an 
[OAuth2 spec](https://docs.docker.com/registry/spec/auth/token/) for people to implement their own solution. This 
is what we're using for our integration, but implementing this spec beyond the capability of most teams.

# 2. [Portus](https://github.com/SUSE/Portus)

Portus is an open-source solution created by the Linux SUSE team. It works alongside the open-source Registry to 
provide a web interface, teams, users and namespaces and audit functionality. Teams and users can either be managed 
manually by an admin user or synced from LDAP. Portus can manage several registries at once. This is a fairly active 
GitHub project with ~1000 stars and ~200 forks.

Portus has downsides. It is complex, with lots of configuration options and lacks a straightforward deployment guide. 
It also requires a separate MariaDB database to hold its data. The database must then be secured and maintained.

# 3. [Atomic Registry](http://www.projectatomic.io/registry/)

[Project Atomic](http://www.projectatomic.io/) is developed and supported by Red Hat. Atomic Registry (AR) is one 
part of it; Atomic Host is a Docker orchestration platform and Atomic App an application specification to run on 
Atomic Host. AR can be used standalone, but is only tested and supported on RHEL, CentOS and Fedora. AR provides a 
web interface, multiple storage options, and RBAC.

Atomic Registry has a lot of compelling features, but is very much tied to OpenStack and Kubernetes. It is also 
[complex to set up and configure](http://docs.projectatomic.io/registry/latest/registry_quickstart/administrators/index.html),
requires 3 separate services (2 of which are stateful). AR does not have much adoption outside the (small) 
OpenStack+Kubernetes community.

# 4. [cesanta/docker_auth](https://github.com/cesanta/docker_auth)

`docker_auth` is an open-source solution for registry authn/authz on GitHub. authn is pretty robust with several 
options, but authz is implemented with either a static list of usernames/passwords or via MongoDB. `docker_auth` 
does not provide a web interface.

`docker_auth` will not cut it for most teams because its authz is under-developed. Static user lists are not much 
better than the htpasswd functionality the default Registry provides. Most teams will be wary of standing up 
MongoDB (losing popularity over the past couple years) just to security their Docker registry.

# 5. [conjurinc/registry-oauth-server](https://github.com/conjurinc/registry-oauth-server)

Our solution is a customization of OpenDNS's [registry-oauth-server](https://github.com/opendns/registry-oauth-server). 
This server is a small Python webapp that implements the OAuth2 spec defined by Docker with pluggable authn/authz 
functions. `registry-oauth-server` is published as a Docker image that runs alongside Registry. When a request is 
made to the registry, registry-oauth-server verifies authn/authz with Conjur. A web interface is not built-in.

There are a couple things to note on our implementation of Registry authn/authz. First, the user flow is 
Docker-native. Users/machines log in to the registry using `docker login` with their own Conjur credentials. When 
they try to push/pull an image Conjur is consulted. This operation is not exposed to the user; as far as they know 
they're just using a Docker registry as usual. Second, deployment and configuration is simply and requires only 1. 
Registry and 2. Conjur. There are no extra files/database to maintain.
