#!/usr/bin/python
# Copyright © 2017 Dell Inc. or its subsidiaries.  All Rights Reserved
import logging
import pika
import json
import time
import requests
import af_support_tools
import pytest
import os
import re


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


@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    global dataInput
    dataInput = dict()
    global path
    path = "/home/autouser/PycharmProjects/auto-framework/test_suites/continuous-integration-deploy-suite/rcm-fitness-ci-cd/d_getRCMDetails/"
    global ssl_options
    ssl_options = {"ca_certs": "/etc/rabbitmq/certs/testca/cacert.pem",
                   "certfile": "/etc/rabbitmq/certs/certs/client/cert.pem",
                   "keyfile": "/etc/rabbitmq/certs/certs/client/key.pem", "cert_reqs": "ssl.CERT_REQUIRED",
                   "ssl_version": "ssl.PROTOCOL_TLSv1_2"}

    # Update config ini files at runtime
    my_data_file = os.environ.get('AF_RESOURCES_PATH') + '/continuous-integration-deploy-suite/getRCMDetails.properties'
    af_support_tools.set_config_file_property_by_data_file(my_data_file)
    logging.getLogger('pika').setLevel(logging.DEBUG)
    # Set config ini file name
    global env_file
    env_file = 'env.ini'

    global hostTLS
    hostTLS = "amqp"
    # host = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='tls_hostname')
    global host
    host = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')
    global portTLS
    portTLS = af_support_tools.get_config_file_property(config_file=env_file, heading='RabbitMQ', property='ssl_port')
    # port = af_support_tools.get_config_file_property(config_file=env_file, heading='RabbitMQ', property='port')
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
    payload_file = 'continuous-integration-deploy-suite/getRCMDetails.ini'
    global payload_header
    payload_header = 'inputs'
    global payload_data
    payload_data = 'data'
    global payload_dataInvalidCorrID
    payload_dataInvalidCorrID = 'datainvalidcorrid'
    global payload_dataIP
    payload_dataIP = 'dataip'
    global payload_dataInvalidRoutingKey
    payload_dataInvalidRoutingKey = 'datainvalidroutingkey'
    global payload_dataInvalidUUID
    payload_dataInvalidUUID = 'datainvaliduuid'
    global payload_dataNoCorrID
    payload_dataNoCorrID = 'datanocorrid'
    global payload_dataNoHostname
    payload_dataNoHostname = 'datanohostname'
    global payload_dataNoKey
    payload_dataNoKey = 'datanokey'
    global payload_dataNoUUID
    payload_dataNoUUID = 'datanouuid'
    global payload_dataAllEmpty
    payload_dataAllEmpty = 'dataallempty'
    global payload_dataSpaces
    payload_dataSpaces = 'dataspaces'
    global payload_dataVxRack1
    payload_dataVxRack1 = 'datavxrack1'
    global payload_dataVxRack2
    payload_dataVxRack2 = 'datavxrack2'
    # global payload_dataVxRack3
    # payload_dataVxRack3 = 'datavxrack3'
    # global payload_dataVxRack4
    # payload_dataVxRack4 = 'datavxrack4'

    ensurePathExists(path)
    purgeOldOutput(path, "getRCMsRe")

    deleteTestQueues('testGetRCMDetailsRequest', 'testGetRCMDetailsResponse')

    getAvailableRCMs("VxRack", "1000 FLEX", "9.2", "9.2.2")
    # with open(path + "getRcmDetailsInputs.json", 'rt') as dataFileIN:
    #     data = json.load(dataFileIN)

    message = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                        property=payload_data)
    print("Message: %s" % message)
    messageInvalidCorrID = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                                     property=payload_dataInvalidCorrID)
    print("MessageInvalidCorrID: %s" % messageInvalidCorrID)
    messageIP = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                          property=payload_dataIP)
    messageInvalidRoutingKey = af_support_tools.get_config_file_property(config_file=payload_file,
                                                                         heading=payload_header,
                                                                         property=payload_dataInvalidRoutingKey)
    messageInvalidUUID = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                                   property=payload_dataInvalidUUID)
    messageNoCorrID = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                                property=payload_dataNoCorrID)
    messageNoHostname = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                                  property=payload_dataNoHostname)
    messageNoKey = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                             property=payload_dataNoKey)
    messageNoUUID = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                              property=payload_dataNoUUID)
    messageAllEmpty = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                                property=payload_dataAllEmpty)
    messageSpaces = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                              property=payload_dataSpaces)
    messageVxrack1 = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                              property=payload_dataVxRack1)
    messageVxrack2 = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                              property=payload_dataVxRack2)
    # messageVxrack3 = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
    #                                                          property=payload_dataVxRack3)
    # messageVxrack4 = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
    #                                                          property=payload_dataVxRack4)

    updatedMessageInvalidCorrID = convertStrToDict(messageInvalidCorrID)
    updatedMessageIP = convertStrToDict(messageIP)
    updatedMessageInvalidRoutingKey = convertStrToDict(messageInvalidRoutingKey)
    updatedMessageNoCorrID = convertStrToDict(messageNoCorrID)
    updatedMessageNoHostname = convertStrToDict(messageNoHostname)
    updatedMessageNoKey = convertStrToDict(messageNoKey)
    updatedMessageVxrack1 = convertStrToDict(messageVxrack1)
    updatedMessageVxrack2 = convertStrToDict(messageVxrack2)
    # updatedMessageVxrack3 = convertStrToDict(messageVxrack3)
    # updatedMessageVxrack4 = convertStrToDict(messageVxrack4)

    updatedMessageInvalidCorrID['uuid'] = getAvailableRCMs("VxRack", "1000 FLEX", "9.2", "9.2.2")
    updatedMessageIP['uuid'] = getAvailableRCMs("VxRack", "1000 FLEX", "9.2", "9.2.2")
    updatedMessageInvalidRoutingKey['uuid'] = getAvailableRCMs("VxRack", "1000 FLEX", "9.2", "9.2.2")
    updatedMessageNoCorrID['uuid'] = getAvailableRCMs("VxRack", "1000 FLEX", "9.2", "9.2.2")
    updatedMessageNoHostname['uuid'] = getAvailableRCMs("VxRack", "1000 FLEX", "9.2", "9.2.2")
    updatedMessageNoKey['uuid'] = getAvailableRCMs("VxRack", "1000 FLEX", "9.2", "9.2.2")
    updatedMessageVxrack1['uuid'] = getAvailableRCMs("VxRack", "1000 FLEX", "9.2", "9.2.2")
    # getAvailableRCMs("VxRack", "1000 FLEX", "9.2", "9.2.1")
    updatedMessageVxrack2['uuid'] = getAvailableRCMs("VxRack", "1000 FLEX", "9.2", "9.2.1")
    # getAvailableRCMs("VxRack", "1000 FLEX", "3.2", "3.2.2")
    # updatedMessageVxrack3['uuid'] = getAvailableRCMs("VxRack", "1000 FLEX", "3.2", "3.2.2")
    # getAvailableRCMs("VxRack", "1000 FLEX", "3.2", "3.2.3")
    # updatedMessageVxrack4['uuid'] = getAvailableRCMs("VxRack", "1000 FLEX", "3.2", "3.2.3")

    strMessageInvalidCorrID = str(updatedMessageInvalidCorrID)
    strMessageInvalidCorrID = restoreStr(strMessageInvalidCorrID)
    strMessageIP = str(updatedMessageIP)
    strMessageIP = restoreStr(strMessageIP)
    strMessageInvalidRoutingKey = str(updatedMessageInvalidRoutingKey)
    strMessageInvalidRoutingKey = restoreStr(strMessageInvalidRoutingKey)
    strMessageNoCorrID = str(updatedMessageNoCorrID)
    strMessageNoCorrID = restoreStr(strMessageNoCorrID)
    strMessageNoHostname = str(updatedMessageNoHostname)
    strMessageNoHostname = restoreStr(strMessageNoHostname)
    strMessageNoKey = str(updatedMessageNoKey)
    strMessageNoKey = restoreStr(strMessageNoKey)
    strMessageVxrack1 = str(updatedMessageVxrack1)
    strMessageVxrack1 = restoreStr(strMessageVxrack1)
    strMessageVxrack2 = str(updatedMessageVxrack2)
    strMessageVxrack2 = restoreStr(strMessageVxrack2)
    # strMessageVxrack3 = str(updatedMessageVxrack3)
    # strMessageVxrack3 = restoreStr(strMessageVxrack3)
    # strMessageVxrack4 = str(updatedMessageVxrack4)
    # strMessageVxrack4 = restoreStr(strMessageVxrack4)

    getRCMRequest(message, 'getRCMsRequest1.json', 'getRCMsResponse1.json')
    getRCMRequest(strMessageInvalidCorrID, 'getRCMsRequest2.json', 'getRCMsResponse2.json')
    getRCMRequest(strMessageIP, 'getRCMsRequest3.json', 'getRCMsResponse3.json')
    getRCMRequest(strMessageInvalidRoutingKey, 'getRCMsRequest4.json', 'getRCMsResponse4.json')
    getRCMRequest(messageInvalidUUID, 'getRCMsRequest5.json', 'getRCMsResponse5.json')
    getRCMRequest(strMessageNoCorrID, 'getRCMsRequest6.json', 'getRCMsResponse6.json')
    getRCMRequest(strMessageNoHostname, 'getRCMsRequest7.json', 'getRCMsResponse7.json')
    getRCMRequest(strMessageNoKey, 'getRCMsRequest8.json', 'getRCMsResponse8.json')
    getRCMRequest(messageNoUUID, 'getRCMsRequest9.json', 'getRCMsResponse9.json')
    getRCMRequest(messageAllEmpty, 'getRCMsRequest10.json', 'getRCMsResponse10.json')
    getRCMRequest(messageSpaces, 'getRCMsRequest11.json', 'getRCMsResponse11.json')
    getRCMRequest(strMessageVxrack1, 'getRCMsRequest12.json', 'getRCMsResponse12.json')
    getRCMRequest(strMessageVxrack2, 'getRCMsRequest13.json', 'getRCMsResponse13.json')
    # getRCMRequest(strMessageVxrack3, 'getRCMsRequest14.json', 'getRCMsResponse14.json')
    # getRCMRequest(strMessageVxrack4, 'getRCMsRequest15.json', 'getRCMsResponse15.json')

    deleteTestQueues('testGetRCMDetailsRequest', 'testGetRCMDetailsResponse')


