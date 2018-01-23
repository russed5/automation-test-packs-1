# Copyright © 2017 Dell Inc. or its subsidiaries.  All Rights Reserved
import pytest
import json
import os
import time
import requests
import af_support_tools




@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    global path
    path = "/home/autouser/PycharmProjects/auto-framework/test_suites/continuous-integration-deploy-suite/network-services-ci-cd/"
    my_data_file = os.environ.get(
        'AF_RESOURCES_PATH') + '/continuous-integration-deploy-suite/symphony-sds-network-VxRack.properties'
    af_support_tools.set_config_file_property_by_data_file(my_data_file)
    global env_file
    env_file = 'env.ini'
    # Set config ini file name
    global hostTLS
    hostTLS = "amqp"
    global host
    host = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')
    global portTLS
    portTLS = af_support_tools.get_config_file_property(config_file=env_file, heading='RabbitMQ', property='ssl_port')

    portTLS = int(portTLS)
    global rmq_username
    rmq_username = af_support_tools.get_config_file_property(config_file=env_file, heading='RabbitMQ',
                                                             property='username')
    global rmq_password
    rmq_password = af_support_tools.get_config_file_property(config_file=env_file, heading='RabbitMQ',
                                                             property='password')

    global ipaddress
    ipaddress = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')
    global cli_username
    cli_username = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                             property='username')
    global cli_password
    cli_password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                             property='password')


    # Set Vars
    global payload_file
    payload_file = 'continuous-integration-deploy-suite/symphony-sds-network-VxRack.ini'
    global payload_header
    payload_header = 'payload'
    global payload_property_sys
    payload_property_sys = 'sys_payload'
    global payload_property_req
    payload_property_req = 'sys_request_payload'
    global payload_property_hal
    payload_property_hal = 'ccv_payload'
    global payload_rackHD
    payload_rackHD = 'register_rackhd'

    data_file = os.environ.get('AF_RESOURCES_PATH') + '/continuous-integration-deploy-suite/setup_config.properties'
    af_support_tools.set_config_file_property_by_data_file(data_file)

    global setup_config_file
    setup_config_file = 'continuous-integration-deploy-suite/setup_config.ini'

    global rackhd_ip
    rackhd_ip = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                          heading="config_details",
                                                          property='rackhd_ip')
    global rackhd_username
    rackhd_username = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                              heading="config_details",
                                                              property='rackhd_username')
    global rackhd_password
    rackhd_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                              heading="config_details",
                                                              property='rackhd_password')


    global rackhd_port
    rackhd_port = '32080'

    global on_nw_port
    on_nw_port ='33080'

    global message_rackHD
    message_rackHD = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                        property=payload_rackHD)

    global nsa_switch_9k_username
    nsa_switch_9k_username = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                       heading="config_details",
                                                                       property='nsa_switch_9k_username')
    global nsa_switch_9k_password
    nsa_switch_9k_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                       heading="config_details",
                                                                       property='nsa_switch_9k_password')
    global nsa_switch_9k_ip
    nsa_switch_9k_ip = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                 heading="config_details",
                                                                 property='nsa_switch_9k_ip')
    global nsa_rackhd_username
    nsa_rackhd_username = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                    heading="config_details",
                                                                    property='nsa_rackhd_username')
    global nsa_rackhd_password
    nsa_rackhd_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                    heading="config_details",
                                                                    property='nsa_rackhd_password')
    global nsa_rackhd_ip
    nsa_rackhd_ip = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                             heading="config_details",
                                                             property='nsa_rackhd_ip')
    global switchVersion
    switchVersion = '7.0(3)I4(3)'

    global switch_type
    switch_type = 'cisco'

    global apibody
    apibody = '{"endpoint":{"ipaddress":"' + nsa_switch_9k_ip + '", "username": "' + nsa_switch_9k_username + '", "password": "' + nsa_switch_9k_password + '", "switchType": "' + switch_type + '"}}'

#######################################################################################################################

