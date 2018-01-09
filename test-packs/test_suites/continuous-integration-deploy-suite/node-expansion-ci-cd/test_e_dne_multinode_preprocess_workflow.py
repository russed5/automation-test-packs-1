#!/usr/bin/python
# Author: russed5
# Revision: 0.1
# Code Reviewed by:
# Description: Testing the ability to enter multiple node details to the PreProcess REST api
#
# Copyright (c) 2018 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information
#

import af_support_tools
import json
import os
import pytest
import requests
import requests.exceptions
import ssl
import time
from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
import atexit
import argparse

@pytest.fixture(scope="module", autouse=True)
def load_test_data(setup):

    # Update config ini files at runtime
    my_data_file = os.environ.get('AF_RESOURCES_PATH') + '/continuous-integration-deploy-suite/symphony-sds.properties'
    af_support_tools.set_config_file_property_by_data_file(my_data_file)

    # Update setup_config.ini file at runtime
    my_data_file = os.environ.get('AF_RESOURCES_PATH') + '/continuous-integration-deploy-suite/setup_config.properties'
    af_support_tools.set_config_file_property_by_data_file(my_data_file)


@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_enterMultiNodes_to_preprocess(setup):
    """ Verify that multiple node details can be input to the preprocess flow and that the correct
         results for the preprocess flow are then returned.

        The preprocess REST call response will be checked for a successful status code.
        The dne job status response will be checked for successful criteria also.

        input parameters :  setup - symphony specifics, see conftest.py

        Post-test environment - DNE will have discovered any compute nodes listed at the rackHD
    """

    global scaleIoToken
    scaleIoToken = retrieveScaleIoToken(setup)

    # ------------------- ARRANGE -------------------------------------------------------------------
    # Objective : to populate the input data (json) to submit to the multi-node dne preprocess api
    #
    # Firstly, Facilitate Symphony discovering as many available nodes as possible
    # by retrieving all known nodes at the rackhd and publishing a node disscovery event for each of them
    # Secondly, query the dne api to retrieve the symphonyUUIDs for the newly discovered nodes
    # Finally, generate the correctly formatted json with the discovered node details. The json will be submitted to
    # the preprocess api input field

    discoverRackHDNodes(setup)
    time.sleep(10)
    nodeIdentifiers = returnUUIDfromDNElisting(setup)

    # use nodeIdentifiers (the list of discovered nodes) to create a json string with the node details
    # to input to the preprocess endpoint
    count = 1
    data_string = "["
    for node in nodeIdentifiers:
        # check that id and serialtag are both allocated for this node
        if len(node) == 2 :
            data_string = data_string + "{" + '"id":"' + node[0] + '", "serviceTag":"' + node[1] + '"}' 
            # check to see if this is the last node, if not include a comma in the json before the next node is entered
            if count < len(nodeIdentifiers):
                 data_string = data_string + ", "
            count += 1
    data_string = data_string +"]"

    nodeCount = count-1
    global nodeCount

    print("\n Nodes to preprocess are: ", data_string)
    
    # ---- ACT -----------------------------------------------------------------------------------------------
    # (1) call the preprocess flow, submitting the list of nodes
    # (2) get the preprocess status for the preprocess job id
    #
    preprocess_result = execute_preprocess(data_string, setup)
    preprocess_result_json = json.loads(preprocess_result.text, encoding='utf-8')
    print('\n jobid', preprocess_result.text)
    time.sleep(30)
    jobStatus_result = execute_status_call(preprocess_result_json['id'], setup)



    # --- ASSERT ---------------------------------------------------------------------------------------------
    # (1) verify the response status from the preprocess REST call is 200 and that a job id was returned
    # (2) Verify that the response status from the job status REST call is 200
    # (3) verify the number of nodes listed in the status response equals the number we submitted our node list
    # (4) verify the status of the overall flow is "COMPLETE"
    # (5) verify the ess recommended vcluster returned is valid
    # (6) verify the ess recommended protection domain inventory returned is valid
    # (7) verify a valid ess recommended storage_pool is returned
    #

    jobStatus_json = json.loads(jobStatus_result.text, encoding='utf-8')

    error_list = []

    if (preprocess_result.status_code != 200):
        error_list.append("Error, in preprocess execute REST call - status %r returned." % preprocess_result.status_code)

    if not preprocess_result.text:
        error_list.append("Error : no job Id was returned")

    if (jobStatus_result.status_code != 200):
        error_list.append("Error, in preprocess status REST call - status %r returned." % jobStatus_result.status_code)

    #if jobStatus_json['additionalProperties']['nrOfInstances'] != nodeCount:
    #    error_list.append("Error : the number of nodes instances in status resp is %r : it should be %r"
    #                                  % (jobStatus_json['additionalProperties']['nrOfInstances'], nodeCount))

    #if jobStatus_json['additionalProperties']['nrOfCompletedInstances'] != nodeCount:
    #    error_list.append("Error : the number of completed nodes in status response is %r : it should be %r"
    #                                   % (jobStatus_json['additionalProperties']['nrOfCompletedInstances'], nodeCount))

    if jobStatus_json['state'] != "COMPLETED":
        error_list.append("Error : the overall state of the flow is %r" % jobStatus_json['state'])


    if check_findVCluster(jobStatus_json, setup) == 0:
        error_list.append("Error : vcenter check failed")

    if check_findProtectionDomain(jobStatus_json,setup) == 0:
        error_list.append("Error : protection domain  check failed")

    if check__findScaleIO(jobStatus_json,setup) == 0:
        error_list.append("Error : storage pool  check failed")


    assert not error_list
    