def convertStrToDict(string):
    s = string.replace("{", "");
    finalStr = s.replace("}", "");
    list = finalStr.split(",")
    dict = {}
    for i in list:
        keyvalue = i.split(":")
        m = keyvalue[0].strip('\'')
        m = m.replace("\"", "")
        dict[m] = keyvalue[1].strip('"\'')

    return dict

def restoreStr(string):
    s = string.replace("\'", "\"");
    s = s.replace(" ", "");

    return s

def getAvailableRCMs(family, model, train, version):
    numRCMs = 0
    option = "ORIGINAL"

    # url = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/rcm/inventory/' + family + "/" + model + "/" + train + "/" + version
    # urlSec = 'https://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/rcm/inventory/' + family + "/" + model + "/" + train + "/" + version
    urlSec = 'https://' + host + ':19080/rcm-fitness-api/api/rcm/inventory/' + family + "/" + model + "/" + train + "/" + version
    # resp = requests.get(url)
    # resp = requests.get(urlSec, verify='/usr/local/share/ca-certificates/taf.cpsd.dell.ca.crt')
    resp = requests.get(urlSec, verify=False)

    data = json.loads(resp.text)
    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    while numRCMs < len(data["rcmInventoryItems"]):
        if (data["rcmInventoryItems"][numRCMs]["viewOption"]) == option:
            global rcmUUID
            rcmUUID = (data["rcmInventoryItems"][numRCMs]["uuid"])
            print(rcmUUID)
        numRCMs += 1
        return rcmUUID