# *** THIS IS THE MAIN TEST *** Add a system
@pytest.mark.daily_status
@pytest.mark.network_services_mvp
@pytest.mark.network_services_mvp_extended
def test_SystemAdditionRequested():
    q_len = 0
    timeout = 0
    cleanupSDS()

    bindSDSQueus()

    # Get the payload data from the config symphony-sds.ini file.
    the_payload = af_support_tools.get_config_file_property(config_file=payload_file,
                                                            heading=payload_header,
                                                            property=payload_property_sys)

    urldefine = 'http://' + host + ':5500/v1/amqp/'
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    requests.post(urldefine, data=the_payload, headers=headers)

    time.sleep(30)

    while q_len < 1:
        time.sleep(1)
        timeout += 1

        q_len = af_support_tools.rmq_message_count(host=hostTLS, port=portTLS, ssl_enabled=True,
                                                   queue='testSystemListRequest')

        print(q_len)

        if timeout > 30:
            print('ERROR: System list Request Message took to long to return. Something is wrong')
            cleanupSDS()
            break

    return_message = af_support_tools.rmq_consume_message(host=hostTLS, port=portTLS, ssl_enabled=True, queue='testSystemListRequest')

    return_json = json.loads(return_message)

    assert return_json['messageProperties']
    assert return_json['convergedSystem']['groups']
    assert return_json['convergedSystem']['definition']
    assert return_json['convergedSystem']['components']
    assert return_json['convergedSystem']['endpoints']

    # Call the function to verify the generated credentials.addition.requested message is correct.
    time.sleep(60)
    verifyCSmessage()

    mess_count = af_support_tools.rmq_message_count(host=hostTLS, port=portTLS, ssl_enabled=True, queue='testSystemDefinitionEvent')
    assert mess_count >= 2, "Unexpected number of components defined."

    # Call the function to verify the system exists. This is not a necessary step but it will return the system UUID.
    verify_SystemExists()
    #verifyConsulUpdate("rcm-fitness-paqx", "rcm-fitness-api")

    cleanupSDS()

#verify the network nodes information in rackhd after registering the reackhd to endpoint in consul
@pytest.mark.daily_status
@pytest.mark.network_services_mvp
@pytest.mark.network_services_mvp_extended
def test_verifyRackhdNodes():
    print("#### Registering Rackhd to Symphony vm ####")
    #registerRackHD(message_rackHD, "out_registerRackHDResp.json")
    registerRackHD()
    time.sleep(360)
    auth_token = retrieveRHDToken()
    json_data = get_rackhd_api_response('nodes',auth_token)
    print(json_data)
    assert json_data != ''

# *** Kick of the collectComponentVersion Msg
@pytest.mark.daily_status
@pytest.mark.network_services_mvp
@pytest.mark.network_services_mvp_extended
def test_CollectComponentVersion():
    the_payload = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                            property=payload_property_hal)

    urlcollect = 'http://' + host + ':5500/v1/amqp/'
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    response = requests.post(urlcollect, data=the_payload, headers=headers)
    print(response.status_code)
    time.sleep(5)
    assert response.status_code == 200

    print('\nTEST: CollectComponentVersions run: PASSED')


@pytest.mark.daily_status
@pytest.mark.network_services_mvp
@pytest.mark.network_services_mvp_extended
def test_get_collected_version():
    auth_token = retrieveRHDToken()
    json_data = get_rackhd_api_response('nodes', auth_token)

    assert json_data != ''

    time.sleep(5)
    firm_ver = "7.0"

    pcmd = "select version from rcds.version"
    sendcommand = "docker exec -t postgres psql -U postgres -d rcm-compliance-data-service -c '" + pcmd + "'"
    print(sendcommand)

    rc = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username,
                                                         password=cli_password,
                                                         command=sendcommand, return_output=True)
    print(rc)

    if rc != '':
        if firm_ver not in rc:
            print("no_version retrieved")
            assert False
        return

    assert False


@pytest.mark.daily_status
@pytest.mark.network_services_mvp
def test_rackhd_login_api():
    # Get the RackHD Authentication Token
    global token
    token = retrieveOnwToken()
    print('The token is: ', token, '\n')
    assert token != ''

@pytest.mark.daily_status
@pytest.mark.network_services_mvp
def test_rackhd_get_switch_firmware():
    switch_api = '/switchFirmware'
    token = retrieveOnwToken()
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


#######################################################################################################################

