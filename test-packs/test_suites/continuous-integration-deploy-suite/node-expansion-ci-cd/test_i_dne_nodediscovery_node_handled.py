#!/usr/bin/python
# Author:
# Revision: 2.0
# Code Reviewed by:
# Description:
#
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information
#

import json
import pytest
import af_support_tools
import time
import requests
import sys
import os


##############################################################################################

@pytest.fixture()
def setup():
    parameters = {}
    env_file = 'env.ini'

    ipaddress = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')
    cli_user = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='username')
    cli_password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                             property='password')

    parameters['IP'] = ipaddress
    parameters['cli_user'] = cli_user
    parameters['cli_password'] = cli_password

    return parameters


#####################################################################
# These are the main tests.
#####################################################################
@pytest.mark.daily_status
@pytest.mark.dne_paqx_parent_mvp
# @pytest.mark.dne_paqx_parent_mvp_extended
def test_dne_discovered_node_handled(setup):
    """
    Title           :       Verify that dne/nodes API has disocvered Dell nodes
    Description     :       A dummy node discovered message is published to trigger the node discovery process
                            It will fail if :
                                A node is already present
                                The NodeID in the API doesn't match what RackHD sent
                                The UUID in the api doesnt match the EIDS generated value
    Parameters      :       none
    Returns         :       None
    """

    print('\nRunning Test on system: ', setup['IP'])

    cleanup('test.rackhd.node.discovered.event')
    cleanup('test.eids.identity.request')
    cleanup('test.eids.identity.response')
    bindQueues('exchange.dell.cpsd.adapter.rackhd.node.discovered.event', 'test.rackhd.node.discovered.event')
    bindQueues('exchange.dell.cpsd.eids.identity.request', 'test.eids.identity.request')
    bindQueues('exchange.dell.cpsd.eids.identity.response', 'test.eids.identity.response')

    time.sleep(2)

    # Step 1: Publish a message to dummy a node discovery. Values used here are all dummy values.
    the_payload = '{"data":{"ipMacAddresses":[{"ipAddress":"172.31.128.12","macAddress":"fb-43-62-54-d4-3a"},{"macAddress":"b9-ce-c4-73-10-35"},{"macAddress":"4d-63-c5-48-9f-5c"},{"macAddress":"1d-97-c3-a0-42-1a"},{"macAddress":"ce-1d-b5-a6-65-ad"},{"macAddress":"30-e5-72-6f-78-79"}],"nodeId":"123456789012345678909777","nodeType":"compute","serial":"XXTESTX","product":"R730 Base","vendor":""},"messageProperties":{"timestamp":"2017-06-27T08:58:32.437+0000"},"action":"discovered","createdAt":"2017-06-27T08:58:31.871Z","nodeId":"123456789012345678909777","severity":"information","type":"node","typeId":"123456789012345678909777","version":"1.0"}'

    af_support_tools.rmq_publish_message(host='amqp', port=5671, ssl_enabled=True,
                                         exchange='exchange.dell.cpsd.adapter.rackhd.node.discovered.event',
                                         routing_key='',
                                         headers={'__TypeId__': 'com.dell.cpsd.component.events.Alert'},
                                         payload=the_payload)

    # Keeping this here for reference as type has changed. '__TypeId__': 'com.dell.cpsd.NodeEventDiscovered'},

    # Step 2: Verify the node was discovered and returned a nodeID
    nodeID = rmqNodeDiscover()

    # Step 3: Verify the EIDS Messages sequence and get the UUID for the new node
    element_id = verifyEidsMessage()

    # Step 4: Verify the Node is in Postgres

    currentNodes = readEntryInNodeComputeTable(setup)
    print(currentNodes)

    error_list = []

    if (nodeID not in currentNodes):
        error_list.append(nodeID)

    if (element_id not in currentNodes):
        error_list.append(nodeID)

    assert not error_list, 'ERROR: Node not in Postgres'

    cleanup('test.rackhd.node.discovered.event')
    cleanup('test.eids.identity.request')
    cleanup('test.eids.identity.response')


#####################################################################
# These are the main functions called in the test.

def rmqNodeDiscover():
    # Verify the Node Discovered Event message
    # Return the newly discovered nodeID value

    assert waitForMsg('test.rackhd.node.discovered.event'), 'Error: No Node Discovered Msg Recieved'
    return_message = af_support_tools.rmq_consume_message(host='amqp', port=5671, ssl_enabled=True,
                                                          queue='test.rackhd.node.discovered.event')

    return_json = json.loads(return_message, encoding='utf-8')

    nodeID = return_json['data']['nodeId']

    return nodeID


def verifyEidsMessage():
    # We need to verify that the triggered eids.identity.request is valid.
    # Check the EIDS request messages
    # Return the EIDS UUID generated value

    assert waitForMsg('test.eids.identity.request'), 'Error: No request sent to EIDS'
    return_message = af_support_tools.rmq_consume_message(host='amqp', port=5671, ssl_enabled=True,
                                                          queue='test.eids.identity.request')

    # Check the EIDS response message
    assert waitForMsg('test.eids.identity.response'), 'Error: Mor response for EIDS'
    return_message = af_support_tools.rmq_consume_message(host='amqp', port=5671, ssl_enabled=True,
                                                          queue='test.eids.identity.response')

    return_json = json.loads(return_message, encoding='utf-8')

    uuid = return_json['elementIdentifications'][0]['elementUuid']

    return uuid


def readEntryInNodeComputeTable(setup):
    """ A Function to get all entries form the postgres table 'compute_node'.

    :parameter: none
    :return: the result of the select * command
    """

    readFromCommand = 'select * FROM compute_node'
    writeToFileCommand = "echo \"" + readFromCommand + "\" > /tmp/sqlRead.txt"
    writeToDockerFileCommand = 'docker cp /tmp/sqlRead.txt postgres:/tmp/sqlRead.txt'
    execSQLCommand = "docker exec -i postgres sh -c \'su - postgres sh -c \"psql \\\"dbname=node-discovery-service options=--search_path=public\\\" -f /tmp/sqlRead.txt\"\'"

    try:

        af_support_tools.send_ssh_command(
            host=setup['IP'],
            username=setup['cli_user'],
            password=setup['cli_password'],
            command=writeToFileCommand,
            return_output=False)

        af_support_tools.send_ssh_command(
            host=setup['IP'],
            username=setup['cli_user'],
            password=setup['cli_password'],
            command=writeToDockerFileCommand,
            return_output=False)

        result = af_support_tools.send_ssh_command(
            host=setup['IP'],
            username=setup['cli_user'],
            password=setup['cli_password'],
            command=execSQLCommand,
            return_output=True)

        return result

    except Exception as err:
        # Return code error
        print(err, '\n')
        raise Exception(err)


#####################################################################
# These are small functions called throughout the test.

def bindQueues(exchange, queue):
    af_support_tools.rmq_bind_queue(host='amqp', port=5671, ssl_enabled=True, routing_key='#', queue=queue,
                                    exchange=exchange)


def cleanup(queue):
    af_support_tools.rmq_delete_queue(host='amqp', port=5671, ssl_enabled=True, queue=queue)


def waitForMsg(queue):
    # This function keeps looping untill a message is in the specified queue. We do need it to timeout and throw an error
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

        q_len = af_support_tools.rmq_message_count(host='amqp', port=5671, ssl_enabled=True, queue=queue)

        if timeout > max_timeout:
            print('ERROR: Message took too long to return. Something is wrong')
            return False

    return True

#######################################################################################################################
