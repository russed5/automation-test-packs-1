#!/usr/bin/python
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
import os


##############################################################################################

@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    import cpsd
    global cpsd

    # Get the typically used passwords
    global setup_config_file
    setup_config_file = 'continuous-integration-deploy-suite/setup_config.ini'

    global setup_config_header
    setup_config_header = 'config_details'

    global rackHD_password
    rackHD_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                heading=setup_config_header,
                                                                property='rackhd_password')

    global rtp_password
    rtp_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                             heading=setup_config_header,
                                                             property='vcenter_password_rtp')

    global fra_password
    fra_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                             heading=setup_config_header,
                                                             property='vcenter_password_fra')


@pytest.fixture()
def setup():
    parameters = {}
    env_file = 'env.ini'
    ipaddress = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                          property='hostname')
    parameters['IP'] = ipaddress
    cli_user = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                         property='username')
    parameters['cli_user'] = cli_user
    cli_password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                             property='password')
    parameters['cli_password'] = cli_password
    return parameters


#####################################################################
# These are the main tests.
#####################################################################

@pytest.mark.parametrize('service, directory', [("dell-cpsd-hal-vcenter-adapter", "vcenter-adapter"),
                                                ("dell-cpsd-hal-rackhd-adapter", "rackhd-adapter"),
                                                ("dell-cpsd-hal-scaleio-adapter", "scaleio-adapter"),
                                                ("dell-cpsd-dne-node-expansion-service", "node-expansion-service"),
                                                ("dell-cpsd-dne-engineering-standards-service", "engineering-standards-service"),
                                                ("dell-cpsd-dne-node-discovery-service", "node-discovery-service"),
                                                ("dell-cpsd-core-credential-service", "credential"),
                                                ("dell-cpsd-core-endpoint-registration-service",
                                                 "registration-services/endpoint-registration")])
@pytest.mark.daily_status
@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_dne_log_files_free_of_passwords(service, directory, setup):
    filePath = '/opt/dell/cpsd/dne/' + directory + '/logs/'

    infoLogFile = directory + '-info.log'

    # Need this exception as the node-discovery-paqx log file format is different to the others
    if filePath == '/opt/dell/cpsd/node-discovery-paqx/logs/':
        infoLogFile = 'node-discovery-info.log'

    if filePath == '/opt/dell/cpsd/credential/logs/':
        infoLogFile = 'cpsd-credentials-service-info.log'

    if filePath == '/opt/dell/cpsd/registration-services/endpoint-registration/logs/':
        infoLogFile = 'endpoint-registration-service-info.log'

    # Verify the log files exist
    sendCommand = 'docker ps | grep ' + service + ' | awk \'{system("docker exec -i "$1" ls ' + filePath + '") }\''

    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['cli_user'],
                                                         password=setup['cli_password'],
                                                         command=sendCommand, return_output=True)
    print(my_return_status)
    error_list = []

    if (infoLogFile not in my_return_status):
        error_list.append(infoLogFile)

    password1 = fra_password
    password2 = rtp_password
    password3 = rackHD_password

    # Verify there are no Password #1
    sendCommand = 'docker ps | grep ' + service + ' | awk \'{system("docker exec -i "$1" cat ' + filePath + infoLogFile + ' | grep ' + password1 + '")}\''
    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['cli_user'],
                                                         password=setup['cli_password'],
                                                         command=sendCommand, return_output=True)
    if (password1 in my_return_status):
        error_list.append(password1)

    # Verify there are no Password #2
    sendCommand = 'docker ps | grep ' + service + ' | awk \'{system("docker exec -i "$1" cat ' + filePath + infoLogFile + ' | grep ' + password2 + '")}\''
    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['cli_user'],
                                                         password=setup['cli_password'],
                                                         command=sendCommand, return_output=True)
    if (password2 in my_return_status):
        error_list.append(password2)

    # Verify there are no Password #3
    sendCommand = 'docker ps | grep ' + service + ' | awk \'{system("docker exec -i "$1" cat ' + filePath + infoLogFile + ' | grep ' + password3 + '")}\''
    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['cli_user'],
                                                         password=setup['cli_password'],
                                                         command=sendCommand, return_output=True)
    if (password3 in my_return_status):
        error_list.append(password3)

    assert not error_list, 'Plain text passwords in log files, Review the ' + infoLogFile + ' file'

    print(
        '\nNo plain text passwords in log files\n')

##############################################################################################
