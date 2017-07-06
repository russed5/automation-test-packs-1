#!/usr/bin/python
#
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information
#

import af_support_tools
import json
import os
import pytest
import requests
import time


@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    import cpsd
    global cpsd

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

    # Common API details
    global headers
    headers = {'Content-Type': 'application/json'}

    global protocol
    protocol = 'http://'

    global dne_port
    dne_port = ':8071'


#####################################################################
# These are the main tests.
#####################################################################
@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_preprocess_request_workflows():
    """
    Title           :       Verify the POST function on /dne/preprocess API
    Description     :       Send a POST to /dne/preprocess where the body of the request is the typical DNE config
                            details body.
                            It will fail if :
                                The expected json response is not correct
    Parameters      :       none
    Returns         :       None
    """

    print("\n=======================Preprocess Work Flow Test Start=======================\n")

    # Step 1: Invoke /dne/preprocess REST API call to gather the info that will be needed for add node.
    print("POST /dne/preprocess REST API call to gather the info that will be needed for add node...\n")

    global preprocess_workflow_id  # set this value as global as it will be used in the next test.

    filePath = os.environ[
                   'AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/payload_addnode.json'
    with open(filePath) as fixture:
        request_body = json.loads(fixture.read())

    try:
        endpoint = '/dne/preprocess'
        url_body = protocol + ipaddress + dne_port + endpoint
        response = requests.post(url_body, json=request_body, headers=headers)
        # verify the status_code
        assert response.status_code == 200, 'Error: Did not get a 200 on dne/preprocess'
        data = response.json()

        preprocess_workflow_id = data['workflowId']

        error_list = []

        if data['workflow'] != 'preProcessWorkflow':
            error_list.append(data['workflow'])

        if data['status'] != 'SUBMITTED' and data['status'] != 'IN_PROGRESS':
            error_list.append(data['status'])

        if not data['workflowId']:
            error_list.append('workflowID')

        assert not error_list, 'Error: missing fields from /dne/preprocess response'

        for link in data['links']:
            if link['rel'] is 'self':
                assert link[
                           'href'] == "/nodes/" + preprocess_workflow_id + "/startPreProcessWorkflow", 'Error: Invalid href in dne/preprocess response'

        print('Valid /dne/preprocess request sent')
        time.sleep(2)

    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)


@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_preprocess_status_workflow():
    """
    Title           :       Verify the GET function on /dne/preprocess/<jobId> API
    Description     :       Send a GET to /dne/preprocess/<jobId>. The <jobId> value is the workFlowID obtained in the
                            previous test_preprocess_request_workflows() test.
                            It will fail if :
                                The expected json response is not correct
    Parameters      :       none
    Returns         :       None
    """
    # Step 2: Invoke /dne/preprocess/{jobId} REST API call to get the status
    print("\n\nGET /dne/preprocess/<jobId> REST API call to get the preprocess job status...\n")

    try:
        endpoint = '/dne/preprocess/'
        url_body = protocol + ipaddress + dne_port + endpoint + preprocess_workflow_id
        response = requests.get(url_body)
        # verify the status_code
        assert response.status_code == 200, 'Error: 200 not returned from dne\preprocess'
        data = response.json()

        error_list = []

        if data['workflowId'] != preprocess_workflow_id:
            error_list.append(data['workflowId'])

        if not data['workflow']:
            error_list.append(data['workflow'])

        if not data['status']:
            error_list.append(data['status'])

        if not data['workflowTasksResponseList']:
            error_list.append(data['workflowTasksResponseList'])

        if not data['links']:
            error_list.append(data['links'])

        assert not error_list, 'Error: Not all tasks returned in /dne/preprocess'
        # Note: we are not asserting on the contents of "workflowTasksResponseList": [] as this is changeable.

        print('Valid /dne/preprocess/{jobId} status returned')

    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)


