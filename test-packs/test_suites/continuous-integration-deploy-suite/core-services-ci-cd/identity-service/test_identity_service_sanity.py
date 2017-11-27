#!/usr/bin/python
# Author:cullia
# Copyright © 2017 Dell Inc. or its subsidiaries.  All Rights Reserved
# Updated by: olearj10
# Date: 6 April 2017
# Revision:2.6
# Refactor by : Toqeer Akhtar
# Date : 27/11/2017
# Description: Standalone testing of the Identity Service. No other services are used. No system needs to be defined
# to run this test.

import af_support_tools
import pytest
import json
import random
import time




@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    # Set config ini file name
    global config_file
    config_file = 'continuous-integration-deploy-suite/identity_service.ini'

    global identifyelement
    identifyelement = af_support_tools.get_config_file_property(config_file=config_file,
                                                                heading='identity_service_payloads',
                                                                property='identifyelement')


##############################################################################################

@pytest.mark.daily_status
@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_ident_status(setup):
    print('\nRunning Identity Status test on system: ', setup['IP'])
    status_command = 'docker ps | grep identity-service'
    status = af_support_tools.send_ssh_command(host = setup['IP'], username= setup['user'], password=setup['password'],
                                               command=status_command, return_output=True)
    assert "Up" in status, "Identity Service not Running"
    print("Identity Service Running")


@pytest.mark.daily_status
@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_identify_element():


    cleanup()
    bind_queues()
    identified_errors = []
    global elementUuid

    print('Sending Identify Element Message\n')


    af_support_tools.rmq_publish_message(host = 'amqp', port = 5671, ssl_enabled=True,
                                         exchange='exchange.dell.cpsd.eids.identity.request',
                                         routing_key='dell.cpsd.eids.identity.request',
                                         headers={'__TypeId__': 'dell.cpsd.core.identity.identify.element'},
                                         payload=identifyelement, payload_type='json')

    return_message = af_support_tools.rmq_consume_message(host='amqp', port=5671, ssl_enabled=True, queue='test.identity.request')
    



    published_json = json.loads(identifyelement, encoding='utf-8')

    return_json = json.loads(return_message, encoding='utf-8')

    # Compare the 2 files. If they match the message was successfully published & received to rabbitMQ test queue.
    print("Verifying Message sent to RabbitMQ...")
    assert published_json == return_json, "Message Not Published to RabbitMQ"
    print('Published Message Received.')


    print('\nConsuming Response Message...')
    # At this stage we have verified that a message was published & received.
    # Next we need to check that we got the expected Response to our request.
    assert waitForMsg('test.identity.response'), "Message took too long to return"
    return_message = af_support_tools.rmq_consume_message(host='amqp', queue='test.identity.response')

    return_json = json.loads(return_message)

    # Verify the response message has the expected format & parameters
    print("Checking Response Message attributes...")
    if not return_json['timestamp']:
        identified_errors.append("No timestamp in message")
    if return_json['correlationId'] not in identifyelement:
        identified_errors.append("correlationId error")

    # Get number of element identifications in response
    total_ele_idents = len(return_json['elementIdentifications'])
    for _ in range(total_ele_idents):
        if return_json['elementIdentifications'][_]['correlationUuid'] not in identifyelement:
            identified_errors.append("correlationUuid error")
        assert return_json['elementIdentifications'][_]['elementUuid']

    # Collect random element uuid for describe, from the total number of identified elements
    # We Subtract one from total_ele_idents to give use a random number from 0 to n
    total_ele_idents -= 1
    elementUuid = return_json['elementIdentifications'][random.randint(0, total_ele_idents)]['elementUuid']

    assert not identified_errors

    print('TEST: All requested CorrelationUuid have had elementUuid values returned: PASSED')
    print('\n*******************************************************')


