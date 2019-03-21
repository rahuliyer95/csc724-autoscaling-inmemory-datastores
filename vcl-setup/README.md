# VCL Setup

[VCL](https://vcl.ncsu.edu/) VM contains the [Kafka](https://kafka.apache.org/) and [ZooKeeper](https://zookeeper.apache.org/) setup.

## ZooKeeper

ZooKeeper is expected to be present in `/opt/zookeeper/3.4.13`

Use the command to setup ZooKeeper (might need to run as root)

```sh
mkdir -p '/opt/zookeeper/'
curl -L 'https://www-us.apache.org/dist/zookeeper/stable/zookeeper-3.4.13.tar.gz' | tar xz -C '/opt/zookeeper/'
mv '/opt/zookeeper/zookeeper-3.4.13' '/opt/zookeeper/3.4.13'
cp '/opt/zookeeper/3.4.13/conf/zoo_sample.cfg' '/opt/zookeeper/3.4.13/conf/zoo.cfg'
```

Copy the [zookeeper.service](./zookeeper.service) file to `/etc/systemd/system/zookeeper.service` and run the following commands to start ZooKeeper.
```sh
systemctl reload-daemon
systemctl start zookeeper
```

## Kafka

Kafka is expected to be present in `/opt/kafka/2.1.1`

Use the command to setup Kafka (might need to run as root)

```sh
mkdir -p '/opt/kafka'
curl -L 'https://www-us.apache.org/dist/kafka/2.1.1/kafka_2.12-2.1.1.tgz' | tar xz -C '/opt/kafka/'
mv '/opt/kafka/kafka_2.12-2.1.1' '/opt/kafka/2.1.1'
```

Copy the [kafka.service](./kafka.service) file to `/etc/systemd/system/kafka.service` and run the following commands to start Kafka.
```sh
systemctl reload-daemon
systemctl start kafka
```

## YCSB (Yahoo! Cloud Serving Benchmark)

Install YCSB using the following commands (run as root)

```sh
curl -L 'https://github.com/brianfrankcooper/YCSB/releases/download/0.15.0/ycsb-0.15.0.tar.gz' | tar xz -C '/opt'
mv '/opt/ycsb-0.15.0' '/opt/ycsb'
```

Copy the [workload_redis](./workload_redis) file to `/opt/ycsb/workloads` directory.

Use the [redis-load.sh](./redis-load.sh) file to run the workload against.

Edit the `REDIS_HOST` variable in the script to point to your Redis host

## Firewall

To allow services through firewall iptables setup needs to be done. Use the following commands to add iptables exception (run as root)

```sh
iptables -I INPUT -p TCP -s 0.0.0.0/0 --dport 2181 -j ACCEPT # Zookeeper
iptables -I INPUT -p TCP -s 0.0.0.0/0 --dport 9092 -j ACCEPT # Kafka
```
