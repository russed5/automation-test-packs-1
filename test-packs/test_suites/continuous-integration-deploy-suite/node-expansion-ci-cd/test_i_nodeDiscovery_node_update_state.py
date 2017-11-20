#!/usr/bin/python
# Author: russed5
# Revision: 1.1 (updated to take into account TLS implementation)
# Code Reviewed by:
# Description: Testing the ability to change the state of nodes in the Node disocvery postgres DB
#
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information
#

import af_support_tools
import json
import os
import pytest
import requests
import requests.exceptions
import time

global testElementId 
testElementId = "44f0d5ac-44a6-48e0-bf98-93eaa7f452d3"
global testNodeId
testNodeId = "443819a2dc8f96b33e08569d"

@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_changeNodeStateToFAILED(setup):
    """ Verify that the state of a Node, persisted by the Node Discovery PAQX, can be set to 'FAILED'"""

    # ARRANGE
    # Add a testNode  to the node discovery 'compute_node' table in the DISCOVERED state
    insertNodeIntoDB(testElementId, testNodeId, 'DISCOVERED', setup)
    symphonyNodeId = testElementId

    # ACT
    # now set the nodeStatus to FAILED
    sendNodeAllocationRequestMessage(symphonyNodeId, "FAILED", setup)

    # ASSERT
    # verify the new state by querying the REST API, then cleanup
    nodeListing = listNodes(setup)
    deleteEntryInNodeComputeTable(testElementId, setup)

    # there may be multiple nodes in the listing

    error_list = []

    if (testNodeId not in nodeListing):
        error_list.append("Error, no node listed in DB")

    if ("PROVISIONING_FAILED" not in nodeListing):
        error_list.append("Error, Status change not persisted")
        
    assert not error_list

##############################################################################################

@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_changeNodeStateToADDED(setup):
    """ Verify that the state of a Node, persisted by the Node Discovery PAQX, can be set to 'ADDED'"""

    # ARRANGE
    # Add a testNode  to the node discovery 'compute_node' table in the DISCOVERED state
    insertNodeIntoDB(testElementId, testNodeId, 'DISCOVERED', setup)
    symphonyNodeId = testElementId

    # ACT
    # now set the nodeStatus to ADDED and verify the new state by querying the REST API
    sendNodeAllocationRequestMessage(symphonyNodeId, "ADDED", setup)

    # ASSERT
    # verify the new state by querying the REST API, then cleanup
    nodeListing = listNodes(setup)
    deleteEntryInNodeComputeTable(testElementId, setup)

    error_list = []

    if (testNodeId not in nodeListing):
        error_list.append("Error, no node listed in DB")

    if ("ADDED" not in nodeListing):
        error_list.append("Error, Status change not persisted")

    assert not error_list

##############################################################################################

@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_changeNodeStateToDISCOVERED(setup):
    """ Verify that the state of a Node, persisted by the Node Discovery PAQX, can be set to 'DISCOVERED'"""

    # ARRANGE
    # Add a testNode  to the node discovery 'compute_node' table in the FAILED state
    insertNodeIntoDB(testElementId, testNodeId, 'FAILED', setup)
    symphonyNodeId = testElementId

    # ACT
    # now set the nodeStatus to DISCOVERED and verify the new state by querying the REST API
    sendNodeAllocationRequestMessage(symphonyNodeId, "DISCOVERED", setup)

    # ASSERT
    # verify the new state by querying the REST API, then cleanup
    nodeListing = listNodes(setup)
    deleteEntryInNodeComputeTable(testElementId, setup)

    error_list = []

    if (testNodeId not in nodeListing):
        error_list.append("Error, no node listed in DB")

    if ("DISCOVERED" not in nodeListing):
        error_list.append("Error, Status change not persisted")

    assert not error_list


##############################################################################################