def deleteTestQueues(testRequest, testResponse):
    # credentials = pika.PlainCredentials(rmq_username, rmq_password)
    # parameters = pika.ConnectionParameters(host, port, '/', credentials)

    messageReqHeader = {'__TypeId__': 'com.dell.cpsd.rfds.rcm.definition.service.get.rcm.details'}
    # propsRequest = pika.BasicProperties(headers=messageReqHeader, content_type='application/json',
    #                                     content_encoding='UTF-8')

    messageResHeader = {'__TypeId__': 'com.dell.cpsd.rcm.definition.service.api.RcmDefinitionsDetailsMessage'}
    # propsResponse = pika.BasicProperties(headers=messageResHeader, content_type='application/json',
    #                                      content_encoding='UTF-8')
    # connection = pika.BlockingConnection(parameters)
    # channel = connection.channel()

    # af_support_tools.rmq_purge_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
    #                                  queue=testRequest)
    # af_support_tools.rmq_purge_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
    #                                  queue=testResponse)

    af_support_tools.rmq_purge_queue(host=hostTLS, port=portTLS, ssl_enabled=True, queue=testRequest)
    af_support_tools.rmq_purge_queue(host=hostTLS, port=portTLS, ssl_enabled=True, queue=testResponse)
    af_support_tools.rmq_delete_queue(host=hostTLS, port=portTLS, ssl_enabled=True, queue=testRequest)
    af_support_tools.rmq_delete_queue(host=hostTLS, port=portTLS, ssl_enabled=True, queue=testResponse)
    # channel.queue_delete(queue=testRequest)
    # channel.queue_delete(queue=testResponse)
    time.sleep(2)

