#!/usr/bin/python
# Author: cullia
# Copyright © 2017 Dell Inc. or its subsidiaries.  All Rights Reserved
# Revision: 2.0
# Code Reviewed by:
# Description: Configure a system and run the collectComponentVersions Message

import af_support_tools
import json
import os
#import paramiko
import pytest
import time
from conftest import JsonMessage

@pytest.fixture(scope="module")
def test_SystemAdditionRequested(rabbitMq):
    print('Sending RMQ System-Definition Message to configure system...')

    rabbitMq.bind_queue_with_key(queue='test.system.list.request',
                                 exchange='exchange.dell.cpsd.syds.system.definition.request',
                                 routing_key='#')

# Get the payload data from the config symphony-sds.ini file.
    the_payload = af_support_tools.get_config_file_property(config_file=payload_file,
                                                            heading='payload',
                                                            property=payload_property_sys)

    headers={'__TypeId__': 'com.dell.cpsd.syds.converged.system.addition.requested'}
    message=JsonMessage(headers=headers, payload=the_payload)
    rabbitMq.publish_message(exchange='exchange.dell.cpsd.syds.system.definition.request',
                             routing_key='dell.cpsd.syds.converged.system.addition.requested',
                             message=message)

    time.sleep(1)

@pytest.fixture(scope="module")
def getSystemDefinitionListMessage(rabbitMq):
    rabbitMq.bind_queue_with_key(queue='test.system.list.found',
                                 exchange='exchange.dell.cpsd.syds.system.definition.response',
                                 routing_key='#')

    the_payload = af_support_tools.get_config_file_property(config_file=payload_file,
                                                            heading='payload',
                                                            property=payload_property_req)

@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    # Update config ini files at runtime
    print("load test")
    my_data_file = os.environ.get('AF_RESOURCES_PATH') + '/continuous-integration-deploy-suite/symphony-sds.properties'
    af_support_tools.set_config_file_property_by_data_file(my_data_file)

    # Set config ini file name
    global env_file
    env_file = 'env.ini'

    # Set Vars
    global payload_file
    payload_file = 'continuous-integration-deploy-suite/symphony-sds.ini'
    global payload_header
    payload_header = {'__TypeId__': 'com.dell.cpsd.hal.orchestrator.service.collect.component.versions'}
    global payload_property_sys
    payload_property_sys = 'sys_payload'
    global payload_property_req
    payload_property_req = 'sys_request_payload'
    global payload_property_req_config
    payload_property_req_config = 'sys_request_payload_with_config'
    global payload_property_hal
    payload_property_hal = 'ccv_payload'


