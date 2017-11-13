#!/usr/bin/python
# Author: cullia
# Revision: 2.1
# Refactor by : Toqeer Akhtar
# Code Reviewed by:
# Description: Verify all expected capabilities are returned for all providers and adapters when the user submits a
#               registry.list.capability Message
#
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information

import af_support_tools
import json
import pytest
import time


@pytest.fixture(scope="session", params=["capability-registry-service"])
def core_container(setup, request):
    ''' Fixture to get names of core service containers'''

    service = request.param
    print(service)
    sendcommand_core = "cat /opt/dell/cpsd/" + service + "/install/docker-compose.yml | grep container_name| cut -f 2 -d ':'"
    my_return_status_core = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                              password=setup['password'], command=sendcommand_core,
                                                              return_output=True)

    if not my_return_status_core:
        print("Unable to find " + service)
    servicename = my_return_status_core.strip()
    yield servicename




#####################################################################
# These are the main tests.
#####################################################################

@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_capabilityRegistry_servicerunning(setup, core_container):
    """
    Title           :       Verify the Capability Registry service is running
    Description     :       This method tests docker service for a container
                            It will fail if :
                                Docker service is not running for the container
    Parameters      :       none
    Returns         :       None
    """


    print(test_capabilityRegistry_servicerunning.__doc__)
    assert core_container, "container name not found"

    sendcommand = "docker ps --filter name=" + core_container + "  --format '{{.Status}}' | awk '{print $1}'"
    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                         password=setup['password'],
                                                         command=sendcommand, return_output=True)
    assert "Up" in my_return_status, " %s is not up" % core_container





@pytest.mark.parametrize('param_providerName, param_capabilities1', [
    ('rackhd-adapter', 'rackhd-consul-register',),
    ('vcenter-adapter', 'vcenter-consul-register'),
    ('endpoint-registry', 'endpoint-registry-lookup'),
    ('scaleio-adapter', 'scaleio-consul-register')])

# @pytest.mark.parametrize('param_providerName, param_capabilities1', [
#
#     ('vcenter-adapter', 'vcenter-consul-register')])
@pytest.mark.daily_status
@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_capabilityRegistry_ListCapabilities_core_1(param_providerName, param_capabilities1):
    """
    Title           :       Verify the registry.list.capability Message returns all capabilities for the provider under test
    Description     :       A registry.list.capability message is sent.  It is expected that a response is returned that
                            includes a list of all the  capabilities.
                            It will fail if :
                               No capability.registry.response is received.
                               The provider is not in the response.
                               The capabilities are not in the response.
    Parameters      :       none
    Returns         :       None
    """
    cleanup()
    bindQueues()

    print(
        "\nTest: Send in a list capabilities message and to verify all capabilities are present")

    return_message = publish_list_capability_msg()

    providerName = param_providerName
    capabilities1 = param_capabilities1

    error_list = []

    if (providerName not in return_message):
        error_list.append(providerName)
    if (capabilities1 not in return_message):
        error_list.append(capabilities1)

    assert not error_list, ('Missing the service or some capabilities')

    print('\nAll expected Capabilities Returned\n')

    cleanup()


@pytest.mark.parametrize('param_providerName, param_capabilities1, param_capabilities2', [
    ('poweredge-compute-data-provider', 'device-data-discovery', 'device-endpoint-validation'),
    ('vcenter-compute-data-provider', 'device-data-discovery', 'device-endpoint-validation')])
@pytest.mark.daily_status
@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_capabilityRegistry_ListCapabilities_core_2(param_providerName, param_capabilities1, param_capabilities2, setup):
    """
    Title           :       Verify the registry.list.capability Message returns all capabilities for the provider under test
    Description     :       A registry.list.capability message is sent.  It is expected that a response is returned that
                            includes a list of all the  capabilities.
                            It will fail if :
                               No capability.registry.response is received.
                               The provider is not in the response.
                               The capabilities are not in the response.
    Parameters      :       none
    Returns         :       None
    """
    cleanup()
    bindQueues()

    print(
        "\nTest: Send in a list capabilities message and to verify all capabilities are present")

    return_message = publish_list_capability_msg()

    providerName = param_providerName
    capabilities1 = param_capabilities1
    capabilities2 = param_capabilities2

    error_list = []

    if (providerName not in return_message):
        error_list.append(providerName)
    if (capabilities1 not in return_message):
        error_list.append(capabilities1)
    if (capabilities2 not in return_message):
        error_list.append(capabilities2)

    assert not error_list, ('Missing the service or some capabilities')

    print('\nAll expected Capabilities Returned\n')

    cleanup()


@pytest.mark.parametrize('param_providerName, param_capabilities1, param_capabilities2', [
    ('node-discovery-paqx', 'list-discovered-nodes', 'manage-node-allocation')])
@pytest.mark.daily_status
@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_capabilityRegistry_ListCapabilities_dne_2(param_providerName, param_capabilities1, param_capabilities2):
    """
    Title           :       Verify the registry.list.capability Message returns all capabilities for the provider under test
    Description     :       A registry.list.capability message is sent.  It is expected that a response is returned that
                            includes a list of all the  capabilities.
                            It will fail if :
                               No capability.registry.response is received.
                               The provider is not in the response.
                               The capabilities are not in the response.
    Parameters      :       none
    Returns         :       None
    """
    cleanup()
    bindQueues()

    print(
        "\nTest: Send in a list capabilities message and to verify all capabilities are present")

    return_message = publish_list_capability_msg()

    providerName = param_providerName
    capabilities1 = param_capabilities1
    capabilities2 = param_capabilities2

    error_list = []

    if (providerName not in return_message):
        error_list.append(providerName)
    if (capabilities1 not in return_message):
        error_list.append(capabilities1)
    if (capabilities2 not in return_message):
        error_list.append(capabilities2)

    assert not error_list, ('Missing the service or some capabilities')

    print('\nAll expected Capabilities Returned\n')

    cleanup()



