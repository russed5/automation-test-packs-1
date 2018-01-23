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

##############################################################################################
#  Common API details
global headers
headers = {'Content-Type': 'application/json'}

global protocol
protocol = 'https://'

global dne_port
dne_port = ':8071'


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
def test_dne_discovered_node_handled(setup):
    """
    Title           :       Verify that dne/nodes API has discovered Dell nodes
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
    global element_id
    element_id = verifyEidsMessage()

    # Step 4: Verify the Node is in Postgres

    currentNodes = readEntryInNodeComputeTable(setup)
    print(currentNodes)

    error_list = []

    if nodeID not in currentNodes:
        error_list.append(nodeID)

    if element_id not in currentNodes:
        error_list.append(nodeID)

    assert not error_list, 'ERROR: Node not in Postgres'

    cleanup('test.rackhd.node.discovered.event')
    cleanup('test.eids.identity.request')
    cleanup('test.eids.identity.response')


#@pytest.mark.dne_paqx_parent_mvp
def test_dne_node_in_esx_cannot_be_provisioned(setup):
    '''
    Attempt to use the dummy node and use the name of an ESXi Hostname existing node
    Expect provisioning to fail
    :param setup:
    :return: none
    '''

    request_body = '[{"id":"' + element_id + '","serviceTag":"XXTESTX","esxiManagementHostname":"fpr1-h14","clusterName":"string","deviceToDeviceStoragePool":{},"esxiManagementIpAddress":"10.0.0.1","esxiManagementGatewayIpAddress":"10.255.255.255","esxiManagementSubnetMask":"255.0.0.0","idracIpAddress":"10.0.0.2","idracGatewayIpAddress":"10.255.255.255","idracSubnetMask":"255.0.0.0","protectionDomainId":"string","protectionDomainName":"string","scaleIoData1SvmIpAddress":"10.0.0.3","scaleIoData1SvmSubnetMask":"255.0.0.0","scaleIoData2SvmIpAddress":"10.0.0.4","scaleIoData2SvmSubnetMask":"255.0.0.0","scaleIoData1EsxIpAddress":"10.0.0.5","scaleIoData1EsxSubnetMask":"255.0.0.0","scaleIoData2EsxIpAddress":"10.0.0.6","scaleIoData2EsxSubnetMask":"255.0.0.0","scaleIoSvmManagementIpAddress":"10.0.0.7","scaleIoSvmManagementGatewayAddress":"10.255.255.255","scaleIoSvmManagementSubnetMask":"255.0.0.0","vMotionManagementIpAddress":"10.0.0.8","vMotionManagementSubnetMask":"255.0.0.0"}]'

    request_body = json.loads(request_body)

    endpoint_post = '/multinode/addnodes'
    url_body_post = protocol + setup['IP'] + dne_port + endpoint_post

    try:
        # POST to the addnode workflow
        response = requests.post(url_body_post, json=request_body, headers=headers, verify=False)
        assert response.status_code == 200, 'Error: Did not get a 200 on /multinode/addnodes'
        data = response.json()

        # save the workflowID as this will be used next to get the status of the job
        addnode_workflow_id = data['id']
        print('WorkflowID: ', addnode_workflow_id)

        time.sleep(15)
        endpoint_get = '/multinode/status/'
        url_body_get = protocol + setup['IP'] + dne_port + endpoint_get + addnode_workflow_id

        # GET on /multinode/status/
        response = requests.get(url_body_get, verify=False)
        assert response.status_code == 200, 'Error: Did not get a 200 response on /multinode/status/'
        data = response.text
        data = json.loads(data, encoding='utf-8')

        jobState = data['state']
        subProcess_jobState = data['subProcesses'][0]['state']
        errorCode = data['subProcesses'][0]['errors'][0]['errorCode']
        errorMessage= data['subProcesses'][0]['errors'][0]['errorMessage']

        error_list = []

        if jobState != 'COMPLETED':
            error_list.append(jobState)

        if subProcess_jobState != 'FAILED':
            error_list.append(subProcess_jobState)

        # if errorCode != 'Verify-Node-Detail-Failed':
        #     error_list.append(errorCode)

        # if errorMessage != '':
        #     error_list.append(errorMessage)

        assert not error_list, 'Test Failed'
        print('Test Pass: Unable to provision node as expected.'
              '\nESXi Hostname already in use.'
              '\nError returned: ' + errorMessage)

    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err, '\n')
        raise Exception(err)


#@pytest.mark.dne_paqx_parent_mvp
def test_dne_node_in_sdc_cannot_be_provisioned(setup):
    '''
    Attempt to use the dummy node and use the IP of an existing ESXi Mgmt node
    Expect provisioning to fail
    :param setup:
    :return: none
    '''

    request_body = '[{"id":"' + element_id + '","serviceTag":"XXTESTX","esxiManagementHostname":"dummy_test","clusterName":"string","deviceToDeviceStoragePool":{},"esxiManagementIpAddress":"10.239.139.21","esxiManagementGatewayIpAddress":"10.239.139.1","esxiManagementSubnetMask":"255.255.255.224","idracIpAddress":"10.0.0.2","idracGatewayIpAddress":"10.255.255.255","idracSubnetMask":"255.0.0.0","protectionDomainId":"string","protectionDomainName":"string","scaleIoData1SvmIpAddress":"10.0.0.3","scaleIoData1SvmSubnetMask":"255.0.0.0","scaleIoData2SvmIpAddress":"10.0.0.4","scaleIoData2SvmSubnetMask":"255.0.0.0","scaleIoData1EsxIpAddress":"10.0.0.5","scaleIoData1EsxSubnetMask":"255.0.0.0","scaleIoData2EsxIpAddress":"10.0.0.6","scaleIoData2EsxSubnetMask":"255.0.0.0","scaleIoSvmManagementIpAddress":"10.0.0.7","scaleIoSvmManagementGatewayAddress":"10.255.255.255","scaleIoSvmManagementSubnetMask":"255.0.0.0","vMotionManagementIpAddress":"10.0.0.8","vMotionManagementSubnetMask":"255.0.0.0"}]'
    request_body = json.loads(request_body)

    endpoint_post = '/multinode/addnodes'
    url_body_post = protocol + setup['IP'] + dne_port + endpoint_post

    try:
        # POST to the addnode workflow
        response = requests.post(url_body_post, json=request_body, headers=headers, verify=False)
        assert response.status_code == 200, 'Error: Did not get a 200 on dne/nodes'
        data = response.json()

        # save the workflowID as this will be used next to get the status of the job
        addnode_workflow_id = data['id']
        print('WorkflowID: ', addnode_workflow_id)

        time.sleep(15)
        endpoint_get = '/multinode/status/'
        url_body_get = protocol + setup['IP'] + dne_port + endpoint_get + addnode_workflow_id

        # GET on /multinode/status/
        response = requests.get(url_body_get, verify=False)
        assert response.status_code == 200, 'Error: Did not get a 200 response'
        data = response.text
        data = json.loads(data, encoding='utf-8')

        jobState = data['state']
        subProcess_jobState = data['subProcesses'][0]['state']
        errorCode = data['subProcesses'][0]['errors'][0]['errorCode']
        errorMessage= data['subProcesses'][0]['errors'][0]['errorMessage']

        error_list = []

        if jobState != 'COMPLETED':
            error_list.append(jobState)

        if subProcess_jobState != 'FAILED':
            error_list.append(subProcess_jobState)

        if errorCode != 'Verify-Node-Detail-Failed':
            error_list.append(errorCode)

        if errorMessage != 'Node details are invalid!  Please correct Node details with the following information and try again. IP Address already in use: ESXi IP Address.':
            error_list.append(errorMessage)

        assert not error_list, 'Test Failed'
        print('Test Pass: Unable to provision node as expected.'
              '\nESXi IP already in use.'
              '\nError returned: ' + errorMessage)

    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err, '\n')
        raise Exception(err)


@pytest.mark.dne_paqx_parent_mvp
def test_dne_preprocess_api_200_response(setup):
    '''
    Use a dummy node to test he multinode\preproess API.
    User should get a 200 response on the POST and GET requests.
    :param setup:
    :return: none
    '''
    request_body = '[{"id":"' + element_id + '","serviceTag":"XXTESTX"}]'
    request_body = json.loads(request_body)

    endpoint_post = '/multinode/preprocess'
    url_body_post = protocol + setup['IP'] + dne_port + endpoint_post

    try:
        # POST to the preprocess workflow
        response = requests.post(url_body_post, json=request_body, headers=headers, verify=False)
        assert response.status_code == 200, 'Error: Did not get a 200 on /multinode/preprocess'
        data = response.json()

        # save the workflowID as this will be used next to get the status of the job
        preprocess_workflow_id = data['id']
        print('WorkflowID: ', preprocess_workflow_id)

        time.sleep(10)

        endpoint_get = '/multinode/status/'
        url_body_get = protocol + setup['IP'] + dne_port + endpoint_get + preprocess_workflow_id

        # GET on /multinode/status/
        response = requests.get(url_body_get, verify=False)
        assert response.status_code == 200, 'Error: Did not get a 200 response on /multinode/status/'
        data = response.text
        data = json.loads(data, encoding='utf-8')

        error_list = []
        jobState = data['state']
        errorCode = data['errors'][0]['errorCode']

        if jobState != 'FAILED':
            error_list.append(jobState)

        if errorCode != 'Inventory-Nodes-Failed':
            error_list.append(errorCode)

        assert not error_list, 'Test Failed'
        print('Test Pass: Preprocess API Responding as expected.')

    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err, '\n')
        raise Exception(err)


@pytest.mark.dne_paqx_parent_mvp
def test_dne_addnodes_api_200_response(setup):
    '''
    Use a dummy node to test he multinode\addnodes API.
    User should get a 200 response on the POST and GET requests.
    :param setup:
    :return: none
    '''
    request_body = '[{"id":"' + element_id + '","serviceTag":"XXTESTX","clusterName":"string","deviceToDeviceStoragePool":{},"esxiManagementGatewayIpAddress":"string","esxiManagementHostname":"string","esxiManagementIpAddress":"string","esxiManagementSubnetMask":"string","idracGatewayIpAddress":"string","idracIpAddress":"string","idracSubnetMask":"string","protectionDomainId":"string","protectionDomainName":"string","scaleIoData1EsxIpAddress":"string","scaleIoData1EsxSubnetMask":"string","scaleIoData1SvmIpAddress":"string","scaleIoData1SvmSubnetMask":"string","scaleIoData2EsxIpAddress":"string","scaleIoData2EsxSubnetMask":"string","scaleIoData2SvmIpAddress":"string","scaleIoData2SvmSubnetMask":"string","scaleIoSvmManagementGatewayAddress":"string","scaleIoSvmManagementIpAddress":"string","scaleIoSvmManagementSubnetMask":"string","vMotionManagementIpAddress":"string","vMotionManagementSubnetMask":"string"}]'
    request_body = json.loads(request_body)

    endpoint_post = '/multinode/addnodes'
    url_body_post = protocol + setup['IP'] + dne_port + endpoint_post

    try:
        # POST to the addnodes workflow
        response = requests.post(url_body_post, json=request_body, headers=headers, verify=False)
        assert response.status_code == 200, 'Error: Did not get a 200 on /multinode/addnodes'
        data = response.json()

        # save the workflowID as this will be used next to get the status of the job
        addnodes_workflow_id = data['id']
        print('WorkflowID: ', addnodes_workflow_id)

        time.sleep(10)

        endpoint_get = '/multinode/status/'
        url_body_get = protocol + setup['IP'] + dne_port + endpoint_get + addnodes_workflow_id

        # GET on /multinode/status/
        response = requests.get(url_body_get, verify=False)
        assert response.status_code == 200, 'Error: Did not get a 200 response on /multinode/status/'
        data = response.text
        data = json.loads(data, encoding='utf-8')

        error_list = []
        jobState = data['state']
        nrOfInstances = data['additionalProperties']['nrOfInstances']
        #subProcess_jobState = data['subProcesses'][0]['state']
        #errorCode = data['subProcesses'][0]['additionalProperties']['errorCode']

        if not (jobState == 'FAILED') or (jobState == 'COMPLETED'):
            error_list.append(jobState)

        if nrOfInstances != 1:
            error_list.append(nrOfInstances)
            
        #if subProcess_jobState != 'FAILED':
        #    error_list.append(subProcess_jobState)

        #if errorCode != 'Verify-Node-Detail-Failed':
        #    error_list.append(errorCode)

        assert not error_list, 'Test Failed'
        print('Test Pass: Addnodes API Responding as expected.')

    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err, '\n')
        raise Exception(err)


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