@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_changeNodeStateToRESERVED(setup):
    """ Verify that the state of a Node, persisted by the Node Discovery PAQX, can be set to 'RESERVED'"""

    # ARRANGE
    # Add a testNode  to the node discovery 'compute_node' table in the DISCOVERED state
    insertNodeIntoDB(testElementId, testNodeId, 'DISCOVERED', setup)
    symphonyNodeId = testElementId


    # ACT
    # now set the nodeStatus to RESERVED and verify the new state by querying the REST API
    sendNodeAllocationRequestMessage(symphonyNodeId, "RESERVED", setup)

    # ASSERT
    # verify the new state by querying the REST API, then cleanup
    nodeListing = listNodes(setup)
    deleteEntryInNodeComputeTable(testElementId, setup)

    error_list = []

    if (testNodeId not in nodeListing):
        error_list.append("Error, no node listed in DB")

    if ("PROVISIONING_IN_PROGRESS" not in nodeListing):
        error_list.append("Error, Status change not persisted")

    assert not error_list


##############################################################################################

@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_lookupNodeState(setup):
    """ Verify that the state(s) of a Node persisted by the Node Discovery PAQX can be looked-up"""

    # ARRANGE
    error_list = []

    # ARRANGE
    # Add a testNode  to the node discovery 'compute_node' table in the DISCOVERED state
    insertNodeIntoDB(testElementId, testNodeId, 'DISCOVERED', setup)
    symphonyNodeId = testElementId
    sendNodeAllocationRequestMessage(symphonyNodeId, "DISCOVERED", setup)

    # bind a test q to the node discovery exchange so that we can consume a response to our message
    # but first we delete it to ensure it doesn't already exist
    cleanupQ('test.dne.paqx.node.response')
    bindQueue('exchange.dell.cpsd.paqx.node.discovery.response', 'test.dne.paqx.node.response')

    # ACT
    # send a LookupNodeAllocationRequestMessage and read-in the response
    sendNodeAllocationRequestMessage(symphonyNodeId, "LOOKUP", setup)


    # ASSERT
    # consume response for verification and cleanup
    lookupResponse = consumeResponse('test.dne.paqx.node.response')
    cleanupQ('test.dne.paqx.node.response')
    deleteEntryInNodeComputeTable(testElementId, setup)


    if lookupResponse['status'] != "SUCCESS":
        error_list.append("Errror : The lookupResponse message did not have a status of SUCCESS")
    if lookupResponse['nodeAllocationInfo']['elementIdentifier'] != symphonyNodeId :
        error_list.append("Errror : The elementIdentifier filed in the lookupResponse message is incorrect")
    if lookupResponse['nodeAllocationInfo']['nodeIdentifier'] != testNodeId:
        error_list.append("Errror : The nodeIdentifier field in the lookupResponse message is incorrect")
    if lookupResponse['nodeAllocationInfo']['allocationStatus'] != "DISCOVERED" :
        error_list.append("Errror : The allocationStatus field in the lookupResponse message is incorrect")
    if lookupResponse['nodeAllocationErrors'] != [] :
        error_list.append("Errror : nodeAllocationErrors in the lookupResponse message : %r" % lookupResponse['nodeAllocationErrors'])

    assert not error_list

##############################################################################################

@pytest.mark.dne_paqx_parent_mvp_extended
def test_getListOfNodes(setup):
    """ Verify that a listing of all Node states can be retrieved."""

    # ARRANGE
    # Add a testNode  to the node discovery 'compute_node' table in the DISCOVERED state
    insertNodeIntoDB(testElementId, testNodeId, 'DISCOVERED', setup)
    symphonyNodeId = testElementId

    # bind a test q to the node discovery exchange so that we can consume a response to our message
    cleanupQ('test.dne.paqx.node.response')
    bindQueue('exchange.dell.cpsd.paqx.node.discovery.response', 'test.dne.paqx.node.response')

    # ACT
    sendNodeAllocationRequestMessage(symphonyNodeId, "LISTING", setup)

    # ASSERT
    # consume response for verification and cleanup
    listingsMsg = consumeResponse('test.dne.paqx.node.response')
    cleanupQ('test.dne.paqx.node.response')
    deleteEntryInNodeComputeTable(testElementId, setup)

    assert listingsMsg['discoveredNodes'], "Error - No discovered nodes were returned in Listing"
    for node in listingsMsg['discoveredNodes']:
        if node['convergedUuid'] == symphonyNodeId :
            assert "DISCOVERED" == node["allocationStatus"], "Error, wrong Node Status returned in listing"
            assert symphonyNodeId == node['convergedUuid'], "Error, wrong converged UUID returned in listing"



