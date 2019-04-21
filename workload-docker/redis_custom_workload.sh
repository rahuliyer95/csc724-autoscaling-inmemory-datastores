#!/bin/bash

set -e

error() {
  echo $* >&2
  exit 1
}

gen_workload() {
  # Records - 100,000
  # not using $YCSB_RECORD_COUNT anymore
  echo -ne "recordcount=${1:-1000}000
operationcount=${1:-1000}000
workload=com.yahoo.ycsb.workloads.CoreWorkload
readallfields=true
readproportion=0.20
updateproportion=0.40
scanproportion=0
insertproportion=0.40
readmodifywriteproportion=0
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

# gen_workload "50" >/tmp/workload

# "$YCSB_DIR/bin/ycsb" load redis -s \
#   -threads "$YCSB_THREAD_COUNT" \
#   -P "/tmp/workload" \
#   -p "redis.host=${REDIS_HOST}" \
#   -p "redis.cluster=true" # >> "$LOG_FILE" 2>&1

TOTAL="$(wc -l "$WORKLOAD_CURVE_FILE" | awk '{print $1}')"
CURR=1

# Run workload
while read -r opCount; do
  echo "Running workload ${CURR} / ${TOTAL} with operation count ${opCount}..."

  gen_workload "$opCount" >/tmp/workload

  "$YCSB_DIR/bin/ycsb" run redis -s \
    -threads "$YCSB_THREAD_COUNT" \
    -P "/tmp/workload" \
    -p "redis.host=${REDIS_HOST}" \
    -p "redis.cluster=true" # >> "$LOG_FILE" 2>&1

  CURR=$((CURR + 1))
done <"$WORKLOAD_CURVE_FILE"