@pytest.mark.daily_status
@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_describe_element():
    cleanup()
    bind_queues()
    describe_errors = []

    # Define Describe message using elementUuid from previous test
    describeelement = '{"timestamp":"2017-01-27T14:51:00.570Z","correlationId":"5d7f6d34-4271-4593-9bad-1b95589e5189","reply-to":"dell.cpsd.eids.identity.request.hal.gouldc-mint","elementUuids":["' + elementUuid + '"]}'

    print("Sending Describe Element for elementUUID: {}...".format(elementUuid))

    af_support_tools.rmq_publish_message(host='amqp', port=5671, ssl_enabled= True,
                                         exchange='exchange.dell.cpsd.eids.identity.request',
                                         routing_key='dell.cpsd.eids.identity.request',
                                         headers={'__TypeId__': 'dell.cpsd.core.identity.describe.element'},
                                         payload=describeelement, payload_type='json')


    return_message = af_support_tools.rmq_consume_message(host='amqp', port=5671, ssl_enabled=True ,
                                                          queue='test.identity.request')

    return_json = json.loads(return_message, encoding='utf-8')

    published_json = json.loads(describeelement, encoding='utf-8')

    # Compare the 2 files. If they match the message was successfully published & received.
    print("Verifying Message sent to RabbitMQ...")
    assert published_json == return_json
    print('Published Message Received.')

    print('\nConsuming Response Message...')
    # At this stage we have verified that a message was published & received.
    # Next we need to check that we got the expected Response to our request.
    assert waitForMsg('test.identity.response'), "Message took too long to return"

    return_message = af_support_tools.rmq_consume_message(host = 'amqp', port=5671, ssl_enabled= True,
                                                          queue='test.identity.response')
    return_json = json.loads(return_message, encoding='utf-8')

    # Verify the response message has the expected format & parameters
    print("Checking Response Message attributes...")
    if not return_json['timestamp']:
        describe_errors.append("No timestamp in message")
    if return_json['correlationId'] not in describeelement:
        describe_errors.append("correlationId error")

    classification = return_json['elementDescriptions'][0]['classification']
    elementType = return_json['elementDescriptions'][0]['elementType']

    # Check values from elementdescribed response against IdentifyElements message, except for 'ELEMENT_UUID'
    for _ in range(len(return_json['elementDescriptions'][0]['businessKeys'])):
        if return_json['elementDescriptions'][0]['businessKeys'][_]['key'] != 'ELEMENT_UUID':
            value = return_json['elementDescriptions'][0]['businessKeys'][_]['value']
            if classification and elementType and value not in identifyelement:
                describe_errors.append('Element Described Message Error')

    assert not describe_errors
    print('TEST: All requested CorrelationUuid have had element description values returned: PASSED')
    print('\n*******************************************************')


@pytest.mark.daily_status
@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
@pytest.mark.parametrize('my_test_type',
                         ['keyaccuracyid_abc', 'keyaccuracyid_ab', 'keyaccuracyid_ac', 'keyaccuracyid_neg'])
def test_key_accuracy(my_test_type):
    cleanup()
    bind_queues()
    accuracy_errors = []
    global assigned_uuid

    payload_message = af_support_tools.get_config_file_property(config_file=config_file,
                                                                heading='identity_service_payloads',
                                                                property=my_test_type)

    print('Sending Identify Element Key Accuracy Messages\n')

    # Publish the message
    af_support_tools.rmq_publish_message(host='amqp', port = 5671, ssl_enabled=True,
                                         exchange='exchange.dell.cpsd.eids.identity.request',
                                         routing_key='dell.cpsd.eids.identity.request',
                                         headers={'__TypeId__': 'dell.cpsd.core.identity.identify.element'},
                                         payload=payload_message,
                                         payload_type='json')

    assert waitForMsg('test.identity.request'), "Message took too long to return"

    return_message = af_support_tools.rmq_consume_message(host='amqp', port=5671, ssl_enabled=True,
                                                          queue='test.identity.request')

    return_json = json.loads(return_message, encoding='utf-8')

    published_json = json.loads(payload_message, encoding='utf-8')

    # Compare the 2 files. If they match the message was successfully published & received.
    print("Verifying Message sent to RabbitMQ...")
    assert published_json == return_json
    print('Published Message Received.')

    print('\nConsuming Response Message...')

    # At this stage we have verified that a message was published & received.
    # Next we need to check that we got the expected Response to our request.

    assert waitForMsg('test.identity.response'), "Message took too long to return"
    return_message = af_support_tools.rmq_consume_message(host='amqp', port = 5671, ssl_enabled=True,
                                                          queue='test.identity.response')

    return_json = json.loads(return_message, encoding='utf-8')

    # Verify the response message has the expected format & parameters
    print("Checking Response Message attributes...")
    if not return_json['timestamp']:
        accuracy_errors.append("No timestamp in message")
    if return_json['correlationId'] not in payload_message:
        accuracy_errors.append("correlationId error")

    for _ in range(len(return_json['elementIdentifications'])):
        if return_json['elementIdentifications'][_]['correlationUuid'] not in payload_message:
            accuracy_errors.append("correlationUuid error")
        assert return_json['elementIdentifications'][_]['elementUuid']

        if my_test_type == 'keyaccuracyid_abc':
            assigned_uuid = return_json['elementIdentifications'][_]['elementUuid']
            print('Response UUID Generated: ', assigned_uuid)
        else:
            identified_uuid = return_json['elementIdentifications'][_]['elementUuid']
            print('Identified UUID: ', identified_uuid)

        if my_test_type == 'keyaccuracyid_neg':
            if identified_uuid == assigned_uuid:
                accuracy_errors.append("Error: ElementUuid match for Key Accuracy negative")
        elif my_test_type != 'keyaccuracyid_abc':
            if identified_uuid != assigned_uuid:
                accuracy_errors.append("ElementUuid Mismatch for Key Accuracy")

    assert not accuracy_errors
    print('TEST: KeyAccuracy test pass.')
    print('\n*******************************************************')


