#!/bin/bash

set -e

error() {
  echo $* >&2
  exit 1
}

SCRIPT_DIR="$(dirname $0)"

[ -r "$SCRIPT_DIR/.redis_load_env" ] && . "$SCRIPT_DIR/.redis_load_env"

# sanity check
YCSB_DIR="${YCSB_DIR:-/opt/ycsb}"
YCSB_THREAD_COUNT="${YCSB_THREAD_COUNT:-16}"
LOG_FILE="${LOG_FILE:-/tmp/redis_batch.log}"

[ -z "$REDIS_HOST" ] && error "Invalid REDIS_HOST=$REDIS_HOST"

[ ! -d "$YCSB_DIR" ] && error "Invalid YCSB_DIR=$YCSB_DIR"

[ ! -r "$YCSB_WORKLOAD_FILE" ] && error "Invalid YCSB_WORKLOAD_FILE=$YCSB_WORKLOAD_FILE"

echo "starting ycsb load..." >> "$LOG_FILE"

# Load data

"$YCSB_DIR/bin/ycsb" load redis -s \
  -threads "$YCSB_THREAD_COUNT" \
  -P "$YCSB_WORKLOAD_FILE" \
  -p "redis.host=${REDIS_HOST}" >> "$LOG_FILE" 2>&1

# Run

"$YCSB_DIR/bin/ycsb" run redis -s \
  -threads "$YCSB_THREAD_COUNT" \
  -P "$YCSB_WORKLOAD_FILE" \
  -p "redis.host=${REDIS_HOST}" >> "$LOG_FILE" 2>&1

echo "batch load complete..." >> "$LOG_FILE"