@pytest.mark.skip(reason="ESTS-136102")
@pytest.mark.daily_status
@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_capabilityRegistry_log_files_exist(setup):
    """
    Title           :       Verify Capability Registry log files exist
    Description     :       This method tests that the Capability Registry log files exist.
                            It will fail:
                                If the the error and/or info log files do not exists
                                If the error log file contains AuthenticationFailureException, RuntimeException or NullPointerException.
    Parameters      :       None
    Returns         :       None
    """

    filePath = '/opt/dell/cpsd/capability-registry-service/logs/'
    errorLogFile = 'capability-registry-error.log'
    infoLogFile = 'capability-registry-info.log'

    # Verify the log files exist
    sendCommand = 'ls ' + filePath
    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                         password=setup['password'],
                                                         command=sendCommand, return_output=True)

    error_list = []

    if (errorLogFile not in my_return_status):
        error_list.append(errorLogFile)

    if (infoLogFile not in my_return_status):
        error_list.append(infoLogFile)

    assert not error_list, 'Log file missing'

    print('Valid log files exist')


@pytest.mark.skip(reason="ESTS-136102")
@pytest.mark.daily_status
@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_capabilityRegistry_log_files_free_of_exceptions(setup):
    """
    Title           :       Verify there are no exceptions in the log files
    Description     :       This method tests that the Capability Registry log files contain no Exceptions.
                            It will fail:
                                If the the error and/or info log files do not exists
                                If the error log file contains AuthenticationFailureException, RuntimeException or NullPointerException.
    Parameters      :       None
    Returns         :       None
    """

    filePath = '/opt/dell/cpsd/capability-registry-service/logs/'
    errorLogFile = 'capability-registry-error.log'
    excep1 = 'AuthenticationFailureException'
    excep2 = 'RuntimeException'
    excep3 = 'NullPointerException'

    error_list = []

    # Verify there are no Authentication errors
    sendCommand = 'cat ' + filePath + errorLogFile + ' | grep \'' + excep1 + '\''
    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                         password=setup['password'],
                                                         command=sendCommand, return_output=True)
    if (excep1 in my_return_status):
        error_list.append(excep1)

    # Verify there are no RuntimeException errors
    sendCommand = 'cat ' + filePath + errorLogFile + ' | grep \'' + excep2 + '\''
    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                         password=setup['password'],
                                                         command=sendCommand, return_output=True)
    if (excep2 in my_return_status):
        error_list.append(excep2)

    # Verify there are no NullPointerException errors
    sendCommand = 'cat ' + filePath + errorLogFile + ' | grep \'' + excep3 + '\''
    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                         password=setup['password'],
                                                         command=sendCommand, return_output=True)
    if (excep3 in my_return_status):
        error_list.append(excep3)

    assert not error_list, 'Exceptions in log files, Review the ' + errorLogFile + ' file'

    print('No Authentication, RuntimeException or NullPointerException in log files\n')


#######################################################################################################################
# These are common functions that are used throughout the main test.

def bindQueues():
    af_support_tools.rmq_bind_queue(host= 'amqp', port=5671,
                                    queue='test.capability.registry.response',
                                    exchange='exchange.dell.cpsd.hdp.capability.registry.response',
                                    routing_key='#', ssl_enabled=True)


def cleanup():
    af_support_tools.rmq_delete_queue(host= 'amqp', port=5671,                                     
                                      queue='test.capability.registry.response',
                                      ssl_enabled=True)


def waitForMsg(queue):
    # This function keeps looping untill a message is in the specified queue. We do need it to timeout and throw an error
    # if a message never arrives. Once a message appears in the queue the function is complete and main continues.

    # The length of the queue, it will start at 0 but as soon as we get a response it will increase
    q_len = 0

    # Represents the number of seconds that have gone by since the method started
    timeout = 0

    # Max number of seconds to wait
    max_timeout = 100

    # Amount of time in seconds that the loop is going to wait on each iteration
    sleeptime = 1

    while q_len < 1:
        time.sleep(sleeptime)
        timeout += sleeptime

        q_len = af_support_tools.rmq_message_count(host='amqp', port=5671,                                                  
                                                   queue=queue, ssl_enabled=True)

        if timeout > max_timeout:
            print('ERROR: Message took too long to return. Something is wrong')
            cleanup()
            break


def checkForErrors(return_message):
    checklist = 'errors'
    if checklist in return_message:
        print('\nBUG: Error in Response Message\n')
        assert False  # This assert is to fail the test


def checkForFailures(return_message):
    checklist = 'failureReasons'
    if checklist in return_message:
        return_json = json.loads(return_message, encoding='utf-8')
        errorMsg = return_json['failureReasons'][0]['message']
        print('The following error has been returned :', errorMsg)
        print('Possible component validation issue')
        assert False  # This assert is to fail the test


def publish_list_capability_msg():
    """
    Description     :       Publish a msg to RMQ that requests a list of all the current capabilities registered.
    Parameters      :       none
    Returns         :       The response message.
    """
    originalcorrelationID = 'capability-registry-list-test'
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
    waitForMsg('test.capability.registry.response')
    return_message = af_support_tools.rmq_consume_message(host='amqp', port=5671,                                                          
                                                          queue='test.capability.registry.response',
                                                          ssl_enabled=True)

    checkForErrors(return_message)
    checkForFailures(return_message)

    return (return_message)

#######################################################################################################################
