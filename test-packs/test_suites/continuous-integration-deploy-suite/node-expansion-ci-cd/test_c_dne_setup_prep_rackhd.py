# !/usr/bin/python
# Author:
# Revision:
# Code Reviewed by:
# Description:
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


##############################################################################################
@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    import cpsd
    global cpsd
    af_support_tools.rmq_get_server_side_certs(host_hostname=cpsd.props.base_hostname,
                                               host_username=cpsd.props.base_username,
                                               host_password=cpsd.props.base_password, host_port=22,
                                               rmq_certs_path=cpsd.props.rmq_cert_path)
    # Set config ini file name
    global env_file
    env_file = 'env.ini'

    # Test VM Details
    global ipaddress
    ipaddress = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')

    global cli_username
    cli_username = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                             property='username')

    global cli_password
    cli_password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                             property='password')

    # Update setup_config.ini file at runtime
    my_data_file = os.environ.get('AF_RESOURCES_PATH') + '/continuous-integration-deploy-suite/setup_config.properties'
    af_support_tools.set_config_file_property_by_data_file(my_data_file)

    # RackHD VM IP & Creds details
    global setup_config_file
    setup_config_file = 'continuous-integration-deploy-suite/setup_config.ini'

    global setup_config_header
    setup_config_header = 'config_details'

    global rackHD_IP
    rackHD_IP = af_support_tools.get_config_file_property(config_file=setup_config_file, heading=setup_config_header,
                                                          property='rackhd_dne_ipaddress')

    global rackHD_username
    rackHD_username = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                heading=setup_config_header, property='rackhd_username')

    global rackHD_password
    rackHD_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                heading=setup_config_header, property='rackhd_password')

    global testNodeMAC
    testNodeMAC = af_support_tools.get_config_file_property(config_file=setup_config_file, heading=setup_config_header,
                                                            property='dne_test_node_mac')

    global idrac_hostname_1
    idrac_hostname_1 = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                 heading=setup_config_header, property='idrac_ipaddress')

    global idrac_hostname_2
    idrac_hostname_2 = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                 heading=setup_config_header, property='idrac_ipaddress_alternative')


    global idrac_username
    idrac_username = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                               heading=setup_config_header, property='idrac_username')

    global idrac_factory_password
    idrac_factory_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                       heading=setup_config_header,
                                                                       property='idrac_factory_password')

    # Common API details
    global headers
    headers = {'Content-Type': 'application/json'}

    global protocol
    protocol = 'http://'

    global dne_port
    dne_port = ':8071'

    global rackhd_port
    rackhd_port = ':32080'

    global rackhd_smi_port
    rackhd_smi_port = ':46018'



#####################################################################
# These is the main script.
#####################################################################

@pytest.mark.dne_paqx_parent_mvp_extended
def test_0_prep():

    global token
    token = retrieveRHDToken()  # Get the RackHD Authentication Token

    global testNodeIdentifier
    testNodeIdentifier = getNodeIdentifier(token, testNodeMAC)  # Get the "id" value for the Node

    global idrac_hostname
    idrac_hostname = getCurrentNodeIP()

    print ('\nActive IP = ' + idrac_hostname)

    deleteExistingNodesObms(token, testNodeIdentifier)

    createRebootWorkflowTask(token)
    time.sleep(2)
    createPxeRebootWorkflow(token)
    time.sleep(2)


@pytest.mark.dne_paqx_parent_mvp_extended
def test_1_enable_pxe_boot():

    assert enablePxeBoot(), 'Failed to enable pxe boot'


@pytest.mark.dne_paqx_parent_mvp_extended
def test_2_reload_node_from_rackHD():

    ###################
    # This is where we need to send a workflow to reboot the node in PXE boot.
    #
    print ('\nThe node id: ', testNodeIdentifier)
    obmsId = putObms(token, testNodeIdentifier)  # Call method to register Obms service to the node

    print("obmsId = ", obmsId)
    assert getObms(token, testNodeIdentifier,
                   obmsId), 'test failed,obms service not registered to the node'  # Call method to get the Obms service to the node

    time.sleep(10)
    graphId = postWorkflow(token, testNodeIdentifier)  # Call method to post workflow

    print("graphId =", graphId)

    status = getWorkflow(token, testNodeIdentifier, graphId)

    if status == 0:
        print ('Node deleted but status is Failed')

    if status == 1:
        print ('Node deleted')
    assert getWorkflow(token, testNodeIdentifier,
                       graphId), 'test failed, set pxe boot and reload didnt work as expected'  # Call method to get workflow


