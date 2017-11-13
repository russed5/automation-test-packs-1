#!/usr/bin/python
# Author:
# Revision:
# Code Reviewed by:
# Description: Testing the RackHD-Adapter Container.
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

    af_support_tools.rmq_get_server_side_certs(host_hostname=cpsd.props.base_hostname,
                                               host_username=cpsd.props.base_username,
                                               host_password=cpsd.props.base_password, host_port=22,
                                               rmq_certs_path=cpsd.props.rmq_cert_path)

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
    global port
    port = af_support_tools.get_config_file_property(config_file=env_file, heading='RabbitMQ',
                                                     property='ssl_port')

    # Update setup_config.ini file at runtime
    my_data_file = os.environ.get('AF_RESOURCES_PATH') + '/continuous-integration-deploy-suite/setup_config.properties'
    af_support_tools.set_config_file_property_by_data_file(my_data_file)

    # RackHD VM IP & Creds details
    global setup_config_file
    setup_config_file = 'continuous-integration-deploy-suite/setup_config.ini'

    global setup_config_header
    setup_config_header = 'config_details'

    global rackHD_IP
    rackHD_IP = af_support_tools.get_config_file_property(config_file=setup_config_file, heading=setup_config_header,
                                                          property='rackhd_integration_ipaddress')

    global rackHD_username
    rackHD_username = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                heading=setup_config_header,
                                                                property='rackhd_username')

    global rackHD_password
    rackHD_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                heading=setup_config_header,
                                                                property='rackhd_password')

#####################################################################
# These are the main tests.
#####################################################################
@pytest.mark.network_services_mvp
def test_enable_rabbitmq_management():
    """
    Title           : Enable rabbitMQ management to bring up port 15762
    Description     : Since symphony ova turns off rabbitmq management by default, need enable it
                      to run following test
    Parameters      : none
    Returns         : none
    """
    sendCommand = "docker exec -d amqp rabbitmq-plugins enable rabbitmq_management"
    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                         command=sendCommand, return_output=True)
    my_return_status = my_return_status.strip()
    print('\namqp rabbitmq-plugins enable rabbitmq_management :', my_return_status, '\n')


@pytest.mark.network_services_mvp
def test_rackHD_adapter_servicerunning():
    """
    Title           :       Verify the RackHD-Adapter service is running
    Description     :       This method tests docker service for a container
                            It will fail if :
                                Docker service is not running for the container
    Parameters      :       none
    Returns         :       None
    """

    print('\n* * * Testing the Node Discovery PAQX on system:', ipaddress, '* * *\n')

    service_name = 'symphony-rackhd-adapter-service'

    # 1. Test the service is running
    sendCommand = "docker ps --filter name=" + service_name + "  --format '{{.Status}}' | awk '{print $1}'"
    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                         command=sendCommand, return_output=True)
    my_return_status = my_return_status.strip()
    print('\nDocker Container is:', my_return_status, '\n')
    assert my_return_status == 'Up', (service_name + " not running")

