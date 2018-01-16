# Copyright © 2017 Dell Inc. or its subsidiaries.  All Rights Reserved
import pytest
import json
import os
import time
import requests
import af_support_tools
#import test-packs.test_suites.continuous-integration-deploy-suite.rcm-fitness-ci-cd.a_systemDefinition.dbUtils.dbconnection as dbconnection
import dbUtils.dbconnection as dbconnection


@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    global path
    path = "/home/autouser/PycharmProjects/auto-framework/test_suites/continuous-integration-deploy-suite/rcm-fitness-ci-cd/a_systemDefinition/"
    my_data_file = os.environ.get(
        'AF_RESOURCES_PATH') + '/continuous-integration-deploy-suite/symphony-sds-VxRack.properties'
    af_support_tools.set_config_file_property_by_data_file(my_data_file)
    global env_file
    env_file = 'env.ini'
    # Set config ini file name
    global host
    host = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')

    # Set Vars
    global payload_file
    payload_file = 'continuous-integration-deploy-suite/symphony-sds-VxRack.ini'
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
    global payload_vcenter
    payload_vcenter = 'register_vcenter'

    global message_rackHD
    message_rackHD = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                        property=payload_rackHD)
    global message_vcenter
    message_vcenter = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                        property=payload_vcenter)


#######################################################################################################################

# *** THIS IS THE MAIN TEST *** Add a system
@pytest.mark.daily_status
@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
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

        q_len = af_support_tools.rmq_message_count(queue='testSystemListRequest')

        print(q_len)

        if timeout > 30:
            print('ERROR: System list Request Message took to long to return. Something is wrong')
            cleanupSDS()
            break

    return_message = af_support_tools.rmq_consume_message(queue='testSystemListRequest')

    return_json = json.loads(return_message)

    assert return_json['messageProperties']
    assert return_json['convergedSystem']['groups']
    assert return_json['convergedSystem']['definition']
    assert return_json['convergedSystem']['components']
    assert return_json['convergedSystem']['endpoints']

    # Call the function to verify the generated credentials.addition.requested message is correct.
    time.sleep(60)
    verifyCSmessage()

    mess_count = af_support_tools.rmq_message_count(queue='testSystemDefinitionEvent')
    assert mess_count >= 4, "Unexpected number of components defined."

    # Call the function to verify the system exists. This is not a necessary step but it will return the system UUID.
    verify_SystemExists()
    verifyConsulUpdate("rcm-fitness-paqx", "rcm-fitness-api")

    cleanupSDS()

# *** Kick of the collectComponentVersion Msg
@pytest.mark.daily_status
@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_HAL_CollectComponentVersion():
    bindHALQueus()
    registerRackHD(message_rackHD, "out_registerRackHDResp.json")
    time.sleep(2)
    registerVcenter(message_vcenter, "out_registerVcenterResp.json")
    print(host)
    # Get the collectComponentVersions payload data from the config symphony-sds.ini file.
    the_payload = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                            property=payload_property_hal)

    urlcollect = 'http://' + host + ':5500/v1/amqp/'
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    requests.post(urlcollect, data=the_payload, headers=headers)
    time.sleep(2)
    return_message = af_support_tools.rmq_consume_message(queue='testHalOrchestratorRequest', remove_message=False)

    return_json = json.loads(return_message, encoding='utf-8')

    print(return_json)
    assert return_json['messageProperties']['correlationId']
    assert return_json['messageProperties']['replyTo']


    # We need to wait until the queue gets the response message and timeout if it never arrives
    q_len = 0
    timeout = 0

    while q_len < 1:
        time.sleep(1)
        timeout += 1

        q_len = af_support_tools.rmq_message_count(queue='testHalOrchestratorResponse')

        if timeout > 500:
            print('ERROR: HAL Responce Message took to long to return. Something is wrong')
            cleanupHAL()
            break

    return_message = af_support_tools.rmq_consume_message(queue='testHalOrchestratorResponse',
                                                          remove_message=False)

    return_json = json.loads(return_message, encoding='utf-8')

    # Only if the message sequence successfully ran will the returned json message have the following attributes.
    assert return_json['messageProperties']['correlationId']
    assert return_json['messageProperties']['replyTo']
    assert return_json['systems']
    assert return_json['groups']
    assert return_json['devices']
    #assert return_json['subComponents']

    #sleep added to wait for rcm database to be updated with collected version
    time.sleep(30)
    query = 'select count(*) from rcds.version;'
    result = dbconnection.test_db(query,"rcm-compliance-data-service")
    assert result.strip() == '1'

    print('\nTEST: CollectComponentVersions run: PASSED')

    cleanupHAL()

