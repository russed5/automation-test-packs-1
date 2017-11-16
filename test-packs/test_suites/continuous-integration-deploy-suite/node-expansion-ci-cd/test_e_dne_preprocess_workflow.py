#!/usr/bin/python
# Author:
# Revision:
# Code Reviewed by:
# Description: This test should only be run once a day.
#
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information
#

import time
import sys
import af_support_tools
import pytest
import string
import requests
import json
import os
from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
import atexit
import argparse
import ssl


@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    import cpsd
    global cpsd

    # Set config ini file name
    global env_file
    env_file = 'env.ini'

    # ~~~~~~~~Test VM Details
    global ipaddress
    ipaddress = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')

    global cli_username
    cli_username = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                             property='username')

    global cli_password
    cli_password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                             property='password')

    #  ~~~~~~~~ Common API details
    global headers
    headers = {'Content-Type': 'application/json'}

    global protocol
    protocol = 'http://'

    global dne_port
    dne_port = ':8071'

    # Update setup_config.properties file at runtime  
    my_data_file = os.environ.get('AF_RESOURCES_PATH') + '/continuous-integration-deploy-suite/setup_config.properties'
    af_support_tools.set_config_file_property_by_data_file(my_data_file)

    # ~~~~~~~~ .ini file and header details
    global setup_config_file
    setup_config_file = 'continuous-integration-deploy-suite/setup_config.ini'

    global setup_config_header
    setup_config_header = 'config_details'

    # ~~~~~~~~RackHD Details
    global rackHD_IP
    rackHD_IP = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                          heading=setup_config_header,
                                                          property='rackhd_dne_ipaddress')

    global rackHD_username
    rackHD_username = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                heading=setup_config_header,
                                                                property='rackhd_username')

    global rackHD_password
    rackHD_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                heading=setup_config_header,
                                                                property='rackhd_password')

    global rackHD_cli_username
    rackHD_cli_username = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                    heading=setup_config_header,
                                                                    property='rackhd_cli_username')

    global rackHD_cli_password
    rackHD_cli_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                    heading=setup_config_header,
                                                                    property='rackhd_cli_password')

    # ~~~~~~~~Customer VCenter Details
    global vcenter_IP
    vcenter_IP = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                           heading=setup_config_header,
                                                           property='vcenter_dne_ipaddress_customer')

    global vcenter_username
    vcenter_username = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                 heading=setup_config_header,
                                                                 property='vcenter_username')

    global vcenter_password
    vcenter_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                 heading=setup_config_header,
                                                                 property='vcenter_password_fra')

    global vcenter_port
    vcenter_port = '443'

    # ~~~~~~~~ScaleIO Details
    global scaleio_IP
    scaleio_IP = af_support_tools.get_config_file_property(config_file=setup_config_file, heading=setup_config_header,
                                                           property='scaleio_integration_ipaddress')

    global scaleio_username
    scaleio_username = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                 heading=setup_config_header,
                                                                 property='scaleio_username')

    global scaleio_password
    scaleio_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                 heading=setup_config_header,
                                                                 property='scaleio_password')

    # ~~~~~~~~Test Node IP & Creds Details
    global testNodeMAC
    testNodeMAC = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                            heading=setup_config_header,
                                                            property='dne_test_node_mac')

    global idrac_ip_address
    idrac_ip_address = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                 heading=setup_config_header,
                                                                 property='idrac_ipaddress')

    global idrac_ip_address_alternative
    idrac_ip_address_alternative = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                             heading=setup_config_header,
                                                                             property='idrac_ipaddress_alternative')

    global idrac_ip_subnetmask
    idrac_ip_subnetmask = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                    heading=setup_config_header,
                                                                    property='idrac_ip_subnetmask')

    global idrac_ip_gateway
    idrac_ip_gateway = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                 heading=setup_config_header,
                                                                 property='idrac_ip_gateway')

    global idrac_username
    idrac_username = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                               heading=setup_config_header,
                                                               property='idrac_username')

    global idrac_common_password
    idrac_common_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                      heading=setup_config_header,
                                                                      property='idrac_common_password')

    global idrac_factory_password
    idrac_factory_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                       heading=setup_config_header,
                                                                       property='idrac_factory_password')

    global esxiManagementHostname
    esxiManagementHostname = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                       heading=setup_config_header,
                                                                       property='esxi_management_hostname')

    global esxiManagementIpAddress
    esxiManagementIpAddress = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                        heading=setup_config_header,
                                                                        property='esxi_management_ipaddress')

    global esxiManagementGatewayIpAddress
    esxiManagementGatewayIpAddress = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                               heading=setup_config_header,
                                                                               property='esxi_management_gateway_ipaddress')

    global esxiManagementSubnetMask
    esxiManagementSubnetMask = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                         heading=setup_config_header,
                                                                         property='esxi_management_subnet_mask')

    global vMotionManagementIpAddress
    vMotionManagementIpAddress = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                           heading=setup_config_header,
                                                                           property='vmotion_ip')

    global vMotionManagementSubnetMask
    vMotionManagementSubnetMask = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                            heading=setup_config_header,
                                                                            property='vmotion_mask')

    global scaleIoSvmManagementIpAddress
    scaleIoSvmManagementIpAddress = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                              heading=setup_config_header,
                                                                              property='scaleio_vm_ip')

    global scaleIoSvmManagementSubnetMask
    scaleIoSvmManagementSubnetMask = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                               heading=setup_config_header,
                                                                               property='scaleio_vm_mask')

    global scaleIoSvmManagementGatewayAddress
    scaleIoSvmManagementGatewayAddress = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                                   heading=setup_config_header,
                                                                                   property='scaleio_vm_gateway')

    global scaleIoData1SvmIpAddress
    scaleIoData1SvmIpAddress = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                         heading=setup_config_header,
                                                                         property='data1_svm_ip')

    global scaleIoSvmData1SubnetMask
    scaleIoSvmData1SubnetMask = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                          heading=setup_config_header,
                                                                          property='data1_svm_kernal_mask')

    global scaleIoData2SvmIpAddress
    scaleIoData2SvmIpAddress = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                         heading=setup_config_header,
                                                                         property='data2_svm_ip')

    global scaleIoSvmData2SubnetMask
    scaleIoSvmData2SubnetMask = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                          heading=setup_config_header,
                                                                          property='data2_svm_kernal_mask')

    global symphonyUuid
    global clustername
    global protectionDomain
    global deviceToDeviceStoragePool

    global serviceName
    serviceName = 'dell-wsman-obm-service'

    ####################

    global Alpha_Node
    Alpha_Node = {'Node_IP': '' + idrac_ip_address + '',
                  'Node_User': '' + idrac_username + '',
                  'Node_Pass': '' + idrac_factory_password + '',
                  'Node_GW': '' + idrac_ip_gateway + '',
                  'Node_Mask': '' + idrac_ip_subnetmask + ''}

    global Beta_Node
    Beta_Node = {'Node_IP': '' + idrac_ip_address_alternative + '',
                 'Node_User': '' + idrac_username + '',
                 'Node_Pass': '' + idrac_factory_password + '',
                 'Node_GW': '' + idrac_ip_gateway + '',
                 'Node_Mask': '' + idrac_ip_subnetmask + ''}