@pytest.mark.dne_paqx_parent_mvp_extended
def test_3_delete_node_from_rackHD():
    # ###################
    # While the node is rebooting we need to remove it from RackHD
    print ('\nAttempting to delete node: ' + testNodeIdentifier)
    delete_node_response = deleteNodes(token, testNodeIdentifier)  # Call method to delete the node

    # A successfully deleted node returns no response body
    if delete_node_response == '':
        print ('Node deleted')

    # If an active RackHD workflow is running on the node we need to cancel it
    if 'active workflow is running' in delete_node_response:
        print ('Active Workflow need to be stopped...')
        cancelWorkflow(token, testNodeIdentifier)  # Call the method to cancel any workflows.

        print ('2nd attempt to delete node: ' + testNodeIdentifier)
        delete_node_response = deleteNodes(token, testNodeIdentifier)  # Try again to delete the node

        if delete_node_response == '':
            print ('Node deleted')

    print('Node ' + testNodeMAC + ' has been successfully deleted')


@pytest.mark.dne_paqx_parent_mvp_extended
def test_4_discover_node_in_rackHD():
    ###################
    # Now that the node has been deleted and rebooted we need to verify it has been rediscovered by RackHD
    # It typically appears in RackHD in a 2-3 minutes

    print('\nWaiting for rediscovery...')

    timeout = 0
    while timeout < 180:
        response = getListNodes(token, testNodeMAC)

        if testNodeMAC in response:
            print('Node has been rediscoverd')
            break

        else:
            timeout = +1
            time.sleep(1)
            if timeout > 179:
                assert False, 'Error: Node not rediscovered'


@pytest.mark.dne_paqx_parent_mvp_extended
def test_5_discover_node_in_symphony():
    ###################
    # Next we need to check that the node is in GET /dne/nodes or Symphoyony.
    # It typically takes approx 8 minutes for the node discovered message to be sent.

    print('\nSend GET /dne/nodes REST API call to verify the discovered node in Symphony\n')

    timeout = 0
    while timeout < 1000:
        endpoint = '/dne/nodes'
        url_body = protocol + ipaddress + dne_port + endpoint
        response = requests.get(url_body)
        assert response.status_code == 200, 'Error: Did not get a 200 on dne/nodes'
        data = response.json()

        if data == []:  # If the response is empty the new node still hasn't been discovered
            response = requests.get(url_body)
            data = response.json()
            timeout += 1
            time.sleep(1)
            if timeout > 999:
                assert False, 'Error: Node not rediscovered'

        if data != []:  # If the response is not empty the node has been discovered
            try:
                assert data[0]['nodeStatus'] == 'DISCOVERED', 'Error: Node not in a discovered state'
                print('Node is ready to be used.')
                time.sleep(1)
                break

            # Error check the response
            except Exception as err:
                # Return code error (e.g. 404, 501, ...)
                print(err)
                print('\n')
                raise Exception(err)


#####################################################################
#There are used by 0_prep
def getCurrentNodeIP():
    ####################
    # There are 2 IP Addresses associated with the Test node.
    # Either of these may be the current IP Address of the node
    # This determines which is the live one.

    response = os.system("ping -c 1 -w2 " + idrac_hostname_1 + " > /dev/null 2>&1")

    if response == 0:  # node is alive
        idrac_hostname = idrac_hostname_1

    else:
        idrac_hostname = idrac_hostname_2

    print((idrac_hostname))
    return idrac_hostname


def retrieveRHDToken():
    # grab a token
    url = "http://" + rackHD_IP + rackhd_port + "/login"
    header = {'Content-Type': 'application/json'}
    body = '{"username": "' + rackHD_username + '", "password": "' + rackHD_password + '"}'
    resp = requests.post(url, headers=header, data=body)
    tokenJson = json.loads(resp.text, encoding='utf-8')
    token = tokenJson["token"]
    return token


def getNodeIdentifier(token, testNodeMAC):
    # Get the node Identifier value

    apipath = '/api/2.0/nodes/'
    url = 'http://' + rackHD_IP + rackhd_port + apipath
    headerstring = {"Content-Type": "application/json", "Authorization": "JWT " + token}
    response = requests.get(url, headers=headerstring)
    data_text = response.text
    data_json = json.loads(response.text, encoding='utf-8')
    assert testNodeMAC in data_text, 'Error: Node not in Rackhd'
    for nodes in data_json:
        if testNodeMAC in nodes['identifiers']:
            testNodeIdentifier = nodes['id']
            return testNodeIdentifier