def cleanupSDS():
    # Delete the test queues
    print('Cleaning up...')

    af_support_tools.rmq_delete_queue(host=hostTLS, port=portTLS, ssl_enabled=True,
                                      queue='testSystemListRequest')
    af_support_tools.rmq_delete_queue(host=hostTLS, port=portTLS, ssl_enabled=True,
                                      queue='testSystemListFound')
    af_support_tools.rmq_delete_queue(host=hostTLS, port=portTLS, ssl_enabled=True,
                                      queue='testComponentCredentialRequest')
    af_support_tools.rmq_delete_queue(host=hostTLS, port=portTLS, ssl_enabled=True,
                                      queue='testSystemDefinitionEvent')

def bindSDSQueus():
    af_support_tools.rmq_bind_queue(host=hostTLS, port=portTLS, ssl_enabled=True,
                                    queue='testSystemListRequest',
                                    exchange='exchange.dell.cpsd.syds.system.definition.request',
                                    routing_key='#')

    af_support_tools.rmq_bind_queue(host=hostTLS, port=portTLS, ssl_enabled=True,
                                    queue='testSystemListFound',
                                    exchange='exchange.dell.cpsd.syds.system.definition.response',
                                    routing_key='#')

    af_support_tools.rmq_bind_queue(host=hostTLS, port=portTLS, ssl_enabled=True,
                                    queue='testSystemDefinitionEvent',
                                    exchange='exchange.dell.cpsd.syds.system.definition.event',
                                    routing_key='#')

    af_support_tools.rmq_bind_queue(host=hostTLS, port=portTLS, ssl_enabled=True,
                                    queue='testComponentCredentialRequest',
                                    exchange='exchange.dell.cpsd.cms.credentials.request',
                                    routing_key='#')

def verifyCSmessage():
    # We need to verify that the triggered component.credentials.addition.requested is valid.

    q_len = 0
    timeout = 0

    while q_len < 1:
        time.sleep(1)
        timeout += 1

        q_len = af_support_tools.rmq_message_count(host=hostTLS, port=portTLS, ssl_enabled=True,
                                                   queue='testComponentCredentialRequest')

        if timeout > 30:
            print('ERROR: CS Request Message took to long to return. Something is wrong')
            cleanupSDS()
            break

    return_message = af_support_tools.rmq_consume_all_messages(host=hostTLS, port=portTLS, ssl_enabled=True,
                                                          queue='testComponentCredentialRequest')

    print(return_message)

    return_json = json.loads(return_message[1], encoding='utf-8')
    print(return_json)

    if 'credentialUuid' not in return_message[1]:
        print('\nTEST FAIL: Invalid "credentials.addition.requested" message structure. credentialUuid missing')
    if 'endpointUuid' not in return_message[1]:
        print('\nTEST FAIL: Invalid "credentials.addition.requested" message structure. endpointUuid missing')
    if 'componentUuid' not in return_message[1]:
        print('\nTEST FAIL: Invalid "credentials.addition.requested" message structure. componentUuid missing')

    assert return_json['messageProperties']['correlationId']
    assert return_json['messageProperties']['replyTo']
    assert return_json['messageProperties']['timestamp']
    assert return_json['endpoints'][0]['credentials'][0]['credentialUuid']
    print('credentials.addition.requested is valid')


