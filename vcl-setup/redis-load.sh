#!/bin/bash

set -e

cd /opt/ycsb

echo "starting ycsb load..." >> /tmp/redis_load.log

export REDIS_HOST="csc724-redis.eastus.azurecontainer.io"
# export REDIS_HOST="localhost"

# Load data
./bin/ycsb load redis -s -P ./workloads/workload_redis -p "redis.host=${REDIS_HOST}" >> /tmp/redis_load.log 2>&1

# Run test
./bin/ycsb run redis -s -P ./workloads/workload_redis -p "redis.host=${REDIS_HOST}" >> /tmp/redis_load.log 2>&1

echo "load complete..." >> /tmp/redis_load.log

