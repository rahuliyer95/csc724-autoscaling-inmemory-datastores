# Workload

This part runs the workload against Redis using [YCSB](https://github.com/brianfrankcooper/YCSB).

## Environment Variables

The workload expects the following environment variables to be present

- `REDIS_HOST` - The host on which redis is running. **Port should be `6379`**
- `WORKLOAD_CURVE_FILE` - The workload curve file to be used
- `YCSB_RECORD_COUNT` - The number of records to be loaded into Redis
- `YCSB_THREAD_COUNT` - The number of threads to be used
