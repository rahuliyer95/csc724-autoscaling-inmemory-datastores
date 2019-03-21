# Redis Docker

This folder contains the files needed to create Redis Docker image.

The generated image can be viewed in Dockerhub under [rahuliyer95/csc724-redis-collectd](https://cloud.docker.com/u/rahuliyer95/repository/docker/rahuliyer95/csc724-redis-collectd/)

The container includes [Redis](https://redis.io/) with [collectd](https://collectd.org/) to push metrics to Kafka.
It expects the following environment variables

- ENV_BROKER: The `host:port` for kafka broker
- ENV_INTERVAL: The interval in seconds for collectd metrics collection

[DataDog](https://docs.datadoghq.com/agent/?tab=agentv6/) agent is also installed in the container and expects the `DD_API_KEY` environment variable to push the metrics.

[entrypoint.sh](./entrypoint.sh) is the docker `ENTRYPOINT` and boots up collectd, datadog-agent, and redis-server.