#######################################################################################
@pytest.mark.dne_paqx_parent_mvp_extended
def test_pre_test_verification():
    """
    Description     : This is a pre test check list. It:
                        1) Determines the correct IP to use
                        2) Notes the original boos settings
                        3) Any other checks...

    Parameters      :       none
    Returns         :       None
    """
    ####################
    # There are 2 IP Addresses (alpha and beta) associated with the Test node.
    # Either of these may be the current IP Address of the node
    # Is alpha_node alive ? if so, set it to be the current_node
    global Current_Node
    global New_Node

    response = os.system("ping -c 1 -w2 " + Alpha_Node['Node_IP'] + " > /dev/null 2>&1")

    if response == 0:  # node is alive
        Current_Node = Alpha_Node
        New_Node = Beta_Node
    else:
        Current_Node = Beta_Node
        New_Node = Alpha_Node

    print('\nNode Idrac IP details:')
    print(New_Node)

    # Get the ScaleIO Auth Token
    global scaleIoToken
    scaleIoToken = retrieveScaleIoToken()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Prepare the Request message body with valid details: IP, Gateway, Mask
    assert update_preprocess_params_json(), 'Error: Unable to update the POST message body'
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


@pytest.mark.dne_paqx_parent_mvp_extended
def test_preporcess_POST_workflow():
    """
    Title           :       Verify the POST function on /dne/preprocess API
    Description     :       Send a POST to /dne/preprocess where the body of the request is the typical DNE config
                            details body.
                            It will fail if :
                                The expected json response is not correct
    Parameters      :       none
    Returns         :       None
    Pre-requisites  :       The DNE-PAQX has already discovered a node and that it is booted into the micro-kernel
    """

    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print('\nSend POST /dne/nodes REST API call to provision an unallocated node...\n')
    global preprocess_workflow_id  # set this value as global as it will be used in the next test.

    endpoint = '/dne/preprocess'
    url_body = protocol + ipaddress + dne_port + endpoint

    # Get & Read the message body from the fixture
    filePath = os.environ[
                   'AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/payload_preprocess.json'
    with open(filePath) as fixture:
        request_body = json.loads(fixture.read())

    try:
        response = requests.post(url_body, json=request_body, headers=headers)
        assert response.status_code == 200, 'Error: Did not get a 200 on dne/nodes'
        data = response.json()

        preprocess_workflow_id = data['workflowId']
        print('WorkflowID: ', preprocess_workflow_id)

        error_list = []

        if data['workflow'] != 'preProcessWorkflow':
            error_list.append(data['workflow'])

        if data['status'] != 'SUBMITTED' and data['status'] != 'IN_PROGRESS':
            error_list.append(data['status'])

        if not data['workflowId']:
            error_list.append(data['workflowId'])

        assert not error_list, 'Error: missing fields from dne/preprocess response'

        print('Valid /dne/preprocess POST request has been sent')
        time.sleep(2)

    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err, '\n')
        raise Exception(err)