#######################################################################################################################
@pytest.mark.core_services_mvp
@pytest.mark.rcm_fitness_mvp
@pytest.mark.core_services_mvp_extended
@pytest.mark.rcm_fitness_cd_mvp_extended
@pytest.mark.usefixtures("load_test_data", "test_SystemAdditionRequested", "getSystemDefinitionListMessage")
def test_HAL_CollectComponentVersion(rabbitMq):
    #af_support_tools.mark_defect(defect_id='', user_id='', comments='', date_marked='')
    print("test start")
    bindHALQueus(rabbitMq)

    print('\n*******************************************************')
    print('Step 5: Sending RMQ HAL CollectComponentVersions Message')
    # Get the collectComponentVersions payload data from the config symphony-sds.ini file.
    the_payload = af_support_tools.get_config_file_property(config_file=payload_file, heading='payload',
                                                            property=payload_property_hal)

    print("the payload is ",payload_header)
    message=JsonMessage(headers=payload_header, payload=the_payload)

    time.sleep(1)
    # Publish the HAL message to collectcomponentversions
    rabbitMq.publish_message(exchange='exchange.dell.cpsd.hal.orchestrator.request',
                             routing_key='dell.cpsd.hal.orchestrator.collect.component.versions',
                             message=message)



    #waitForMsg('test.hal.orchestrator.request')
    return_json=rabbitMq.consume_message_from_queue('test.hal.orchestrator.request')
    #return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
    #                                                      rmq_password=rmq_password,
    #                                                      queue='test.hal.orchestrator.request')

    print("jk consumed message is ",return_json)
    published_json = json.loads(the_payload, encoding='utf-8')
    ##-return_json = json.loads(return_message, encoding='utf-8')

    # Checking the "Message received" matches the "Message published"
    assert published_json == return_json
    print('\nTEST: Published Message Received: PASSED\n')

    ####################################################################################################################
    #
    # Verifying all Messages in the sequence are triggered correctly.
    #
    # 1. Verify that a System is returned
    ##-waitForMsg('test.system.definition.response')

    ##-return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
    ##-                                                      rmq_password=rmq_password,
    ##-                                                      queue='test.system.definition.response')
    ##-checklist = '"uuid":[]'
    ##-if checklist in return_message:
    ##-    print('\nBUG: No System is returned in system.list.found Message\n')
    ##-    assert False

    ##-return_json = json.loads(return_message, encoding='utf-8')
    ##-assert return_json['convergedSystems'][0]['uuid']
    ##-print('Step 5a: A System has been returned')

    # 2. Verify that a List of components for that system is returned
    ##-waitForMsg('test.system.definition.response')
    ##-return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
    ##-                                                      rmq_password=rmq_password,
    ##-                                                      queue='test.system.definition.response')
    ##-checklist = '"components":[]'
    ##-if checklist in return_message:
    ##-    print('\nBUG: No Components are returned in component.configuration.found Message\n')
    ##-assert False

    ##-return_json = json.loads(return_message, encoding='utf-8')
    ##-assert return_json['convergedSystems'][0]['components'][0]
    ##-assert return_json['convergedSystems'][0]['endpoints'][0]
    ##-print('Step 5b: The components for the System have been returned')

    # 3. Verify that a Component Credentials are returned
    ##-waitForMsg('test.cms.credentials.response')
    ##-return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
    ##-                                                      rmq_password=rmq_password,
    ##-                                                      queue='test.cms.credentials.response')
    ##-checklist = 'errors'
    ##-if checklist in return_message:
    ##-    print('\nBUG: Error in cms.credentials.response Message\n')
    ##-    assert False

    ##-return_json = json.loads(return_message, encoding='utf-8')
    ##-assert return_json['credentials'][0]['credentialElement']
    ##-print('Step 5c: The credentials for the components belonging to the System have been returned')

    ##-print('\nPlease wait. This next process can take a few minutes...\n')

    ####################################################################################################################
    #
    # We need to wait until the queue gets the response message and timeout if it never arrives
    ##-q_len = 0
    ##-timeout = 0

    ##-while q_len < 1:
    ##-time.sleep(1)
    ##-timeout += 1

    ##-q_len = af_support_tools.rmq_message_count(host=ipaddress,
    ##-                                           port=port,
    ##-                                           rmq_username=rmq_username,
    ##-                                           rmq_password=rmq_password,
    ##-                                           queue='test.hal.orchestrator.response')

    # If the test queue doesn't get a message them something is wrong. Time out needs to be high as msg can take 3+ minutes
    ##-if timeout > 500:
    ##-print('ERROR: HAL Response Message took to long to return. Something is wrong')
    ##-cleanup()
    ##-assert False

    # We are deliberately not removing the message from the queue as it will be consumed in a later test. ref: Joe
    ##-return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
    ##-                                                      rmq_password=rmq_password,
    ##-                                                      queue='test.hal.orchestrator.response',
    ##-                                                      remove_message=False)

    ##-return_json = json.loads(return_message, encoding='utf-8')

    # Only if the message sequence successfully ran will the returned json message have the following attributes.
    ##-assert return_json['messageProperties']['timestamp']
    ##-assert return_json['messageProperties']['correlationId']
    ##-assert return_json['messageProperties']['replyTo']
    ##-assert return_json['systems'][0]['uuid']
    ##-assert return_json['groups']

    ##-devices =  return_json['devices']
    #print(devices)
    ##-if devices == None:
    ##-    print("No devices returned")
    ##-    assert return_json['devices']
    ##-assert return_json['subComponents']

    ##-assert return_json['groups'][0]['parentSystemUuids']
    ##-assert return_json['devices'][0]['uuid']

    ##-print("Step 5d: HAL has returned a valid response\n")

    ##-verifyHalContent()

    # 4, Verify the EIDS message
    ##-verifyHALEidsMessage()

    ##-print('TEST: HAL CollectComponentVersions Completed: PASSED')
    ##-print('\n*******************************************************')

    cleanup(rabbitMq)