@pytest.mark.parametrize('stepName', [('findAvailableNodes'), ('configIdrac'), ('findVCluster')])
@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_preprocess_step_workflow(stepName):
    """
    Title           :       Verify the POST function on /dne/preprocess/step/{stepName} API
    Description     :       Send a POST to /dne/preprocess/step/{stepName}. The 3 {stepName} values are "findAvailableNodes"
                            "configIdrac" & "findVCluster"
                            It will fail if :
                                The expected json response is not correct
    Parameters      :       none
    Returns         :       None
    """

    # Step 3: Invoke /dne/preprocess/step/{stepName} REST API call to get the status
    print("\n\nPOST /dne/preprocess/step/{stepName} REST API call to get the step status...\n")

    filePath = os.environ[
                   'AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/payload_addnode.json'
    with open(filePath) as fixture:
        request_body = json.loads(fixture.read())

    try:
        endpoint = '/dne/preprocess/step/'
        url_body = protocol + ipaddress + dne_port + endpoint + stepName

        print (url_body)
        response = requests.post(url_body, json=request_body, headers=headers)
        # verify the status_code
        assert response.status_code == 200, 'Error: 200 not returned from dne\preprocess'
        data = response.json()

        error_list = []

        if not data['correlationId']:
            error_list.append(data['correlationId'])

        if not data['workflowId']:
            error_list.append(data['workflowId'])

        if not data['workflow']:
            error_list.append(data['workflow'])

        if not data['status']:
            error_list.append(data['status'])

        if not data['links']:
            error_list.append(data['links'])

        assert not error_list, 'Error: Not all tasks returned in /dne/preprocess'
        # Note: we are not asserting on the contents of "workflowTasksResponseList": [] as this is changeable.

        print('Valid /dne/preprocess/step' + stepName + ' status returned')

    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)


#####################################################################


@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_nodes_GET_workflows():
    """
    Title           :       Verify the GET function on /dne/nodes API
    Description     :       Send a GET to /dne/nodes details body.
                            We are not asserting on the content of the response as this is variable.
                            It will fail if :
                                The expected json response is not correct
    Parameters      :       none
    Returns         :       None
    """

    print('\n=======================Add Node Work Flow Test Begin=======================\n')

    # Invoke /dne/nodes REST API call to gather the info that will be needed for add node.
    print('GET /dne/nodes REST API call to get the discovered node and it\'s uuid...\n')

    try:
        endpoint = '/dne/nodes'
        url_body = protocol + ipaddress + dne_port + endpoint
        response = requests.get(url_body)
        # verify the status_code
        assert response.status_code == 200, 'Error: Did not get a 200 on dne/nodes'
        data = response.json()

        print('Valid /dne/nodes GET sent')
        time.sleep(1)

    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)


@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_nodes_request_workflows():
    """
    Title           :       Verify the POST function on /dne/nodes API
    Description     :       Send a POST to /dne/nodes where the body of the request is the typical DNE config
                            details body.
                            It will fail if :
                                The expected json response is not correct
    Parameters      :       none
    Returns         :       None
    """

    # Invoke POST /dne/nodes REST API
    print('POST /dne/nodes REST API call to provision an unallocated node...\n')

    global nodes_workflow_id  # set this value as global as it will be used in the next test.

    filePath = os.environ[
                   'AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/payload_addnode.json'
    with open(filePath) as fixture:
        request_body = json.loads(fixture.read())

    try:
        endpoint = '/dne/nodes'
        url_body = protocol + ipaddress + dne_port + endpoint
        response = requests.post(url_body, json=request_body, headers=headers)
        # verify the status_code
        assert response.status_code == 200, 'Error: Did not get a 200 on dne/nodes'
        data = response.json()

        nodes_workflow_id = data['workflowId']

        error_list = []

        if data['workflow'] != 'addNode':
            error_list.append(data['workflow'])

        if data['status'] != 'SUBMITTED' and data['status'] != 'IN_PROGRESS':
            error_list.append(data['status'])

        if not data['workflowId']:
            error_list.append(data['workflowId'])

        assert not error_list, 'Error: missing fields from dne/nodes response'

        for link in data['links']:
            if link['rel'] is 'self':
                assert link[
                           'href'] == "/nodes/" + nodes_workflow_id + "/startAddNodeWorkflow", 'Error: Invalid href in dne/nodes response'

        print('Valid /dne/nodes request sent')
        time.sleep(2)

    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)


