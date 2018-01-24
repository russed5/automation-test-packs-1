#!/usr/bin/python
# Copyright © 2018 Dell Inc. or its subsidiaries.  All Rights Reserved
import pytest
import json
import af_support_tools
import os


@pytest.fixture(scope="session")
def setup():
    parameters = {}

    # Update config ini files at runtime
    my_data_file = os.environ.get('AF_RESOURCES_PATH') + '/continuous-integration-deploy-suite/symphony-sds.properties'
    af_support_tools.set_config_file_property_by_data_file(my_data_file)

    # Update setup_config.ini file at runtime
    my_data_file = os.environ.get('AF_RESOURCES_PATH') + '/continuous-integration-deploy-suite/setup_config.properties'
    af_support_tools.set_config_file_property_by_data_file(my_data_file)

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

    # RackHD VM IP & Creds details
    setup_config_file = '/continuous-integration-deploy-suite/setup_config.ini'

    setup_config_header = 'config_details'

    # ~~~~~~~~RackHD Details
    rackHD_IP = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                          heading=setup_config_header,
                                                          property='rackhd_dne_ipaddress')
    parameters['rackHD_IP'] = rackHD_IP

    rackHD_username = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                heading=setup_config_header,
                                                                property='rackhd_username')
    parameters['rackHD_username'] = rackHD_username

    rackHD_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                heading=setup_config_header,
                                                                property='rackhd_password')
    parameters['rackHD_password'] = rackHD_password


    vcenter_IP_customer = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                          heading=setup_config_header,
                                                          property='vcenter_dne_ipaddress_customer')
    parameters['vcenter_IP_customer'] = vcenter_IP_customer


    vcenter_username = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                heading=setup_config_header,
                                                                property='vcenter_username')
    parameters['vcenter_username'] = vcenter_username


    vcenter_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                heading=setup_config_header,
                                                                property='vcenter_password_fra')
    parameters['vcenter_password'] = vcenter_password

    scaleio_IP_gateway = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                          heading=setup_config_header,
                                                          property='scaleio_integration_ipaddress')
    parameters['scaleio_IP_gateway'] = scaleio_IP_gateway


    scaleio_username = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                heading=setup_config_header,
                                                                property='scaleio_username')
    parameters['scaleio_username'] = scaleio_username


    scaleio_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                heading=setup_config_header,
                                                                property='scaleio_password')
    parameters['scaleio_password'] = scaleio_password



    return parameters
