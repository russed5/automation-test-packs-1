#!/usr/bin/python
# Author:
# Revision: 1.1
# Code Reviewed by:
# Description: Testing the vCenter-Adapter Container.
#
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information
#
import af_support_tools
import pytest
import json
import requests
import os
import time


##############################################################################################

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
    global rabbitmq_hostname ,port
    port = af_support_tools.get_config_file_property(config_file=env_file, heading='RabbitMQ',
                                                     property='ssl_port')
    rabbitmq_hostname = "amqp.cpsd.dell"

    #Consul Details
    global consul_hostname
    consul_hostname = "consul.cpsd.dell"

    # Update setup_config.ini file at runtime
    my_data_file = os.environ.get('AF_RESOURCES_PATH') + '/continuous-integration-deploy-suite/setup_config.properties'
    af_support_tools.set_config_file_property_by_data_file(my_data_file)

    # vCenter VM IP & Creds details
    global setup_config_file
    setup_config_file = 'continuous-integration-deploy-suite/setup_config.ini'

    global setup_config_header
    setup_config_header = 'config_details'

    global vcenter_IP
    vcenter_IP = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                           heading=setup_config_header, property='vcenter_ipaddress')
    global vcenter_username
    vcenter_username = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                 heading=setup_config_header,
                                                                 property='vcenter_username')
    global vcenter_password
    vcenter_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                 heading=setup_config_header,
                                                                 property='vcenter_password')
    global rpm_name
    rpm_name = "dell-cpsd-hal-vcenter-adapter"

    global service_name
    service_name = 'dell-cpsd-hal-vcenter-adapter'

    global vcenter_port
    vcenter_port = '443'




#####################################################################
# These are the main tests.
#####################################################################

@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_vcenter_adapter_servicerunning():
    """
    Title           :       Verify the vCenter-Adapter service is running
    Description     :       This method tests docker service for a container
                            It will fail if :
                                Docker service is not running for the container
    Parameters      :       none
    Returns         :       None
    """

    print('\n* * * Testing the VCenter-Adapter Service on system:', ipaddress, '* * *\n')


    # 1. Test the service is running
    sendCommand = "docker ps --filter name=" + service_name + "  --format '{{.Status}}' | awk '{print $1}'"
    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                         command=sendCommand, return_output=True)
    my_return_status = my_return_status.strip()
    print('\nDocker Container is:', my_return_status, '\n')
    assert my_return_status == 'Up', (service_name + " not running")


@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_registerVcenter():
    # Until consul is  working properly & integrated with the vcenter adapter in the same environment we need to register
    # it manually by sending this message.

    cleanup('test.controlplane.vcenter.response')
    cleanup('test.endpoint.registration.event')
    bindQueues('exchange.dell.cpsd.controlplane.vcenter.response', 'test.controlplane.vcenter.response')
    bindQueues('exchange.dell.cpsd.endpoint.registration.event', 'test.endpoint.registration.event')

    time.sleep(2)

    af_support_tools.rmq_purge_queue(host='amqp', port=5671,
                                     ssl_enabled=True,
                                     queue='test.controlplane.vcenter.response')

    af_support_tools.rmq_purge_queue(host='amqp', port=5671,
                                     ssl_enabled=True,
                                     queue='test.endpoint.registration.event')

    the_payload = '{"messageProperties":{"timestamp":"2010-01-01T12:00:00Z","correlationId":"vcenter-registtration-corr-id","replyTo":"localhost"},"registrationInfo":{"address":"https://' + vcenter_IP + ':' + vcenter_port + '","username":"' + vcenter_username + '","password":"' + vcenter_password + '"}}'
    
    af_support_tools.rmq_publish_message(host='amqp', port=5671,
                                         ssl_enabled=True,
                                         exchange='exchange.dell.cpsd.controlplane.vcenter.request',
                                         routing_key='controlplane.hypervisor.vcenter.endpoint.register',
                                         headers={
                                             '__TypeId__': 'com.dell.cpsd.vcenter.registration.info.request'},
                                         payload=the_payload)

    # Verify the vcenter is validated
    assert waitForMsg('test.controlplane.vcenter.response'), 'ERROR: No validation Message Returned'
    return_message = af_support_tools.rmq_consume_message(host='amqp', port=5671,
                                                          ssl_enabled=True,
                                                          queue='test.controlplane.vcenter.response',
                                                          remove_message=True)
    return_json = json.loads(return_message, encoding='utf-8')
    
    assert return_json['responseInfo']['message'] == 'SUCCESS', 'ERROR: Vcenter validation failure'

    #May remove the below commented test due to test cases already existing for consul registration further down

    # # Verify the system triggers a msg to register vcenter with consul
    # assert waitForMsg('test.endpoint.registration.event'), 'ERROR: No message to register with Consul sent'
    # return_message = af_support_tools.rmq_consume_message(host='amqp', port=5671,
    #                                                       ssl_enabled=True,
    #                                                       queue='test.endpoint.registration.event',
    #                                                       remove_message=True)
    #
    # return_json = json.loads(return_message, encoding='utf-8')
    # print (return_json)
    # assert return_json['endpoint']['type'] == 'vcenter', 'vcenter not registered with endpoint'

    cleanup('test.controlplane.vcenter.response')
    cleanup('test.endpoint.registration.event')

    time.sleep(3)