#############################################################################

def execute_preprocess(preprocess_data, setup):
    """ Call the dne preprocess REST call
        Parameters : preprocess_data - the list of discovered nodes in json format
                                           {
                                                "id": "string",
                                                "serviceTag": "string"
                                           }
                     setup - test environment specifics
        Returns : The REST response data (status and jobId)
    """

    apipath = '/multinode/preprocess/'
    url = 'https://' + setup['IP'] + ':8071' + apipath
    headerstring = {"Content-Type": "application/json"}

    try:
     response = requests.post(url, headers=headerstring, data=preprocess_data, verify=False)
    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)

    return response

##############################################################################

def execute_status_call(job_id, setup):
    """ Call the dne job status REST call
        Parameters :  job_id - an id associated with a dne preprocess request.
                      setup - test environment specifics
        Returns : The status response data
    """

    apipath = '/multinode/status/'
    url = 'https://' + setup['IP'] + ':8071' + apipath + job_id
    headerstring = {"Content-Type": "application/json"}

    try:
     response = requests.get(url, headers=headerstring, verify=False)
    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)

    return response

##############################################################################

def returnUUIDfromDNElisting(setup):
    """ Call the DNE endpoint /dne/nodes to get a list of discovered nodes
        Parameters : setup - test environment specifics
        Returns : A list of nodes [symphonyUUId, serialtag] as listed at <IP>:8071/dne/nodes
                : will return "" if no nodes listed
    """

    apipath = '/dne/nodes/'
    url = 'https://' + setup['IP'] + ':8071' + apipath
    headerstring = {"Content-Type": "application/json"}

    try:
     response = requests.get(url, headers=headerstring, verify=False)

    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)

    data_text = response.text
    data_json = json.loads(response.text, encoding='utf-8')

    nodeList = []
    
    if data_text != "[]" :
        for entry in data_json :
            node = [entry['symphonyUuid'], entry['serialNumber']]
            nodeList.append(node)
            
    return nodeList

##############################################################################


def retrieveRHDToken(setup):
    """"
    Description :       retrieve the rackHD token allowing api querying
    Returns :           rackHD api token (string)

    """
    url = "http://" + setup['rackHD_IP'] + ":32080/login"
    header = {'Content-Type': 'application/json'}
    body = '{"username": "' + setup['rackHD_username'] + '", "password": "' + setup['rackHD_password'] + '"}'

    try:
        resp = requests.post(url, headers=header, data=body)

    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)


    tokenJson = json.loads(resp.text, encoding='utf-8')
    token = tokenJson["token"]
    return token

#####################################################################

