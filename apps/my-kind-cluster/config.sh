#!/bin/sh

KIND_CLUSTER_NAME=$1
KIND_NODE_VERSION=v1.23.6

RELEASE_NAME=v1

reg_name='kind-registry'
reg_port='5001'

mkdir -p out
