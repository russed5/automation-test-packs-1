#!/usr/bin/python
# Author:
# Revision: 1.2
# Code Reviewed by:
# Description: Testing the ESS on vCenter Cluster.

#
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information
#

import af_support_tools
import pytest
import json
import time
import os


#####################################################################
# These are the main tests.
#####################################################################

@pytest.mark.daily_status
@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_handle_validateVcenterCluster_message_1():
    '''
    Input: 2 valid, 2 invalid clusters
    Expect: 2 clusters & 2 warnings

    :return:
    '''
    cleanupQ('test.ess.service.response')
    bindQueue('exchange.dell.cpsd.service.ess.response', 'test.ess.service.response')

    filePath = os.environ[
                   'AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/ess_vCenterClusters/ess_clusterInfo_1.json'

    with open(filePath) as fixture:
        my_payload = fixture.read()

    print("Send validate vcenter cluster request message ...\n")
    simulate_validateVcenterClusterRequest_message(my_payload);

    print("Consume validate vcenter cluster response message ...\n")
    responseMsg = consumeResponse()

    print(responseMsg)

    error_list = []

    if responseMsg['clusters']['XXTESTXX1'] != 'test_cluster_63hosts':
        error_list.append('Error :wrong cluster identified')
    if responseMsg['clusters']['XXTESTXX2'] != 'test_cluster_63hosts':
        error_list.append('Error :wrong cluster identified')
    if responseMsg['clusters']['XXTESTXX3'] != 'test_cluster_63hosts':
        error_list.append('Error :wrong cluster identified')


    if responseMsg['failedCluster'][0] != 'REQUIRED:  No more than 64 nodes per cluster -- Cluster test_cluster_64hosts with 64 nodes failed rule checking.':
        error_list.append('Error :Warning returned')

    if responseMsg['failedCluster'][1] != 'REQUIRED:  No more than 64 nodes per cluster -- Cluster test_cluster_65hosts with 65 nodes failed rule checking.':
        error_list.append('Error :Warning returned')

    assert not error_list

    cleanupQ('test.ess.service.response')


@pytest.mark.daily_status
@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_handle_validateVcenterCluster_message_2():
    '''
    Input: 1 invalid clusters
    Expect: 1 warnings

    :return:
    '''
    cleanupQ('test.ess.service.response')
    bindQueue('exchange.dell.cpsd.service.ess.response', 'test.ess.service.response')

    filePath = os.environ[
                   'AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/ess_vCenterClusters/ess_clusterInfo_2.json'

    with open(filePath) as fixture:
        my_payload = fixture.read()

    print("Send validate vcenter cluster request message ...\n")
    simulate_validateVcenterClusterRequest_message(my_payload);

    print("Consume validate vcenter cluster response message ...\n")
    responseMsg = consumeResponse()

    print(responseMsg)

    error_list = []

    if responseMsg['failedCluster'][0] != 'REQUIRED:  No more than 64 nodes per cluster -- Cluster test_cluster_100host with 100 nodes failed rule checking.':
        error_list.append('Error :Warning returned')

    assert not error_list

    cleanupQ('test.ess.service.response')


@pytest.mark.daily_status
@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_handle_validateVcenterCluster_message_3():
    '''
    Input: 0 clusters
    Expect: 2 clusters & 2 warnings

    :return:
    '''
    cleanupQ('test.ess.service.response')
    bindQueue('exchange.dell.cpsd.service.ess.response', 'test.ess.service.response')

    filePath = os.environ[
                   'AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/ess_vCenterClusters/ess_clusterInfo_3.json'

    with open(filePath) as fixture:
        my_payload = fixture.read()

    print("Send validate vcenter cluster request message ...\n")
    simulate_validateVcenterClusterRequest_message(my_payload);

    print("Consume validate vcenter cluster response message ...\n")
    responseMsg = consumeResponse()

    print(responseMsg)

    error_list = []

    if len(responseMsg['failedCluster']) != 0:
        error_list.append('Error :Warning returned')

    if len(responseMsg['failedCluster']) != 0:
        error_list.append('Error :Warning returned')

    assert not error_list

    cleanupQ('test.ess.service.response')

#######################################################################################################################

def simulate_validateVcenterClusterRequest_message(my_payload):

    print(" Publishing a vcenterCluster request message .. ")

    af_support_tools.rmq_publish_message(host='amqp', port=5671, ssl_enabled=True,
                                         exchange='exchange.dell.cpsd.service.ess.request',
                                         routing_key='ess.service.request',
                                         headers={
                                             '__TypeId__': 'com.dell.cpsd.vcenter.validateClusterRequest'},
                                         payload=my_payload,
                                         payload_type='json')


def consumeResponse():
    """ Consume the next message received on the testqueue and return the message in json format"""

    waitForMsg('test.ess.service.response')

    return_message = af_support_tools.rmq_consume_message(host='amqp', port=5671, ssl_enabled=True,
                                                          queue='test.ess.service.response')

    return_message = json.loads(return_message, encoding='utf-8')
    return return_message


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
    q_len = 0
    timeout = 0
    max_timeout = 15
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