#######################################################################################################################

def checkRMQStatus():
    sendCommand = 'systemctl status rabbitmq-server'
    my_return_text = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                       command=sendCommand, return_output=True)

    running = 'Active: active (running)'
    assert running in my_return_text
    print('Rabbit Status:', running)


def cleanup(rabbitMq):
    # Delete the test queues
    print('Cleaning up...')
    #rabbitMq.delete_queue(
    #                                      queue='test.system.list.request')
    #rabbitMq.delete_queue(
    #                                      queue='test.system.list.found')
    rabbitMq.delete_queue(
        queue='test.hal.orchestrator.request')

    # Commented out as Joe's Script needs to consume it too.
    # af_support_tools.rmq_delete_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
    #                                   queue='test.hal.orchestrator.response')


    #queue='test.component.credential.request')

    #queue='test.system.definition.response')

    #queue='test.cms.credentials.response')

    #queue='test.eids.identity.request')

    #queue='test.eids.identity.response')



def bindHALQueus(rabbitMq):
    print('Creating HAL Queues')
    rabbitMq.bind_queue_with_key(
        queue='test.hal.orchestrator.request',
        exchange='exchange.dell.cpsd.hal.orchestrator.request',
        routing_key='#')

    #   queue='test.hal.orchestrator.response',
    #   exchange='exchange.dell.cpsd.hal.orchestrator.response',

    #  queue='test.system.definition.response',
    # exchange='exchange.dell.cpsd.syds.system.definition.response',

    #queue='test.cms.credentials.response',
    #exchange='exchange.dell.cpsd.cms.credentials.response',
    #routing_key='#')

    #queue='test.eids.identity.request',
    #exchange='exchange.dell.cpsd.eids.identity.request',

    #queue='test.eids.identity.response',
    #exchange='exchange.dell.cpsd.eids.identity.response',

    print('finished creating HAL Queues')
    time.sleep(2)


def verifyCSmessage():
    # We need to verify that the triggered component.credentials.addition.requested is valid.
    time.sleep(1)
    print('\n*******************************************************')
    print('Step 2. Verifying the trigged component.credentials.addition.requested is valid...')

    # We need to wait until the queue gets the response message
    waitForMsg('test.component.credential.request')

    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.component.credential.request')

    return_json = json.loads(return_message, encoding='utf-8')

    # These 3 values must be returned.
    if 'credentialUuid' not in return_message:
        print('\nTEST FAIL: Invalid "credentials.addition.requested" message structure. credentialUuid missing')
        assert False

    if 'endpointUuid' not in return_message:
        print('\nTEST FAIL: Invalid "credentials.addition.requested" message structure. endpointUuid missing')
        assert False

    if 'componentUuid' not in return_message:
        print('\nTEST FAIL: Invalid "credentials.addition.requested" message structure. componentUuid missing')
        assert False

    assert return_json['messageProperties']['correlationId']
    assert return_json['messageProperties']['replyTo']
    assert return_json['messageProperties']['timestamp']
    assert return_json['endpoints'][0]['credentials'][0]['credentialUuid']
    assert return_json['endpoints'][0]['endpointUuid']
    assert return_json['componentUuid']
    print('\nTEST: credentials.addition.requested is valid: PASSED')
    time.sleep(1)