def deleteExistingNodesObms(token, testNodeIdentifier):

    apipath = '/api/2.0/nodes/' + testNodeIdentifier
    url = 'http://' + rackHD_IP + rackhd_port + apipath
    headerstring = {"Content-Type": "application/json", "Authorization": "JWT " + token}
    response = requests.get(url, headers=headerstring)
    data_text = response.text
    data_json = json.loads(response.text, encoding='utf-8')

    for item in data_json['obms']:
        obmid = item['ref']

        apipath = obmid
        url = 'http://' + rackHD_IP + rackhd_port + apipath
        headerstring = {"Content-Type": "application/json", "Authorization": "JWT " + token}
        response = requests.delete(url, headers=headerstring)
        assert response.status_code == 204, 'Error: Did not get a 204 response'


def createRebootWorkflowTask(token):
    apipath = '/api/2.0/workflows/tasks'
    url = 'http://' + rackHD_IP + rackhd_port + apipath
    headerstring = {"Content-Type": "application/json", "Authorization": "JWT " + token}
    body = '{"friendlyName":"RebootStart","implementsTask":"Task.Base.Obm.Node","injectableName":"Task.Obm.Node.Reboot","options":{"action":"reboot"},"properties":{}}'
    response = requests.put(url, headers=headerstring, data=body)
    data = response.text
    #assert response.status_code == 201
    print (data)


def createPxeRebootWorkflow(token):
    apipath = '/api/2.0/workflows/graphs'
    url = 'http://' + rackHD_IP + rackhd_port + apipath
    headerstring = {"Content-Type": "application/json", "Authorization": "JWT " + token}
    #body = '{"friendlyName":"Set Pxe and Reboot Node","injectableName":"Graph.SetPxeAndReboot","options":{},"tasks":[{"label":"set-boot-pxe","taskName":"Task.Obm.Node.PxeBoot","ignoreFailure":true},{"label":"reboot-start","taskName":"Task.Obm.Node.Reboot","waitOn":{"set-boot-pxe":"finished"}}]}'
    body = '{"friendlyName":"Set Pxe and Reboot Node","injectableName":"Graph.SetPxeAndReboot","options":{},"tasks":[{"label":"set-boot-pxe","taskName":"Task.Obm.Node.PxeBoot","ignoreFailure":true},{"label":"reboot","waitOn":{"set-boot-pxe":"finished"},"taskName":"Task.Obm.Node.Reboot"}]}'
    response = requests.put(url, headers=headerstring, data=body)
    data = response.text
    #assert response.status_code == 201
    print (data)


#####################################################################
# This is used by 1_enable_pxe
# Enable PXE Boot on the server - is disabled during /addnode workflow

def enablePxeBoot():
    msgbody = '{"componentNames":[""],"fileName":"fne-pre-os-config.xml","serverIP":"'+idrac_hostname+'","serverPassword":"'+idrac_factory_password+'","serverUsername":"'+idrac_username+'","shareAddress":"'+rackHD_IP+'","shareName":"/opt/dell/public","sharePassword":"'+cli_password+'","shareType":0,"shareUsername":"'+cli_username+'","shutdownType":1}'

    print(idrac_hostname)
    print(msgbody)

    apipath = '/api/1.0/server/configuration/import/'
    url = 'http://' + rackHD_IP + rackhd_smi_port + apipath
    response = requests.post(url, data=msgbody, headers=headers)
    status = response.status_code

    print (response.text)

    response_json = json.loads(response.text, encoding='utf-8')
    if response_json['xmlConfig']['message'] != 'No configuration changes requiring a system restart need to be applied.':

        time.sleep(200) # need to wait till system has fully rebooted

    if (status != 200):
        print ("test failed")
        return 0
    else:
        return 1


#####################################################################
# These are used by 2_reload_node
#Tasks needed to reboot the node

def putObms(token, testNodeIdentifier):
    """
    Description:    This method will enable ipmi-obm-service on the node id
    Parameters:     1. token     - Name of the token for Rackhd (STRING)
                    2. testNodeIdentifier          - Id of the Idrac Node (STRING)
    Returns:        obms_id (STRING)
    """
    apipath = '/api/2.0/obms/'
    url = 'http://' + rackHD_IP + rackhd_port + apipath
    headerstring = {"Content-Type": "application/json", "Authorization": "JWT " + token}
    body = '{"nodeId": "' + testNodeIdentifier + '","service": "ipmi-obm-service","config": {"host": "' + idrac_hostname + '" ,"user": "' + idrac_username + '","password": "' + idrac_factory_password + '"}}'
    print ('putObms body =', body)
    response = requests.put(url, headers=headerstring, data=body)
    data = response.text
    data_json = json.loads(response.text, encoding='utf-8')
    obms_id = data_json['id']
    return obms_id