@pytest.mark.parametrize('exchange, queue', [
    ('exchange.dell.cpsd.controlplane.vcenter.request', 'queue.dell.cpsd.controlplane.vcenter.add.host.license'),
    ('exchange.dell.cpsd.controlplane.vcenter.request', 'queue.dell.cpsd.controlplane.vcenter.addhostdvswitch'),
    ('exchange.dell.cpsd.controlplane.vcenter.request', 'queue.dell.cpsd.controlplane.vcenter.cluster.discover'),
    ('exchange.dell.cpsd.controlplane.vcenter.request', 'queue.dell.cpsd.controlplane.vcenter.clusteroperation'),
    ('exchange.dell.cpsd.controlplane.vcenter.request', 'queue.dell.cpsd.controlplane.vcenter.deployVMFromTemplate'),
    ('exchange.dell.cpsd.controlplane.vcenter.request', 'queue.dell.cpsd.controlplane.vcenter.discover'),
    ('exchange.dell.cpsd.controlplane.vcenter.request', 'queue.dell.cpsd.controlplane.vcenter.host.enter-maintenance'),
    ('exchange.dell.cpsd.controlplane.vcenter.request', 'queue.dell.cpsd.controlplane.vcenter.host.powercommand'),
    ('exchange.dell.cpsd.controlplane.vcenter.request', 'queue.dell.cpsd.controlplane.vcenter.pci.enable.passthrough'),
    ('exchange.dell.cpsd.controlplane.vcenter.request', 'queue.dell.cpsd.controlplane.vcenter.pci.passthrough'),
    ('exchange.dell.cpsd.controlplane.vcenter.request', 'queue.dell.cpsd.controlplane.vcenter.register'),
    ('exchange.dell.cpsd.controlplane.vcenter.request', 'queue.dell.cpsd.controlplane.vcenter.softwareVIB'),
    ('exchange.dell.cpsd.controlplane.vcenter.request', 'queue.dell.cpsd.controlplane.vcenter.softwareVIBConfigure'),
    ('exchange.dell.cpsd.controlplane.vcenter.request', 'queue.dell.cpsd.controlplane.vcenter.vm.destroy'),
    ('exchange.dell.cpsd.hdp.hal.data.provider.vcenter.compute.data.provider.request',
     'queue.dell.cpsd.hdp.hal.data.provider.device.data.discovery.request.vcenter-compute-data-provider'),
    ('exchange.dell.cpsd.hdp.hal.data.provider.vcenter.compute.data.provider.request',
     'queue.dell.cpsd.hdp.hal.data.provider.endpoint.validation.request.vcenter-compute-data-provider'),
    ('exchange.dell.cpsd.syds.system.definition.response',
     'queue.dell.cpsd.adapter.vcenter.component.configuration.found'),
    ('exchange.dell.cpsd.cms.credentials.response', 'queue.dell.cpsd.adapter.vcenter.component.credentials.found'),
    ('exchange.dell.cpsd.endpoint.registration.event', 'queue.dell.cpsd.controlplane.vcenter.endpoint-events'),
    ('exchange.dell.cpsd.hdp.capability.registry.control',
     'queue.dell.cpsd.hdp.capability.registry.control.vcenter-adapter'),
    ('exchange.dell.cpsd.hdp.capability.registry.event',
     'queue.dell.cpsd.hdp.capability.registry.event.vcenter-adapter'),
    ('exchange.dell.cpsd.hdp.capability.registry.response',
     'queue.dell.cpsd.hdp.capability.registry.response.vcenter-adapter')])