def verifySDSEidsMessage():
    # We need to verify that the triggered eids.identity.request is valid.
    time.sleep(1)
    print('\n*******************************************************')
    print('Step 3. Verifying the trigged eids.identity.request & response are valid...')

    # Check the EIDS request message
    # We need to wait until the queue gets the request message
    waitForMsg('test.eids.identity.request')

    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.eids.identity.request')

    return_json = json.loads(return_message, encoding='utf-8')

    # Check how many Uuids are requested by EIDS this should match how many were originally configured at the start
    elementIdentities = 0
    for x in return_json['elementIdentities']:
        elementIdentities += 1

    originalNum = getNumItems()

    assert originalNum == elementIdentities
    print(elementIdentities, ' UUIDs requested. ', originalNum, ' Originally configured.')

    # These are commented out until RMQ refactoring happens
    # assert return_json['messageProperties']['correlationId']
    # assert return_json['messageProperties']['replyTo']
    # assert return_json['messageProperties']['timestamp']
    assert return_json['elementIdentities'][0]['correlationUuid']
    assert return_json['elementIdentities'][0]['identity']['elementType']
    assert return_json['elementIdentities'][0]['identity']['contextualKeyAccuracy']

    # Check the EIDS ressponse message
    # We need to wait until the queue gets the response message
    waitForMsg('test.eids.identity.response')

    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.eids.identity.response')

    return_json = json.loads(return_message, encoding='utf-8')

    # Check how many Uuids are returned by EIDS this should match what were originally configured
    elementIdentifications = 0
    for x in return_json['elementIdentifications']:
        elementIdentifications += 1

    originalNum = getNumItems()

    assert originalNum == elementIdentifications
    print(elementIdentifications, ' UUIDs created. ', originalNum, ' Originally configured.')

    # These are commented out until RMQ refactoring happens
    # assert return_json['messageProperties']['correlationId']
    # assert return_json['messageProperties']['replyTo']
    # assert return_json['messageProperties']['timestamp']
    assert return_json['elementIdentifications'][0]['correlationUuid']
    assert return_json['elementIdentifications'][0]['elementUuid']

    print('\nTEST: trigged eids.identity.request & response: PASSED')
    time.sleep(1)


def verifySystemExists():
    # Check that the system exists
    print('\n*******************************************************')
    print('Step 4. Verifying System has been configured...')

    # Get the payload data from the config symphony-sds.ini file.
    the_payload = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                            property=payload_property_req)

    time.sleep(1)
    af_support_tools.rmq_publish_message(host=ipaddress,
                                         port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                         exchange='exchange.dell.cpsd.syds.system.definition.request',
                                         routing_key='dell.cpsd.syds.converged.system.list.requested',
                                         headers={'__TypeId__': 'com.dell.cpsd.syds.converged.system.list.requested'},
                                         payload=the_payload,
                                         payload_type='json')

    waitForMsg('test.system.list.request')
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.system.list.request')

    published_json = json.loads(the_payload, encoding='utf-8')
    return_json = json.loads(return_message, encoding='utf-8')

    # Checking the "Message received" matches the "Message published"
    assert published_json == return_json
    print('\nTEST: Published Message Received: PASSED')

    # We need to wait until the queue gets the response message
    waitForMsg('test.system.list.found')
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port,
                                                          rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.system.list.found')

    return_json = json.loads(return_message, encoding='utf-8')

    # Here we verify that a system is returned. Cannot be overly specific checking parameters as values will vary.
    assert return_json['messageProperties']['correlationId']
    assert return_json['messageProperties']['replyTo']
    assert return_json['messageProperties']['timestamp']
    assert return_json['convergedSystems']
    assert return_json['convergedSystems'][0]['uuid']
    assert not return_json['convergedSystems'][0]['groups']
    assert not return_json['convergedSystems'][0]['endpoints']
    assert not return_json['convergedSystems'][0]['subSystems']
    assert not return_json['convergedSystems'][0]['components']

    my_systemUuid = return_json['convergedSystems'][0]['uuid']
    print('\nTEST: System Exists - System UUID: ', my_systemUuid, ': PASSED\n')

    time.sleep(1)


