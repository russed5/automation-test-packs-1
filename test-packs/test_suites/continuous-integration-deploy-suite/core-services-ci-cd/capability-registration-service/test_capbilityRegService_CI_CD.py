#!/usr/bin/python
# Author: cullia
# Revision: 2.1
# Code Reviewed by:
# Description: Verify the service is running, logfiles exist and all RMQ bindings are present.
#
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information
#
import af_support_tools
import json
import pytest
import requests
import time


@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    import cpsd
    global cpsd

   

    # Set config ini file name
    global env_file
    env_file = 'env.ini'

    # Test VM Details
    global ipaddress
    ipaddress = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')

    global cli_username
    cli_username = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                             property='username')

    global cli_password
    cli_password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                             property='password')

    # RMQ Details
    global rmq_username
    rmq_username = af_support_tools.get_config_file_property(config_file=env_file, heading='RabbitMQ',
                                                             property='username')
    global rmq_password
    rmq_password = af_support_tools.get_config_file_property(config_file=env_file, heading='RabbitMQ',
                                                             property='password')
    global rmq_port
    rmq_port = af_support_tools.get_config_file_property(config_file=env_file, heading='RabbitMQ',
                                                         property='ssl_port')


#####################################################################
# These are the main tests.
#####################################################################


@pytest.mark.daily_status
@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_enable_rabbitmq_management_plugin():
    """ A function to enable the rabbitmq_management plugin
    It won't cause any errrors if it is already enabled"""
    command = 'docker exec -d amqp rabbitmq-plugins enable rabbitmq_management'
    af_support_tools.send_ssh_command(
        host=ipaddress,
        username=cli_username,
        password=cli_password,
        command=command,
        return_output=False)

### "
@pytest.mark.skip(reason="The test is moved into test_capbilityRegService_ListCapabilities_CI_CD.py")
@pytest.mark.daily_status
@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_capabilityRegistry_servicerunning():
    """
    Title           :       Verify the Capability Registry service is running
    Description     :       This method tests docker service for a container
                            It will fail if :
                                Docker service is not running for the container
    Parameters      :       none
    Returns         :       None
    """

    print('\n* * * Testing the Capability Registry on system:', ipaddress, '* * *\n')

    service_name = 'symphony-capability-registry-service'

    # 1. Test the service is running
    sendCommand = "docker ps --filter name=" + service_name + "  --format '{{.Status}}' | awk '{print $1}'"
    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                         command=sendCommand, return_output=True)
    my_return_status = my_return_status.strip()
    print('\nDocker Container is:', my_return_status, '\n')
    assert my_return_status == 'Up', (service_name + " not running")

    time.sleep(20)


@pytest.mark.daily_status
@pytest.mark.parametrize('exchange, queue', [
    ('exchange.dell.cpsd.hdp.capability.registry.binding', 'queue.dell.cpsd.hdp.capability.registry.binding'),
    ('exchange.dell.cpsd.hdp.capability.registry.control', 'queue.dell.cpsd.hdp.capability.registry.control.coprhd-adapter'),
    ('exchange.dell.cpsd.hdp.capability.registry.control', 'queue.dell.cpsd.hdp.capability.registry.control.endpoint-registry'),
    ('exchange.dell.cpsd.hdp.capability.registry.control', 'queue.dell.cpsd.hdp.capability.registry.control.poweredge-compute-data-provider'),
    ('exchange.dell.cpsd.hdp.capability.registry.control', 'queue.dell.cpsd.hdp.capability.registry.control.rackhd-adapter'),
    ('exchange.dell.cpsd.hdp.capability.registry.control', 'queue.dell.cpsd.hdp.capability.registry.control.vcenter-adapter'),
    ('exchange.dell.cpsd.hdp.capability.registry.control', 'queue.dell.cpsd.hdp.capability.registry.control.vcenter-compute-data-provider'),
    ('exchange.dell.cpsd.hdp.capability.registry.event','queue.dell.cpsd.hdp.capability.registry.event.rackhd-adapter'),
    ('exchange.dell.cpsd.hdp.capability.registry.event','queue.dell.cpsd.hdp.capability.registry.event.vcenter-adapter'),
    ('exchange.dell.cpsd.hdp.capability.registry.event','queue.dell.cpsd.hdp.capability.registry.event.coprhd-adapter'),
    ('exchange.dell.cpsd.hdp.capability.registry.request','queue.dell.cpsd.hdp.capability.registry.request'),
    ('exchange.dell.cpsd.hdp.capability.registry.response','queue.dell.cpsd.hdp.capability.registry.response.coprhd-adapter'),
    ('exchange.dell.cpsd.hdp.capability.registry.response','queue.dell.cpsd.hdp.capability.registry.response.rackhd-adapter'),
    ('exchange.dell.cpsd.hdp.capability.registry.response','queue.dell.cpsd.hdp.capability.registry.response.vcenter-adapter'),
    ('exchange.dell.cpsd.hdp.capability.registry.response','queue.dell.cpsd.hdp.capability.registry.response.hal-orchestrator-service')])