def getNodeIdentifiers(token,setup):
    """ Return a list of nodes from rackhd

       Parameters :  token   -  a rackhd token to allow querying via the api
                     setup - test environment specifics

       Returns : a list of nodes from rackhd in the form
                  [[nodeId, serialTag, macaddress], [nodeId, serialTag, macaddress], ...]] """

    apipath = '/api/2.0/nodes/'
    url = 'http://' + setup['rackHD_IP'] + ':32080' + apipath
    headerstring = {"Content-Type": "application/json", "Authorization": "JWT " + token}

    try:
     response = requests.get(url, headers=headerstring)
    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)
    
    nodesList = []
    
    data_text = response.text
    data_json = json.loads(response.text, encoding='utf-8')

    # find each compute node and add its nodeId to the list of nodes
    for node in data_json:
        if node['type'] == "compute":
            testNodeIdentifier = [node['id']]
            nodesList.append(testNodeIdentifier)
 
    # for each nodeId found, find the associated enclosure and extract the serialTag
    for nodeId in nodesList:
        for node in data_json:
            if  node['type'] == 'enclosure' and node['relations'] :
                # check if the NodeID is listed as a target in this enclosure
                if node['relations'][0]['targets'][0] == nodeId[0] :
                    # if its is, extract the serial tag from the encloser name
                    a,b,serialTag = node['name'].split(" ")
                    nodeId.append(serialTag)

    # go back through the list of nodes and retrieve the  MAC address associated
    # with each nodeId
    for nodeId in nodesList:
        for node in data_json:
            if  node['id'] == nodeId[0] :
                nodeId.append(node['name'])

    return nodesList
    
#############################################################################

def discoverRackHDNodes(setup):
    """ publish a node discovery event for each node in a list of rackhd-discovered nodes """

    token = retrieveRHDToken(setup)
    nodeList = getNodeIdentifiers(token, setup)
    publishNodeDiscoveredEvents(nodeList)

    return None

#############################################################################

def publishNodeDiscoveredEvents(nodeList):
    """ publish a node discovery event for each node in a list of rackhd-discovered nodes
        The nodes in the  nodeList are of the form [id, serial tag, mac address]
        Returns : Nothing """

    count = 0

    for node in nodeList :
        if len(node) == 3 :
            cleanup('test.rackhd.node.discovered.event')
            cleanup('test.eids.identity.request')
            cleanup('test.eids.identity.response')
            bindQueues('exchange.dell.cpsd.adapter.rackhd.node.discovered.event', 'test.rackhd.node.discovered.event')
            bindQueues('exchange.dell.cpsd.eids.identity.request', 'test.eids.identity.request')
            bindQueues('exchange.dell.cpsd.eids.identity.response', 'test.eids.identity.response')

            time.sleep(2)

            # Step 1: Publish a node discovery event to the amqp bus. Some Values used here are dummy values
            # For each node in nodeList the format is [id, serial tag, mac address]
            # The Count variable is used to provide a different string for certain fields (eg. IP address) at each loop
            #
            the_payload = '{"data":{"ipMacAddresses":[{"ipAddress":"172.31.128.' + str(count) + '","macAddress":"' + node[2] + '"},' \
                  '{"macAddress":"b9-ce-c4-73-10-3' + str(count) + '"},{"macAddress":"4d-63-c5-48-9f-5' + str(count) + '"},' \
                  '{"macAddress":"1d-97-c3-a0-42-1' + str(count) + '"},{"macAddress":"ce-1d-b5-a6-65-a' + str(count) + '"},' \
                  '{"macAddress":"30-e5-72-6f-78-7' + str(count) + '"}],' \
                  '"nodeId":"' + node[0] + '",' \
                  '"nodeType":"compute",' \
                  '"serial":"' + node[1] + '","product":"R730 Base","vendor":""},' \
                  '"messageProperties":{"timestamp":"2017-06-27T08:5' + str(count) + ':32.437+0000"},"action":"discovered",' \
                  '"createdAt":"2017-06-27T08:5' + str(count) + ':31.871Z",' \
                  '"nodeId":"' + node[0] + '",' \
                  '"severity":"information","type":"node","typeId":"12345678901234567890977' + str(count) + '","version":"1.0"}'

            af_support_tools.rmq_publish_message(host='amqp', port=5671, ssl_enabled=True,
                                         exchange='exchange.dell.cpsd.adapter.rackhd.node.discovered.event',
                                         routing_key='',
                                         headers={'__TypeId__': 'com.dell.cpsd.component.events.Alert'},
                                         payload=the_payload)
            time.sleep(10)
            count += 1

    return None

