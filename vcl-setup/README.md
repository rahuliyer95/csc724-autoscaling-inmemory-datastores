# VCL Setup

[VCL](https://vcl.ncsu.edu/) VM contains the [Kafka](https://kafka.apache.org/) and [ZooKeeper](https://zookeeper.apache.org/) setup.

## ZooKeeper

ZooKeeper is expected to be present in `/opt/zookeeper`

Use the command to setup ZooKeeper (might need to run as root)

```sh
mkdir -p '/opt/zookeeper/'
curl -SL 'https://www-us.apache.org/dist/zookeeper/stable/zookeeper-3.4.14.tar.gz' | tar xz -C '/opt/zookeeper/' --strip-components=1
cp '/opt/zookeeper/conf/zoo_sample.cfg' '/opt/zookeeper/conf/zoo.cfg'
```

Copy the [zookeeper.service](./zookeeper.service) file to `/etc/systemd/system/zookeeper.service` and run the following commands to start ZooKeeper.
```sh
systemctl reload-daemon
systemctl start zookeeper
```

## Kafka

Kafka is expected to be present in `/opt/kafka`

Use the command to setup Kafka (might need to run as root)

```sh
mkdir -p '/opt/kafka'
curl -SL 'https://www-us.apache.org/dist/kafka/2.1.1/kafka_2.12-2.1.1.tgz' | tar xz -C '/opt/kafka/' --strip-components=1
```

Copy the [kafka.service](./kafka.service) file to `/etc/systemd/system/kafka.service` and run the following commands to start Kafka.
```sh
systemctl daemon-reload
systemctl start kafka
```

## Firewall

To allow services through firewall iptables setup needs to be done. Use the following commands to add iptables exception (run as root)

```sh
iptables -I INPUT -p TCP -s 0.0.0.0/0 --dport 2181 -j ACCEPT # Zookeeper
iptables -I INPUT -p TCP -s 0.0.0.0/0 --dport 9092 -j ACCEPT # Kafka
```

## Topics

The system needs two topics `collectd` and `prediction` to function.

Create them using the following commands

```sh
/opt/kafka/bin/kafka-topics.sh --zookeeper localhost:2181 --create --topic collectd --partitions 1 --replication-factor 1
/opt/kafka/bin/kafka-topics.sh --zookeeper localhost:2181 --create --topic prediction --partitions 1 ---replication-factor 1
```