def getNumItems():
    orignumSystems = 0
    orignumGroups = 0
    orignumSubSystems = 0
    orignumComponents = 0

    # Get the payload data from the config symphony-sds.ini file.
    originalSys = af_support_tools.get_config_file_property(config_file=payload_file,
                                                            heading=payload_header,
                                                            property=payload_property_sys)

    originalSys_json = json.loads(originalSys, encoding='utf-8')

    orignumSystems += 1

    for x in originalSys_json['convergedSystem']['groups']:
        orignumGroups += 1

    for x in originalSys_json['convergedSystem']['subSystems']:
        orignumSubSystems += 1

    for x in originalSys_json['convergedSystem']['components']:
        orignumComponents += 1

    totalNum = orignumSystems + orignumGroups + orignumSubSystems + orignumComponents
    return totalNum


def verifyUniqueUuids():
    print('*******************************************************')
    print('Step 5. Verifying all UUIDs are Unique...')

    # Get the payload data from the config symphony-sds.ini file.
    the_payload = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                            property=payload_property_req_config)

    time.sleep(1)
    af_support_tools.rmq_publish_message(host=ipaddress,
                                         port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                         exchange='exchange.dell.cpsd.syds.system.definition.request',
                                         routing_key='dell.cpsd.syds.converged.system.list.requested',
                                         headers={'__TypeId__': 'com.dell.cpsd.syds.converged.system.list.requested'},
                                         payload=the_payload,
                                         payload_type='json')

    waitForMsg('test.system.list.request')
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.system.list.request')

    published_json = json.loads(the_payload, encoding='utf-8')
    return_json = json.loads(return_message, encoding='utf-8')

    # Checking the "Message received" matches the "Message published"
    assert published_json == return_json
    print('\nTEST: Published Message Received: PASSED')

    # We need to wait until the queue gets the response message
    waitForMsg('test.system.list.found')
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port,
                                                          rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.system.list.found')

    return_json = json.loads(return_message, encoding='utf-8')

    found_list = return_json['convergedSystems']
    uuid_found_list = []

    for node in found_list:
        element_data = node['groups']
        for element in element_data:
            uuid = element.get('uuid')
            uuid_found_list.append(uuid)

    for node in found_list:
        element_data = node['endpoints']
        for element in element_data:
            uuid = element.get('uuid')
            uuid_found_list.append(uuid)

    for node in found_list:
        element_data = node['subSystems']
        for element in element_data:
            uuid = element.get('uuid')
            uuid_found_list.append(uuid)

    for node in found_list:
        element_data = node['components']
        for element in element_data:
            uuid = element.get('uuid')
            uuid_found_list.append(uuid)

    # Call the function to check for duplicates in the list
    dups_found = af_support_tools.check_for_dups_in_list(uuid_found_list)
    unique_ids = False

    # If the function says there were no duplicates in the list then we can change the unique_ids flag to True
    if dups_found == False:
        unique_ids = True

    if unique_ids == True:
        print('\nTest: Verify all UUID values are unique: PASSED')
    assert unique_ids


def waitForMsg(queue):
    q_len = 0
    timeout = 0

    while q_len < 1:
        time.sleep(1)
        timeout += 1

        q_len = af_support_tools.rmq_message_count(host=ipaddress,
                                                   port=port,
                                                   rmq_username=rmq_username,
                                                   rmq_password=rmq_password,
                                                   queue=queue)

        if timeout > 50:
            print('ERROR: Message took to long to return. Something is wrong')
            checkForErrorMsg()