#######################################################################################################################


def cleanupSDS():
    # Delete the test queues
    print('Cleaning up...')

    af_support_tools.rmq_delete_queue(queue='testSystemListRequest')
    af_support_tools.rmq_delete_queue(queue='testSystemListFound')
    af_support_tools.rmq_delete_queue(queue='testComponentCredentialRequest')
    af_support_tools.rmq_delete_queue(queue='testSystemDefinitionEvent')


def cleanupHAL():
    # Delete the test queues
    print('Cleaning up...')
    af_support_tools.rmq_delete_queue(queue='testHalOrchestratorRequest')
    af_support_tools.rmq_delete_queue(queue='testHalOrchestratorResponse')


def bindSDSQueus():
    af_support_tools.rmq_bind_queue(queue='testSystemListRequest',
                                    exchange='exchange.dell.cpsd.syds.system.definition.request',
                                    routing_key='#')

    af_support_tools.rmq_bind_queue(queue='testSystemListFound',
                                    exchange='exchange.dell.cpsd.syds.system.definition.response',
                                    routing_key='#')

    af_support_tools.rmq_bind_queue(queue='testSystemDefinitionEvent',
                                    exchange='exchange.dell.cpsd.syds.system.definition.event',
                                    routing_key='#')

    af_support_tools.rmq_bind_queue(queue='testComponentCredentialRequest',
                                    exchange='exchange.dell.cpsd.cms.credentials.request',
                                    routing_key='#')


def bindHALQueus():
    af_support_tools.rmq_bind_queue(queue='testHalOrchestratorRequest',
                                    exchange='exchange.dell.cpsd.hal.orchestrator.request',
                                    routing_key='#')

    # Create a test queue that will bind to system.definition.response
    af_support_tools.rmq_bind_queue(queue='testHalOrchestratorResponse',
                                    exchange='exchange.dell.cpsd.hal.orchestrator.response',
                                    routing_key='#')


def verifyCSmessage():
    # We need to verify that the triggered component.credentials.addition.requested is valid.

    q_len = 0
    timeout = 0

    while q_len < 1:
        time.sleep(1)
        timeout += 1

        q_len = af_support_tools.rmq_message_count(queue='testComponentCredentialRequest')

        if timeout > 30:
            print('ERROR: CS Request Message took to long to return. Something is wrong')
            cleanupSDS()
            break

    return_message = af_support_tools.rmq_consume_all_messages(queue='testComponentCredentialRequest')

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

    af_support_tools.rmq_purge_queue(queue='testSystemListFound')
    af_support_tools.rmq_purge_queue(queue='testSystemListFound')

    af_support_tools.rmq_publish_message(exchange='exchange.dell.cpsd.syds.system.definition.request',
                                         routing_key='dell.cpsd.syds.converged.system.list.requested',
                                         headers={'__TypeId__': 'com.dell.cpsd.syds.converged.system.list.requested'},
                                         payload=the_payload, payload_type='json')

    q_len = 0
    timeout = 0

    while q_len < 1:
        time.sleep(1)
        timeout += 1

        q_len = af_support_tools.rmq_message_count(queue='testSystemListFound')

        if timeout > 10:
            print('ERROR: Sys Found Response Message took to long to return. Something is wrong')
            cleanupSDS()
            break

    return_message = af_support_tools.rmq_consume_all_messages(queue='testSystemListFound')

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


def verifyConsulUpdate(paqx, context):
    url = 'https://' + host + ':8500/v1/catalog/services'
    resp = requests.get(url, verify=False)
    data = json.loads(resp.text)

    print("Requesting Consul info....")
    print(data)
    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    if data != "":
        if paqx in data:
            assert len(data[paqx]) == 1, "Unexpected number of RCM Fitness Paqx returned."
            assert "contextPath=/" in data[paqx][0], "Unexpected string value returned."
            assert data[paqx][0].endswith(context), "Unexpected end to path string returned."
            print("Consul info verified.")
        return

    assert False, "No Consul info returned."


