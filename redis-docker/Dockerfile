FROM redis:latest

# pre-req
RUN mkdir -p /usr/share/man/man1

# requirements
RUN apt-get update && \
      apt-get install -y apt-utils apt-transport-https curl collectd collectd-utils dirmngr gnupg2 librdkafka-dev libhiredis-dev --option=Dpkg::Options::=--force-confdef

RUN echo 'deb https://apt.datadoghq.com/ stable 6' > /etc/apt/sources.list.d/datadog.list && \
      apt-key adv --recv-keys --keyserver "hkp://keyserver.ubuntu.com:80" 382E94DE && \
      apt-get update -o Dir::Etc::sourcelist="sources.list.d/datadog.list" -o Dir::Etc::sourceparts="-" -o APT::Get::List-Cleanup="0" && \
      apt-get install -y datadog-agent && \
      apt-get clean

ADD conf.d/redisdb.yaml /etc/datadog-agent/conf.d/redisdb.yaml

ADD redis.conf /usr/local/etc/redis.conf

ADD collectd.conf /etc/collectd/collectd.conf

ADD entrypoint.sh /opt/entrypoint.sh

EXPOSE 6379

EXPOSE 6380

RUN ["chmod", "+x", "/opt/entrypoint.sh"]

ENTRYPOINT ["/opt/entrypoint.sh"]

