FROM bitnami/python

ENV REDIS_VERSION 5.0.4
ENV REDIS_DOWNLOAD_URL http://download.redis.io/releases/redis-5.0.4.tar.gz
ENV AZURE_AUTH_LOCATION /opt/scale/azure-credentials.json

RUN install_packages curl ca-certificates gcc libc6-dev make

RUN mkdir -p /usr/src/redis && \
  curl -SL "$REDIS_DOWNLOAD_URL" | tar xz --strip-components=1 -C /usr/src/redis && \
  grep -q '^#define CONFIG_DEFAULT_PROTECTED_MODE 1$' /usr/src/redis/src/server.h && \
  sed -ri 's!^(#define CONFIG_DEFAULT_PROTECTED_MODE) 1$!\1 0!' /usr/src/redis/src/server.h && \
  grep -q '^#define CONFIG_DEFAULT_PROTECTED_MODE 0$' /usr/src/redis/src/server.h && \
  make -C /usr/src/redis -j "$(nproc)" && \
  make -C /usr/src/redis install && \
  rm -rf /usr/src/redis

RUN pip3 install --upgrade pip

RUN pip3 install --no-deps pipenv

WORKDIR /opt/scale

RUN mkdir -p /opt/scale

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock
COPY azure_helpers.py azure_helpers.py
COPY redis_helpers.py redis_helpers.py
COPY scale.py scale.py
COPY entrypoint.sh entrypoint.sh

RUN pipenv install --deploy --system

RUN chmod 755 ./entrypoint.sh

ENTRYPOINT ./entrypoint.sh

