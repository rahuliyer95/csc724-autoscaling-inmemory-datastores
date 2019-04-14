"""
Azure communications
"""
import azure.mgmt.containerinstance.models as acimodels
import os
import re
import time
from azure.common.client_factory import get_client_from_auth_file
from azure.mgmt.containerinstance import ContainerInstanceManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient

_ACI_CLIENT = None
_ARM_CLIENT = None
_ANM_CLIENT = None
_DATADOG_API_KEY = os.getenv('DD_API_KEY', default='')
_COLLECTD_INTERVAL = os.getenv('ENV_INTERVAL', default='')
_REDIS_PORTS = [6379, 6380, 16379]
_CONTAINER_IMAGE = 'rahuliyer95/csc724-redis-collectd'
_RESOURCE_GROUP = 'csc724'
_NETWORK_PROFILE = 'aci-network-profile-csc724-default'
_REDIS_MASTER_REGEX = re.compile(r'^csc724-redis-[0-9]*$')
_REDIS_SLAVE_REGEX = re.compile(r'^csc724-redis-slave-[0-9]*$')


def _get_aci_client():
    """ Retrieves a `ContainerInstanceManagementClient` """
    global _ACI_CLIENT
    if not _ACI_CLIENT:
        _ACI_CLIENT = get_client_from_auth_file(ContainerInstanceManagementClient)
    return _ACI_CLIENT


def _get_arm_client():
    """ Retrieves a `ResourceManagementClient` """
    global _ARM_CLIENT
    if not _ARM_CLIENT:
        _ARM_CLIENT = get_client_from_auth_file(ResourceManagementClient)
    return _ARM_CLIENT


def _get_anm_client():
    """ Retrieves a `NetworkManagementClient` """
    global _ANM_CLIENT
    if not _ANM_CLIENT:
        _ANM_CLIENT = get_client_from_auth_file(NetworkManagementClient)
    return _ANM_CLIENT


def get_redis_master_nodes():
    """ Retrieves a list of redis master nodes """
    az = _get_aci_client()
    return [cntr for cntr in az.container_groups.list() if _REDIS_MASTER_REGEX.match(cntr.name)]


def get_redis_slave_nodes():
    """ Retrieves a list of redis slave nodes """
    az = _get_aci_client()
    return [cntr for cntr in az.container_groups.list() if _REDIS_SLAVE_REGEX.match(cntr.name)]


def add_redis_node(name, kafka_host, kafka_port):
    """
    Deploy a new redis cluster node

    :param name: name of the new container
    """
    aci = _get_aci_client()
    arm = _get_arm_client()
    anm = _get_anm_client()

    resource_group = arm.resource_groups.get(_RESOURCE_GROUP)

    envs = [
        acimodels.EnvironmentVariable(name='DD_API_KEY', value=_DATADOG_API_KEY),
        acimodels.EnvironmentVariable(name='ENV_BROKER', value=kafka_host + ':' + str(kafka_port)),
        acimodels.EnvironmentVariable(name='ENV_INTERVAL', value=_COLLECTD_INTERVAL)
    ]

    container = acimodels.Container(
        name=name,
        image=_CONTAINER_IMAGE,
        resources=acimodels.ResourceRequirements(
            requests=acimodels.ResourceRequests(memory_in_gb=1, cpu=1.0)),
        environment_variables=envs,
        ports=[acimodels.ContainerPort(port=p) for p in _REDIS_PORTS])

    network_profile = acimodels.ContainerGroupNetworkProfile(
        id=anm.network_profiles.get(_RESOURCE_GROUP, _NETWORK_PROFILE).id)

    ports = [
        acimodels.Port(protocol=acimodels.ContainerGroupNetworkProtocol.tcp, port=p)
        for p in _REDIS_PORTS
    ]
    ip_address = acimodels.IpAddress(ports=ports,
                                     type=acimodels.ContainerGroupIpAddressType.private)

    # Configure the container group
    container_group = acimodels.ContainerGroup(location=resource_group.location,
                                               containers=[container],
                                               os_type=acimodels.OperatingSystemTypes.linux,
                                               network_profile=network_profile,
                                               ip_address=ip_address)

    aci.container_groups.create_or_update(resource_group.name, name, container_group)


def wait_for_container(name):
    """ Wait for container to be created """
    aci = _get_aci_client()
    while True:
        cg = aci.container_groups.get(_RESOURCE_GROUP, name)
        if cg.containers[0].instance_view \
                and cg.containers[0].instance_view.current_state.state.lower() == 'running':
            return cg
        time.sleep(3)
    return None
