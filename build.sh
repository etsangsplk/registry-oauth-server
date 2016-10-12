#!/bin/bash -e

# Create certificate used by registry
mkdir -p certs
if [ ! -f cert/server.key ] & [ ! -f certs/server.crt ]; then
    openssl req -subj '/CN=localhost/O=Registry Demo/C=US' -new -newkey rsa:2048 -days 365 -nodes -x509 -keyout certs/server.key -out certs/server.crt
fi
# Create dhparam file
if [ ! -f dhparam.pem ]; then
  openssl dhparam -out ./dhparam.pem 2048
fi

docker-compose build

# Bring up Conjur
docker-compose up -d conjur

# Configure Conjur
docker exec registryoauthserver_conjur_1 evoke configure master \
  -h localhost -p password myorg || true
yes 'yes' | conjur init -f .conjurrc.myorg -h localhost:443
cp conjur-myorg.pem certs/

# Log in as Conjur admin user and load policy.yml
export CONJURRC=.conjurrc.myorg
conjur authn login -u admin -p password
conjur policy load --as-group security_admin --context policy.json policy.yml

# Export the created host's API key
export CONJUR_REGISTRY_HOST_API_KEY=$(cat policy.json | jq -r '."myorg:host:docker/registry"')

export DH_PARAM_PEM=$(cat dhparam.pem)

# Start the other services
docker-compose up -d