@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_nodes_status_workflow():
    """
    Title           :       Verify the GET function on /dne/nodes/<jobId> API
    Description     :       Send a GET to /dne/nodes/<jobId>. The <jobId> value is the workFlowID obtained in the
                            previous test_nodes_request_workflows() test.
                            It will fail if :
                                The expected json response is not correct
    Parameters      :       none
    Returns         :       None
    """
    # Step 2: Invoke /dne/nodes/{jobId} REST API call to get the status
    print("\n\nGET /dne/nodes/<jobId> REST API call to get the nodes job status...\n")

    try:
        endpoint = '/dne/nodes/'
        url_body = protocol + ipaddress + dne_port + endpoint + nodes_workflow_id
        response = requests.get(url_body)
        # verify the status_code
        assert response.status_code == 200, 'Error: 200 not returned from dne\\nodes'
        data = response.json()

        error_list = []

        if data['workflowId'] != nodes_workflow_id:
            error_list.append(data['workflowId'])

        if not data['workflow']:
            error_list.append(data['workflow'])

        if not data['status']:
            error_list.append(data['status'])

        if not data['workflowTasksResponseList']:
            error_list.append(data['workflowTasksResponseList'])

        if not data['links']:
            error_list.append(data['links'])

        assert not error_list, 'Error: Not all tasks returned in /dne/nodes'
        # Note: we are not asserting on the contents of "workflowTasksResponseList": [] as this is changeable.

        print('Valid /dne/nodes/{jobId} status returned')

    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)


@pytest.mark.parametrize('stepName', [('findAvailableNodes')])
@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_nodes_step_workflow(stepName):
    """
    Title           :       Verify the POST function on /dne/nodes/step/{stepName} API
    Description     :       Send a POST to /dne/nodes/step/{stepName}. The 3 {stepName} values are "findAvailableNodes"
                            & "configIdrac"
                            It will fail if :
                                The expected json response is not correct
    Parameters      :       none
    Returns         :       None
    """

    # Step 3: Invoke /dne/nodes/step/{stepName} REST API call to get the status
    print("\n\nPOST /dne/nodes/step/{stepName} REST API call to get the step status...\n")

    filePath = os.environ[
                   'AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/payload_addnode.json'
    with open(filePath) as fixture:
        request_body = json.loads(fixture.read())

    try:
        endpoint = '/dne/nodes/step/'
        url_body = protocol + ipaddress + dne_port + endpoint + stepName

        print (url_body)
        response = requests.post(url_body, json=request_body, headers=headers)
        # verify the status_code
        assert response.status_code == 200, 'Error: 200 not returned from dne\\nodes'
        data = response.json()

        error_list = []

        if not data['correlationId']:
            error_list.append(data['correlationId'])

        if not data['workflowId']:
            error_list.append(data['workflowId'])

        if not data['workflow']:
            error_list.append(data['workflow'])

        if not data['status']:
            error_list.append(data['status'])

        if not data['links']:
            error_list.append(data['links'])

        assert not error_list, 'Error: Not all tasks returned in /dne/nodes'
        # Note: we are not asserting on the contents of "workflowTasksResponseList": [] as this is changeable.

        print('Valid /dne/nodes/step' + stepName + ' status returned')

    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)

    print('\n=======================Add Node Work Flow Test End=======================\n')

#####################################################################
@pytest.mark.parametrize('endpoint', [('/dne/nodes/'), ('/dne/preprocess/')])
@pytest.mark.dne_paqx_parent
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

        if not data['path'] :
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

#######################################################################################################

@pytest.mark.parametrize('endpoint', [('/dne/nodes/'), ('/dne/preprocess/')])
@pytest.mark.dne_paqx_parent
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
        if 'node' in endpoint :
            jobId = preprocess_workflow_id
        else:
            jobId = nodes_workflow_id

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

        if not data['path'] :
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

###################################################################################################

@pytest.mark.parametrize('endpoint', [('/dne/nodes/step/'), ('/dne/preprocess/step/')])
@pytest.mark.dne_paqx_parent
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
            'Error: Did not get a 400-series on ' + endpoint +  '{invalid_step_name}'
        data = response.json()
        print(data)

        error_list = []

        if not data['error']:
            error_list.append(data['error'])

        if 'exception' in data :
            if 'java' in data['exception']:
                error_list.append('\"java\" text should not be displayed')

        if 'message' not in data:
            error_list.append(data['message'])
        else:
            if 'java' in data['message']:
                error_list.append('\"java\" text should not be displayed')

        if not data['path'] :
            error_list.append(data['path'])
        else :
            if not invalid_step_name in data['path']:
                error_list.append('the invalid step name should be listed in the path field')

        assert not error_list, 'Error: Issue found with  ' + endpoint +  '{invalid-step-name} Response'


    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)

    print('\n======================= invalid stepname Test End=======================\n')

###########################################################################################################