#####################################################################

def check_findVCluster(data, setup):
    """ Check the vcluster as recommended by the ESS is a valid cluster
        Parameters : data - the preprocess status response message containing
                            the ESS recommended vcluster.
                     setup - test environment specifics
        Returns :  1 = success
                   0 = failure
    """

    global clustername

    actualvCenterClusterList = getRealVcenterInfo(setup)
    error_list = []

    if not data:
        return ""
    
    for node in  data['additionalProperties']['NodeDetails'] :
        clustername = node['clusterName']
        if clustername not in actualvCenterClusterList:
            error_list.append('Error :  Expected and Recieved VCluster Names do not match for the node %r : \
            expected %r    :     recieved %r ' % (node, actualvCenterClusterList, clustername))

    if error_list == []:
        print('-----------------------------------------------------')
        print(' VCenter Cluster check is good ')
        print(' Valid VCenter Cluster detected: ', actualvCenterClusterList)
        print('-----------------------------------------------------')
        return 1
    else:
        print('-----------------------------------------------------')
        print(' VCenter Cluster check fails ')
        print(' errorlist :', error_list)
        print('-----------------------------------------------------')
        return 0

################################################################################

def get_obj(content, vimtype, name=None):
    return [item for item in content.viewManager.CreateContainerView(
        content.rootFolder, [vimtype], recursive=True).view]

################################################################################

def getRealVcenterInfo(setup):
    """ Queries the customer vcenter and returns the names of the vclusters defined there
    Parameters : setup - test environment specifics
    Returns : a list of vcenter clusters"""

    # Disabling urllib3 ssl warnings
    requests.packages.urllib3.disable_warnings()

    # Disabling SSL certificate verification
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    context.verify_mode = ssl.CERT_NONE

    # connect this thing
    si = SmartConnect(
        host=setup['vcenter_IP_customer'],
        user=setup['vcenter_username'],
        pwd=setup['vcenter_password'],
        port='443',
        sslContext=context)

    # disconnect this thing
    atexit.register(Disconnect, si)

    content = si.RetrieveContent()

    clusterList = []

    for cluster_obj in get_obj(content, vim.ComputeResource):
        cluster = (cluster_obj.name)
        clusterList.append(cluster)

    return clusterList




#######################################################################################################################

def check_findProtectionDomain(data, setup):
    """ Check the protection domain as recommended by the ESS is valid at scaleIO or
        complies with the naming for proposed new PDs (ie. PD_ess-created-N, where N=0,1,2...)
        Parameters : data - the preprocess status response message containing
                            the ESS recommended PDs.
                     setup - test environment specifics
        Returns :  1 = success
                   0 = failure
    """

    global protectionDomain
    actualProtectionDomain = retrieveScaleIOProtectionDomain(setup)
    
    error_list = []
    pdList = []

    for node in data['additionalProperties']['NodeDetails']:
        # the recommended PD name should be either one already present in ScaleIO
        # or a new one of the from 'PD_ess-created-N'
        pdList.append(node['protectionDomainName'])
        if (node['protectionDomainName'] not in actualProtectionDomain) and \
                ('PD_ess-created' not in node['protectionDomainName']):
            error_list.append('Error : The Protection Domain name is invalid')

    if error_list == []:
        print('-----------------------------------------------------')
        print(' Protection Domain check is good ')
        print(" the protection domains selected are : ", pdList)
        print('-----------------------------------------------------')
        return 1
    else:
        print('-----------------------------------------------------')
        print(' Protection Domain check fails ')
        print(' errorlist', error_list)
        print('-----------------------------------------------------')
        return 0


#######################################################################################################################

