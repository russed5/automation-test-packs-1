#!/usr/bin/python
# Copyright © 2017 Dell Inc. or its subsidiaries.  All Rights Reserved
import pika
import json
import time
import af_support_tools
import pytest
import os
import re
import traceback
import requests
from collections import Counter


@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    global path
    path = "/home/autouser/PycharmProjects/auto-framework/test_suites/continuous-integration-deploy-suite/rcm-fitness-ci-cd/m_updateFirmware/"
    global restCorrID
    restCorrID = []
    global progURL

    global ssl_options
    ssl_options = {"ca_certs": "/etc/rabbitmq/certs/testca/cacert.pem",
                   "certfile": "/etc/rabbitmq/certs/certs/client/cert.pem",
                   "keyfile": "/etc/rabbitmq/certs/certs/client/key.pem", "cert_reqs": "ssl.CERT_REQUIRED",
                   "ssl_version": "ssl.PROTOCOL_TLSv1_2"}

    # Update config ini files at runtime
    # my_data_file = 'listRCMs.properties'
    my_data_file = os.environ.get(
        'AF_RESOURCES_PATH') + '/continuous-integration-deploy-suite/updateInputs.properties'
    af_support_tools.set_config_file_property_by_data_file(my_data_file)

    # Set config ini file name
    global env_file
    env_file = 'env.ini'

    global host
    host = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')
    global port
    port = af_support_tools.get_config_file_property(config_file=env_file, heading='RabbitMQ', property='port')
    port = int(port)

    global rmq_username
    rmq_username = af_support_tools.get_config_file_property(config_file=env_file, heading='RabbitMQ',
                                                             property='username')
    global rmq_password
    rmq_password = af_support_tools.get_config_file_property(config_file=env_file, heading='RabbitMQ',
                                                             property='password')

    # Set Vars
    global payload_file
    payload_file = 'continuous-integration-deploy-suite/updateInputs.ini'
    global payload_header
    payload_header = 'payload'
    global payload_message
    payload_message = 'dataupdate'
    # global dup_payload_message
    # dup_payload_message = 'dupupdate'
    # global another_dup_payload_message
    # dup2_payload_message = 'anotherdupupdate'
    global payload_rackHD
    payload_rackHD = 'registerrackhd'
    global payload_vcenter
    payload_vcenter = 'registervcenter'

    global ipaddress
    ipaddress = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')
    global cli_username
    cli_username = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                             property='username')
    global cli_password
    cli_password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                             property='password')

    ensurePathExists(path)
    purgeOldOutput(path, "out_")
    print("Previous test output removed at this point.")

    global message_update
    message_update = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                        property=payload_message)
    # global message_dup_update
    # message_dup_update = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
    #                                                     property=dup_payload_message)
    # global message_dup2_update
    # message_dup2_update = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
    #                                                     property=dup2_payload_message)
    global message_rackHD
    message_rackHD = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                        property=payload_rackHD)
    global message_vcenter
    message_vcenter = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                        property=payload_vcenter)

    getSystemDefinition()
    registerRackHD(message_rackHD, "out_registerRackHDResp.json")
    time.sleep(2)
    registerVcenter(message_vcenter, "out_registerVcenterResp.json")

def ensurePathExists(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def purgeOldOutput(dir, pattern):
    for f in os.listdir(dir):
        if re.search(pattern, f) and f.endswith(".json"):
            os.remove(os.path.join(dir, f))
            print("Old output files successfully deleted.")
        else:
            print('Unable to locate output files to remove.')

def resetTestQueues(testRequest, testResponse, testCredsReq, testCredsResp, testSysList, testSysFound):

    credentials = pika.PlainCredentials(rmq_username, rmq_password)
    parameters = pika.ConnectionParameters(host, port, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    af_support_tools.rmq_purge_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username, queue=testRequest,
                                     ssl_enabled=False)
    af_support_tools.rmq_purge_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                     queue=testResponse, ssl_enabled=False)
    af_support_tools.rmq_purge_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                     queue=testCredsReq, ssl_enabled=False)
    af_support_tools.rmq_purge_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                     queue=testCredsResp, ssl_enabled=False)
    af_support_tools.rmq_purge_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                     queue=testSysList, ssl_enabled=False)
    af_support_tools.rmq_purge_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                     queue=testSysFound, ssl_enabled=False)
    # af_support_tools.rmq_purge_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
    #                                  queue=testCompReq, ssl_enabled=False)
    # af_support_tools.rmq_purge_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
    #                                  queue=testCompFound, ssl_enabled=False)

    time.sleep(2)
    print("Old test queues successfully purged.")

    af_support_tools.rmq_bind_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                    queue=testRequest, exchange='exchange.dell.cpsd.controlplane.rackhd.request',
                                    routing_key='#', ssl_enabled=False)
    af_support_tools.rmq_bind_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                    queue=testResponse,
                                    exchange='exchange.dell.cpsd.controlplane.rackhd.response',
                                    routing_key='#', ssl_enabled=False)
    af_support_tools.rmq_bind_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                    queue=testCredsReq, exchange='exchange.dell.cpsd.cms.credentials.request',
                                    routing_key='#', ssl_enabled=False)
    af_support_tools.rmq_bind_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                    queue=testCredsResp, exchange='exchange.dell.cpsd.cms.credentials.response',
                                    routing_key='#', ssl_enabled=False)
    af_support_tools.rmq_bind_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                    queue=testSysList, exchange='exchange.dell.cpsd.syds.system.definition.request',
                                    routing_key='#', ssl_enabled=False)
    af_support_tools.rmq_bind_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                    queue=testSysFound, exchange='exchange.dell.cpsd.syds.system.definition.response',
                                    routing_key='#', ssl_enabled=False)
    # af_support_tools.rmq_bind_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
    #                                 queue=testCompReq, exchange='exchange.dell.cpsd.cms.credentials.response',
    #                                 routing_key='#', ssl_enabled=False)
    # af_support_tools.rmq_bind_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
    #                                 queue=testCompFound, exchange='exchange.dell.cpsd.cms.credentials.response',
    #                                 routing_key='#', ssl_enabled=False)

    print("New test queues successfully initialized.")

