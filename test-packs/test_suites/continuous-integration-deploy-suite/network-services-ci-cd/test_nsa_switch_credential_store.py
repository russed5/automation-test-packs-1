import af_support_tools
import os
import pytest
import json
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
    global payload_file
    payload_file = 'symphony-sds.ini'
    global payload_header
    payload_header = 'payload'
    global payload_property_sys
    payload_property_sys = 'sys_payload'

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
    global switch_username
    switch_username = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                               heading=setup_config_header, property='switch_n9a_username')

    global switch_password
    switch_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                       heading=setup_config_header,
                                                                       property='switch_n9a_password')

    global switch_community
    switch_community = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                heading=setup_config_header,
                                                                property='switch_n9a_community')

#####################################################################
# These are the main tests.
#####################################################################

@pytest.mark.network_services_mvp
def test_AddVxRackSystem():
    print('Setup: Add VxRack RTP system via SDS Service')
    #origin_file = config_file_path + sysdef_payload_file
    origin_file = config_file_path + payload_file
    dest_file = '/tmp/nsa_add_vxrack.json'

    # Get the switch data from the nsa_add_vxrack.json file and publish message using amqp-post tool.
    cmd = 'curl --header "Content-Type: application/json" -X POST --data @%s http://127.0.0.1:5500/v1/amqp/system-definition/' % (
    dest_file)
    print(cmd)


    af_support_tools.file_copy_put(host=ip_address, port=22, username=username, password=password,
                                   source_file=origin_file, destination_file=dest_file)

    rc = af_support_tools.send_ssh_command(host=ip_address, username=username, password=password,
                                           command=cmd, return_output=False)
    # print (rc)
    if int(rc) == 0:
        print('success runing cmd:%s' % (cmd))
    else:
        raise Exception('Error: Error running command:%s' % (cmd))


@pytest.mark.network_services_mvp
def test_switch_credential_store():
    """
    Description :   This method tests whether the switch credentials are stored in system definition service
                    it will asserts if :
                    If switch json file doesnt exists
                    If AMQP tool is not able to execute the command properly
                    If credential keys for switch are not created properly
    Parameters  :   None
    Returns     :   None
    """
    # Get the payload data from the config symphony-sds.ini file.
    #the_payload = af_support_tools.get_config_file_property(config_file=payload_file,
    #                                                        heading=payload_header,
    #                                                        property=payload_property_sys)
    container_id = get_vault_container_id()
    assert check_vault_credential_keys(container_id), 'test failed: switch credentials are not stored properly'


def get_vault_container_id():
    """    
    Description         :       This method gets the container id    
    Parameters          :       None    
    Returns             :       container_id     -       container id string coming from 'docker ps' command(STRING).    
    """
    cmd = 'docker ps | grep vault'
    output = af_support_tools.send_ssh_command(host=ip_address, username=username, password=password, command=cmd,
                                               return_output=True).strip()
    assert (output != ""), 'test failed: ' + container + ' docker service is not running'
    output_list = output.split()
    container_id = output_list[0]
    return container_id


def check_vault_credential_keys(container_id):
    """
    Description         :       This method checks whether the credentials are created for SWITCH in system definition
                                also This method will delete the IDRAC.json file
    Parameters          :       1. container_id    -       Container id of Vault (STRING)
    Returns             :       output_length      -       if the credential keys are not found (INTEGER)
                                0 or 1 (Boolean)
    """
    cmd = "docker exec " + container_id + " vault list secret"
    print ("cmd:", cmd)
    output = af_support_tools.send_ssh_command(host=ip_address, username=username, password=password, command=cmd,
                                               return_output=True).strip()
    output_list = output.split("\n")
    print ("output_list:", output_list)

    credential_list_json = ""
    credential_list_stored = 0
    # if credential keys are not found return, else check the credentials using Vault commands and compare with json input 
    del output_list[0]
    print ("output_list1:", output_list)
    del output_list[0]
    print ("output_list2:", output_list)
    output_length = len(output_list)
    print("Last uuid in the list: ", output_list[0])
    uuid = output_list[0]
    #for uuid in output_list:
    cmd1 = "docker exec " + container_id + " vault list secret/" + uuid
    print ("cmd1:", cmd1)
    output1 = af_support_tools.send_ssh_command(host=ip_address, username=username, password=password, command=cmd1,
                                                    return_output=True).strip()
    output_list1 = output1.split("\n")
    endpoint1_uuid = output_list1[2]
    endpoint2_uuid = output_list1[3]
    # get endpoint1_uuid for username and password
    cmd2 = "docker exec " + container_id + " vault list secret/" + uuid + endpoint1_uuid
    print ("cmd2;", cmd2)
    output2 = af_support_tools.send_ssh_command(host=ip_address, username=username, password=password, command=cmd2,
                                                    return_output=True).strip()
    output_list2 = output2.split("\n")
    output_length2 = len(output_list2)
    print ("output_length:", output_length2)
    # get switch username and password
    print ("output_list2:", output_list2)
    switch_key = output_list2[2]
    cmd3 = "docker exec " + container_id + " vault read secret/" + uuid + endpoint1_uuid + switch_key
    print ("cmd3:", cmd3)
    output3 = af_support_tools.send_ssh_command(host=ip_address, username=username, password=password,
                                                        command=cmd3, return_output=True).strip()
    switchUsrname, switchPasswd = get_switch_credentials(output3)

    # get switch community
    cmd4 = "docker exec " + container_id + " vault list secret/" + uuid + endpoint2_uuid
    print("cmd4;", cmd4)
    output4 = af_support_tools.send_ssh_command(host=ip_address, username=username, password=password, command=cmd4,
                                            return_output=True).strip()
    output_list4 = output4.split("\n")
    output_length2 = len(output_list4)
    print("output_length:", output_length2)

    print("output_list4:", output_list4)
    switch_key = output_list4[2]
    cmd5 = "docker exec " + container_id + " vault read secret/" + uuid + endpoint2_uuid + switch_key
    print("cmd5:", cmd5)
    output6 = af_support_tools.send_ssh_command(host=ip_address, username=username, password=password,
                                            command=cmd5, return_output=True).strip()

    switchCommunity = get_switch_community(output6)
    #check if switch credentials are stored correctly
    credential_list_json = [switch_username, switch_password, switch_community]
    print ("credential_list_json:", credential_list_json)
    credential_list_stored = [switchUsrname, switchPasswd, switchCommunity]
    print ("credential_list_stored:", credential_list_stored)
    #if credential_list_stored:
    #        break
    for element in credential_list_json:
        if (element in credential_list_stored):
            continue
        else:
            return 0
    return 1


def get_switch_credentials(command_output):
    """
    Description         :       This method processes the command output and gets the switch username and password
    Parameters          :       1. command_output    -       Command output to be processed (STRING)
    Returns             :       switchUsername        -       SWITCH username (STRING)
                                switchPassword        -       SWITCH password (STRING)
    """
    output_list = command_output.split("\n")
    switch_username_list = output_list[5].split("\t")
    switchUsername = switch_username_list[1]
    switch_passwd_list = output_list[4].split("\t")
    switchPasswd = switch_passwd_list[1]
    return switchUsername, switchPasswd

def get_switch_community(command_output):
    """
    Description         :       This method processes the command output and gets the switch community
    Parameters          :       1. command_output    -       Command output to be processed (STRING)
    Returns             :       switchCommunity        -       SWITCH community (STRING)
    """
    output_list = command_output.split("\n")
    switchCommunity_list = output_list[3].split("\t")
    switchCommunity = switchCommunity_list[1]
    return switchCommunity