##############################################################################################

def insertNodeIntoDB(elementId, nodeId, nodeStatus, setup):
    """ Insert a new node entry, DISCOVERED state, into the compute_node table in the postgres database.

    :parameter: elementId - symphonyUUID (eg. '44f0d5ac-44a6-48e0-bf98-93eaa7f452d3')
    :parameter: nodeId - rackHD-node-ID (eg. '443819a2dc8f96b33e08569d')
    :parameter: nodeStatus - state (eg. RESERVED or DISCOVERED or ADDED ...)
    :return: The result of the psql command (success result is 'INSERT 0 1')
    """

    nodeSerial = "88888888"
    nodeProduct = "R730 Base"
    nodeVendor = ""

    # write the INSERT command into a file on the remote host for ease of execution
    # then copy that file into the postgres docker container
    # then  ask postgres to execute the command in the file
    insertCmd = "insert into compute_node(ELEMENT_ID, NODE_ID, NODE_STATUS, NODE_SERIAL, NODE_PRODUCT, NODE_VENDOR, LOCKING_VERSION) values (\'" + \
                elementId + "\', \'" + nodeId + "\', \'" + nodeStatus + "\', \'" + nodeSerial + "\',\'" + nodeProduct + "\',\'" + nodeVendor + "\', 0);"


    writeToFileCmd = "echo \"" + insertCmd + "\" > /tmp/sqlInsert.txt"

    copyFileToContainerCmd = "docker cp /tmp/sqlInsert.txt postgres:/tmp/sqlInsert.txt"

    execSQLCommand = "docker exec -i postgres sh -c \'su - postgres sh -c \"psql \\\"dbname=node-discovery-service\\\" -f /tmp/sqlInsert.txt\"\'"

    try:
        result = af_support_tools.send_ssh_command(
           host=setup['IP'],
           username=setup['cli_user'],
           password=setup['cli_password'],
           command=writeToFileCmd,
           return_output=True)

    
        result = af_support_tools.send_ssh_command(
           host=setup['IP'],
           username=setup['cli_user'],
           password=setup['cli_password'],
           command=copyFileToContainerCmd,
           return_output=True)


        result = af_support_tools.send_ssh_command(
            host=setup['IP'],
            username=setup['cli_user'],
            password=setup['cli_password'],
            command=execSQLCommand,
            return_output=True)

        sleeptime = 10

        return result

    except Exception as err:
        # Return code error
        print(err, '\n')
        raise Exception(err)


################################################################################################

def deleteEntryInNodeComputeTable(elementId, setup):
    """ A Function to clear all entries form the postgres table 'compute_node'.

    :parameter: elementId - symphonyUUID (eg. '44f0d5ac-44a6-48e0-bf98-93eaa7f452d3')
    :return: the result of the delete command (sample success result is 'DELETE #'
    where '#' is the number of entries deleted. """

    execSQLCommand = "docker exec -i postgres sh -c \'su postgres sh -c \"psql \\\"dbname=node-discovery-service \\\" -c \\\"delete FROM compute_node;\\\"\"\'"

    try:

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

################################################################################################