@pytest.mark.dne_paqx_parent_mvp_extended
def test_preprocess_GET_workflow_status():
    """
    Title           :       Verify the GET function on /dne/preprocess/<jobId> API
    Description     :       Send a GET to /dne/preprocess/<jobId>. The <jobId> value is the workFlowID obtained in the
                            previous test_preporcess_POST_workflow() test.
                            Each expected step in the workflow process will be checked.

                            This test will be updated as new steps are added to the workflow
                            It will fail if :
                                Any of the steps along the wat fail
    Parameters      :       none
    Returns         :       None
    """

    print("\n\nGET /dne/preprocess/<jobId> REST API call to get the nodes job status...\n")
    workflow_status = ''
    # preprocess_workflow_id = ''  # This is used for test purposes
    json_number = 0

    workflow_step1 = 'List ScaleIO components'
    workflow_step2 = 'List vCenter components'
    workflow_step3 = 'Discover ScaleIO'
    workflow_step4 = 'Discover vCenter'
    # workflow_step5 = 'Discover Rackhd Node Inventory'
    workflow_step6 = 'Configure server out of band IP address'
    workflow_step7 = 'Ping server out of band IP address'
    workflow_step8 = 'Configure out of band management settings'
    workflow_step9 = 'Configure server boot device and boot sequence'
    workflow_step10 = 'Find vCenter cluster'
    workflow_step11 = 'Find or create protection domain'
    workflow_step12 = 'Find or create valid storage pool'

    endpoint = '/dne/preprocess/'
    url_body = protocol + ipaddress + dne_port + endpoint + preprocess_workflow_id

    while workflow_status != 'SUCCEEDED':

        try:
            # Get the latest state of the workflow from the API
            data = get_latest_api_response(url_body)

            # If the process has failed immediately then fail the test outright
            assert data['status'] != 'FAILED', 'ERROR: The preprocess workflow overall status = Failed'

            data = get_latest_api_response(url_body)

            # List ScaleIO Components
            if data['workflowTasksResponseList'][json_number]['workFlowTaskName'] == workflow_step1:
                check_the_workflow_task(url_body, data, json_number, workflow_step1)
                json_number += 1

            data = get_latest_api_response(url_body)

            # List VCenter Components
            if data['workflowTasksResponseList'][json_number]['workFlowTaskName'] == workflow_step2:
                check_the_workflow_task(url_body, data, json_number, workflow_step2)
                json_number += 1

            data = get_latest_api_response(url_body)

            # Discover ScaleIO
            if data['workflowTasksResponseList'][json_number]['workFlowTaskName'] == workflow_step3:
                check_the_workflow_task(url_body, data, json_number, workflow_step3)
                json_number += 1

            data = get_latest_api_response(url_body)

            # Discover VCenter
            if data['workflowTasksResponseList'][json_number]['workFlowTaskName'] == workflow_step4:
                check_the_workflow_task(url_body, data, json_number, workflow_step4)
                json_number += 1

            # data = get_latest_api_response(url_body)
            #
            # # Discover Rackhd Node Inventory
            # if data['workflowTasksResponseList'][json_number]['workFlowTaskName'] == workflow_step5:
            #     check_the_workflow_task(url_body, data, json_number, workflow_step5)
            #     json_number += 1

            data = get_latest_api_response(url_body)

            # Configuring Out of Band Management
            if data['workflowTasksResponseList'][json_number]['workFlowTaskName'] == workflow_step6:
                check_the_workflow_task(url_body, data, json_number, workflow_step6)
                assert check_configIdrac(data, json_number, url_body), 'Check on ' + workflow_step6 + ' failed'
                json_number += 1

            data = get_latest_api_response(url_body)

            # Ping iDRAC IP Address
            if data['workflowTasksResponseList'][json_number]['workFlowTaskName'] == workflow_step7:
                check_the_workflow_task(url_body, data, json_number, workflow_step7)
                assert check_pingIdrac(), 'Check on ' + workflow_step7 + ' failed'
                json_number += 1

            data = get_latest_api_response(url_body)

            # Configuring Obm Settings
            if data['workflowTasksResponseList'][json_number]['workFlowTaskName'] == workflow_step8:
                check_the_workflow_task(url_body, data, json_number, workflow_step8)
                json_number += 1

            data = get_latest_api_response(url_body)

            # Configure Boot Device Idrac
            if data['workflowTasksResponseList'][json_number]['workFlowTaskName'] == workflow_step9:
                check_the_workflow_task(url_body, data, json_number, workflow_step9)
                assert check_configureBootDeviceIdrac(), 'Check on ' + workflow_step9 + ' failed'
                json_number += 1

            data = get_latest_api_response(url_body)

            # Find vcluster
            if data['workflowTasksResponseList'][json_number]['workFlowTaskName'] == workflow_step10:
                check_the_workflow_task(url_body, data, json_number, workflow_step10)
                assert check_findVCluster(data), 'Check on ' + workflow_step10 + ' failed'
                json_number += 1

            data = get_latest_api_response(url_body)

            # Find Protection Domain
            if data['workflowTasksResponseList'][json_number]['workFlowTaskName'] == workflow_step11:
                check_the_workflow_task(url_body, data, json_number, workflow_step11)
                assert check_findProtectionDomain(data), 'Check on ' + workflow_step11 + ' failed'
                json_number += 1

            data = get_latest_api_response(url_body)

            # Find ScaleIO
            if data['workflowTasksResponseList'][json_number]['workFlowTaskName'] == workflow_step12:
                check_the_workflow_task(url_body, data, json_number, workflow_step12)
                assert check__findScaleIO(data), 'Check on ' + workflow_step12 + ' failed'
                json_number += 1

                print('\nPreprocess Workflow Completed Successfully')
            ######################### Done

            workflow_status = data['status']


        # Error check the response
        except Exception as err:
            # Return code error (e.g. 404, 501, ...)
            print(err)
            print('\n')
            raise Exception(err)

    time.sleep(5)
    createAddNodeMsgJson()