def registerRackHD(payLoad, responseRegRackHD):
    messageHeaderRequest = {'__TypeId__': 'com.dell.cpsd.rackhd.registration.info.request'}

    credentials = pika.PlainCredentials(rmq_username, rmq_password)
    parameters = pika.ConnectionParameters(host, port, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    af_support_tools.rmq_purge_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                     queue='testRegisterRackHDRequest', ssl_enabled=False)
    af_support_tools.rmq_purge_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                     queue='testRegisterRackHDResponse', ssl_enabled=False)

    time.sleep(2)

    af_support_tools.rmq_bind_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                    queue='testRegisterRackHDRequest', exchange='exchange.dell.cpsd.controlplane.rackhd.request',
                                    routing_key='#', ssl_enabled=False)
    af_support_tools.rmq_bind_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                    queue='testRegisterRackHDResponse', exchange='exchange.dell.cpsd.controlplane.rackhd.response',
                                    routing_key='#', ssl_enabled=False)

    print(payLoad)
    print(messageHeaderRequest)

    af_support_tools.rmq_publish_message(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                         exchange="exchange.dell.cpsd.controlplane.rackhd.request",
                                         routing_key="controlplane.rackhd.endpoint.register",
                                         headers=messageHeaderRequest, payload=payLoad, payload_type='json',
                                         ssl_enabled=False)

    print("RackHD register request published.")
    time.sleep(5)

    my_response_credentials_body = af_support_tools.rmq_consume_message(host=host, port=port,
                                                                        rmq_username=rmq_username,
                                                                        rmq_password=rmq_username,
                                                                        queue='testRegisterRackHDResponse',
                                                                        ssl_enabled=False)
    af_support_tools.rmq_payload_to_file(my_response_credentials_body, path + responseRegRackHD)
    print("\nRegister response consumed.")
    data_RackHD = open(path + responseRegRackHD, 'rU')
    dataRackHD = json.load(data_RackHD)

    af_support_tools.rmq_purge_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                     queue='testRegisterRackHDRequest', ssl_enabled=False)
    af_support_tools.rmq_purge_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                     queue='testRegisterRackHDResponse', ssl_enabled=False)

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

    credentials = pika.PlainCredentials(rmq_username, rmq_password)
    parameters = pika.ConnectionParameters(host, port, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    af_support_tools.rmq_purge_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                     queue='testRegisterVcenterRequest', ssl_enabled=False)
    af_support_tools.rmq_purge_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                     queue='testRegisterVcenterResponse', ssl_enabled=False)

    time.sleep(2)

    af_support_tools.rmq_bind_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                    queue='testRegisterVcenterRequest', exchange='exchange.dell.cpsd.controlplane.vcenter.request',
                                    routing_key='#', ssl_enabled=False)
    af_support_tools.rmq_bind_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                    queue='testRegisterVcenterResponse', exchange='exchange.dell.cpsd.controlplane.vcenter.response',
                                    routing_key='#', ssl_enabled=False)

    af_support_tools.rmq_publish_message(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                         exchange="exchange.dell.cpsd.controlplane.vcenter.request",
                                         routing_key="controlplane.hypervisor.vcenter.endpoint.register",
                                         headers=messageReqHeader, payload=payLoad, payload_type='json',
                                         ssl_enabled=False)

    print("\nVcenter register request published.")
    time.sleep(5)

    my_response_credentials_body = af_support_tools.rmq_consume_message(host=host, port=port,
                                                                        rmq_username=rmq_username,
                                                                        rmq_password=rmq_username,
                                                                        queue='testRegisterVcenterResponse',
                                                                        ssl_enabled=False)
    af_support_tools.rmq_payload_to_file(my_response_credentials_body, path + responseRegVcenter)
    print("\nRegister response consumed.")
    data_Vcenter = open(path + responseRegVcenter, 'rU')
    dataVcenter = json.load(data_Vcenter)

    af_support_tools.rmq_purge_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                     queue='testRegisterVcenterRequest', ssl_enabled=False)
    af_support_tools.rmq_purge_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                     queue='testRegisterVcenterResponse', ssl_enabled=False)

    if dataVcenter is not None:

        assert "timestamp" in dataVcenter["messageProperties"], "No timestamp included in consumed response."
        assert "message" in dataVcenter["responseInfo"], "No message included in consumed response."
        assert dataVcenter["responseInfo"]["message"] == "SUCCESS", "Registration attempt not returned as success."
        print("\nAll verification steps executed successfully.....")
        print("\nVcenter successfully registered....")
        return

    assert False, "Consumed message not as expected."