def getRCMRequest(payLoad, requestFile, responseFile):
    # credentials = pika.PlainCredentials(rmq_username, rmq_password)
    # parameters = pika.ConnectionParameters(host, port, '/', credentials)

    messageReqHeader = {'__TypeId__': 'com.dell.cpsd.rfds.rcm.definition.service.get.rcm.details'}
    # propsRequest = pika.BasicProperties(headers=messageReqHeader, content_type='application/json',
    #                                     content_encoding='UTF-8')

    messageResHeader = {'__TypeId__': 'com.dell.cpsd.rcm.definition.service.api.RcmDefinitionsDetailsMessage'}
    # propsResponse = pika.BasicProperties(headers=messageResHeader, content_type='application/json',
    #                                      content_encoding='UTF-8')
    # connection = pika.BlockingConnection(parameters)
    # channel = connection.channel()
    # deleteTestQueues('testGetRCMDetailsRequest', 'testGetRCMDetailsResponse')

    # af_support_tools.rmq_bind_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
    #                                 queue='testGetRCMDetailsRequest',
    #                                 exchange='exchange.dell.cpsd.rfds.rcm.definition.request',
    #                                 routing_key='#')
    # af_support_tools.rmq_bind_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
    #                                 queue='testGetRCMDetailsResponse',
    #                                 exchange='exchange.dell.cpsd.rfds.rcm.definition.response',
    #                                 routing_key='#')
    # af_support_tools.rmq_publish_message(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
    #                                      exchange="exchange.dell.cpsd.rfds.rcm.definition.request",
    #                                      routing_key="dell.cpsd.rfds.rcm.definition.request",
    #                                      headers=messageReqHeader, payload=payLoad, payload_type='json')
    # time.sleep(2)
    # my_request_body = af_support_tools.rmq_consume_message(host=host, port=port, rmq_username=rmq_username,
    #                                                        rmq_password=rmq_password, queue='testGetRCMDetailsRequest')
    # my_response_body = af_support_tools.rmq_consume_message(host=host, port=port, rmq_username=rmq_username,
    #                                                         rmq_password=rmq_password,
    #                                                         queue='testGetRCMDetailsResponse')


    af_support_tools.rmq_bind_queue(host=hostTLS, port=portTLS, ssl_enabled=True,
                                    queue='testGetRCMDetailsRequest',
                                    exchange='exchange.dell.cpsd.rfds.rcm.definition.request',
                                    routing_key='#')
    af_support_tools.rmq_bind_queue(host=hostTLS, port=portTLS, ssl_enabled=True,
                                    queue='testGetRCMDetailsResponse',
                                    exchange='exchange.dell.cpsd.rfds.rcm.definition.response',
                                    routing_key='#')
    af_support_tools.rmq_publish_message(host=hostTLS, port=portTLS, ssl_enabled=True,
                                         exchange="exchange.dell.cpsd.rfds.rcm.definition.request",
                                         routing_key="dell.cpsd.rfds.rcm.definition.request",
                                         headers=messageReqHeader, payload=payLoad, payload_type='json')
    time.sleep(2)
    my_request_body = af_support_tools.rmq_consume_message(host=hostTLS, port=portTLS, ssl_enabled=True, queue='testGetRCMDetailsRequest')
    my_response_body = af_support_tools.rmq_consume_message(host=hostTLS, port=portTLS, ssl_enabled=True,
                                                            queue='testGetRCMDetailsResponse')

    af_support_tools.rmq_payload_to_file(my_request_body, path + requestFile)
    af_support_tools.rmq_payload_to_file(my_response_body, path + responseFile)

    time.sleep(1)

    deleteTestQueues('testGetRCMDetailsRequest', 'testGetRCMDetailsResponse')

