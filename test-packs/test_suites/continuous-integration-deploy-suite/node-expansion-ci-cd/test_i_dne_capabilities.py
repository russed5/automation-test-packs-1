#!/usr/bin/python
# Author:
# Revision:
# Code Reviewed by:
# Description: Testing all Capability Register capabilities for DNE are present.
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


#####################################################################
# These are the main tests.
#####################################################################

@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_dne_node_discovery_service_capabilities():
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

    return_message = full_ListCapabilities()

    providerName = 'dell-cpsd-dne-node-discovery-service'
    capabilities1 = 'list-discovered-nodes'
    capabilities2 = 'manage-node-allocation'
    capabilities3 = 'start-node-allocation'
    capabilities4 = 'fail-node-allocation'

    error_list = []

    if (providerName not in return_message):
        error_list.append(providerName)
    if (capabilities1 not in return_message):
        error_list.append(capabilities1)
    if (capabilities2 not in return_message):
        error_list.append(capabilities2)
    if (capabilities3 not in return_message):
        error_list.append(capabilities3)
    if (capabilities4 not in return_message):
        error_list.append(capabilities4)

    assert not error_list, ('Missing the '+ providerName +' service or some capabilities')

    print('\nAll expected '+ providerName +' Capabilities Returned\n')


@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_dne_rackhd_adapter_capabilities():
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
    time.sleep(60)
    return_message = full_ListCapabilities()

    providerName = 'rackhd-adapter'
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
    capabilities11 = 'rackhd-configure-pxe-boot'
    capabilities12 = 'rackhd-set-node-obm-setting'
    capabilities13 = 'rackhd-configure-bmc-settings'
    capabilities14 = 'rackhd-set-idrac-credentials'
    capabilities15 = 'rackhd-node-inventory'

    error_list = []

    if (providerName not in return_message):
        error_list.append(providerName)
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

    assert not error_list, ('Missing the '+ providerName +' service or some capabilities')

    print('\nAll expected '+ providerName +' Capabilities Returned\n')


@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_dne_scaleio_adapter_capabilities():
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
    time.sleep(180)
    return_message = full_ListCapabilities()

    # Verify the scaleio Apapter Response
    providerName = 'scaleio-adapter'
    capabilities1 = 'scaleio-consul-register'
    capabilities2 = 'scaleio-discover'
    capabilities3 = 'scaleio-sds-remove'
    capabilities4 = 'scaleio-sdc-remove'
    capabilities5 = 'scaleio-list-components'
    capabilities6 = 'scaleio-add-host-to-protection-domain'
    capabilities7 = 'scaleio-update-sdc-performance-profile'
    capabilities8 = 'scaleio-map-volume-to-sdc'
    capabilities9 = 'scaleio-create-device-volume'
    capabilities10 = 'scaleio-create-storage-pool'
    capabilities11 = 'scaleio-create-protection-domain'
    capabilities12 = 'scaleio-create-fault-set'
    capabilities13 = 'scaleio-rename-sdc'

    error_list = []

    if (providerName not in return_message):
        error_list.append(providerName)
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


    assert not error_list, ('Missing some scaleio capabilities')

    print('All expected scaleio-adapter Capabilities Returned\n')

    assert not error_list, ('Missing the '+ providerName +' service or some capabilities')

    print('\nAll expected '+ providerName +' Capabilities Returned\n')


@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_dne_vcenter_adapter_capabilities():
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
    time.sleep(120)
    return_message = full_ListCapabilities()

    # Verify the vcenter Apapter Response
    providerName = 'vcenter-adapter'
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
    capabilities25 = 'vcenter-inventory'

    error_list = []

    if (providerName not in return_message):
        error_list.append(providerName)
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
    if (capabilities25 not in return_message):
        error_list.append(capabilities25)

    assert not error_list, ('Missing the '+ providerName +' service or some capabilities')

    print('\nAll expected '+ providerName +' Capabilities Returned\n')



#####################################################################

def full_ListCapabilities():
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
    originalcorrelationID = 'capability-registry-list-all-corID'
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
    assert waitForMsg('test.capability.registry.response'), 'Error: No List Capability Responce message received'
    return_message = af_support_tools.rmq_consume_message(host='amqp', port=5671,
                                                          queue='test.capability.registry.response',
                                                          ssl_enabled=True)
    time.sleep(5)

    cleanup('test.capability.registry.response')
    print (return_message)

    return (return_message)


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