def checkForErrorMsg():
    print('Checking for error messages...')
    msg_count = af_support_tools.rmq_message_count(host=ipaddress,
                                                   port=port,
                                                   rmq_username=rmq_username,
                                                   rmq_password=rmq_password,
                                                   queue='test.system.list.found')

    if msg_count == 1:
        return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                              rmq_password=rmq_password,
                                                              queue='test.system.list.found')

        return_json = json.loads(return_message, encoding='utf-8')

        error_msg = return_json['errors'][0]['message']
        print('\nRMQ Error Message:: ', error_msg)
        assert False

    msg_count = af_support_tools.rmq_message_count(host=ipaddress,
                                                   port=port,
                                                   rmq_username=rmq_username,
                                                   rmq_password=rmq_password,
                                                   queue='test.system.definition.response')

    if msg_count == 1:
        return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                              rmq_password=rmq_password,
                                                              queue='test.system.definition.response')

        return_json = json.loads(return_message, encoding='utf-8')

        error_msg = return_json['errors'][0]['message']
        print('\nRMQ Error Message:: ', error_msg)
        assert False


    else:
        print('No specific error looked for.')
        assert False


def verifyHalContent():

    print('Verifying content of the HAL response message...')
    # Get the payload data from the config symphony-sds.ini file.
    originalSys = af_support_tools.get_config_file_property(config_file=payload_file,
                                                            heading=payload_header,
                                                            property=payload_property_sys)

    originalSys_json = json.loads(originalSys, encoding='utf-8')

    orignumComponents = 0
    for x in originalSys_json['convergedSystem']['components']:
        orignumComponents += 1

    # We are deliberately not removing the message from the queue as it will be consumed in a later test. ref: Joe
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.hal.orchestrator.response',
                                                          remove_message=False)

    return_json = json.loads(return_message, encoding='utf-8')

    returnnumDevices = 0
    for x in return_json['devices']:
        returnnumDevices += 1

    print('Original: ',orignumComponents, ' Returned: ', returnnumDevices)

    if orignumComponents != returnnumDevices:
        print('ERROR: Not all components have returned values. Possible h/w or credential issue.')
        assert orignumComponents == returnnumDevices

    print('Step 5e: All devices have been returned\n')


def verifyHALEidsMessage():
    # We need to verify that the triggered eids.identity.request is valid.
    # Check the EIDS request messages
    print('Verifying EIDS returns UIDS for all discovered subcomponents')
    waitForMsg('test.eids.identity.request')
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.eids.identity.request')

    return_json = json.loads(return_message, encoding='utf-8')

    assert return_json['correlationId']
    # assert return_json['replyTo']
    assert return_json['timestamp']
    assert return_json['elementUuids'][0]

    # Test the 2nd message
    waitForMsg('test.eids.identity.request')
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.eids.identity.request')

    return_json = json.loads(return_message, encoding='utf-8')

    assert return_json['correlationId']
    # assert return_json['replyTo']
    assert return_json['timestamp']
    assert return_json['elementIdentities'][0]['correlationUuid']
    assert return_json['elementIdentities'][0]['identity']['elementType']
    assert return_json['elementIdentities'][0]['identity']['contextualKeyAccuracy']

    # Check the EIDS response message
    waitForMsg('test.eids.identity.response')
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.eids.identity.response')

    return_json = json.loads(return_message, encoding='utf-8')

    assert return_json['correlationId']
    # assert return_json['replyTo']
    assert return_json['timestamp']
    assert return_json['elementDescriptions'][0]['elementUuid']

    # Test the 2nd message
    waitForMsg('test.eids.identity.response')
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.eids.identity.response')

    return_json = json.loads(return_message, encoding='utf-8')

    assert return_json['correlationId']
    # assert return_json['replyTo']
    assert return_json['timestamp']
    assert return_json['elementIdentifications'][0]['correlationUuid']
    assert return_json['elementIdentifications'][0]['elementUuid']

    print('Step 5f: EIDS requests & receives messages for all discovered subcomponents \n')
    time.sleep(1)

#######################################################################################################################