def registerRackHD(payLoad, responseRegRackHD):
    messageHeaderRequest = {'__TypeId__': 'com.dell.cpsd.rackhd.registration.info.request'}

    af_support_tools.rmq_purge_queue(queue='testRegisterRackHDRequest')
    af_support_tools.rmq_purge_queue(queue='testRegisterRackHDResponse')

    time.sleep(2)

    af_support_tools.rmq_bind_queue(queue='testRegisterRackHDRequest', exchange='exchange.dell.cpsd.controlplane.rackhd.request',
                                    routing_key='#')
    af_support_tools.rmq_bind_queue(queue='testRegisterRackHDResponse', exchange='exchange.dell.cpsd.controlplane.rackhd.response',
                                    routing_key='#')

    af_support_tools.rmq_publish_message(exchange="exchange.dell.cpsd.controlplane.rackhd.request",
                                         routing_key="controlplane.rackhd.endpoint.register",
                                         headers=messageHeaderRequest, payload=payLoad, payload_type='json')

    print("RackHD register request published.")
    time.sleep(5)

    q_len = 0
    timeout = 0

    while q_len < 1:
        time.sleep(1)
        timeout += 1

        q_len = af_support_tools.rmq_message_count(queue='testRegisterRackHDResponse')

        if timeout > 10:
            print('ERROR: Sys Found Response Message took to long to return. Something is wrong')
            break

    my_response_credentials_body = af_support_tools.rmq_consume_message(queue='testRegisterRackHDResponse')
    print(my_response_credentials_body)
    af_support_tools.rmq_payload_to_file(my_response_credentials_body, path + responseRegRackHD)
    print("\nRegister response consumed.")
    data_RackHD = open(path + responseRegRackHD, 'rU')
    dataRackHD = json.load(data_RackHD)

    af_support_tools.rmq_purge_queue(queue='testRegisterRackHDRequest')
    af_support_tools.rmq_purge_queue(queue='testRegisterRackHDResponse')

    if dataRackHD is not None:

        assert "timestamp" in dataRackHD["messageProperties"], "No timestamp included in consumed response."
        assert "message" in dataRackHD["responseInfo"], "No message included in consumed response."
        assert dataRackHD["responseInfo"]["message"] == "SUCCESS", "Registration attempt not returned as success."
        print("\nAll verification steps executed successfully.....")
        print("\nRackHD successfully registered....")
        return

    assert False, "Consumed message not as expected."


def registerVcenter(payLoad, responseRegVcenter):
    messageReqHeader = {'__TypeId__': 'com.dell.cpsd.vcenter.registration.info.request'}

    af_support_tools.rmq_purge_queue(queue='testRegisterVcenterRequest')
    af_support_tools.rmq_purge_queue(queue='testRegisterVcenterResponse')

    time.sleep(2)

    af_support_tools.rmq_bind_queue(queue='testRegisterVcenterRequest', exchange='exchange.dell.cpsd.controlplane.vcenter.request',
                                    routing_key='#')
    af_support_tools.rmq_bind_queue(queue='testRegisterVcenterResponse', exchange='exchange.dell.cpsd.controlplane.vcenter.response',
                                    routing_key='#')

    af_support_tools.rmq_publish_message(exchange="exchange.dell.cpsd.controlplane.vcenter.request",
                                         routing_key="controlplane.hypervisor.vcenter.endpoint.register",
                                         headers=messageReqHeader, payload=payLoad, payload_type='json')

    print("\nVcenter register request published.")
    time.sleep(5)

    q_len = 0
    timeout = 0

    # We need to wait until the queue gets the response message
    while q_len < 1:
        time.sleep(1)
        timeout += 1

        q_len = af_support_tools.rmq_message_count(queue='testRegisterVcenterResponse')

        # If the test queue doesn't get a message then something is wrong
        if timeout > 10:
            print('ERROR: Sys Found Response Message took to long to return. Something is wrong')
            break

    my_response_credentials_body = af_support_tools.rmq_consume_message(queue='testRegisterVcenterResponse')
    print(my_response_credentials_body)
    af_support_tools.rmq_payload_to_file(my_response_credentials_body, path + responseRegVcenter)
    print("\nRegister response consumed.")
    data_Vcenter = open(path + responseRegVcenter, 'rU')
    dataVcenter = json.load(data_Vcenter)

    af_support_tools.rmq_purge_queue(queue='testRegisterVcenterRequest')
    af_support_tools.rmq_purge_queue(queue='testRegisterVcenterResponse')

    if dataVcenter is not None:

        assert "timestamp" in dataVcenter["messageProperties"], "No timestamp included in consumed response."
        assert "message" in dataVcenter["responseInfo"], "No message included in consumed response."
        assert dataVcenter["responseInfo"]["message"] == "SUCCESS", "Registration attempt not returned as success."
        print("\nAll verification steps executed successfully.....")
        print("\nVcenter successfully registered....")
        return

    assert False, "Consumed message not as expected."

#######################################################################################################################
