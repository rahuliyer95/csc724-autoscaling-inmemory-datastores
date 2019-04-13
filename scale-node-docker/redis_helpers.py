import subprocess
from scale import LOG

_REDIS_COMMAND_PATH = '/usr/local/bin/redis-cli'


def join_cluster(container_group, cluster):
    for node in cluster:
        LOG.info('Trying to attach to %s', node.name)
        result = _cluster_meet(node.ip_address.ip, 6379, container_group.ip_address.ip, 6379)
        if result.returncode == 0:  # Successful
            LOG.info('Sucessfully met with cluster using %s', node.name)
            return True
        else:
            LOG.error('Unable to join cluster using %s. Trying the rest', node.name)

    LOG.error('%s failed to join cluster...', container_group.name)
    return False


def _cluster_meet(host_ip, host_port, node_ip, node_port):
    return subprocess.run([
        _REDIS_COMMAND_PATH, '-h', host_ip, '-p',
        str(host_port), '-c', 'cluster', 'meet', node_ip,
        str(node_port)
    ])


def attach_slave(master_cntr_grp, slave_cntr_grp):
    """ Attach slave to the provided master """
    # Extract master node id
    cmd = [_REDIS_COMMAND_PATH, '-h', master_cntr_grp.ip_address.ip, '-p', 6379, 'cluster', 'nodes']
    cluster_nodes_ps = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    master_node_id = subprocess.check_output(['awk', '{print $1}'], stdin=cluster_nodes_ps.stdout)
    cluster_nodes_ps.wait()

    if not master_node_id:
        LOG.error('Unable to extract master node id from %s', master_cntr_grp.ip_address.ip)
        return False

    result = subprocess.run([
        _REDIS_COMMAND_PATH, '-h', slave_cntr_grp.ip_address.ip, '-p', '6379', 'cluster',
        'replicate', master_node_id
    ])

    return result.returncode == 0