########################################################################################

# Run the api query
def get_latest_api_response(url_body):
    response = requests.get(url_body)
    assert response.status_code == 200, 'Error: Did not get a 200 response'
    data = response.text
    data = json.loads(data, encoding='utf-8')
    return data


# Update the json that will be used in the POST /dne?preprocess command with valid values
def update_preprocess_params_json():
    """
    Description:    This method will update the json file with the symphonyUuid & nodeId values. Others wil be added as needed
    Parameters:     None
    Returns:        0 or 1 (Boolean)
    """

    symphonyUuid = get_SymphonyUuid_of_discovered_node()

    filePath = os.environ[
                   'AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/payload_preprocess.json'

    if (os.path.isfile(filePath) == 0):
        return 0

    with open(filePath) as json_file:
        data = json.load(json_file)

    data['symphonyUuid'] = symphonyUuid

    data['idracIpAddress'] = New_Node['Node_IP']
    data['idracSubnetMask'] = New_Node['Node_Mask']
    data['idracGatewayIpAddress'] = New_Node['Node_GW']
    data['esxiManagementHostname'] = esxiManagementHostname
    data['esxiManagementIpAddress'] = esxiManagementIpAddress
    data['esxiManagementSubnetMask'] = esxiManagementSubnetMask
    data['esxiManagementGatewayIpAddress'] = esxiManagementGatewayIpAddress

    data['vMotionManagementIpAddress'] = vMotionManagementIpAddress
    data['vMotionManagementSubnetMask'] = vMotionManagementSubnetMask

    data['scaleIoSvmManagementIpAddress'] = scaleIoSvmManagementIpAddress
    data['scaleIoSvmManagementSubnetMask'] = scaleIoSvmManagementSubnetMask
    data['scaleIoSvmManagementGatewayAddress'] = scaleIoSvmManagementGatewayAddress

    data['scaleIoData1SvmIpAddress'] = scaleIoData1SvmIpAddress
    data['scaleIoSvmData1SubnetMask'] = scaleIoSvmData1SubnetMask
    data['scaleIoData2SvmIpAddress'] = scaleIoData2SvmIpAddress
    data['scaleIoSvmData2SubnetMask'] = scaleIoSvmData2SubnetMask

    with open(filePath, 'w') as outfile:
        json.dump(data, outfile)

    print('\nPreProcess POST message body:')
    print(data)

    return 1


# Create the json file that will be used in the addnode test
def createAddNodeMsgJson():
    """
    Description:    This method will update the json file with the symphonyUuid & nodeId values. Others wil be added as needed
    Parameters:     None
    Returns:        0 or 1 (Boolean)
    """

    symphonyUuid = get_SymphonyUuid_of_discovered_node()

    filePath = os.environ[
                   'AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/payload_addnode.json'

    if (os.path.isfile(filePath) == 0):
        return 0

    with open(filePath) as json_file:
        data = json.load(json_file)

    data['symphonyUuid'] = symphonyUuid

    data['idracIpAddress'] = New_Node['Node_IP']
    data['idracSubnetMask'] = New_Node['Node_Mask']
    data['idracGatewayIpAddress'] = New_Node['Node_GW']
    data['esxiManagementHostname'] = esxiManagementHostname
    data['esxiManagementIpAddress'] = esxiManagementIpAddress
    data['esxiManagementSubnetMask'] = esxiManagementSubnetMask
    data['esxiManagementGatewayIpAddress'] = esxiManagementGatewayIpAddress

    data['vMotionManagementIpAddress'] = vMotionManagementIpAddress
    data['vMotionManagementSubnetMask'] = vMotionManagementSubnetMask

    data['scaleIoSvmManagementIpAddress'] = scaleIoSvmManagementIpAddress
    data['scaleIoSvmManagementSubnetMask'] = scaleIoSvmManagementSubnetMask
    data['scaleIoSvmManagementGatewayAddress'] = scaleIoSvmManagementGatewayAddress

    data['scaleIoData1SvmIpAddress'] = scaleIoData1SvmIpAddress
    data['scaleIoSvmData1SubnetMask'] = scaleIoSvmData1SubnetMask
    data['scaleIoData2SvmIpAddress'] = scaleIoData2SvmIpAddress
    data['scaleIoSvmData2SubnetMask'] = scaleIoSvmData2SubnetMask

    data['clusterName'] = clustername
    data['protectionDomainId'] = protectionDomain
    data['deviceToDeviceStoragePool'] = deviceToDeviceStoragePool

    with open(filePath, 'w') as outfile:
        json.dump(data, outfile)

    print('\nAddNode POST message body:')
    print(data)

    return 1


######################
# This is the main response workflow test

def check_the_workflow_task(url_body, data, json_number, workflow_step):
    print('\n*******************************************************\n')
    if data['workflowTasksResponseList'][json_number]['workFlowTaskName'] == workflow_step:
        assert data['workflowTasksResponseList'][json_number][
                   'workFlowTaskStatus'] != 'FAILED', 'ERROR: Workflow Failed: "' + workflow_step

        print(workflow_step)
        timeout = 0
        while timeout < 601:

            # Get the latest state of the workflow from the API
            data = get_latest_api_response(url_body)

            if data['workflowTasksResponseList'][json_number]['workFlowTaskStatus'] == 'IN_PROGRESS':
                time.sleep(1)
                timeout += 1
                # If the task is still in progress wait and then refresh the API data

            if data['workflowTasksResponseList'][json_number]['workFlowTaskStatus'] == 'SUCCEEDED':
                print(workflow_step + ' successful. (Note: Task took', timeout, 'seconds to complete)')
                time.sleep(1)
                break

            if data['workflowTasksResponseList'][json_number]['workFlowTaskStatus'] == 'FAILED':
                print('(Note: Task took', timeout, 'seconds to fail)\n')
                print(data['workflowTasksResponseList'][json_number]['errors'])
                assert data['workflowTasksResponseList'][json_number][
                           'workFlowTaskStatus'] != 'FAILED', 'Error in Step 1: ' + workflow_step + ' failed'
                # If the task has failed then fail the entire test.


######################
# Functions to check the steps of the workflow actually did something ###########

# Check the new IP address is returned in the results
def check_configIdrac(data, json_num, url_body):
    time.sleep(3)
    data = get_latest_api_response(url_body)
    error_list = []
    if data['workflowTasksResponseList'][json_num]['workFlowTaskName'] == 'Configure server out of band IP address':
        if data['workflowTasksResponseList'][json_num]['results']['idracIpAddress'] != New_Node['Node_IP']:
            error_list.append('Error : The new IP has not been set correctly')

        if data['workflowTasksResponseList'][json_num]['results']['idracSubnetMask'] != New_Node['Node_Mask']:
            error_list.append('Error : The new IP Mask has not been set correctly')

        if data['workflowTasksResponseList'][json_num]['results']['idracGatewayIpAddress'] != New_Node['Node_GW']:
            error_list.append('Error : The new IP Gateway has not been set correctly')

    if error_list == []:
        print('IP credentials have been correctly configured')
        return 1
    else:
        return 0


# Check we can ping the new IP address
def check_pingIdrac():
    # Contact the new IP address and check the network settings
    error_list = []

    ipaddres = New_Node['Node_IP']

    sendCommand = 'ping ' + ipaddres + ' -c 2'

    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                         command=sendCommand, return_output=True)

    nonresponsive = '2 packets transmitted, 0 received, 100% packet loss,'

    if nonresponsive in my_return_status:
        error_list.append('Error : System not pining')
        return 0
    else:
        print('System is pinging')
        return 1


# Check the bios setting has changed.
def check_configureBootDeviceIdrac():
    # export the bios configuration again and check the DNE relevant attributes have been updated
    response = get_BIOS_settings(New_Node)
    assert response.status_code == 200, 'Error, '
    updated_HddSeq_value = get_exported_bios_setting('HddSeq')
    updated_BiosBootSeq_value = get_exported_bios_setting('BiosBootSeq')

    error_list = []

    if 'Disk.SATAEmbedded.D-1, NonRAID.Integrated.1-1' not in updated_HddSeq_value:
        error_list.append('Error : The new HddSeq value is not correct')

    if 'NIC.Integrated.1-1-1, HardDisk.List.1-1' not in updated_BiosBootSeq_value:
        error_list.append('Error : The new BiosBootSeq value is not correct')

    if error_list == []:
        print('Bios Settings are verified')
        return 1
    else:
        return 0


# Check the cluster retunred is retunred from source also
def check_findVCluster(data):
    global clustername

    actualvCenterClusterList = getRealVcenterInfo()

    error_list = []
    for step in data['workflowTasksResponseList']:
        if step['workFlowTaskName'] == 'Find vCenter cluster':
            if not step['results']['clusterName']:
                error_list.append('Error : No clusters detected')
            clustername = step['results']['clusterName']

            if clustername not in actualvCenterClusterList:
                error_list.append('Error : Cluster Names do not match')

    if error_list == []:
        print('Valid Center Cluster detected: ' + clustername)
        return 1
    else:
        return 0


# Check that the Protection Domain is returned
def check_findProtectionDomain(data):
    global protectionDomain
    actualProtectionDomain = retrieveScaleIOProtectionDomain(scaleIoToken)

    error_list = []
    for step in data['workflowTasksResponseList']:
        if step['workFlowTaskName'] == 'Find or create protection domain':
            if not step['results']['protectionDomainName']:
                error_list.append('Error : No Protection Domains detected')
            protectionDomain = step['results']['protectionDomainName']
            print(protectionDomain)
            if protectionDomain not in actualProtectionDomain:
                error_list.append('Error : Protection Domain Names do not match')

    if error_list == []:
        print('Valid Protection Domain detected: ' + protectionDomain)
        return 1
    else:
        return 0


# Check that ScaleIO data  is returned
def check__findScaleIO(data):
    global deviceToDeviceStoragePool

    actualStoragePool = retrieveScaleIOStoragePool(scaleIoToken)

    error_list = []
    for step in data['workflowTasksResponseList']:
        if step['workFlowTaskName'] == 'Find or create valid storage pool':
            if not ['deviceToStoragePoolMap']:
                error_list.append('Error : No storage pool detected')

            # This will be used to create the json later
            deviceToDeviceStoragePool = step['deviceToStoragePoolMap']

            # if storagePoolName not in actualStoragePool:

    if error_list == []:
        print('Valid Storage Pool detected')
        return 1
    else:
        return 0


######## Supporting Function to get the symphonyUuid of the discovered node ############

def get_SymphonyUuid_of_discovered_node():
    endpoint = '/dne/nodes'
    url_body = protocol + ipaddress + dne_port + endpoint
    response = requests.get(url_body)
    # verify the status_code
    assert response.status_code == 200, 'Error: Did not get a 200 on dne/nodes'
    data = response.json()

    # global symphonyUuid
    symphonyUuid = data[0]['symphonyUuid']

    return symphonyUuid


######## Supporting Functions to get Node Bios Details ##########

def get_BIOS_settings(Node):
    """ Query the RHD Swagger interface """

    url = 'http://' + rackHD_IP + ':46018/api/1.0/server/configuration/export'

    header = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    body = '{"componentNames": [""], \
                "fileName": "tempExport.xml", \
                "serverIP": "' + Node['Node_IP'] + '", \
                "serverPassword": "' + Node['Node_Pass'] + '", \
                "serverUsername": "' + Node['Node_User'] + '", \
                "shareAddress": "' + rackHD_IP + '", \
                "shareName": "/opt/dell/public/write", \
                "shareType": 0, \
                "shutdownType": 0}'

    try:
        response = requests.post(url, headers=header, data=body)
        response.raise_for_status()
        return response

    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err, '\n')
        raise Exception(err)