@pytest.mark.network_services_mvp
def test_registerRackHD():
    # Until consul is  working properly & integrated with the rackhd adapter in the same environment we need to register
    # it manually by sending this message.  This test is a prerequisite to getting the full list of

    cleanup('test.controlplane.rackhd.response')
    cleanup('test.endpoint.registration.event')
    bindQueues('exchange.dell.cpsd.controlplane.rackhd.response', 'test.controlplane.rackhd.response')
    bindQueues('exchange.dell.cpsd.endpoint.registration.event', 'test.endpoint.registration.event')

    time.sleep(2)

    af_support_tools.rmq_purge_queue(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                     rmq_username=cpsd.props.rmq_username, rmq_password=cpsd.props.rmq_password,
                                     ssl_enabled=cpsd.props.rmq_ssl_enabled,
                                     queue='test.controlplane.rackhd.response')

    af_support_tools.rmq_purge_queue(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                     rmq_username=cpsd.props.rmq_username, rmq_password=cpsd.props.rmq_password,
                                     ssl_enabled=cpsd.props.rmq_ssl_enabled,
                                     queue='test.endpoint.registration.event')

    the_payload = '{"messageProperties":{"timestamp":"2017-06-14T12:00:00Z","correlationId":"manually-reg-rackhd-3fb0-9696-3f7d28e17f72"},"registrationInfo":{"address":"http://' + rackHD_IP + ':8080/swagger-ui/","username":"' + rackHD_username + '","password":"' + rackHD_password + '"}}'
    print(the_payload)

    af_support_tools.rmq_publish_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                         rmq_username=cpsd.props.rmq_username, rmq_password=cpsd.props.rmq_password,
                                         exchange='exchange.dell.cpsd.controlplane.rackhd.request',
                                         routing_key='controlplane.rackhd.endpoint.register',
                                         headers={
                                             '__TypeId__': 'com.dell.cpsd.rackhd.registration.info.request'},
                                         payload=the_payload, ssl_enabled=cpsd.props.rmq_ssl_enabled)

    # Verify the RackHD account can be validated
    assert waitForMsg('test.controlplane.rackhd.response'), 'Error: No RackHD validation message received'
    return_message = af_support_tools.rmq_consume_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                                          rmq_username=cpsd.props.rmq_username,
                                                          rmq_password=cpsd.props.rmq_password,
                                                          ssl_enabled=cpsd.props.rmq_ssl_enabled,
                                                          queue='test.controlplane.rackhd.response',
                                                          remove_message=True)
    return_json = json.loads(return_message, encoding='utf-8')
    print (return_json)
    assert return_json['responseInfo']['message'] == 'SUCCESS', 'ERROR: RackHD validation failure'

    # Verify that an event to register the rackHD with endpoint registry is triggered
    assert waitForMsg('test.endpoint.registration.event'), 'Error: No message to register with Consul sent by system'
    return_message = af_support_tools.rmq_consume_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                                          rmq_username=cpsd.props.rmq_username,
                                                          rmq_password=cpsd.props.rmq_password,
                                                          ssl_enabled=cpsd.props.rmq_ssl_enabled,
                                                          queue='test.endpoint.registration.event',
                                                          remove_message=True)

    return_json = json.loads(return_message, encoding='utf-8')
    print (return_json)
    assert return_json['endpoint']['type'] == 'rackhd', 'rackhd not registered with endpoint'

    cleanup('test.controlplane.rackhd.response')
    cleanup('test.endpoint.registration.event')

    time.sleep(3)


@pytest.mark.parametrize('exchange, queue', [
    ('exchange.dell.cpsd.controlplane.rackhd.request', 'controlplane.hardware.list.nodes'),
    ('exchange.dell.cpsd.controlplane.rackhd.request', 'dell.cpsd.service.rcm.capability.update.firmware.requested'),
    ('exchange.dell.cpsd.controlplane.rackhd.request', 'queue.cpsd.service.configure.idrac.network.settings.requested'),
    ('exchange.dell.cpsd.controlplane.rackhd.request', 'queue.dell.cpsd.controlplane.change.idrac.credentials.request'),
    ('exchange.dell.cpsd.controlplane.rackhd.request', 'queue.dell.cpsd.controlplane.hardware.idrac.configure.request'),
    ('exchange.dell.cpsd.controlplane.rackhd.request', 'queue.dell.cpsd.controlplane.rackhd.register'),
    ('exchange.dell.cpsd.controlplane.rackhd.request', 'queue.dell.cpsd.controlplane.hardware.update.switch.firmware'),
    ('exchange.dell.cpsd.hdp.capability.registry.control',
     'queue.dell.cpsd.hdp.capability.registry.control.rackhd-adapter'),
    (
    'exchange.dell.cpsd.hdp.capability.registry.event', 'queue.dell.cpsd.hdp.capability.registry.event.rackhd-adapter'),
    ('exchange.dell.cpsd.hdp.capability.registry.response',
     'queue.dell.cpsd.hdp.capability.registry.response.rackhd-adapter'),
    ('exchange.dell.cpsd.syds.system.definition.response', 'queue.dell.cpsd.controlplane.rackhd.system.list.found'),
    ('exchange.dell.cpsd.syds.system.definition.response',
     'queue.dell.cpsd.controlplane.rackhd.component.configuration.found'),
    ('exchange.dell.cpsd.cms.credentials.response', 'queue.dell.cpsd.controlplane.rackhd.credentials.response'),
    ('exchange.dell.cpsd.endpoint.registration.event', 'queue.dell.cpsd.controlplane.rackhd.endpoint-events'),
    ('exchange.dell.cpsd.controlplane.rackhd.request', 'queue.dell.cpsd.controlplane.rackhd.register')])