def updateFWRequest(payLoad, requestFile, requestCredentials, responseCredentials, responseFile, systemList, systemFound):
    messageReqHeader = {'__TypeId__': 'com.dell.cpsd.service.rcm.capability.update.firmware.requested'}
    print("Host: %s" % host)
    print("Port: %d" % port)

    credentials = pika.PlainCredentials(rmq_username, rmq_password)
    parameters = pika.ConnectionParameters(host, port, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    resetTestQueues('testUpdateFWRequest', 'testUpdateFWResponse', 'testUpdateFWCredsRequest', 'testUpdateFWCredsResp', 'testSystemList', 'testSystemFound')
    print("Queues reset.")

    af_support_tools.rmq_publish_message(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                         exchange="exchange.dell.cpsd.controlplane.rackhd.request",
                                         routing_key="dell.cpsd.service.rcm.capability.update.firmware.requested",
                                         headers=messageReqHeader, payload=payLoad, payload_type='json',
                                         ssl_enabled=False)

    print("\nUpdate request published.")
    time.sleep(20)

    my_request_body = af_support_tools.rmq_consume_message(host=host, port=port,
                                                           rmq_username=rmq_username, rmq_password=rmq_username,
                                                           queue='testUpdateFWRequest',
                                                           ssl_enabled=False)
    af_support_tools.rmq_payload_to_file(my_request_body, path + requestFile)

    my_request_credentials_body = af_support_tools.rmq_consume_all_messages(host=host, port=port,
                                                                       rmq_username=rmq_username,
                                                                       rmq_password=rmq_username,
                                                                        queue='testSystemList',
                                                                        ssl_enabled=False)
    af_support_tools.rmq_payload_to_file(my_request_credentials_body, path + systemList)

    my_response_credentials_body = af_support_tools.rmq_consume_all_messages(host=host, port=port,
                                                                        rmq_username=rmq_username,
                                                                        rmq_password=rmq_username,
                                                                        queue='testSystemFound',
                                                                        ssl_enabled=False)
    af_support_tools.rmq_payload_to_file(my_response_credentials_body, path + systemFound)

    print("\nSystem list and config request/response consumed.")

    my_request_credentials_body = af_support_tools.rmq_consume_message(host=host, port=port,
                                                                       rmq_username=rmq_username,
                                                                       rmq_password=rmq_username,
                                                                        queue='testUpdateFWCredsRequest',
                                                                        ssl_enabled=False)
    af_support_tools.rmq_payload_to_file(my_request_credentials_body, path + requestCredentials)

    my_response_credentials_body = af_support_tools.rmq_consume_message(host=host, port=port,
                                                                        rmq_username=rmq_username,
                                                                        rmq_password=rmq_username,
                                                                        queue='testUpdateFWCredsResp',
                                                                        ssl_enabled=False)
    af_support_tools.rmq_payload_to_file(my_response_credentials_body, path + responseCredentials)

    print("\nUpdate request and credential request/response consumed.")

    time.sleep(180)

    my_response_download_body = af_support_tools.rmq_consume_all_messages(host=host, port=port,
                                                                          rmq_username=rmq_username,
                                                                          rmq_password=rmq_username,
                                                                          queue='testUpdateFWResponse',
                                                                          ssl_enabled=False)
    af_support_tools.rmq_payload_to_file(my_response_download_body, path + responseFile)

    print("\nUpdate progress messages consumed, and expected result.")


def restResponse(input):
    assert "10000/rcm-fitness-paqx/rcm-fitness-api/api/install/firmware" in input["link"][
        "href"], "No URL included in response to query subsequent progress."
    assert input["link"]["method"] == "GET", "Unexpected method returned in response."
    assert len(input["uuid"]) > 16, "Unexpected correlation ID returned"

    print("Link: %s" % input["link"]["href"])
    print("Method: %s" % input["link"]["method"])
    print("length response: %d" % len(input["uuid"]))
    print("Rel: %s" % input["link"]["rel"])
    print("State: %s" % input["state"])
    restCorrID.append(input["uuid"])
    print("Total CorrIDs: %d" % len(restCorrID))

def getSystemDefinition():
    url = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/system/definition/'
    resp = requests.get(url)
    data = json.loads(resp.text)

    if data != "":
        if data["systems"][0]["uuid"] != "":
            with open(path + 'rcmSystemDefinition-VxRack.json', 'w') as outfile:
                json.dump(data, outfile, sort_keys=True, indent=4, ensure_ascii=False)

            global systemUUID
            global secondSystemUUID
            systemUUID = data["systems"][0]["uuid"]
            if len(data["systems"]) > 1:
                secondSystemUUID = data["systems"][1]["uuid"]

        else:
            print("\nNo System UUID returned in REST response")
    return systemUUID

def verifyCorrelationIDs():
    for item in listCorrID:
        print(item)
        print(origCorrID)
        assert origCorrID in item, "Unexpected Correlation ID detailed."
        print("All associated corrIDs verified to include original requests corrID.")
        return
    assert False, "No list of Correlation IDs available."


def duplicateUpdateFWRequest(payLoad, dupPayLoad, anotherDupPayLoad, requestFile, requestCredentials, responseCredentials, responseFile):
    messageReqHeader = {'__TypeId__': 'com.dell.cpsd.service.rcm.capability.update.firmware.requested'}
    print("Host: %s" % host)
    print("Port: %d" % port)

    credentials = pika.PlainCredentials(rmq_username, rmq_password)
    parameters = pika.ConnectionParameters(host, port, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    resetTestQueues('testUpdateFWRequest', 'testUpdateFWResponse', 'testUpdateFWCredsRequest', 'testUpdateFWCredsResp')
    print("Queues reset.")

    af_support_tools.rmq_publish_message(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                         exchange="exchange.dell.cpsd.controlplane.rackhd.request",
                                         routing_key="dell.cpsd.service.rcm.capability.update.firmware.requested",
                                         headers=messageReqHeader, payload=payLoad, payload_type='json',
                                         ssl_enabled=False)

    print("Update request publish.")
    time.sleep(20)

    af_support_tools.rmq_publish_message(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                         exchange="exchange.dell.cpsd.controlplane.rackhd.request",
                                         routing_key="dell.cpsd.service.rcm.capability.update.firmware.requested",
                                         headers=messageReqHeader, payload=dupPayLoad, payload_type='json',
                                         ssl_enabled=False)

    print("Update request publish.")
    time.sleep(20)

    af_support_tools.rmq_publish_message(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                         exchange="exchange.dell.cpsd.controlplane.rackhd.request",
                                         routing_key="dell.cpsd.service.rcm.capability.update.firmware.requested",
                                         headers=messageReqHeader, payload=anotherDupPayLoad, payload_type='json',
                                         ssl_enabled=False)

    print("Update request publish.")
    time.sleep(20)

    my_request_body = af_support_tools.rmq_consume_message(host=host, port=port,
                                                           rmq_username=rmq_username, rmq_password=rmq_username,
                                                           queue='testUpdateFWRequest',
                                                           ssl_enabled=False)
    af_support_tools.rmq_payload_to_file(my_request_body, path + requestFile)

    my_request_credentials_body = af_support_tools.rmq_consume_message(host=host, port=port,
                                                                       rmq_username=rmq_username,
                                                                       rmq_password=rmq_username,
                                                                        queue='testUpdateFWCredsRequest',
                                                                        ssl_enabled=False)
    af_support_tools.rmq_payload_to_file(my_request_credentials_body, path + requestCredentials)

    my_response_credentials_body = af_support_tools.rmq_consume_message(host=host, port=port,
                                                                        rmq_username=rmq_username,
                                                                        rmq_password=rmq_username,
                                                                        queue='testUpdateFWCredsResp',
                                                                        ssl_enabled=False)
    af_support_tools.rmq_payload_to_file(my_response_credentials_body, path + responseCredentials)

    print("Update request and credential request/response consumed.")

    time.sleep(180)

    my_response_download_body = af_support_tools.rmq_consume_all_messages(host=host, port=port,
                                                                          rmq_username=rmq_username,
                                                                          rmq_password=rmq_username,
                                                                          queue='testUpdateFWResponse',
                                                                          ssl_enabled=False)
    af_support_tools.rmq_payload_to_file(my_response_download_body, path + responseFile)

    print("Update progress messages consumed.")

def verifyPublishedAttributes(filename):
    paramIndex = 0
    global listCorrID
    listCorrID = []
    with open(filename, "rU") as dataFile:
        dataInput = json.load(dataFile)

    print(dataInput.keys())
    print("\nName of file: %s" % dataFile.name)

    print("\nVerifying each of the published message attributes.")

    if dataInput is not None:
        assert "messageProperties" in dataInput, "Message Props missing from published request."
        assert "commandBody" in dataInput, "Command Body missing from published request."
        assert "componentBody" in dataInput, "Component Body missing from published request."

        if len(dataInput["messageProperties"]) > 0:
            assert "timestamp" in dataInput["messageProperties"], "Timestamp not included in published attributes."
            assert "correlationId" in dataInput["messageProperties"], "Correlation Id not included in published attributes."
            assert "replyTo" in dataInput["messageProperties"], "Reply To not included in published attributes."
            print("\nPublished messageProperties attributes verified.")
            listCorrID.append(dataInput["messageProperties"]["correlationId"])
            global origCorrID
            origCorrID = dataInput["messageProperties"]["correlationId"]
            assert len(dataInput["commandBody"]) > 0, "Command Body is empty."
            assert dataInput["commandBody"]["CommandType"] == "UpdateFirmware", "Command Type value not as expected."
            assert len(dataInput["commandBody"]["CommandParameters"]) == 3, "Incomplete Command Parameters published."
            print("\nPublished commandBody attributes verified.")
            print("Number of command parameters: %d" % len(dataInput["commandBody"]["CommandParameters"]))

            for index in range((len(dataInput["commandBody"]["CommandParameters"]))):
                print("Loop %d" % index)
                if dataInput["commandBody"]["CommandParameters"][index]["key"] == "EmulateWorkflow":
                    print("Work Flow Key: %s" % dataInput["commandBody"]["CommandParameters"][index]["value"])
                    assert "on" in dataInput["commandBody"]["CommandParameters"][index]["value"], "Expected workFlow not included in published request."
                    print("FLOW: You are here...")

                if dataInput["commandBody"]["CommandParameters"][index]["key"] == "serverFilePath":
                    print("File Path Key: %s" % dataInput["commandBody"]["CommandParameters"][index]["value"])
                    assert "BIOS_PFWCY" in dataInput["commandBody"]["CommandParameters"][index]["value"], "Expected filename not included in published request."
                    global updatePath
                    updatePath = dataInput["commandBody"]["CommandParameters"][index]["value"]
                    print(updatePath)
                    print("PATH: You are here...")

                if dataInput["commandBody"]["CommandParameters"][index]["key"] == "subComponentType":
                    print("Sub Comp Key: %s" % dataInput["commandBody"]["CommandParameters"][index]["value"])
                    assert "BIOS" in dataInput["commandBody"]["CommandParameters"][index]["value"], "Expected subComp not included in published request."
                    global subComp
                    subComp = dataInput["commandBody"]["CommandParameters"][index]["value"]
                    print(subComp)
                    print("COMP: You are here...")

            assert dataInput["componentBody"]["componentUuid"] is not None, "Component UUID seems to be empty."
            global subCompUUID
            subCompUUID = dataInput["componentBody"]["componentUuid"]
            print(subCompUUID)
            print("\nPublished commandParameters attributes verified.")
            print("All Done: You are here......")
            return

    assert False, ("Publish download request message not complete.")

def verifyConsumedAttributes(requestFile, responseFile):
    paramIndex = 0
    messageIndex = 0
    ackCount = 0
    count = 0
    completeCount = 0

    data_request = open(requestFile, 'rU')
    dataInput = json.load(data_request)

    data_resp = open(responseFile, 'rU')
    dataResp = json.load(data_resp)

    messageCount = len(dataResp)
    print("Number of messages consumed: %d" % messageCount)

    if dataResp is not None:
        while messageIndex < messageCount:
            if dataResp[messageIndex]["controlPlaneCommand"] == "UpdateFirmware":
                print("\nStarting to verify START attributes consumed....")
                assert messageIndex == 0, "First message in response is not the expected ack."
                # assert data["controlPlaneCommand"] == "UpdateFirmware", "Incorrect control plane command included, expected UPDATEFIRMWARE."
                for index in range(3):
                    if dataResp[messageIndex]["CommandParameters"][index]["value"] == "running":
                        assert dataResp[messageIndex]["CommandParameters"][index]["key"] == "status"
                    if "Racadm" in dataResp[messageIndex]["CommandParameters"][index]["value"]:
                        assert dataResp[messageIndex]["CommandParameters"][index]["key"] == "name"
                    if dataResp[messageIndex]["CommandParameters"][index]["value"] == "123":
                        assert dataResp[messageIndex]["CommandParameters"][index]["key"] == "InstanceID"

                    assert "timestamp" in dataResp[messageIndex]["messageProperties"], "No timestamp included in consumed start message."
                    listCorrID.append(dataResp[messageIndex]["messageProperties"]["correlationId"])
                    assert dataResp[messageIndex]["messageProperties"]["correlationId"] == dataInput["messageProperties"]["correlationId"], "Response CorrID does not match requests."
                    assert dataResp[messageIndex]["messageProperties"]["replyTo"] == "rcm-fitness-client-parent.rcm-fitness-client", "Unexpected value returned in replyTo field."
                    print("\nSTART: You are here..... Index: %d" % index)
                ackCount += 1
                print("Acknowledge: %d" % ackCount)
                print("\nReturned acknowledge message attributes verified.")

            if dataResp[messageIndex]["controlPlaneCommand"] == "Status":
                print("\nStarting to verify RUNNING attributes consumed....")
                print("ParamIndex: %d" % paramIndex)
                while paramIndex < 3:
                    print("Entering....")
                    print("ParamIndex: %d" % paramIndex)
                    print("Value: %s" % dataResp[messageIndex]["CommandParameters"][paramIndex]["value"])
                    if dataResp[messageIndex]["CommandParameters"][paramIndex]["value"] == "running":
                        for index in range(3):
                            if dataResp[messageIndex]["CommandParameters"][index]["value"] == "running":
                                assert dataResp[messageIndex]["CommandParameters"][index]["key"] == "status", "Unexpected Status"
                                print("\nProgress %d status correct." % messageIndex)
                            if "Racadm" in dataResp[messageIndex]["CommandParameters"][index]["value"]:
                                assert dataResp[messageIndex]["CommandParameters"][index]["key"] == "name", "Unexpected Name"
                                print("\nProgress %d Name correct." % messageIndex)
                            if dataResp[messageIndex]["CommandParameters"][index]["value"] == "123":
                                assert dataResp[messageIndex]["CommandParameters"][index]["key"] == "InstanceID", "Unexpected InstanceID"
                                print("\nProgress %d Instance correct." % messageIndex)

                        assert "timestamp" in dataResp[messageIndex]["messageProperties"], "No timestamp included in consumed start message."
                        listCorrID.append(dataResp[messageIndex]["messageProperties"]["correlationId"])
                        assert dataResp[messageIndex]["messageProperties"]["correlationId"] == dataInput["messageProperties"]["correlationId"], "Response CorrID does not match requests."
                        assert dataResp[messageIndex]["messageProperties"]["replyTo"] == "rcm-fitness-client-parent.rcm-fitness-client", "Unexpected value returned in replyTo field."
                        print("\nReturned progress message attributes verified.")

                    if dataResp[messageIndex]["CommandParameters"][paramIndex]["value"] == "succeeded":
                        print("\nStarting to verify SUCCEEDED attributes consumed....")
                        completeCount += 1
                        for index in range(3):
                            if dataResp[messageIndex]["CommandParameters"][index]["value"] == "succeeded":
                                assert dataResp[messageIndex]["CommandParameters"][index]["key"] == "status", "Unexpected Status"
                                print("\nComplete %d status correct." % completeCount)
                            if "Racadm" in dataResp[messageIndex]["CommandParameters"][index]["value"]:
                                assert dataResp[messageIndex]["CommandParameters"][index]["key"] == "name", "Unexpected Name"
                                print("\nComplete %d Name correct." % completeCount)
                            if dataResp[messageIndex]["CommandParameters"][index]["value"] == "123":
                                assert dataResp[messageIndex]["CommandParameters"][index]["key"] == "InstanceID", "Unexpected InstanceID"
                                print("\nComplete %d Instance correct." % completeCount)

                        assert "timestamp" in dataResp[messageIndex]["messageProperties"], "No timestamp included in consumed start message."
                        listCorrID.append(dataResp[messageIndex]["messageProperties"]["correlationId"])
                        assert dataResp[messageIndex]["messageProperties"]["correlationId"] == dataInput["messageProperties"]["correlationId"], "Response CorrID does not match requests."
                        assert dataResp[messageIndex]["messageProperties"]["replyTo"] == "rcm-fitness-client-parent.rcm-fitness-client", "Unexpected value returned in replyTo field."
                        assert messageIndex == messageCount - 1, "Success message is not the last consume, are all in sequence?"
                        print("\nReturned complete message attributes verified.")
                    paramIndex += 1
                paramIndex = 0
                count += 1
                print("\nComplete count: %d" % completeCount)
                print("\nCount: %d" % count)

            messageIndex += 1
        print("Final count: %d" % count)
        assert count >= 10, "Unexpected number of progress messages returned."
        assert ackCount == 1, "Unexpected number of acknowledge messages returned."
        assert completeCount == 1, "Unexpected number of Succeeded messages returned."
        return
    assert False, "Consumed message not as expected."

def verifyCredentialRequest(filename, credRequest, component):
    index = 0
    with open(filename, "rU") as dataFile:
        dataInput = json.load(dataFile)

    with open(credRequest, "rU") as dataFile:
        dataCredRequest = json.load(dataFile)

    if dataCredRequest is not None:
        while index < len(dataCredRequest["componentCredentials"]):
            assert len(dataCredRequest["componentCredentials"]) == 5, "Unexpected number of component credentials requested."
            if dataCredRequest["componentCredentials"][index]["componentUuid"] == dataInput["componentBody"]["componentUuid"]:
                assert "timestamp" in dataCredRequest["messageProperties"], "No timestamp included in credential request message."
                listCorrID.append(dataCredRequest["messageProperties"]["correlationId"])
                assert dataInput["messageProperties"]["correlationId"] in dataCredRequest["messageProperties"]["correlationId"], "Correlation ID not matching original request."
                assert "rackhd-adapter" in dataCredRequest["messageProperties"]["replyTo"], "Unexpected replyTo value detailed in request."
                # assert dataInput["componentBody"]["componentUuid"] == dataCredRequest["componentCredentials"][index]["componentUuid"]
                assert dataCredRequest["componentCredentials"][index]["name"] == component, "Unexpected component name detailed."
                assert dataCredRequest["encryptionParameters"]["algorithm"] == "RSA", "Unexpected Encryption algorithm detailed."
                assert len(dataCredRequest["encryptionParameters"]["publicKeyString"]) > 100, "Unexpected public key value detailed."
                assert len(dataCredRequest["componentCredentials"][index]["endpointUuid"]) > 24, "Unexpected endpointUuid detailed."
                assert len(dataCredRequest["componentCredentials"][index]["credentialUuid"]) > 24, "Unexpected credentialUuid detailed."
                print("\nPublished credential request attributes verified.")
            index += 1
        return
    assert False, "Consumed message not as expected."

def verifyCredentialResponse(filename, credRequest, credResponse, component):
    epUuid = []
    credUuid = []
    compUuid = []
    index = 0
    with open(filename, "rU") as dataFile:
        dataInput = json.load(dataFile)
    with open(credRequest, "rU") as dataFile:
        dataCredRequest = json.load(dataFile)
    with open(credResponse, "rU") as dataFile:
        dataCredResponse = json.load(dataFile)

    if dataCredResponse is not None:
        while index < len(dataCredResponse["componentCredentialElements"]):
            assert len(dataCredResponse["componentCredentialElements"]) == 5, "Unexpected number of component credentials returned."
            epUuid.append(dataCredResponse["componentCredentialElements"][index]["endpointUuid"])
            credUuid.append(dataCredResponse["componentCredentialElements"][index]["credentialUuid"])
            compUuid.append(dataCredResponse["componentCredentialElements"][index]["componentUuid"])

            if dataInput["componentBody"]["componentUuid"] == dataCredResponse["componentCredentialElements"][index]["componentUuid"]:
                assert "timestamp" in dataCredResponse["messageProperties"], "No timestamp included in credential response message."
                listCorrID.append(dataCredResponse["messageProperties"]["correlationId"])
                assert dataCredRequest["messageProperties"]["correlationId"] == dataCredResponse["messageProperties"]["correlationId"], "Correlation ID not matching original request."
                assert "credentials-service" in dataCredResponse["messageProperties"]["replyTo"], "Unexpected replyTo value detailed in response."
                assert dataCredResponse["componentCredentialElements"][index]["name"] == component, "Unexpected component name detailed in response."
                assert len(dataCredResponse["componentCredentialElements"][index]["credentialElement"]["username"]) > 100, "Unexpected encrypted username detailed."
                assert len(dataCredResponse["componentCredentialElements"][index]["credentialElement"]["password"]) > 100, "Unexpected encrypted username detailed."
                assert len(dataCredResponse["componentCredentialElements"][index]["endpointUuid"]) > 24, "Unexpected endpointUuid detailed."
                print("EpUUID: %s" % dataCredResponse["componentCredentialElements"][index]["endpointUuid"])
                assert len(dataCredResponse["componentCredentialElements"][index]["credentialUuid"]) > 24, "Unexpected credentialUuid detailed."
                print("CredUUID: %s" % dataCredResponse["componentCredentialElements"][index]["credentialUuid"])
            index += 1

        epUuid = set(epUuid)
        assert len(epUuid) == len(dataCredResponse["componentCredentialElements"]), "EndPt IDs are not all unique."
        credUuid = set(credUuid)
        assert len(credUuid) == len(dataCredResponse["componentCredentialElements"]), "Cred IDs are not all unique."
        compUuid = set(compUuid)
        assert len(compUuid) == len(dataCredResponse["componentCredentialElements"]), "Comp IDs are not all unique."

        # print(epUuid)

        for i in range(len(dataCredResponse["componentCredentialElements"])):
            assert dataCredResponse["componentCredentialElements"][i]["credentialElement"]["username"] != dataCredResponse["componentCredentialElements"][i]["credentialElement"]["password"], "Username and password should not match."
            # print("Username: %s" % dataCredResponse["componentCredentialElements"][i]["credentialElement"]["username"])
            # print("Password: %s" % dataCredResponse["componentCredentialElements"][i]["credentialElement"]["password"])

        print("\nReturned credential request attributes verified.")
        return
    assert False, "Consumed message not as expected."

def verifySystemDefRequest(sysRequest, identifier):
    # paramIndex = 0
    with open(sysRequest, "rU") as dataFile:
        dataInput = json.load(dataFile)

    print("Verifying each of the published message attributes.")

    if dataInput is not None:
        if len(dataInput[0]["messageProperties"]) > 0:
            assert "timestamp" in dataInput[0]["messageProperties"], "Timestamp not included in published attributes."
            listCorrID.append(dataInput[0]["messageProperties"]["correlationId"])
            assert "correlationId" in dataInput[0]["messageProperties"], "Correlation Id not included in published attributes."
            assert "replyTo" in dataInput[0]["messageProperties"], "Reply To not included in published attributes."
            print("\nSystem List request verified....")

        if len(dataInput[1]["messageProperties"]) > 0:
            if len(dataInput[1]["componentsFilter"]) > 0:
                assert "timestamp" in dataInput[1]["messageProperties"], "Timestamp not included in published attributes."
                listCorrID.append(dataInput[1]["messageProperties"]["correlationId"])
                assert "correlationId" in dataInput[1]["messageProperties"], "Correlation Id not included in published attributes."
                assert "replyTo" in dataInput[1]["messageProperties"], "Reply To not included in published attributes."
                assert dataInput[1]["componentsFilter"]["systemIdentifier"] == identifier, "Identifier not included in config request."
                assert dataInput[1]["componentsFilter"]["systemUuid"] == systemUUID, "System UUID not included in config request."
                print("\nSystem config request verified....")

        assert dataInput[0]["messageProperties"]["replyTo"] == dataInput[1]["messageProperties"]["replyTo"]
        print("\nPublished system definition request attributes verified.")
        return

    assert False, ("Publish system config request message not complete.")

def verifySystemDefResponse(sysResponse, identifier):

    with open(sysResponse, "rU") as dataFile:
        dataResp = json.load(dataFile)

    print("Verifying each of the returned System Definition message attributes.")
    if dataResp is not None:
        if len(dataResp[0]["messageProperties"]) > 0:
            assert "timestamp" in dataResp[0]["messageProperties"], "Timestamp not included in returned attributes."
            listCorrID.append(dataResp[0]["messageProperties"]["correlationId"])
            assert "correlationId" in dataResp[0]["messageProperties"], "Correlation Id not included in returned attributes."
            assert "replyTo" in dataResp[0]["messageProperties"], "Reply To not included in returned attributes."
            if len(dataResp[0]["convergedSystems"]) > 0:
                assert dataResp[0]["convergedSystems"][0]["uuid"] == systemUUID, "System UUID not included in list response."
                assert dataResp[0]["convergedSystems"][0]["identity"]["identifier"] == identifier, "System Identifier not included in list response."
                assert len(dataResp[0]["convergedSystems"][0]["groups"])  == 0, "Expected no groups detailed in list response."
                assert len(dataResp[0]["convergedSystems"][0]["endpoints"]) == 0, "Expected no endpoints detailed in list response."
                assert len(dataResp[0]["convergedSystems"][0]["components"]) == 0, "Expected no components detailed in list response."
                print("\nSystem List message properties verified.")
        if len(dataResp[0]["messageProperties"]) > 0:
            assert "timestamp" in dataResp[1]["messageProperties"], "Timestamp not included in returned attributes."
            listCorrID.append(dataResp[1]["messageProperties"]["correlationId"])
            assert "correlationId" in dataResp[1]["messageProperties"], "Correlation Id not included in returned attributes."
            assert "replyTo" in dataResp[1]["messageProperties"], "Reply To not included in returned attributes."
            if len(dataResp[1]["convergedSystems"]) > 0:
                assert dataResp[1]["convergedSystems"][0]["uuid"] == systemUUID, "System UUID not included in list response."
                assert dataResp[1]["convergedSystems"][0]["identity"]["identifier"] == identifier, "System Identifier not included in list response."
                if len(dataResp[1]["convergedSystems"][0]["groups"]) > 0:
                    groupTotal = len(dataResp[1]["convergedSystems"][0]["groups"])
                    for groupIndex in range(groupTotal):
                        if dataResp[1]["convergedSystems"][0]["groups"][groupIndex]["type"] == "VIRTUALIZATION":
                            assert dataResp[1]["convergedSystems"][0]["groups"][groupIndex]["name"] == "SystemVirtualization", "Group name not as expected."
                            assert dataResp[1]["convergedSystems"][0]["groups"][groupIndex]["parentSystemUuids"][0] == systemUUID, "Group parentSysID not as expected."
                        if dataResp[1]["convergedSystems"][0]["groups"][groupIndex]["type"] == "COMPUTE":
                            assert dataResp[1]["convergedSystems"][0]["groups"][groupIndex]["name"] == "SystemCompute", "Group name not as expected."
                            assert dataResp[1]["convergedSystems"][0]["groups"][groupIndex]["parentSystemUuids"][0] == systemUUID, "Group parentSysID not as expected."
                        print("\nSystem Config group message properties verified.")
                if len(dataResp[1]["convergedSystems"][0]["endpoints"]) > 0:
                    epTotal = len(dataResp[1]["convergedSystems"][0]["endpoints"])
                    for epIndex in range(epTotal):
                        assert "credentialUuid" in \
                               dataResp[1]["convergedSystems"][0]["endpoints"][epIndex]["credentials"][0], "No credUUID detailed for endpoint."
                        print("Credential UUID length: %d" % len(dataResp[1]["convergedSystems"][0]["endpoints"][epIndex]["credentials"][0]["credentialUuid"]))
                        assert len(dataResp[1]["convergedSystems"][0]["endpoints"][epIndex]["credentials"][0]["credentialUuid"]) > 32, "Unexpected credUUID detailed for endpoint."
                        print("\nSystem Config endpoint message properties verified.")
                        #print("Here you are....3")

            assert dataResp[0]["messageProperties"]["replyTo"] == dataResp[1]["messageProperties"]["replyTo"]
            print("\nReturned system definition request attributes verified.")
            return
    assert False, ("Publish system config response message not complete.")

def verifyRESTupdateRequest(filename):

    resetTestQueues('testUpdateFWRequest', 'testUpdateFWResponse', 'testUpdateFWCredsRequest', 'testUpdateFWCredsResp', 'testSystemList', 'testSystemFound')
    #resetTestQueues('testUpdateFWRequest', 'testUpdateFWResponse')
    print("Queues reset.")

    print("Path: %s" % updatePath)
    print("SubComp: %s" % subComp)
    print("subCompUUID: %s" % subCompUUID)
    mode = 'on'
    url = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/install/firmware/'
    payload = {'filePath': updatePath, 'subComponentType': subComp, 'deviceId': subCompUUID, 'emulationMode': mode}
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    resp = requests.post(url, data=json.dumps(payload), headers=headers)
    # data = json.dumps(payload)


    print("Returned status code: %d" % resp.status_code)
    data = json.loads(resp.text)
    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    with open(filename, 'a') as outfile:
        json.dump(data, outfile, sort_keys=True, indent=4, ensure_ascii=False)

    print(data)
    if data != "":
        if data["state"] == "IN_PROGRESS":
            restResponse(data)
            global origRestCorrID
            origRestCorrID = data["uuid"]
            global progURL
            progURL = data["link"]["href"]
            print("Update request's initial response verified.")
            return
    assert False, ("Initial REST update request not complete.")

def verifyRESTupdateResponse(filename):
    url = progURL
    print(restCorrID)
    print("\n")
    resp = requests.get(url)
    data = json.loads(resp.text)
    assert resp.status_code == 200, "Request has not been acknowledged as expected."
    with open(filename, 'a') as outfile:
        json.dump(data, outfile, sort_keys=True, indent=4, ensure_ascii=False)

    if data != "":
        if data["state"] == "IN_PROGRESS":
            restResponse(data)
            print("First progress update verified.")

    time.sleep(100)
    resp = requests.get(url)
    data = json.loads(resp.text)
    if data != "":
        if data["state"] == "IN_PROGRESS":
            restResponse(data)
            print("Second progress update verified.")

    time.sleep(100)
    resp = requests.get(url)
    data = json.loads(resp.text)
    if data != "":
        if data["state"] == "COMPLETE":
            restResponse(data)
            print("Progress response marked COMPLETE verified.")

    time.sleep(5)
    resp = requests.get(url)
    data = json.loads(resp.text)
    if data != "":
        if data["state"] == "COMPLETE":
            restResponse(data)
            print("Progress response on repeated query marked COMPLETE verified.")

        for item in restCorrID:
            print("Total CorrIDs: %d" % len(restCorrID))
            print(item)
            print(origRestCorrID)
            assert len(restCorrID) == 5, "Unexpected number of total Correlation IDs in list."
            assert origRestCorrID in item, "Unexpected Correlation ID detailed."

            print("All associated REST corrIDs verified to include original request's corrID.")

        return
    assert False, ("At least one of REST update response not complete.")



@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.rcm_fitness_mvp
def test_updateFWRequest():
    updateFWRequest(message_update, "out_updateRequest.json", "out_requestCreds.json", "out_responseCreds.json", "out_updateResponse.json", "out_systemDefReq.json", "out_systemDefResp.json")

@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.rcm_fitness_mvp
def test_verifyPublishedAttributes():
    verifyPublishedAttributes(path + "out_updateRequest.json")

@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.rcm_fitness_mvp
def test_verifyConsumedAttributes():
    verifyConsumedAttributes(path + "out_updateRequest.json", path + "out_updateResponse.json")

@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.rcm_fitness_mvp
def test_verifySystemDefRequest():
    verifySystemDefRequest(path + "out_systemDefReq.json", "VXRACKFLEX")


@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.rcm_fitness_mvp
def test_verifySystemDefResponse():
    verifySystemDefResponse(path + "out_systemDefResp.json", "VXRACKFLEX")

@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.rcm_fitness_mvp
def test_verifyCredentialRequest():
    verifyCredentialRequest(path + "out_updateRequest.json", path + "out_requestCreds.json", "RACKHD")

@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.rcm_fitness_mvp
def test_verifyCredentialResponse():
    verifyCredentialResponse(path + "out_updateRequest.json", path +  "out_requestCreds.json", path + "out_responseCreds.json", "RACKHD")


@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.rcm_fitness_mvp
def test_verifyCorrelationIDs():
    verifyCorrelationIDs()

# @pytest.mark.rcm_fitness_mvp_extended
# @pytest.mark.rcm_fitness_mvp
# def test_verifyRESTupdateRequest():
#     verifyRESTupdateRequest("out_restRequest.json")
#
# @pytest.mark.rcm_fitness_mvp_extended
# @pytest.mark.rcm_fitness_mvp
# def test_verifyRESTupdateResponse():
#     verifyRESTupdateResponse("out_restResponse.json")

#@pytest.mark.rcm_fitness_mvp_extended
#@pytest.mark.rcm_fitness_mvp
# def test_duplicateUpdateFWRequest():
#     duplicateUpdateFWRequest(message_update, message_dup_update, message_dup2_update, "out_dupUpdateRequest.json", "out_dupRequestCreds.json", "out_dupResponseCreds.json", "out_dupUpdateResponse.json")