def get_exported_bios_setting(attribute):
    grepCommand = 'cat /opt/dell/public/write/tempExport.xml | grep ' + attribute

    returnedAttributeValue = af_support_tools.send_ssh_command(
        host=rackHD_IP,
        username=rackHD_cli_username,
        password=rackHD_cli_password,
        command=grepCommand,
        return_output=True)

    return returnedAttributeValue


######## Supporting Functions for Vcenter ##########

# These functions get the info direct from the specified vcenter
def get_obj(content, vimtype, name=None):
    return [item for item in content.viewManager.CreateContainerView(
        content.rootFolder, [vimtype], recursive=True).view]


def getRealVcenterInfo():
    # Disabling urllib3 ssl warnings
    requests.packages.urllib3.disable_warnings()

    # Disabling SSL certificate verification
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    context.verify_mode = ssl.CERT_NONE

    # connect this thing
    si = SmartConnect(
        host=vcenter_IP,
        user=vcenter_username,
        pwd=vcenter_password,
        port=vcenter_port,
        sslContext=context)

    # disconnect this thing
    atexit.register(Disconnect, si)

    content = si.RetrieveContent()

    clusterList = []

    for cluster_obj in get_obj(content, vim.ComputeResource):
        # cluster = {'name': (cluster_obj.name), 'numberOfHosts': (len(cluster_obj.host))}
        cluster = (cluster_obj.name)
        clusterList.append(cluster)

    return clusterList