def verify_SystemExists():
    # Check that the system exists
    print('Verifying system does exist...')
    time.sleep(2)
    # Get the payload data from the config symphony-sds.ini file.
    the_payload = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                            property=payload_property_req)

    af_support_tools.rmq_purge_queue(host=hostTLS, port=portTLS, ssl_enabled=True, queue='testSystemListFound')
    af_support_tools.rmq_purge_queue(host=hostTLS, port=portTLS, ssl_enabled=True, queue='testSystemListFound')

    af_support_tools.rmq_publish_message(host=hostTLS, port=portTLS, ssl_enabled=True,
                                         exchange='exchange.dell.cpsd.syds.system.definition.request',
                                         routing_key='dell.cpsd.syds.converged.system.list.requested',
                                         headers={'__TypeId__': 'com.dell.cpsd.syds.converged.system.list.requested'},
                                         payload=the_payload, payload_type='json')

    q_len = 0
    timeout = 0

    while q_len < 1:
        time.sleep(1)
        timeout += 1

        q_len = af_support_tools.rmq_message_count(host=hostTLS, port=portTLS, ssl_enabled=True,
                                                   queue='testSystemListFound')

        if timeout > 10:
            print('ERROR: Sys Found Response Message took to long to return. Something is wrong')
            cleanupSDS()
            break

    return_message = af_support_tools.rmq_consume_all_messages(host=hostTLS, port=portTLS, ssl_enabled=True,
                                                          queue='testSystemListFound')

    return_json = json.loads(return_message[0], encoding='utf-8')

    assert return_json['messageProperties']['correlationId']
    assert return_json['messageProperties']['replyTo']
    assert return_json['messageProperties']['timestamp']
    assert return_json['convergedSystems']
    assert return_json['convergedSystems'][0]['uuid']
    assert not return_json['convergedSystems'][0]['groups']
    assert not return_json['convergedSystems'][0]['endpoints']
    assert not return_json['convergedSystems'][0]['subSystems']
    assert not return_json['convergedSystems'][0]['components']

    config = json.loads(return_message[0], encoding='utf-8')
    my_systemUuid = config['convergedSystems'][0]['uuid']
    print('\nTEST: System Exists - System UUID: ', my_systemUuid)

def verifyConsulUpdate(paqx):
    url = 'https://' + host + ':8500/v1/catalog/services'
    resp = requests.get(url, verify=False)
    data = json.loads(resp.text)
    print(url)
    print("Requesting Consul info....")
    print(data)
    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    if data != "":
        if paqx in data:
           print("Consul info verified.")
        return

    assert False, "No Consul info returned."

def retrieveRHDToken():
    # retrieve rackhd auth token
    url = "http://" + rackhd_ip +":"+ rackhd_port + "/login"
    header = {'Content-Type': 'application/json'}
    body = '{"username": "' + rackhd_username + '", "password": "' + rackhd_password + '"}'

    resp = requests.post(url, headers=header, data=body)
    tokenJson = json.loads(resp.text, encoding='utf-8')
    token = tokenJson["token"]

    return token

def get_rackhd_api_response(rackhdapi, token):
    "http://10.234.122.45:32080/api/2.0/nodes"
    url = 'http://' + rackhd_ip + ':' + rackhd_port +'/api/2.0/'+ rackhdapi
    print(url)
    headers = {'Content-type': 'application/json', 'Accept': 'application/json', "Authorization": "JWT " + token}
    print(headers)
    #headerstring = {"Content-Type": "application/json", "Authorization": "JWT " + token}

    response = requests.get(url, headers=headers)
    data_json = json.loads(response.text, encoding='utf-8')
    print('retrieved json:', data_json, '\n')
    assert response.status_code == 200
    return data_json

def retrieveOnwToken():
    # retrieve a token
    url = 'http://' + nsa_rackhd_ip + ':' + on_nw_port + '/login'
    header = {'Content-Type': 'application/json'}
    body = '{"username": "' + nsa_rackhd_username + '", "password": "' + nsa_rackhd_password + '"}'

    resp = requests.post(url, headers=header, data=body)
    tokenJson = json.loads(resp.text, encoding='utf-8')
    token = tokenJson["token"]

    return token

def get_switch_api(switch_api, apibody, token):
    # Test rackhd API can retrieve switch firmware version
    url = 'http://' + nsa_rackhd_ip + ':' + on_nw_port + switch_api
    #print('token passed is: ', apibody, '\n')
    headerstring = {"Content-Type": "application/json", "Authorization": "Bearer " + token}
    #print('The headstring for switch api: ', headerstring)
    response = requests.post(url, headers=headerstring, data=apibody)
    data_text = response.text
    data_json = json.loads(response.text, encoding='utf-8')
    print('returned json: ', data_json , '\n')
    return data_json

def registerRackHD():
    urldefine = 'http://' + host + ':5500/v1/amqp/'
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

    the_payload = af_support_tools.get_config_file_property(config_file=payload_file,
                                                            heading=payload_header,
                                                            property=payload_rackHD)

    requests.post(urldefine, data=the_payload, headers=headers)

    verifyConsulUpdate("rackhd")

#######################################################################################################################
