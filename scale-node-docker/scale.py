import azure_helpers as az
import click
import json
import jsonschema
import logging
import redis_helpers as rh
import time
from kafka import KafkaConsumer

LOG = logging.getLogger('scale')
MESSAGE_SCHEMA = {
    "type": "object",
    "properties": {
        "average_load": {
            "type": "number"
        },
        "peak_load": {
            "type": "number"
        },
        "nodes": {
            "type": "integer",
            "minimum": 1
        },
        "scale": {
            "type": "string",
            "pattern": "(up|no|down)"
        }
    }
}


def setup_logger(verbose):
    global LOG
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    LOG.setLevel(logging.DEBUG if verbose else logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    LOG.addHandler(ch)


def get_kafka_consumer(host, port, topic):
    return KafkaConsumer(topic,
                         bootstrap_servers='%s:%d' % (host, port),
                         group_id='scale-ng',
                         auto_offset_reset='earliest')


def scale_up(kafka_host, kafka_port):
    LOG.info('Prediction asked to scale up')
    LOG.info('Fetching master nodes in the cluster')

    cluster = az.get_redis_master_nodes()
    LOG.debug('Redis nodes = %r', ', '.join(n.name for n in cluster))

    new_node_id = max((int(n.name.split('-')[-1]) for n in cluster), default=0) + 1
    master_name = 'csc724-redis-%d' % (new_node_id)
    # slave_name = 'csc724-redis-slave-%d' % (new_node_id)

    LOG.info('Creating new master %s', master_name)
    az.add_redis_node(master_name, kafka_host, kafka_port)

    LOG.info('Waiting for %s container to be created...', master_name)
    try:
        master_container_grp = az.wait_for_container(master_name)
        LOG.debug('Master container %r', master_container_grp.as_dict())
    except Exception:
        LOG.error('Failed to create master container')
        return

    LOG.info('Adding master to cluster')
    rh.join_cluster(master_container_grp, cluster)

    cluster.append(master_container_grp)

    time.sleep(1)

    LOG.info('Fixing existing cluster')
    rh.cluster_fix(cluster)

    time.sleep(1)

    LOG.info('Rebalancing cluster')
    rh.cluster_rebalance(cluster)

    # LOG.info('Creating new slave %s', slave_name)
    # az.add_redis_node(slave_name, kafka_host, kafka_port)

    # LOG.info('Waiting for %s container to be created...', slave_name)
    # slave_container_grp = az.wait_for_container(slave_name)
    # LOG.debug('Slave container %r', slave_container_grp.as_dict())

    # LOG.info('Adding slave to cluster')
    # rh.join_cluster(slave_container_grp, cluster)

    # time.sleep(2)

    # LOG.info('Attaching slave to master')
    # rh.attach_slave(master_container_grp, slave_container_grp)

    LOG.info('Scale up complete!')
    # LOG.info('Fixing cluster just in case ;)')
    # rh.cluster_fix(cluster)


def scale_down():
    LOG.info('Prediction asked to scale down')
    LOG.info('Fetching master nodes in the cluster')

    cluster = az.get_redis_master_nodes()
    LOG.debug('Redis nodes = %r', ', '.join(n.name for n in cluster))

    max_node_id = max((int(n.name.split('-')[-1]) for n in cluster), default=0)
    if max_node_id == 0:
        LOG.error('No nodes in cluster')
        return
    elif max_node_id == 1:
        LOG.error('Need atleast 1 node in the cluster')
        return

    master_name = 'csc724-redis-%d' % (max_node_id)
    # slave_name = 'csc724-redis-slave-%d' % (max_node_id)

    # LOG.info('Waiting for slave container group')
    # try:
    #     slave_container_grp = az.wait_for_container(slave_name)
    #     LOG.debug('Slave container %r', slave_container_grp.as_dict())
    # except Exception:
    #     LOG.error('Unable to get slave container')
    #     slave_container_grp = None

    # if slave_container_grp:
    #     LOG.info('Removing slave %s from cluster', slave_name)
    #     rh.del_node(slave_container_grp, cluster)

    #     LOG.info('Removing %s from Azure', slave_name)
    #     az.del_redis_node(slave_name)

    master_container_grp = cluster.pop()

    if not master_container_grp:
        LOG.error('Invalid master container group')
        return

    LOG.info('Resharding')
    rh.reshard(master_container_grp, cluster)

    time.sleep(1)

    LOG.info('Removing master %s from cluster', master_name)
    rh.del_node(master_container_grp, cluster)

    time.sleep(1)

    LOG.info('Removing %s from Azure', master_name)
    az.del_redis_node(master_name)

    LOG.info('Scale down complete!')
    LOG.info('Fixing cluster just in case ;)')
    rh.cluster_fix(cluster)


@click.command()
@click.option('--kafka-host', help='Kafka host to connect', required=True)
@click.option('--kafka-port', type=int, help='Kafka port to connect', required=True)
@click.option('--topic', help='Kafka topic to read data from', required=True)
@click.option('--verbose/--no-verbose', default=False)
def main(kafka_host, kafka_port, topic, verbose):
    global LOG
    setup_logger(verbose)

    consumer = get_kafka_consumer(kafka_host, kafka_port, topic)
    for message in consumer:
        payload = None
        try:
            payload = json.loads(message.value)
            jsonschema.validate(payload, MESSAGE_SCHEMA)
        except Exception as e:
            LOG.error('Invalid message\n%r', e)
            continue

        LOG.debug('Payload = %r', payload)

        if payload['scale'] == 'no':
            LOG.info('Prediction said not to scale')
            continue

        if payload['scale'] == 'up':
            scale_up(kafka_host, kafka_port)
        else:
            scale_down()


if __name__ == '__main__':
    main()