######## Supporting Functions for ScaleIO ##########

def retrieveScaleIoToken():
    # grab a token
    url = 'https://' + scaleio_IP + '/api/login'
    header = {'Content-Type': 'application/json'}
    resp = requests.get(url, auth=(scaleio_username, scaleio_password), verify=False)
    scaleIoToken = resp.text
    scaleIoToken = scaleIoToken.strip('"')
    return scaleIoToken


def retrieveScaleIOProtectionDomain(scaleIoToken):
    url = 'https://' + scaleio_IP + '/api/types/ProtectionDomain/instances'
    header = {'Content-Type': 'application/json'}
    resp = requests.get(url, auth=(scaleio_username, scaleIoToken), verify=False)
    return resp.text


def retrieveScaleIOStoragePool(scaleIoToken):
    url = 'https://' + scaleio_IP + '/api/types/StoragePool/instances'
    header = {'Content-Type': 'application/json'}
    resp = requests.get(url, auth=(scaleio_username, scaleIoToken), verify=False)
    return resp.text


#####################################################################
# These are Negative Tests tests.
#####################################################################
@pytest.mark.skip(reason='Need to update with move to Multinode')
@pytest.mark.parametrize('endpoint', [('/dne/preprocess/')])
@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_GETjobid_using_invalid_jobid(endpoint):
    """
    Title           :       Verify the dne REST API handles invalid job-id's correctly
    Description     :       Send a GET to /dne/nodes/{job-Id} with an invalid job-id.
                            Send a GET to /dne/preprocess/{job-Id} with an invalid job-id.
                            It will fail if :
                                The returned error exposes  java NPE details
    Parameters      :       none
    Returns         :       None
    """

    print("\n======================= invalid jobId  Test Start =======================\n")

    # Step 1: Invoke a REST API call with invalid jobId .
    print("GET /dne/{nodes/preprocess}/{job-Id} REST API call with invalid jobId\n")

    filePath = os.environ[
                   'AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/payload_addnode.json'
    with open(filePath) as fixture:
        request_body = json.loads(fixture.read())

    try:
        invalid_job_id = "ab55bf0c-73b0-4a16-acc6-1ff36b6cf655"
        url_body = protocol + ipaddress + dne_port + endpoint + invalid_job_id
        print(url_body)

        response = requests.get(url_body, json=request_body, headers=headers)
        # verify the status_code
        assert response.status_code == 404 or response.status_code == 400, \
            'Error: Did not get a 400-series error on ' + endpoint + '{invalid-job-Id}'
        data = response.json()
        print(data)

        error_list = []

        if not data['error']:
            error_list.append(data['error'])

        if 'exception' in data:
            if 'java' in data['exception']:
                error_list.append('\"java\" text should not be displayed')

        if 'message' not in data:
            error_list.append(data['message'])
        else:
            if 'java' in data['message']:
                error_list.append('\"java\" text should not be displayed')

        if not data['path']:
            error_list.append(data['path'])
        else:
            if not invalid_job_id in data['path']:
                error_list.append('the invalid job id should be listed in the path field')

        assert not error_list, 'Error: Issue found with ' + endpoint + '{invalid-jobId} Response'


    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)

    print('\n======================= invalid jobId Test End=======================\n')

