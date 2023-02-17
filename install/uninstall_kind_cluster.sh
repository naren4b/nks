#!/bin/sh
set -o errexit
source config.sh
kind delete clusters ${KIND_CLUSTER_NAME}