@pytest.mark.network_services_mvp
def test_rackHD_RMQ_bindings_core(exchange, queue):
    """
    Title           :       Verify the RMQ bindings
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
    ('exchange.dell.cpsd.controlplane.rackhd.response', 'controlplane.hardware.list.nodes.response')])

@pytest.mark.network_services_mvp
def test_rackHD_RMQ_bindings_dne(exchange, queue):
    """
    Title           :       Verify the RMQ bindings
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


#@pytest.mark.parametrize('exchange, queue', [
#    ('exchange.dell.cpsd.adapter.rackhd.node.discovered.event', 'queue.dell.cpsd.frupaqx.node.discovered-event')])

#@pytest.mark.network_services_mvp
def test_rackHD_RMQ_bindings_fru(exchange, queue):
    """
    Title           :       Verify the RMQ bindings
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

@pytest.mark.network_services_mvp
def test_rackHD_adapter_full_ListCapabilities():
    """
    Title           :       Verify the registry.list.capability Message returns all rackhd-adapter capabilities
    Description     :       A registry.list.capability message is sent.  It is expected that a response is returned that
                            includes a list of all the rackhd-adapter capabilities.
                            It will fail if :
                               No capability.registry.response is received.
                               The rackhd-adapter is not in the response.
                               The rackhd-adapter capabilites are not in the response.
    Parameters      :       none
    Returns         :       None
    """
    cleanup('test.capability.registry.response')
    bindQueues('exchange.dell.cpsd.hdp.capability.registry.response', 'test.capability.registry.response')

    print("\nTest: Send in a list capabilities message and to verify all RackHD Adapter capabilities are present")

    # Send in a "list capabilities message"
    originalcorrelationID = 'capability-registry-list-rackhd-adapter-corID'
    the_payload = '{}'

    af_support_tools.rmq_publish_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                         rmq_username=cpsd.props.rmq_username, rmq_password=cpsd.props.rmq_password,
                                         exchange='exchange.dell.cpsd.hdp.capability.registry.request',
                                         routing_key='dell.cpsd.hdp.capability.registry.request',
                                         headers={
                                             '__TypeId__': 'com.dell.cpsd.hdp.capability.registry.list.capability.providers'},
                                         payload=the_payload,
                                         payload_type='json',
                                         correlation_id={originalcorrelationID}, ssl_enabled=cpsd.props.rmq_ssl_enabled)

    # Wait for and consume the Capability Response Message
    assert waitForMsg('test.capability.registry.response'), 'Error: No List Capability Responce message received'
    return_message = af_support_tools.rmq_consume_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                                          rmq_username=cpsd.props.rmq_username,
                                                          rmq_password=cpsd.props.rmq_password,
                                                          queue='test.capability.registry.response',
                                                          ssl_enabled=cpsd.props.rmq_ssl_enabled)
    time.sleep(5)

    # Verify the RackHD Apapter Response
    identity = 'rackhd-adapter'
    capabilities1 = 'rackhd-consul-register'
    capabilities2 = 'rackhd-list-nodes'
    capabilities3 = 'rackhd-upgrade-firmware-dellr730-server'
    capabilities4 = 'rackhd-upgrade-firmware-dell-idrac'
    capabilities5 = 'node-discovered-event'
    capabilities6 = 'rackhd-install-esxi'
    capabilities7 = 'rackhd-configure-raid-controller'
    capabilities8 = 'rackhd-list-node-catalogs'
    capabilities9 = 'rackhd-configure-idrac-network'
    capabilities10 = 'rackhd-configure-boot-device-idrac'
    capabilities11 = 'rackhd-set-node-obm-setting'
    capabilities12 = 'rackhd-configure-bmc-settings'
    capabilities13 = 'rackhd-set-idrac-credentials'
    capabilities14 = 'update-switch-firmware'

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

    assert not error_list, ('Missing some rackHD capabilities')

    print('All expected rackhd-adapter Capabilities Returned\n')

    cleanup('test.capability.registry.response')

@pytest.mark.network_services_mvp
def test_consul_verify_rackHD_registered():
    """
    Test Case Title :       Verify RackHD is registered with Consul
    Description     :       This method tests that vault is registered in the Consul API http://{SymphonyIP}:8500/v1/agent/services
                            It will fail if :
                                The line 'Service: "rackhd"' is not present
    Parameters      :       none
    Returns         :       None
    """

    service = 'rackhd'

    url_body = ':8500/v1/agent/services'
    my_url = 'http://' + ipaddress + url_body

    print('GET:', my_url)

    try:
        url_response = requests.get(my_url)
        url_response.raise_for_status()

        # A 200 has been received
        print(url_response)

        the_response = url_response.text

        # Create the sting as it should appear in the API
        serviceToCheck = '"Service": "' + service + '"'

        assert serviceToCheck in the_response, ('ERROR:', service, 'is not in Consul\n')

        print(service, 'Registered in Consul')

    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)

@pytest.mark.network_services_mvp
def test_consul_verify_rackHD_passing_status():
    """
    Test Case Title :       Verify RackHD is Passing in Consul
    Description     :       This method tests that RackHD-adapter has a passing status in the Consul API http://{SymphonyIP}:8500/v1/health/checks/vault
                            It will fail if :
                                The line '"Status": "passing"' is not present
    Parameters      :       none
    Returns         :       None
    """
    service = 'rackhd'

    url_body = ':8500/v1/health/checks/' + service
    my_url = 'http://' + ipaddress + url_body

    print('GET:', my_url)

    try:
        url_response = requests.get(my_url)
        url_response.raise_for_status()

        # A 200 has been received
        print(url_response)
        the_response = url_response.text

        serviceStatus = '"Status": "passing"'
        assert serviceStatus in the_response, ('ERROR:', service, 'is not Passing in Consul\n')
        print(service, 'Status = Passing in consul\n\n')

    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)

@pytest.mark.network_services_mvp
def test_rackHD_adapter_log_files_exist():
    """
    Title           :       Verify rackhd_adapter log files exist
    Description     :       This method tests that the RackHD Adapter log files exist.
                            It will fail:
                                If the the error and/or info log files do not exists
    Parameters      :       None
    Returns         :       None
    """

    service = 'rackhd-adapter-service'
    filePath = '/opt/dell/cpsd/rackhd-adapter-service/logs/'
    errorLogFile = 'rackhd-adapter-error.log'
    infoLogFile = 'rackhd-adapter-info.log'

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

@pytest.mark.network_services_mvp
def test_rackhd_adapter_log_files_free_of_exceptions():
    """
    Title           :       Verify there are no exceptions in the log files
    Description     :       This method tests that the rackhd_adapter log files contain no Exceptions.
                            It will fail:
                                If the the error and/or info log files do not exists
                                If the error log file contains AuthenticationFailureException, RuntimeException, NullPointerException or BeanCreationException.
    Parameters      :       None
    Returns         :       None
    """

    service = 'rackhd-adapter-service'
    filePath = '/opt/dell/cpsd/rackhd-adapter-service/logs/'
    errorLogFile = 'rackhd-adapter-error.log'
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


##############################################################################################
def bindQueues(exchange, queue):
    af_support_tools.rmq_bind_queue(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                    rmq_username=cpsd.props.rmq_username,
                                    rmq_password=cpsd.props.rmq_password,
                                    queue=queue,
                                    exchange=exchange,
                                    routing_key='#', ssl_enabled=cpsd.props.rmq_ssl_enabled)


def cleanup(queue):
    af_support_tools.rmq_delete_queue(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                      rmq_username=cpsd.props.rmq_username,
                                      rmq_password=cpsd.props.rmq_password,
                                      queue=queue, ssl_enabled=cpsd.props.rmq_ssl_enabled)


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

        q_len = af_support_tools.rmq_message_count(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                                   rmq_username=cpsd.props.rmq_username,
                                                   rmq_password=cpsd.props.rmq_password,
                                                   queue=queue, ssl_enabled=cpsd.props.rmq_ssl_enabled)

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
    url = 'http://%s:%s/api/exchanges/%s/%s/bindings/source' % (host, port, virtual_host, exchange)
    response = requests.get(url, auth=(user, password))
    queues = [q['destination'] for q in response.json()]
    return queues

    #######################################################################################################################