@pytest.mark.skip(reason='Need to update with move to Multinode')
@pytest.mark.parametrize('endpoint', [('/dne/preprocess/')])
@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_GETjobid_using_valid_but_incorrect_jobid(endpoint):
    """
    Title           :       Verify the dne REST API handles valid, but incorrect, job-id's correctly
    Description     :       Send a GET to /dne/nodes/{job-Id} with a preprocess job-id.
                            Send a GET to /dne/preprocess/{job-Id} with a nodes job-id.
                            It will fail if :
                                The returned error exposes  java NPE details
    Parameters      :       none
    Returns         :       None
    """

    print("\n======================= valid jobId but incorrect Test Start =======================\n")

    # Step 1: Invoke a REST API call with invalid jobId .
    print("GET /dne/{nodes/preprocess}/{job-Id} REST API call with an incorrect jobId\n")

    filePath = os.environ[
                   'AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/payload_addnode.json'
    with open(filePath) as fixture:
        request_body = json.loads(fixture.read())

    try:
        jobId = '14cf9e3f-b651-4e14-8f35-e0c012cb0e9c'

        url_body = protocol + ipaddress + dne_port + endpoint + jobId
        print(url_body)

        response = requests.get(url_body, json=request_body, headers=headers)
        # verify the status_code
        assert response.status_code == 400 or response.status_code == 404, \
            'Error: Did not get a 400-series error ' + endpoint + '{incorrect-job-Id}'
        data = response.json()
        print(data)

        error_list = []

        if not data['error']:
            error_list.append(data['error'])

        if 'exception' in data:
            if 'java' in data['exception']:
                error_list.append('\"java\" text should not be displayed')

        if 'message' not in data:
            error_list.append(data['message'])
        else:
            if 'java' in data['message']:
                error_list.append('\"java\" text should not be displayed')

        if not data['path']:
            error_list.append(data['path'])
        else:
            if not jobId in data['path']:
                error_list.append('the incorrect job id should be listed in the path field')

        assert not error_list, 'Error: Issue found with ' + endpoint + '{incorrect-jobId} Response'


    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)

    print('\n======================= valid jobId but incorrect Test End=======================\n')