def getObms(token, testNodeIdentifier, obms_id):
    """
    Description:    This method will get the status of  ipmi-obm-service on the node id
    Parameters:     1. token     - Name of the token for Rackhd (STRING)
                    2. testNodeIdentifier          - Id of the Idrac Node (STRING)
                    3. obms_id        - OBMS ID (STRING)
    Returns:        0 or 1 (Boolean)
    """
    apipath = '/api/2.0/obms/' + obms_id
    url = 'http://' + rackHD_IP + rackhd_port + apipath
    headerstring = {"Content-Type": "application/json", "Authorization": "JWT " + token}
    response = requests.get(url, headers=headerstring)
    data_text = response.text
    data_json = json.loads(response.text, encoding='utf-8')
    if (testNodeIdentifier not in data_text):
        print ("test failed")
        return 0
    else:
        return 1


def postWorkflow(token, testNodeIdentifier):
    """
    Description:    This method will post the workflow with the given graph_name on the node id
    Parameters:     1. token     - Name of the token for Rackhd (STRING)
                    2. testNodeIdentifier          - Id of the Idrac Node (STRING)
    Returns:        graphID (STRING)
    """
    apipath = '/api/2.0/nodes/' + testNodeIdentifier + '/workflows/'
    url = 'http://' + rackHD_IP + rackhd_port + apipath
    headerstring = {"Content-Type": "application/json", "Authorization": "JWT " + token}
    body = '{ "name": "Graph.SetPxeAndReboot", "options": { "defaults": { "graphOptions": {}}}}'
    resp = requests.post(url, headers=headerstring, data=body)
    data = resp.text
    data_json = json.loads(resp.text, encoding='utf-8')
    graphID = data_json['logContext']['graphInstance']
    print ("graphID =", graphID)
    return graphID


def getWorkflow(token, testNodeIdentifier, graphID):
    """
    Description:    This method will get the workflow with the given graph_id and Validate
    Parameters:     1. token                - Name of the token for Rackhd (STRING)
                    2. testNodeIdentifier   - Id of the Idrac Node (STRING)
                    3. graphID              - ID of the graph  (STRING)
    Returns:        0 or 1 (Boolean)
    """
    time.sleep(60)
    apipath = '/api/2.0/nodes/' + testNodeIdentifier + '/workflows/'
    # apipath = '/api/2.0/nodes/workflows/'
    url = 'http://' + rackHD_IP + rackhd_port + apipath
    headerstring = {"Content-Type": "application/json", "Authorization": "JWT " + token}
    response = requests.get(url, headers=headerstring)
    data_text = response.text
    data_json = json.loads(response.text, encoding='utf-8')

    for item in data_json:
        if (item['definition']['friendlyName'] == 'Set Pxe and Reboot Node'):

            if (item['_status'] == 'succeeded'):
                print ('_status', item['_status'])
            if (item['_status'] != 'succeeded'):
                print ("failed")
                return 0
            else:
                return 1

#####################################################################
# These are used by 3_delete_node

def deleteNodes(token, testNodeIdentifier):
    apipath = '/api/2.0/nodes/'
    url = 'http://' + rackHD_IP + rackhd_port + apipath + testNodeIdentifier
    headerstring = {"Content-Type": "application/json", "Authorization": "JWT " + token}
    response = requests.delete(url, headers=headerstring)
    data = response.text
    return data


def cancelWorkflow(token, testNodeIdentifier):
    print ('Attempting to cancel workflow')
    attempt = 1

    while attempt < 5:

        apipath = '/api/2.0/nodes/'
        url = 'http://' + rackHD_IP + rackhd_port + apipath + testNodeIdentifier + '/workflows/action'
        headerstring = {"Content-Type": "application/json", "Authorization": "JWT " + token}
        body = '{"command": "cancel"}'
        response = requests.put(url, headers=headerstring, data=body)
        data = response.text
        print (data)

        if 'No active workflow graph found for node' in data:
            attempt = 5

        attempt += 1

#####################################################################
# This is used by 4_discover_node

def getListNodes(token, testNodeMAC):
    # Get a list of the nodes
    apipath = '/api/2.0/nodes/'
    url = 'http://' + rackHD_IP + rackhd_port + apipath
    headerstring = {"Content-Type": "application/json", "Authorization": "JWT " + token}
    response = requests.get(url, headers=headerstring)
    data_text = response.text
    data_json = json.loads(response.text, encoding='utf-8')
    return (data_text)


######################################################################################################################