def verifyPublishedAttributes(filename):
    with open(filename, "rU") as dataFile:
        dataInput = json.load(dataFile)

    assert ("correlationId") in dataInput.keys(), "Correlation ID not included in published attributes."
    assert ("hostname") in dataInput.keys(), "Hostname not included in published attributes."
    assert ("routingKey") in dataInput.keys(), "Routing Key not included in published attributes."
    assert ("uuid") in dataInput.keys(), "RCM UUID not included in published attributes."

    return dataInput

def verifyConsumedAttributes(requestFile, responseFile, train, version, model, family):
    requestData = open(requestFile, "rU")
    dataInput = json.load(requestData)

    dataFile = open(responseFile, "rU")
    data = json.load(dataFile)

    if "errorCode" in data.keys():
        if "errorMessage" in data.keys():
            assert (data["errorCode"][:-2]) in (data["errorMessage"]), "Returned Error Code not included in Error Message."
            assert 'orrelation' or 'uid' in (data["errorMessage"]), "Returned Error Message does not reflect missing correlation ID."
            return

    if "rcmDetails" in data.keys():
        numRCMs = len(data["rcmDetails"])
        if numRCMs > 0:
            assert (dataInput['correlationId']) == (data["correlationId"]), "Correlation Ids on request and response do not match."
            if numRCMs == 1:
                assert data["rcmDetails"][0]["uuid"] == dataInput['uuid'], "Not the single RCM returned as expected."
                assert data["rcmDetails"][0]["rcmTrain"] == train, "Train does not match."
                assert data["rcmDetails"][0]["rcmVersion"] == version, "Version does not match."
                assert data["rcmDetails"][0]["systemModelFamily"] == model, "Model does not match."
                assert data["rcmDetails"][0]["systemProductFamily"] == family, "Product does not match."
                return
        else:
            assert dataInput['correlationId'] == data["correlationId"], "Correlation Ids on request and response do not match."
            assert len(data["rcmDetails"]) == 0, "Expected empty list not included in response."
            return

    assert False, "Response attributes don't match those defined in request."