def check__findScaleIO(data, setup):
    """ Check that storage pools are recommended by the ESS for each node
        Parameters : data - the preprocess status response message containing
                            the ESS recommended storage pools.
                     setup - test environment specifics
        Returns :  1 = success
                   0 = failure
    """
    global deviceToDeviceStoragePool

    actualStoragePool = retrieveScaleIOStoragePool(setup)
    scaleIO_storage_pool_list = []
    ess_storage_pool_list = []

    # Make a list of the storage pools retrieved from ScaleIO
    scaleioData_json = json.loads(actualStoragePool, encoding='utf-8')
    for l in scaleioData_json:
        scaleIO_storage_pool_list.append(l['name'])

    error_list = []

    # check the details for each node in the status response and verify that
    # each storage device is assigned to a current ScaleIO storage pool or that the ESS has proposed a new storage pool name

    for node in data['additionalProperties']['NodeDetails']:

        if node['deviceToDeviceStoragePool']:

        # The format of each storage device listed per node in NodeDetails|deviceToDeviceStoragePool is of the following form :
        #     "500003978c8b8f49": {
        #       "deviceId": "500003978c8b8f49",
        #       "serialNumber": "17u0a01wtf2e",
        #       "logicalName": "/dev/disk/by-id/wwn-0x500003978c8b8f49",
        #       "deviceName": "/dev/sdl scsi",
        #       "storagePoolName": "temp-1"
        #     },
        #
            for device in node['deviceToDeviceStoragePool']:
                if node['deviceToDeviceStoragePool'][device]['storagePoolName']:
                    # append the storage pool name to the list of ESS storage pools for debug purposes
                    node_spool = node['deviceToDeviceStoragePool'][device]['storagePoolName']
                    ess_storage_pool_list.append(node_spool)
                    
                    # check if the storage pool name in the status response is one of those names returned from Scaelio,
                    # OR, check that the name proposed by the ESS is of the form 'temp-N' where N is 1,2.... 
                    if (node_spool  not in scaleIO_storage_pool_list) and ('temp-' not in node_spool):
                       error_list.append('Error : Storage Pool naming error %r for node %r' % (node_spool, node['id']) )

            data_json = json.dumps(node['deviceToDeviceStoragePool'])

            if ('storagePoolName'  not in  data_json) and ( node['deviceToDeviceStoragePool'][device] != "null") :
               error_list.append('Error : No storage pool has been allocated to this node %r' % node['id'])
        else :
        # deviceToDeviceStoragePool is not present in NodeDetails
            error_list.append('Error : No storage pools are listed for node %r' % node['id'])

    if error_list == []:
        print('-----------------------------------------------------')
        print(' Storage Pool Check is good ')
        print(' The list of storage pools retrieved from ScaleIO is : ', scaleIO_storage_pool_list)
        print(' The list of ESS proposed pools is :', ess_storage_pool_list)
        print('-----------------------------------------------------')
        return 1
    else:
        print('-----------------------------------------------------')
        print(' Storage Pool Check fails ')
        print(' errorlist', error_list)
        print('-----------------------------------------------------')
        return 0


#######################################################################################################################

######## Supporting Functions for ScaleIO ##########

def retrieveScaleIoToken(setup):
    # grab a token
    url = "https://" + setup['scaleio_IP_gateway'] + "/api/login"
    header = {'Content-Type': 'application/json'}
    resp = requests.get(url, auth=(setup['scaleio_username'], setup['scaleio_password']), verify=False)
    token = resp.text
    token = token.strip('"')
    return token


def retrieveScaleIOProtectionDomain(setup):
    url = "https://" + setup['scaleio_IP_gateway'] + "/api/types/ProtectionDomain/instances"
    header = {'Content-Type': 'application/json'}
    resp = requests.get(url, auth=(setup['scaleio_username'], scaleIoToken), verify=False)
    return resp.text


def retrieveScaleIOStoragePool(setup):
    url = "https://" + setup['scaleio_IP_gateway'] + "/api/types/StoragePool/instances"
    header = {'Content-Type': 'application/json'}
    resp = requests.get(url, auth=(setup['scaleio_username'], scaleIoToken), verify=False)
    return resp.text

#####################################################################
# These are small functions called throughout the test.

def bindQueues(exchange, queue):
    af_support_tools.rmq_bind_queue(host='amqp', port=5671, ssl_enabled=True, routing_key='#', queue=queue,
                                    exchange=exchange)


def cleanup(queue):
    af_support_tools.rmq_delete_queue(host='amqp', port=5671, ssl_enabled=True, queue=queue)