@pytest.mark.skip(reason='Need to update with move to Multinode')
@pytest.mark.parametrize('endpoint', [('/dne/preprocess/step/')])
@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_POSTstepname_using_invalid_stepName(endpoint):
    """
    Title           :       Verify the dne REST API handles invalid step-names correctly
    Description     :       Send a POST to /dne/nodes/step/{stepName} with an invalid stepName
                            Send a POST to /dne/preprocess/step/{stepName} with an invalid stepName
                            It will fail if :
                                The returned error exposes  java NPE details
    Parameters      :       none
    Returns         :       None
    """

    print("\n======================= invalid stepname Test Start =======================\n")

    # Step 1: Invoke /dne/{preprocess,step}/{stepName} REST API call with invalid step name .
    print("POST /dne/../step/{step-id}} REST API call with invalid step name\n")

    filePath = os.environ[
                   'AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/payload_addnode.json'
    with open(filePath) as fixture:
        request_body = json.loads(fixture.read())

    try:
        invalid_step_name = "invalidStep"
        url_body = protocol + ipaddress + dne_port + endpoint + invalid_step_name
        print(url_body)

        response = requests.post(url_body, json=request_body, headers=headers)
        # verify the status_code
        assert response.status_code == 404 or response.status_code == 400, \
            'Error: Did not get a 400-series on ' + endpoint + '{invalid_step_name}'
        data = response.json()
        print(data)

        error_list = []

        if not data['error']:
            error_list.append(data['error'])

        if 'exception' in data:
            if 'java' in data['exception']:
                error_list.append('\"java\" text should not be displayed')

        if 'message' not in data:
            error_list.append(data['message'])
        else:
            if 'java' in data['message']:
                error_list.append('\"java\" text should not be displayed')

        if not data['path']:
            error_list.append(data['path'])
        else:
            if not invalid_step_name in data['path']:
                error_list.append('the invalid step name should be listed in the path field')

        assert not error_list, 'Error: Issue found with  ' + endpoint + '{invalid-step-name} Response'


    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)

    print('\n======================= invalid stepname Test End=======================\n')

    #####################################################################