def sendNodeAllocationRequestMessage(node, state, setup):
    """ Use the AMQP bus to send a start/cancel/fail/complete/lookup message to the node-discovery paqx for a specific node.

    :parameter: node - the symphonyUUID of a Node (eg. dc38f716-8d9e-42d6-a61b-fddf0269f5ac)
    :parameter: state - a string equal to DISCOVERED/FAILED/ADDED/LOOKUP or RESERVED"""

    if state == "DISCOVERED" : messageType = "cancel"
    elif state == "FAILED"   : messageType = "fail"
    elif state == "ADDED"    : messageType = "complete"
    elif state == "RESERVED" : messageType = "start"
    elif state == "LOOKUP" : messageType = "lookup"
    elif state == "LISTING": messageType = "list"

    my_exchange = "exchange.dell.cpsd.paqx.node.discovery.request"
    my_routing_key = "dell.cpsd.paqx.node.discovery.request"

    if messageType == "list" :
        my_type_id = "dell.converged.discovered." + messageType + ".nodes"
        my_payload = {"messageProperties": { "timestamp":"2017-09-07T03:54:39.500Z", \
                                         "correlationId":"90035098-3cd2-3fb0-9696-3f7d28e17f72", \
                                         "replyTo": "reply.to.queue.binding"}}
    else :
        my_type_id = "dell.converged.discovered.nodes." + messageType + ".node.allocation.request"
        my_payload = {"messageProperties": { "timestamp":"2017-09-07T03:54:39.500Z", \
                                         "correlationId":"90035098-3cd2-3fb0-9696-3f7d28e17f72", \
                                         "replyTo": "reply.to.queue.binding"}, \
                                         "elementIdentifier": node}

    try:
        # publish the AMQP message to set the state of the node
        af_support_tools.rmq_publish_message(host='amqp',
                                         port=5671, ssl_enabled=True,
                                         exchange=my_exchange,
                                         routing_key=my_routing_key,
                                         headers={
                                             '__TypeId__': my_type_id},
                                         payload=json.dumps(my_payload))
        return None

    except Exception as err:
        # Return code error
        print(err, '\n')
        raise Exception(err)

##############################################################################################

def getFirstValidNodeID() :
    "Get a list of all discovered nodes from the DNE and return the nodeID of the first one."

    allNodes = listNodes()
    firstNodeId = allNodes[0]['symphonyUuid']
    return firstNodeId


##################################################################################################

def bindQueue(exchange, testqueue):
    """ Bind 'testqueue' to 'exchange'."""

    af_support_tools.rmq_bind_queue(host='amqp',
                                    port=5671, ssl_enabled=True,
                                    queue=testqueue,
                                    exchange=exchange,
                                    routing_key='#')

####################################################################################################

def consumeResponse(testqueue):
    """ Consume the next message received on the testqueue and return the message in json format"""
    waitForMsg('test.dne.paqx.node.response')
    rxd_message = af_support_tools.rmq_consume_message(host='amqp', port=5671,
                                                              queue=testqueue,
                                                              ssl_enabled=True)

    rxd_json = json.loads(rxd_message, encoding='utf-8')
    return rxd_json

####################################################################################################

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
    sleeptime = 10

    while q_len < 1:
        time.sleep(sleeptime)
        timeout += sleeptime

        q_len = af_support_tools.rmq_message_count(host='amqp',
                                                   port=5671,
                                                   ssl_enabled=True,
                                                   queue=queue)

        if timeout > max_timeout:
            print('ERROR: Message took too long to return. Something is wrong')
            cleanupQ(queue)
            break

####################################################################################################

def cleanupQ(testqueue):
    """ Delete the passed-in queue."""

    af_support_tools.rmq_delete_queue(host='amqp', port=5671,
                                      ssl_enabled=True,
                                    queue=testqueue)


####################################################################################################
def listNodes(setup):
    """ A Function to get all entries form the postgres table 'compute_node'.

    :parameter: none
    :return: the result of the select * command
    """

    execSQLCommand = "docker exec -i postgres sh -c \'su postgres sh -c \"psql \\\"dbname=node-discovery-service \\\" -c \\\"select * FROM compute_node;\\\"\"\'"

    try:

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

