#!/bin/sh

# collectd
sed -i 's/\${ENV_BROKER}/'"${ENV_BROKER:-localhost:9092}"'/g' /etc/collectd/collectd.conf
sed -i 's/\${ENV_INTERVAL}/'"${ENV_INTERVAL:-150}"'/g' /etc/collectd/collectd.conf
service collectd start

# datadog
cp "/etc/datadog-agent/datadog.yaml.example" "/etc/datadog-agent/datadog.yaml"
sed -i 's/^api_key:/api_key: '"${DD_API_KEY}"'/g' "/etc/datadog-agent/datadog.yaml"
service datadog-agent start

# redis
redis-server /usr/local/etc/redis.conf