@pytest.mark.skip(reason="These tests can't run in future asRMQ username/password functionality will be removed, These test  should be running "
                         "as a part of unit tests")
@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_capability_registry_RMQ_bindings_core(exchange, queue):
    """
    Title           :       Verify the Capability Registry expected RMQ bindings.
    Description     :       This method tests that a binding exists between a RMQ Exchange & a RMQ Queue.
                            It uses the RMQ API to check.
                            It will fail if :
                                The RMQ binding does not exist
    Parameters      :       1. RMQ Exchange. 2. RQM Queue
    Returns         :       None
    """

    queues = rest_queue_list(user=rmq_username, password=rmq_password, host=ipaddress, port=15672, virtual_host='%2f',
                             exchange=exchange)
    queues = json.dumps(queues)

    assert queue in queues, 'The queue "' + queue + '" is not bound to the exchange "' + exchange + '"'
    print(exchange, '\nis bound to\n', queue, '\n')


@pytest.mark.parametrize('exchange, queue', [
    ('exchange.dell.cpsd.hdp.capability.registry.control', 'queue.dell.cpsd.hdp.capability.registry.control.node-discovery-paqx'),
    ('exchange.dell.cpsd.hdp.capability.registry.event', 'queue.dell.cpsd.hdp.capability.registry.event.node-discovery-paqx'),
    ('exchange.dell.cpsd.hdp.capability.registry.event', 'queue.dell.cpsd.hdp.capability.registry.event.dne-paqx'),
    ('exchange.dell.cpsd.hdp.capability.registry.response','queue.dell.cpsd.hdp.capability.registry.response.dne-paqx'),
    ('exchange.dell.cpsd.hdp.capability.registry.response','queue.dell.cpsd.hdp.capability.registry.response.node-discovery-paqx')])

@pytest.mark.skip(reason="These tests can't run in future asRMQ username/password functionality will be removed, These test  should be running "
                         "as a part of unit tests")
@pytest.mark.dne_paqx_parent
@pytest.mark.dne_paqx_parent_mvp_extended
def test_capability_registry_RMQ_bindings_dne(exchange, queue):
    """
    Title           :       Verify the Capability Registry expected RMQ bindings.
    Description     :       This method tests that a binding exists between a RMQ Exchange & a RMQ Queue.
                            It uses the RMQ API to check.
                            It will fail if :
                                The RMQ binding does not exist
    Parameters      :       1. RMQ Exchange. 2. RQM Queue
    Returns         :       None
    """
    enable_rabbitmq_management_plugin()
    queues = rest_queue_list(user=rmq_username, password=rmq_password, host=ipaddress, port=15672, virtual_host='%2f',
                             exchange=exchange)
    queues = json.dumps(queues)

    assert queue in queues, 'The queue "' + queue + '" is not bound to the exchange "' + exchange + '"'
    print(exchange, '\nis bound to\n', queue, '\n')


@pytest.mark.parametrize('exchange, queue', [
    ('exchange.dell.cpsd.hdp.capability.registry.event','queue.dell.cpsd.hdp.capability.registry.event.fru-paqx'),
    ('exchange.dell.cpsd.hdp.capability.registry.response','queue.dell.cpsd.hdp.capability.registry.response.fru-paqx'),])

@pytest.mark.skip(reason="These tests can't run in future asRMQ username/password functionality will be removed, These test  should be running "
                         "as a part of unit tests")
@pytest.mark.fru_paqx_parent
@pytest.mark.fru_mvp
def test_capability_registry_RMQ_bindings_fru(exchange, queue):
    """
    Title           :       Verify the Capability Registry expected RMQ bindings.
    Description     :       This method tests that a binding exists between a RMQ Exchange & a RMQ Queue.
                            It uses the RMQ API to check.
                            It will fail if :
                                The RMQ binding does not exist
    Parameters      :       1. RMQ Exchange. 2. RQM Queue
    Returns         :       None
    """

    queues = rest_queue_list(user=rmq_username, password=rmq_password, host=ipaddress, port=15672, virtual_host='%2f',
                             exchange=exchange)
    queues = json.dumps(queues)

    assert queue in queues, 'The queue "' + queue + '" is not bound to the exchange "' + exchange + '"'
    print(exchange, '\nis bound to\n', queue, '\n')



#######################################################################################################################
# These are common functions that are used throughout the main test.

def rest_queue_list(user=None, password=None, host=None, port=None, virtual_host=None, exchange=None):
    url = 'http://%s:%s/api/exchanges/%s/%s/bindings/source' % (host, port, virtual_host, exchange)
    response = requests.get(url, auth=(user, password))
    queues = [q['destination'] for q in response.json()]
    return queues

#######################################################################################################################

def enable_rabbitmq_management_plugin():
    """ A function to enable the rabbitmq_management plugin
    It won't cause any errrors if it is already enabled"""
    command = "docker exec -d amqp rabbitmq-plugins enable rabbitmq_management"
    af_support_tools.send_ssh_command(
        host=ipaddress,
        username=cli_username,
        password=cli_password,
        command=command,
        return_output=True)
