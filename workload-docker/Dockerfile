FROM bitnami/minideb:stretch

ENV YCSB_URL https://github.com/brianfrankcooper/YCSB/releases/download/0.15.0/ycsb-0.15.0.tar.gz

ENV YCSB_ZIP_DIR ycsb-0.15.0

# Requirements
RUN install_packages ca-certificates curl openjdk-8-jre-headless python python3

RUN cd /opt && \
    curl -SL "$YCSB_URL" | tar xz && \
    mv "$YCSB_ZIP_DIR" ycsb && \
    cd /opt/ycsb && \
    rm -rf accumulo1.6-binding accumulo1.7-binding accumulo1.8-binding aerospike-binding && \
    rm -rf arangodb-binding asynchbase-binding azuredocumentdb-binding azuretablestorage-binding && \
    rm -rf cassandra-binding cloudspanner-binding couchbase2-binding couchbase-binding dynamodb-binding && \
    rm -rf elasticsearch5-binding elasticsearch-binding foundationdb-binding geode-binding googlebigtable-binding && \
    rm -rf googledatastore-binding hbase098-binding hbase10-binding hbase12-binding hbase14-binding && \
    rm -rf hbase20-binding hypertable-binding ignite-binding infinispan-binding kudu-binding maprdb-binding && \
    rm -rf maprjsondb-binding memcached-binding mongodb-binding nosqldb-binding orientdb-binding rados-binding && \
    rm -rf rest-binding riak-binding rocksdb-binding s3-binding solr-binding tarantool-binding

# Add files
ADD redis_custom_workload.sh /opt/workload.sh

ADD curve_nasa_60_2 /opt/curve_nasa_60_2

ADD curve_nasa_10_2 /opt/curve_nasa_10_2

RUN ["chmod", "+x", "/opt/workload.sh"]

ENTRYPOINT ["/opt/workload.sh"]