def verifyCorrectCorrelationID(requestFile, responseFile):
    data_request = open(requestFile, 'r')
    requestData = json.load(data_request)

    data_response = open(responseFile, 'r')
    responseData = json.load(data_response)

    if requestData["correlationId"] != "":
        if responseData["correlationId"] != "":
            assert requestData["correlationId"] == responseData[
                "correlationId"], "Correlation ID on response message does not match."
            return
    else:
        assert responseData["correlationId"] == "", "No Corr ID expected on request and response."
        return

    assert False, "Corr IDs not matching."

# print("Verifying each of the published message attributes.")


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes1():
    verifyPublishedAttributes(path + 'getRCMsRequest1.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes2():
    verifyPublishedAttributes(path + 'getRCMsRequest2.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes3():
    verifyPublishedAttributes(path + 'getRCMsRequest3.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes4():
    verifyPublishedAttributes(path + 'getRCMsRequest4.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes5():
    verifyPublishedAttributes(path + 'getRCMsRequest5.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes6():
    verifyPublishedAttributes(path + 'getRCMsRequest6.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes7():
    verifyPublishedAttributes(path + 'getRCMsRequest7.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes8():
    verifyPublishedAttributes(path + 'getRCMsRequest8.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes9():
    verifyPublishedAttributes(path + 'getRCMsRequest9.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes10():
    verifyPublishedAttributes(path + 'getRCMsRequest10.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes11():
    verifyPublishedAttributes(path + 'getRCMsRequest11.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes12():
    verifyPublishedAttributes(path + 'getRCMsRequest12.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes13():
    verifyPublishedAttributes(path + 'getRCMsRequest13.json')

# @pytest.mark.rcm_fitness_mvp_extended
# def test_verifyPublishedAttributes14():
#     verifyPublishedAttributes(path + 'getRCMsRequest14.json')
#
# @pytest.mark.rcm_fitness_mvp_extended
# def test_verifyPublishedAttributes15():
#     verifyPublishedAttributes(path + 'getRCMsRequest15.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes1():
    verifyConsumedAttributes(path + 'getRCMsRequest1.json', path + 'getRCMsResponse1.json', "1.2", "1.2.33", "340",
                             "Vblock")

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes2():
    verifyConsumedAttributes(path + 'getRCMsRequest2.json', path + 'getRCMsResponse2.json', "9.2", "9.2.2", "1000 FLEX",
                             "VxRack")

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes3():
    verifyConsumedAttributes(path + 'getRCMsRequest3.json', path + 'getRCMsResponse3.json', "9.2", "9.2.2", "1000 FLEX",
                             "VxRack")

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes4():
    verifyConsumedAttributes(path + 'getRCMsRequest4.json', path + 'getRCMsResponse4.json', "9.2", "9.2.2", "1000 FLEX",
                             "VxRack")

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes5():
    verifyConsumedAttributes(path + 'getRCMsRequest5.json', path + 'getRCMsResponse5.json', "9.2", "9.2.2", "1000 FLEX",
                             "VxRack")

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes6():
    verifyConsumedAttributes(path + 'getRCMsRequest6.json', path + 'getRCMsResponse6.json', "9.2", "9.2.2", "1000 FLEX",
                             "VxRack")

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes7():
    verifyConsumedAttributes(path + 'getRCMsRequest7.json', path + 'getRCMsResponse7.json', "9.2", "9.2.2", "1000 FLEX",
                             "VxRack")

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes8():
    verifyConsumedAttributes(path + 'getRCMsRequest8.json', path + 'getRCMsResponse8.json', "9.2", "9.2.2", "1000 FLEX",
                             "VxRack")

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes9():
    verifyConsumedAttributes(path + 'getRCMsRequest9.json', path + 'getRCMsResponse9.json', "9.2", "9.2.2", "1000 FLEX",
                             "VxRack")

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes10():
    verifyConsumedAttributes(path + 'getRCMsRequest10.json', path + 'getRCMsResponse10.json', "9.2", "9.2.2", "1000 FLEX",
                             "VxRack")

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes11():
    verifyConsumedAttributes(path + 'getRCMsRequest11.json', path + 'getRCMsResponse11.json', "9.2", "9.2.2", "1000 FLEX",
                             "VxRack")

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes12():
    verifyConsumedAttributes(path + 'getRCMsRequest12.json', path + 'getRCMsResponse12.json', "9.2", "9.2.2", "1000 FLEX",
                             "VxRack")

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes13():
    verifyConsumedAttributes(path + 'getRCMsRequest13.json', path + 'getRCMsResponse13.json', "9.2", "9.2.1", "1000 FLEX",
                             "VxRack")

# @pytest.mark.rcm_fitness_mvp_extended
# def test_verifyConsumedAttributes14():
#     verifyConsumedAttributes(path + 'getRCMsRequest14.json', path + 'getRCMsResponse14.json', "3.2", "3.2.2", "1000 FLEX",
#                              "VxRack")
#
# @pytest.mark.rcm_fitness_mvp_extended
# def test_verifyConsumedAttributes15():
#     verifyConsumedAttributes(path + 'getRCMsRequest15.json', path + 'getRCMsResponse15.json', "3.2", "3.2.3", "1000 FLEX",
#                              "VxRack")

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyCorrectCorrelationID1():
    verifyCorrectCorrelationID(path + 'getRCMsRequest1.json', path + 'getRCMsResponse1.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyCorrectCorrelationID2():
    verifyCorrectCorrelationID(path + 'getRCMsRequest2.json', path + 'getRCMsResponse2.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyCorrectCorrelationID3():
    verifyCorrectCorrelationID(path + 'getRCMsRequest3.json', path + 'getRCMsResponse3.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyCorrectCorrelationID4():
    verifyCorrectCorrelationID(path + 'getRCMsRequest4.json', path + 'getRCMsResponse4.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyCorrectCorrelationID5():
    verifyCorrectCorrelationID(path + 'getRCMsRequest5.json', path + 'getRCMsResponse5.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyCorrectCorrelationID6():
    verifyCorrectCorrelationID(path + 'getRCMsRequest6.json', path + 'getRCMsResponse6.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyCorrectCorrelationID7():
    verifyCorrectCorrelationID(path + 'getRCMsRequest7.json', path + 'getRCMsResponse7.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyCorrectCorrelationID8():
    verifyCorrectCorrelationID(path + 'getRCMsRequest8.json', path + 'getRCMsResponse8.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyCorrectCorrelationID9():
    verifyCorrectCorrelationID(path + 'getRCMsRequest9.json', path + 'getRCMsResponse9.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyCorrectCorrelationID10():
    verifyCorrectCorrelationID(path + 'getRCMsRequest10.json', path + 'getRCMsResponse10.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyCorrectCorrelationID11():
    verifyCorrectCorrelationID(path + 'getRCMsRequest11.json', path + 'getRCMsResponse11.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyCorrectCorrelationID12():
    verifyCorrectCorrelationID(path + 'getRCMsRequest12.json', path + 'getRCMsResponse12.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyCorrectCorrelationID13():
    verifyCorrectCorrelationID(path + 'getRCMsRequest13.json', path + 'getRCMsResponse13.json')

# @pytest.mark.rcm_fitness_mvp_extended
# def test_verifyCorrectCorrelationID14():
#     verifyCorrectCorrelationID(path + 'getRCMsRequest14.json', path + 'getRCMsResponse14.json')
#
# @pytest.mark.rcm_fitness_mvp_extended
# def test_verifyCorrectCorrelationID15():
#     verifyCorrectCorrelationID(path + 'getRCMsRequest15.json', path + 'getRCMsResponse15.json')
