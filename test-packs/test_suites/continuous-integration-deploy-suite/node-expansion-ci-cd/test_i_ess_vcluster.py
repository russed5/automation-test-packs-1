#!/usr/bin/python
# Author:
# Revision: 1.2
# Code Reviewed by:
# Description: Testing the ESS on VCluster.

#
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information
#

import af_support_tools
import pytest
import json
import time
import requests
import os
import uuid


#####################################################################
# These are the main tests.
#####################################################################

@pytest.mark.daily_status
@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_handle_validateVcenterCluster_message():
    print("\n======================= Handle validateVcenterCluster Request message =======================\n")

    cleanupQ('test.ess.service.response')
    bindQueue('exchange.dell.cpsd.service.ess.response', 'test.ess.service.response')

    print("Send validate vcenter cluster request message ...\n")
    simulate_validateVcenterClusterRequest_message();

    print("Consume validate vcenter cluster response message ...\n")
    listingsMsg = consumeResponse('queue.dell.cpsd.ess.service.response')
    cleanupQ('test.ess.service.response')

    assert len(listingsMsg['clusters']) == 2, "Error - should have 2 valid clusters"
    assert len(listingsMsg['failedCluster']) == 2, "Error - should have 2 failed clusters"

#######################################################################################################################

def simulate_validateVcenterClusterRequest_message():

    print(" Publishing a vcenterCluster request message .. ")
    my_routing_key = 'ess.service.request.' + str(uuid.uuid4())

    filePath = os.environ['AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/ess_clusterInfo.json'

    with open(filePath) as fixture:

        my_payload = fixture.read()
        af_support_tools.rmq_publish_message(host='amqp', port=5671, ssl_enabled=True,
                                             exchange='exchange.dell.cpsd.service.ess.request',
                                             routing_key=my_routing_key,
                                             headers={
                                                 '__TypeId__': 'com.dell.cpsd.vcenter.validateClusterRequest'},
                                             payload=my_payload,
                                             payload_type='json')

####################################################################################################
def consumeResponse(testqueue):
    """ Consume the next message received on the testqueue and return the message in json format"""

    waitForMsg('test.ess.service.response')

    return_message = af_support_tools.rmq_consume_message(host='amqp', port=5671, ssl_enabled=True,
                                                          queue='test.ess.service.response')

    return_message = json.loads(return_message, encoding='utf-8')

    print ( json.dumps(return_message))
    return return_message

####################################################################################################


def cleanupQ(testqueue):
    """ Delete the passed-in queue."""

    af_support_tools.rmq_delete_queue(host='amqp', port=5671, ssl_enabled=True,
                                      queue=testqueue)


def bindQueue(exchange, testqueue):
    """ Bind 'testqueue' to 'exchange'."""
    af_support_tools.rmq_bind_queue(host='amqp', port=5671, ssl_enabled=True,
                                    queue=testqueue,
                                    exchange=exchange,
                                    routing_key='#')


def waitForMsg(queue):
    # This function keeps looping untill a message is in the specified queue. We do need it to timeout and throw an error
    # if a message never arrives. Once a message appears in the queue the function is complete and main continues.

    print ('Waiting for message')
    # The length of the queue, it will start at 0 but as soon as we get a response it will increase
    q_len = 0

    # Represents the number of seconds that have gone by since the method started
    timeout = 0

    # Max number of seconds to wait
    max_timeout = 15

    # Amount of time in seconds that the loop is going to wait on each iteration
    sleeptime = 10

    while q_len < 1:
        time.sleep(sleeptime)
        timeout += sleeptime

        q_len = af_support_tools.rmq_message_count(host='amqp', port=5671, ssl_enabled=True,
                                                   queue=queue)

        if timeout > max_timeout:
            print('ERROR: Message took too long to return. Something is wrong')
            cleanupQ(queue)
            break
