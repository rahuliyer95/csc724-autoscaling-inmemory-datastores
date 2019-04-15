import subprocess
from retrying import retry
from scale import LOG

_REDIS_COMMAND_PATH = '/usr/local/bin/redis-cli'
_REDIS_PORT = '6379'


@retry(retry_on_result=lambda r: not r, stop_max_attempt_number=15, wait_fixed=1000)
def join_cluster(container_group, cluster):
    for node in cluster:
        LOG.info('Trying to attach to %s', node.name)
        result = subprocess.run([
            _REDIS_COMMAND_PATH, '-h', container_group.ip_address.ip, '-p', _REDIS_PORT, '-c',
            'cluster', 'meet', node.ip_address.ip, _REDIS_PORT
        ])
        if result.returncode == 0:  # Successful
            LOG.info('Sucessfully met with cluster using %s', node.name)
            return True
        else:
            LOG.error('Unable to join cluster using %s. Trying the rest', node.name)

    LOG.error('%s failed to join cluster...', container_group.name)
    return False


def cluster_fix(cluster):
    for node in cluster:
        LOG.info('Fixing cluster using %s', node.name)
        result = subprocess.run([
            _REDIS_COMMAND_PATH, '-h', node.ip_address.ip, '-p', _REDIS_PORT, '--cluster', 'fix',
            node.ip_address.ip + ':' + _REDIS_PORT, '--cluster-yes'
        ])
        if result.returncode == 0:
            LOG.info('Cluster fixed')
        else:
            LOG.warn('Unable to fix cluster using %s. Trying using other nodes', node.name)


def cluster_rebalance(cluster):
    for node in cluster:
        LOG.info('Rebalancing cluster using %s', node.name)
        result = subprocess.run([
            _REDIS_COMMAND_PATH, '-h', node.ip_address.ip, '-p', _REDIS_PORT, '--cluster',
            'rebalance', node.ip_address.ip + ':' + _REDIS_PORT, '--cluster-use-empty-masters',
            '--cluster-yes'
        ])
        if result.returncode == 0:
            LOG.info('Rebalancing successful')
        else:
            LOG.warn('Rebalancing failed using %s. Trying using other nodes', node.name)


def get_node_id(source_ip, host):
    """ Return the id of the provided host """
    cmd = [_REDIS_COMMAND_PATH, '-h', source_ip, '-p', _REDIS_PORT, '-c', 'cluster', 'nodes']
    nodes_ps = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    grep_ps = subprocess.Popen(['grep', host], stdout=subprocess.PIPE, stdin=nodes_ps.stdout)
    node_id = subprocess.check_output(['awk', '{print $1}'], stdin=grep_ps.stdout)
    nodes_ps.wait()
    return node_id.strip() if node_id else None


@retry(retry_on_result=lambda r: not r, stop_max_attempt_number=15, wait_fixed=1000)
def attach_slave(master_cntr_grp, slave_cntr_grp):
    """ Attach slave to the provided master """
    # Extract master node id
    master_node_id = get_node_id(slave_cntr_grp.ip_address.ip, master_cntr_grp.ip_address.ip)

    if not master_node_id:
        LOG.error('Unable to extract master node id from %s', master_cntr_grp.ip_address.ip)
        return False

    result = subprocess.run([
        _REDIS_COMMAND_PATH, '-h', slave_cntr_grp.ip_address.ip, '-p', _REDIS_PORT, '-c', 'cluster',
        'replicate', master_node_id
    ])

    return result.returncode == 0


def del_node(cntr_grp, cluster):
    """ Drop container from the cluster """
    for node in cluster:
        LOG.info('Trying to delete %s from %s', cntr_grp.name, node.ip_address.ip)

        cntr_id = get_node_id(node.ip_address.ip, cntr_grp.ip_address.ip)
        if not cntr_id:
            LOG.error('Unable to get id of %s', cntr_grp.name)
            continue

        result = subprocess.run([
            _REDIS_COMMAND_PATH, '-h', node.ip_address.ip, '-p', _REDIS_PORT, '--cluster',
            'del-node', node.ip_address.ip + ':' + _REDIS_PORT, cntr_id
        ])

        if result.returncode == 0:
            LOG.info('Succesfully removed %s from cluster', cntr_grp.name)
            break
        else:
            LOG.warn('Failed to remove %s from cluster using %s, trying with other nodes',
                     cntr_grp.name, node.ip_address.ip)


def reshard(cntr_grp, cluster):
    """ Reshard the provided node """
    for node in cluster:
        LOG.info('Trying to reshard from %s to %s', cntr_grp.name, node.name)

        cntr_id = get_node_id(node.ip_address.ip, cntr_grp.ip_address.ip)
        if not cntr_id:
            LOG.error('Unable to get id of %s', cntr_grp.name)
            return

        node_id = get_node_id(node.ip_address.ip, node.ip_address.ip)

        if not node_id:
            LOG.error('Unable to find id for %s', node.name)
            continue

        result = subprocess.run([
            _REDIS_COMMAND_PATH, '-h', node.ip_address.ip, '-p', _REDIS_PORT, '--cluster',
            'reshard', cntr_grp.ip_address.ip + ':' + _REDIS_PORT, '--cluster-from', cntr_id,
            '--cluster-to', node_id, '--cluster-slots', '16384', '--cluster-yes'
        ])

        if result.returncode == 0:
            LOG.info('Reshard successful')
            break
        else:
            LOG.warn('Unable to reshard from %s to %s, trying with other nodes', cntr_grp.name,
                     node.name)