@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
@pytest.mark.skip(reason="Currently under review if these tests should be performed at unit test level")
def test_vcenter_adapter_RMQ_bindings_core(exchange, queue):
    """
    Title           :       Verify the RMQ bindings
    Description     :       This method tests that a binding exists between a RMQ Exchange & a RMQ Queue.
                            It uses the RMQ API to check.
                            It will fail if :
                                The RMQ binding does not exist
    Parameters      :       1. RMQ Exchange. 2. RQM Queue
    Returns         :       None
    """

    queues = rest_queue_list(user="guest", password="guest", host=rabbitmq_hostname, port=15672, virtual_host='%2f',
                             exchange=exchange)
    queues = json.dumps(queues)

    assert queue in queues, 'The queue "' + queue + '" is not bound to the exchange "' + exchange + '"'
    

@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_vcenter_adapter_full_ListCapabilities():
    """
    Title           :       Verify the registry.list.capability Message returns all vcenter-adapter capabilities
    Description     :       A registry.list.capability message is sent.  It is expected that a response is returned that
                            includes a list of all the vcenter-adapter capabilities.
                            It will fail if :
                               No capability.registry.response is received.
                               The vcenter-adapter is not in the response.
                               The vcenter-adapter capabilites are not in the response.
    Parameters      :       none
    Returns         :       None
    """
    cleanup('test.capability.registry.response')
    bindQueues('exchange.dell.cpsd.hdp.capability.registry.response', 'test.capability.registry.response')

    print("\nTest: Send in a list capabilities message and to verify all vCenter Adapter capabilities are present")

    # Send in a "list capabilities message"
    originalcorrelationID = 'capability-registry-list-vcenter-adapter-corID'
    the_payload = '{}'

    af_support_tools.rmq_publish_message(host='amqp', port=5671,
                                         exchange='exchange.dell.cpsd.hdp.capability.registry.request',
                                         routing_key='dell.cpsd.hdp.capability.registry.request',
                                         headers={
                                             '__TypeId__': 'com.dell.cpsd.hdp.capability.registry.list.capability.providers'},
                                         payload=the_payload,
                                         payload_type='json',
                                         correlation_id={originalcorrelationID}, ssl_enabled=True)

    # Wait for and consume the Capability Response Message
    assert waitForMsg('test.capability.registry.response'), 'ERROR: No List Capabilities Message returned'
    time.sleep(10)
    return_message = af_support_tools.rmq_consume_message(host='amqp', port=5671,
                                                          queue='test.capability.registry.response',
                                                          ssl_enabled=True)
     
    # Verify the vcenter Apapter Response
    identity = 'vcenter-adapter'
    capabilities1 = 'vcenter-consul-register'
    capabilities2 = 'vcenter-discover'
    capabilities3 = 'vcenter-enterMaintenance'
    capabilities4 = 'vcenter-destroy-virtualMachine'
    capabilities5 = 'vcenter-powercommand'
    capabilities6 = 'vcenter-discover-cluster'
    capabilities7 = 'vcenter-remove-host'
    capabilities8 = 'vcenter-addhostvcenter'
    capabilities9 = 'vcenter-install-software-vib'
    capabilities10 = 'vcenter-configure-software-vib'
    capabilities11 = 'vcenter-setPCIpassthrough'
    capabilities12 = 'vcenter-addhostlicense'
    capabilities13 = 'vcenter-deployvmfromtemplate'
    capabilities14 = 'vcenter-enablePCIpassthroughHost'
    capabilities15 = 'vcenter-addhostdvswitch'
    capabilities16 = 'vcenter-rename-datastore'
    capabilities17 = 'vcenter-list-components'
    capabilities18 = 'esxi-credential-details'
    capabilities21 = 'vcenter-update-software-acceptance'
    capabilities22 = 'vcenter-vm-powercommand'
    capabilities23 = 'vcenter-configure-vm-network'
    capabilities24 = 'vcenter-execute-remote-ssh-commands'


    error_list = []

    if (identity not in return_message):
        error_list.append(identity)
    if (capabilities1 not in return_message):
        error_list.append(capabilities1)
    if (capabilities2 not in return_message):
        error_list.append(capabilities2)
    if (capabilities3 not in return_message):
        error_list.append(capabilities3)
    if (capabilities4 not in return_message):
        error_list.append(capabilities4)
    if (capabilities5 not in return_message):
        error_list.append(capabilities5)
    if (capabilities6 not in return_message):
        error_list.append(capabilities6)
    if (capabilities7 not in return_message):
        error_list.append(capabilities7)
    if (capabilities8 not in return_message):
        error_list.append(capabilities8)
    if (capabilities9 not in return_message):
        error_list.append(capabilities9)
    if (capabilities10 not in return_message):
        error_list.append(capabilities10)
    if (capabilities11 not in return_message):
        error_list.append(capabilities11)
    if (capabilities12 not in return_message):
        error_list.append(capabilities12)
    if (capabilities13 not in return_message):
        error_list.append(capabilities13)
    if (capabilities14 not in return_message):
        error_list.append(capabilities14)
    if (capabilities15 not in return_message):
        error_list.append(capabilities15)
    if (capabilities16 not in return_message):
        error_list.append(capabilities16)
    if (capabilities17 not in return_message):
        error_list.append(capabilities17)
    if (capabilities18 not in return_message):
        error_list.append(capabilities18)
    if (capabilities21 not in return_message):
        error_list.append(capabilities21)
    if (capabilities22 not in return_message):
        error_list.append(capabilities22)
    if (capabilities23 not in return_message):
        error_list.append(capabilities23)
    if (capabilities24 not in return_message):
        error_list.append(capabilities24)


    assert not error_list, ('Missing some vcenter-adapter capabilities')

    print('All expected vcenter-adapter Capabilities Returned\n')

    cleanup('test.capability.registry.response')


