# !/usr/bin/python
# Author: fengs7
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


@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    # Set config ini file name
    global env_file
    env_file = 'env.ini'
    # Update config ini files at runtime
    global config_file_path
    config_file_path = os.environ['AF_TEST_SUITE_PATH'] + '/config_files/continuous-integration-deploy-suite/'

    my_data_file = os.environ.get('AF_RESOURCES_PATH') + '/continuous-integration-deploy-suite/symphony-sds.properties'
    af_support_tools.set_config_file_property_by_data_file(my_data_file)
    # Set Vars
    global ip_address
    ip_address = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')
    global username
    username = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='username')
    global password
    password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='password')
    # Update setup_config.properties file at runtime
    data_file = os.environ.get('AF_RESOURCES_PATH') + '/continuous-integration-deploy-suite/setup_config.properties'
    af_support_tools.set_config_file_property_by_data_file(data_file)
    # IDrac Server IP & Creds details
    global setup_config_file
    setup_config_file = 'continuous-integration-deploy-suite/setup_config.ini'
    global setup_config_header
    setup_config_header = 'config_details'
    global nsa_switch_9k_username
    nsa_switch_9k_username = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                       heading=setup_config_header,
                                                                       property='nsa_switch_9k_username')
    global nsa_switch_9k_password
    nsa_switch_9k_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                       heading=setup_config_header,
                                                                       property='nsa_switch_9k_password')
    global nsa_switch_9k_ip
    nsa_switch_9k_ip = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                heading=setup_config_header,
                                                                property='nsa_switch_9k_ip')
    global nsa_rackhd_username
    nsa_rackhd_username = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                heading=setup_config_header,
                                                                property='nsa_rackhd_username')
    global nsa_rackhd_password
    nsa_rackhd_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                heading=setup_config_header,
                                                                property='nsa_rackhd_password')
    global nsa_rackhd_ip
    nsa_rackhd_ip = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                    heading=setup_config_header,
                                                                    property='nsa_rackhd_ip')

    global rackhd_port
    rackhd_port = ':33080'

    global switchVersion
    switchVersion = '7.0(3)I4(3)'

    global switch_type
    switch_type = 'cisco'

    global apibody
    apibody = '{"endpoint":{"ipaddress":"' + nsa_switch_9k_ip + '", "username": "' + nsa_switch_9k_username + '", "password": "' + nsa_switch_9k_password + '", "switchType": "' + switch_type + '"}}'
#####################################################################
# These are the main tests.
#####################################################################
@pytest.mark.daily_status
@pytest.mark.network_services_mvp
def test_rackhd_login_api():
    # Get the RackHD Authentication Token
    global token
    token = retrieveRHDToken()
    print('The token is: ', token, '\n')

@pytest.mark.daily_status
@pytest.mark.network_services_mvp
def test_rackhd_get_switch_firmware():
    switch_api = '/switchFirmware'
    switch_firmware = get_switch_api(switch_api, apibody, token)
    assert switch_firmware["version"] == switchVersion
    print('The switch firmware is: ', switch_firmware)

@pytest.mark.daily_status
@pytest.mark.network_services_mvp
def test_rackhd_get_switch_version():
    switch_api = '/switchVersion'
    switch_version = get_switch_api(switch_api, apibody, token)
    assert switch_version["rr_sys_ver"] == switchVersion
    print('The switch version is: ', switch_version)

@pytest.mark.daily_status
@pytest.mark.network_services_mvp
def test_rackhd_get_switch_config():
    switch_api = '/switchConfig'
    switch_config = get_switch_api(switch_api, apibody, token)
    assert 'config' in switch_config
    print('The switch configuration is: ', switch_config)


def retrieveRHDToken():
        # retrieve a token
        url = "http://" + nsa_rackhd_ip + rackhd_port + "/login"
        header = {'Content-Type': 'application/json'}
        body = '{"username": "' + nsa_rackhd_username + '", "password": "' + nsa_rackhd_password + '"}'
        resp = requests.post(url, headers=header, data=body)
        tokenJson = json.loads(resp.text, encoding='utf-8')
        token = tokenJson["token"]
        return token

def get_switch_api(switch_api, apibody, token):
    # Test rackhd API can retrieve switch firmware version
    url = 'http://' + nsa_rackhd_ip + rackhd_port + switch_api
    #print('token passed is: ', apibody, '\n')
    headerstring = {"Content-Type": "application/json", "Authorization": "Bearer " + token}
    #print('The headstring for switch api: ', headerstring)
    response = requests.post(url, headers=headerstring, data=apibody)
    data_text = response.text
    data_json = json.loads(response.text, encoding='utf-8')
    print('returned json: ', data_json , '\n')
    return data_json