#!/bin/bash

set -e

error() {
  echo "$@" >&2
  exit 1
}

gen_load_workload() {
  # Operations & Records - $1 / 10,000
  # not using $YCSB_RECORD_COUNT anymore
  echo -ne "recordcount=${1:-10000}
operationcount=${1:-10000}
workload=com.yahoo.ycsb.workloads.CoreWorkload
readallfields=true
readproportion=0
updateproportion=0
scanproportion=0
insertproportion=1
readmodifywriteproportion=0
requestdistribution=zipfian"
}

gen_read_workload() {
  # Operations & Records - $1 / 10,000
  # not using $YCSB_RECORD_COUNT anymore
  echo -ne "recordcount=${1:-10000}
operationcount=${1:-10000}
workload=com.yahoo.ycsb.workloads.CoreWorkload
readallfields=true
readproportion=0.1
updateproportion=0
scanproportion=0
insertproportion=0.80
readmodifywriteproportion=0.1
requestdistribution=zipfian"
}

SCRIPT_DIR="$(dirname "$0")"

[ -r "$SCRIPT_DIR/.redis_custom_workload_env" ] && . "$SCRIPT_DIR/.redis_custom_workload_env"

# sanity check
YCSB_DIR="${YCSB_DIR:-/opt/ycsb}"
YCSB_THREAD_COUNT="${YCSB_THREAD_COUNT:-16}"
LOG_FILE="${LOG_FILE:-/tmp/redis_custom_workload.log}"

[ -z "$REDIS_HOST" ] && error "Invalid REDIS_HOST=$REDIS_HOST"

[ ! -d "$YCSB_DIR" ] && error "Invalid YCSB_DIR=$YCSB_DIR"

[ ! -f "$WORKLOAD_CURVE_FILE" ] && error "Invalid workload curve file=$WORKLOAD_CURVE_FILE"

echo "Starting ycsb load..." # >> "$LOG_FILE"

# gen_load_workload "$YCSB_RECORD_COUNT" >/tmp/workload

# "$YCSB_DIR/bin/ycsb" load redis -s \
#   -threads "$YCSB_THREAD_COUNT" \
#   -P "/tmp/workload" \
#   -p "redis.host=${REDIS_HOST}" \
#   -p "redis.cluster=true" # >> "$LOG_FILE" 2>&1

TOTAL="$(wc -l "$WORKLOAD_CURVE_FILE" | awk '{print $1}')"
CURR=1

# Run workload
while read -r opCount; do
  echo "Running workload ${CURR} / ${TOTAL} with operation count $((opCount * 1000))..."

  gen_read_workload "$((opCount * 1000))" >/tmp/workload

  "$YCSB_DIR/bin/ycsb" run redis -s \
    -threads "$YCSB_THREAD_COUNT" \
    -P "/tmp/workload" \
    -p "redis.host=${REDIS_HOST}" \
    -p "redis.cluster=true" # >> "$LOG_FILE" 2>&1

  CURR=$((CURR + 1))
done <"$WORKLOAD_CURVE_FILE"
