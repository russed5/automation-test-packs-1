#!/usr/bin/python
# Author: Shane McGowan
# Revision: 1.0
# Code Reviewed by: Toqeer Akhtar
# Description: Testing the Converged System Components Rest API V's JSON input file
#
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information

import time
import sys
import af_support_tools
import pytest
import string
import requests
import json
import os


@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    # Update config ini files at runtime
    my_data_file = os.environ.get('AF_RESOURCES_PATH') + '/continuous-integration-deploy-suite/symphony-sds.properties'
    af_support_tools.set_config_file_property_by_data_file(my_data_file)

    # Set config ini file name
    global env_file
    env_file = 'env.ini'

    # Set Vars
    global payload_file
    payload_file = 'continuous-integration-deploy-suite/symphony-sds.ini'
    global payload_header
    payload_header = 'payload'
    global payload_property_sysadd
    payload_property_sysadd = 'amqp_payload'

    # Test VM Details
    global ipaddress
    ipaddress = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')
    global cli_username
    cli_username = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                             property='username')
    global cli_password
    cli_password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                             property='password')

@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_common_ui_install(setup):
    """
    Title: Verify that the common-ui rpm is installed correctly
    Description: This test verifies that the common-ui service is installed correctly
    Params: List of service names
    Returns: None
    """
    print(test_common_ui_install.__doc__)

    err = []

    common_ui = "dell-cpsd-common-ui"

    sendcommand = "yum install -y " + common_ui
    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username,
                                                             password=cli_password,
                                                            command=sendcommand, return_output=True)

    rpmcheck_ui = af_support_tools.check_for_installed_rpm(host=ipaddress, username=cli_username,
                                                             password=cli_password, rpm_name=common_ui)

    if rpmcheck_ui != True:
        err.append(common_ui+ " did not install properly")
    assert not err

@pytest.mark.skip(reason="common_ui not tls enabled yet")
@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_ConvergedSystem_RestAPI():
    test_errors = []

    """ Verify the Converged System Components Rest API V's JSON input file.

    Pre-requisite : The system has already been defined and discovered.
                    You can open a browser to the Converged System Rest API (e.g. http://10.20.30.40:10000/sds/convergedsystems)
    """

    # Check the JSON system definition input file
    the_payload = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                            property=payload_property_sysadd)
    sysadd = json.loads(the_payload)

    # =================================================================
    # Converged System Rest API
    time.sleep(5)
    RestAPIurl = 'http://' + ipaddress + ':10000/sds/convergedsystems'
    resp = requests.get(RestAPIurl)
    Rest_data = json.loads(resp.text)
    time.sleep(5)


    # Find the Converged Systems UUID to build the Converged Systems Components Rest API
    #Rest_Component_element = Rest_data[0]["uuid"]

    RestAPI_Component_url = u'http://' + ipaddress + u':10000/sds/convergedsystems/' + Rest_data[0]["uuid"] + u'/components'
    comp_resp = requests.get(RestAPI_Component_url)
    Rest_Component_data = json.loads(comp_resp.text)

    # Check Common UI - System Definition


    if Rest_data[0]["identity"]["identifier"] != sysadd["body"]["convergedSystem"]["identity"]["identifier"]:
        test_errors.append("Error---System types / identifier not matching")
    assert not test_errors

    if Rest_data[0]["identity"]["serialNumber"] != sysadd["body"]["convergedSystem"]["identity"]["serialNumber"]:
        test_errors.append("Error---Serial numbers not matching")
    assert not test_errors

    if Rest_data[0]["definition"]["productFamily"] != sysadd["body"]["convergedSystem"]["definition"]["productFamily"]:
        test_errors.append("Error---Product Family not matching")
    assert not test_errors

    if Rest_data[0]["definition"]["product"] != sysadd["body"]["convergedSystem"]["definition"]["product"]:
        test_errors.append("Error---Product not matching")
    assert not test_errors

    if Rest_data[0]["definition"]["model"] != sysadd["body"]["convergedSystem"]["definition"]["model"]:
        test_errors.append("Error---Model not matching")
    assert not test_errors

    # Check Common UI - System Components - Row 0

    if Rest_Component_data[0]["identity"]["elementType"] != \
            sysadd["body"]["convergedSystem"]["components"][0]["identity"]["elementType"]:
        test_errors.append("Error---Component Type not matching")
    assert not test_errors

    ## ---TA --- Disabling following checks as indexing can be different each time system is added

    # if Rest_Component_data[0]["identity"]["identifier"] != sysadd["body"]["convergedSystem"]["components"][2]["identity"]["identifier"]:
    #     test_errors.append("Error---Component Name / identifier not matching")
    # assert not test_errors
    #
    # if Rest_Component_data[0]["definition"]["productFamily"] != sysadd["body"]["convergedSystem"]["components"][0]["definition"]["productFamily"]:
    #     test_errors.append("Error---Component Product family not matching")
    # assert not test_errors
    #
    # if Rest_Component_data[0]["definition"]["modelFamily"]!= sysadd["body"]["convergedSystem"]["components"][0]["definition"]["modelFamily"]:
    #     test_errors.append("Error---Component Model family not matching")
    # assert not test_errors
    #
    # if  Rest_Component_data[0]["definition"]["model"]!= sysadd["body"]["convergedSystem"]["components"][0]["definition"]["model"]:
    #     test_errors.append("Error---Component Model not matching")
    # assert not test_errors

    # ---------------------------------------------------------------------