@pytest.mark.daily_status
@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
@pytest.mark.parametrize('my_test_type', ['ident_no_element_type', 'describe_no_element'])
def test_negative_messages(my_test_type):
    cleanup()
    bind_queues()
    negative_errors = []

    if my_test_type == 'describe_no_element':
        payload_message = af_support_tools.get_config_file_property(config_file=config_file,
                                                                    heading='identity_service_payloads',
                                                                    property='describe_no_element')
        headers = {'__TypeId__': 'dell.cpsd.core.identity.describe.element'}
    if my_test_type == 'ident_no_element_type':
        payload_message = af_support_tools.get_config_file_property(config_file=config_file,
                                                                    heading='identity_service_payloads',
                                                                    property='ident_no_element_type')
        headers = {'__TypeId__': 'dell.cpsd.core.identity.identify.element'}



    # Publish the message
    print('Sending Negative test Messages\n')

    af_support_tools.rmq_publish_message(host='amqp', port= 5671, ssl_enabled=True,
                                         exchange='exchange.dell.cpsd.eids.identity.request',
                                         routing_key='dell.cpsd.eids.identity.request',
                                         headers= headers,
                                         payload=payload_message,
                                         payload_type='json')

    assert waitForMsg('test.identity.request'), "Message took too long to return"
    return_message = af_support_tools.rmq_consume_message(host='amqp', port=5671, ssl_enabled=True,
                                                          queue='test.identity.request')



    return_json = json.loads(return_message, encoding='utf-8')

    published_json = json.loads(payload_message, encoding='utf-8')

    # Compare the 2 files. If they match the message was successfully published & received.
    print("Verifying Message sent to RabbitMQ...")
    assert published_json == return_json
    print('Published Message Received.')
    print('\nConsuming Response Message...')
    # At this stage we have verified that a message was published & received.
    # Next we need to check that we got the expected Response to our request.
    return_message = af_support_tools.rmq_consume_message(host='amqp', port=5671, ssl_enabled=True,
                                                          queue='test.identity.response')

    return_json = json.loads(return_message, encoding='utf-8')

    # Convert the returned message to json format and run asserts on the expected output.
    print("Checking Response Message attributes...")

    # Verify the response message has the expected format & parameters
    if not return_json['timestamp']:
        negative_errors.append("No timestamp in message")
    if return_json['correlationId'] not in payload_message:
        negative_errors.append("correlationId error")

    if my_test_type == 'ident_no_element_type':
        if return_json['errorMessage'] != 'EIDS1004E Invalid request message':
            negative_errors.append("Error message incorrect")
            print("Incorrect error message responce" + return_json)

    assert not negative_errors
    print("Negative Message Test Passed")


#######################################################################################################################

# Delete the test queue
def cleanup():
    print('Cleaning up...')

    af_support_tools.rmq_delete_queue(host='amqp', port=5671, ssl_enabled=True, queue='test.identity.request')

    af_support_tools.rmq_delete_queue(host='amqp', port=5671, ssl_enabled=True, queue='test.identity.response')


# Create & bind the test queues
def bind_queues():
    print('Creating the test EIDS Queues')
    af_support_tools.rmq_bind_queue(host='amqp', queue='test.identity.request',
                                    exchange='exchange.dell.cpsd.eids.identity.request',
                                    routing_key='#', ssl_enabled=True)

    af_support_tools.rmq_bind_queue(host='amqp', queue='test.identity.response',
                                    exchange='exchange.dell.cpsd.eids.identity.response',
                                    routing_key='#', ssl_enabled=True)


def waitForMsg(queue):
    print("Waiting for message on queue:" + queue)
    # This function keeps looping until a message is in the specified queue. We do need it to timeout and throw an error
    # if a message never arrives. Once a message appears in the queue the function is complete and main continues.
    # The length of the queue, it will start at 0 but as soon as we get a response it will increase
    q_len = 0
    # Represents the number of seconds that have gone by since the method started
    timeout = 0
    # Max number of seconds to wait
    max_timeout = 10
    # Amount of time in seconds that the loop is going to wait on each iteration
    sleeptime = 1

    while q_len < 1:
        time.sleep(sleeptime)
        timeout += sleeptime

        q_len = af_support_tools.rmq_message_count(host='amqp', port=5671, queue=queue, ssl_enabled=True)

        if timeout > max_timeout:
            print('ERROR: Message took too long to return. Something is wrong')
            cleanup()
            return False
    return True
