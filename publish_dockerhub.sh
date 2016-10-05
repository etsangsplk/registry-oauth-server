#!/bin/bash -e

docker build -t conjurinc/registry-oauth-server .

docker push conjurinc/registry-oauth-server