@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_vcenter_adapter_log_files_exist():
    """
    Title           :       Verify vcenter-adapter log files exist
    Description     :       This method tests that the vCenter Adapter log files exist.
                            It will fail:
                                If the the error and/or info log files do not exists
    Parameters      :       None
    Returns         :       None
    """

    service = 'dell-cpsd-hal-vcenter-adapter'
    filePath = '/opt/dell/cpsd/vcenter-adapter/logs/'
    errorLogFile = 'vcenter-adapter-error.log'
    infoLogFile = 'vcenter-adapter-info.log'

    sendCommand = 'docker ps | grep ' + service + ' | awk \'{system("docker exec -i "$1" ls ' + filePath + '") }\''

    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                         command=sendCommand, return_output=True)
    error_list = []

    if (errorLogFile not in my_return_status):
        error_list.append(errorLogFile)

    if (infoLogFile not in my_return_status):
        error_list.append(infoLogFile)

    assert not error_list, 'Log file missing'

    print('Valid log files exist')


@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_vcenter_adapter_log_files_free_of_exceptions():
    """
    Title           :       Verify there are no exceptions in the log files
    Description     :       This method tests that the vcenter-adapter log files contain no Exceptions.
                            It will fail:
                                If the the error and/or info log files do not exists
                                If the error log file contains AuthenticationFailureException, RuntimeException, NullPointerException or BeanCreationException.
    Parameters      :       None
    Returns         :       None
    """

    service = 'dell-cpsd-hal-vcenter-adapter'
    filePath = '/opt/dell/cpsd/vcenter-adapter/logs/'
    errorLogFile = 'vcenter-adapter-error.log'
    excep1 = 'AuthenticationFailureException'
    excep2 = 'RuntimeException'
    excep3 = 'NullPointerException'
    excep4 = 'BeanCreationException'

    # Verify the log files exist
    sendCommand = 'docker ps | grep ' + service + ' | awk \'{system("docker exec -i "$1" ls ' + filePath + '") }\''

    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                         command=sendCommand, return_output=True)

    assert errorLogFile in my_return_status, 'Log file does not exist so unable to check for exceptions'

    error_list = []

    # Verify there are no Authentication errors
    sendCommand = 'docker ps | grep ' + service + ' | awk \'{system("docker exec -i "$1" cat /' + filePath + errorLogFile + ' | grep ' + excep1 + '") }\''
    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                         command=sendCommand, return_output=True)
    print (my_return_status)
    if (excep1 in my_return_status):
        error_list.append(excep1)

    # Verify there are no RuntimeException errors
    sendCommand = 'docker ps | grep ' + service + ' | awk \'{system("docker exec -i "$1" cat /' + filePath + errorLogFile + ' | grep ' + excep2 + '") }\''
    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                         command=sendCommand, return_output=True)
    if (excep2 in my_return_status):
        error_list.append(excep2)

    # Verify there are no NullPointerException errors
    sendCommand = 'docker ps | grep ' + service + ' | awk \'{system("docker exec -i "$1" cat /' + filePath + errorLogFile + ' | grep ' + excep3 + '") }\''
    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                         command=sendCommand, return_output=True)
    if (excep3 in my_return_status):
        error_list.append(excep3)

    # Verify there are no BeanCreationException errors
    sendCommand = 'docker ps | grep ' + service + ' | awk \'{system("docker exec -i "$1" cat /' + filePath + errorLogFile + ' | grep ' + excep4 + '") }\''
    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                         command=sendCommand, return_output=True)
    if (excep4 in my_return_status):
        error_list.append(excep4)

    assert not error_list, 'Exceptions in log files, Review the ' + errorLogFile + ' file'

    print('No ' + excep1, excep2, excep3, excep4 + ' exceptions in log files\n')


