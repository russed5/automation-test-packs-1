# Copyright © 2017 Dell Inc. or its subsidiaries.  All Rights Reserved
import af_support_tools
import pytest
import os
import json
import requests
import time

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
    global payload_property_amqp
    payload_property_amqp = 'amqp_payload'

    global ipaddress
    ipaddress = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')
    global cli_username
    cli_username = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                             property='username')
    global cli_password
    cli_password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                             property='password')
    global consulHost
    consulHost = 'consul.cpsd.dell'

@pytest.mark.tls_enabled
@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_install_amqpapi():
    err = []

    amqpapi = "dell-cpsd-amqp-rest-api"

    sendcommand_install =  "yum install -y " + amqpapi
    my_return_status = af_support_tools.send_ssh_command(host= ipaddress, username=cli_username, password=cli_password,
                                                             command=sendcommand_install, return_output=True)

    rpm_check = af_support_tools.check_for_installed_rpm(host=ipaddress, username=cli_username, password=cli_password,
                                                         rpm_name=amqpapi)

    if rpm_check != True:
        err.append(amqpapi+ " did not install properly")
    assert not err

@pytest.mark.tls_enabled
@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_api_addsystem():
    err=[]


    api_url = 'http://' + ipaddress + ':5500/v1/amqp/system-definition/'

    the_payload = af_support_tools.get_config_file_property(config_file=payload_file, heading= payload_header,
                                                            property= payload_property_amqp )
    
    sysadd = json.loads(the_payload)
    
    time.sleep(10)
    header = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    r = requests.post(api_url, headers = header,  data=the_payload)    
    resp = json.loads(r.text)


    ## Validating contents of json file and message returned from Rest API
    if resp == None:
        err.append("Error---System not added successfully")
    assert not err

    if sysadd["body"]["convergedSystem"]["identity"]["serialNumber"] != resp["body"]["convergedSystem"]["identity"]["serialNumber"]:
        err.append("Error---Correct Serial number not returned")
    assert not err


    if (sysadd["body"]["convergedSystem"]["components"][0] != resp["body"]["convergedSystem"]["components"][0]and
            sysadd["body"]["convergedSystem"]["components"][1] != resp["body"]["convergedSystem"]["components"][1]and
                sysadd["body"]["convergedSystem"]["components"][1] != resp["body"]["convergedSystem"]["components"][2]and
                    sysadd["body"]["convergedSystem"]["components"][3] != resp["body"]["convergedSystem"]["components"][3]):

        err.append("Error---All Components are not added successfully")
    assert not err

@pytest.mark.tls_enabled
def test_sds_consul():
    """
            Title: sds Registered in con
            Description: This test verify SystemDefinition Services is registered with consul
            Params: None
            Returns: None
        """
    print(test_sds_consul.__doc__)
    err = []


    consul_url = 'https://' + consulHost + ':8500/v1/catalog/services'
    resp = requests.get(consul_url, verify= '/usr/local/share/ca-certificates/taf.cpsd.dell.ca.crt')
    data = json.loads(resp.text)

    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    if 'system-definition-service' not in data:
        err.append("Error--- system-definition-service not registered in Consul")
    assert not err

    if 'postgres' not in data:
        err.append("Error--- Postgres not registered in Consul")
    assert not err