@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
@pytest.mark.skip(reason="This test will be moved to another suite")
def test_vcenter_removerpm():
    err = []

    sendCommand = "yum remove -y " + rpm_name
    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                         command=sendCommand, return_output=True)

    # 1. Test the service is
    sendCommand = "docker ps --filter name=" + service_name + "  --format '{{.Status}}' | awk '{print $1}'"
    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                         command=sendCommand, return_output=True)
    my_return_status = my_return_status.strip()
    print('\nDocker Container is:', my_return_status, '\n')
    assert my_return_status != 'Up', (service_name + " still running")


    sendCommand = 'ls /opt/dell/cpsd/ | grep "hal-mediation" '
    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                         command=sendCommand, return_output=True)

    if "hal-mediation" in my_return_status:
        err.append('hal-mediation-service not removed')
    assert not err
    
    
     #installing rpm
    sendCommand = "yum install -y " + rpm_name
    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                         command=sendCommand, return_output=True)

    # 1. Test the service is running
    sendCommand = "docker ps --filter name=" + service_name + "  --format '{{.Status}}' | awk '{print $1}'"
    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                         command=sendCommand, return_output=True)
    my_return_status = my_return_status.strip()
    print('\nDocker Container is:', my_return_status, '\n')
    assert my_return_status == 'Up', (service_name + " not running")


##############################################################################################


def bindQueues(exchange, queue):
    af_support_tools.rmq_bind_queue(host='amqp', port=5671,
                                    queue=queue,
                                    exchange=exchange,
                                    routing_key='#', ssl_enabled=True)


def cleanup(queue):
    af_support_tools.rmq_delete_queue(host='amqp', port=5671,
                                      queue=queue, ssl_enabled=True)


def waitForMsg(queue):
    # This function keeps looping until a message is in the specified queue. We do need it to timeout and throw an error
    # if a message never arrives. Once a message appears in the queue the function is complete and main continues.

    # The length of the queue, it will start at 0 but as soon as we get a response it will increase
    q_len = 0

    # Represents the number of seconds that have gone by since the method started
    timeout = 0

    # Max number of seconds to wait
    max_timeout = 500

    # Amount of time in seconds that the loop is going to wait on each iteration
    sleeptime = 1

    while q_len < 1:
        time.sleep(sleeptime)
        timeout += sleeptime

        q_len = af_support_tools.rmq_message_count(host='amqp', port=5671,
                                                   queue=queue, ssl_enabled=True)

        if timeout > max_timeout:
            print('ERROR: Message took too long to return. Something is wrong')
            return False

    return True

def rest_queue_list(user=None, password=None, host=None, port=None, virtual_host=None, exchange=None):
    """
    Description     :       This method returns all the RMQ Queues that are bound to a names RMQ Exchange.
    Parameters      :       RMQ User, RMQ password, host, port & exchange. Always virtual_host = '%2f'
    Returns         :       A list of the Queues bound to the named Exchange/
    """
    url = 'https://%s:%s/api/exchanges/%s/%s/bindings/source' % (host,port, virtual_host, exchange)
    response = requests.get(url, verify ="/usr/local/share/ca-certificates/cpsd.dell.ca.crt", auth=(user, password))
    queues = [q['destination'] for q in response.json()]
    return queues

    #######################################################################################################################
