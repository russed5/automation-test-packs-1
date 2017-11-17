#!/usr/bin/python
# Copyright © 2017 Dell Inc. or its subsidiaries.  All Rights Reserved
import logging
import af_support_tools
import pika
import json
import sys
import time
import pytest
from collections import Counter
from pprint import pprint
import os
import re


@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    global bodyList    
    bodyList = []
    global dictUUID
    dictUUID = dict()
    global dataInput
    dataInput = dict()

    global path
    path = '/home/autouser/PycharmProjects/auto-framework/test_suites/continuous-integration-deploy-suite/rcm-fitness-ci-cd/b_insertRCMs/'
    global ssl_options
    ssl_options = {"ca_certs": "/etc/rabbitmq/certs/testca/cacert.pem",
                   "certfile": "/etc/rabbitmq/certs/certs/client/cert.pem",
                   "keyfile": "/etc/rabbitmq/certs/certs/client/key.pem", "cert_reqs": "ssl.CERT_REQUIRED",
                   "ssl_version": "ssl.PROTOCOL_TLSv1_2"}

    # Update config ini files at runtime
    my_data_file = os.environ.get('AF_RESOURCES_PATH') + '/continuous-integration-deploy-suite/insertRCMs.properties'
    print("Data file: %s" % my_data_file)
    af_support_tools.set_config_file_property_by_data_file(my_data_file)

    # Set config ini file name
    global env_file
    env_file = 'env.ini'

    global hostTLS
    hostTLS = "amqp"
    global host
    host = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')
    global portTLS
    portTLS = af_support_tools.get_config_file_property(config_file=env_file, heading='RabbitMQ', property='ssl_port')
    portTLS = int(portTLS)

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
    payload_file = 'continuous-integration-deploy-suite/insertRCMs.ini'
    global payload_header
    payload_header = 'payload'
    global payload_dataManu
    payload_dataManu = 'datamanu'
    global payload_xdataManu
    global payload_dataAddendum
    global payload_dataAddendum2
    global payload_dataAddendum3
    global payload_xdataAddendum
    global payload_dataOriginal
    global payload_xdataOriginal
    global payload_vxrackDataOriginal
    global payload_vxrackDataOriginal2
    global payload_vxrackDataOriginal3
    global payload_vxrackDataManu
    global payload_vxrackDataAddendum
    global payload_vxrackDataAddendum2

    payload_xdataManu = 'xdatamanu'
    payload_dataAddendum = 'dataaddendum'
    payload_dataAddendum2 = 'dataaddendum2'
    payload_dataAddendum3 = 'dataaddendum3'
    payload_xdataAddendum = 'xdataaddendum'
    payload_dataOriginal = 'dataoriginal'
    payload_xdataOriginal = 'xdataoriginal'
    payload_vxrackDataOriginal = 'vxrackdataoriginal'
    payload_vxrackDataOriginal2 = 'vxrackdataoriginal2'
    payload_vxrackDataOriginal3 = 'vxrackdataoriginal3'
    payload_vxrackDataManu = 'vxrackdatamanu'
    payload_vxrackDataAddendum = 'vxrackdataaddendum'
    payload_vxrackDataAddendum2 = 'vxrackdataaddendum2'

    global messageManu
    global xmessageManu
    global messageAddendum
    global messageAddendum2
    global messageAddendum3
    global xmessageAddendum
    global messageOriginal
    global xmessageOriginal
    global vxrackMessageOriginal
    global vxrackMessageOriginal2
    global vxrackMessageOriginal3
    global vxrackMessageManu
    global vxrackMessageAddendum
    global vxrackMessageAddendum2

    messageManu = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                            property=payload_dataManu)
    xmessageManu = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                             property=payload_xdataManu)
    messageAddendum = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                                property=payload_dataAddendum)
    messageAddendum2 = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                                 property=payload_dataAddendum2)
    messageAddendum3 = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                                 property=payload_dataAddendum3)
    xmessageAddendum = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                                 property=payload_xdataAddendum)
    messageOriginal = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                                property=payload_dataOriginal)
    xmessageOriginal = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                                 property=payload_xdataOriginal)
    vxrackMessageOriginal = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                                      property=payload_vxrackDataOriginal)
    vxrackMessageOriginal2 = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                                      property=payload_vxrackDataOriginal2)
    vxrackMessageOriginal3 = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                                      property=payload_vxrackDataOriginal3)
    vxrackMessageManu = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                                  property=payload_vxrackDataManu)
    vxrackMessageAddendum = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                                      property=payload_vxrackDataAddendum)
    vxrackMessageAddendum2 = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                                       property=payload_vxrackDataAddendum2)

    deleteTestQueues('testInsertRCMDefinitionsRequest', 'testInsertRCMDefinitionsResponse')
    ensurePathExists(path)
    purgeOldOutput(path, "insertRCMRe")

    insertDummyRCMRequest(messageManu, 'insertRCMRequest1.json', 'insertRCMResponse1.json')
    insertDummyRCMRequest(xmessageManu, 'insertRCMRequest2.json', 'insertRCMResponse2.json')
    insertDummyRCMRequest(messageAddendum, 'insertRCMRequest3.json', 'insertRCMResponse3.json')
    insertDummyRCMRequest(messageAddendum2, 'insertRCMRequest4.json', 'insertRCMResponse4.json')
    insertDummyRCMRequest(messageAddendum3, 'insertRCMRequest5.json', 'insertRCMResponse5.json')
    insertDummyRCMRequest(xmessageAddendum, 'insertRCMRequest6.json', 'insertRCMResponse6.json')
    insertDummyRCMRequest(messageOriginal, 'insertRCMRequest7.json', 'insertRCMResponse7.json')
    insertDummyRCMRequest(xmessageOriginal, 'insertRCMRequest8.json', 'insertRCMResponse8.json')
    insertDummyRCMRequest(vxrackMessageOriginal, 'insertRCMRequest9.json', 'insertRCMResponse9.json')
    insertDummyRCMRequest(vxrackMessageOriginal2, 'insertRCMRequest13.json', 'insertRCMResponse13.json')
    insertDummyRCMRequest(vxrackMessageOriginal3, 'insertRCMRequest14.json', 'insertRCMResponse14.json')
    insertDummyRCMRequest(vxrackMessageManu, 'insertRCMRequest10.json', 'insertRCMResponse10.json')
    insertDummyRCMRequest(vxrackMessageAddendum, 'insertRCMRequest11.json', 'insertRCMResponse11.json')
    insertDummyRCMRequest(vxrackMessageAddendum2, 'insertRCMRequest12.json', 'insertRCMResponse12.json')


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
            continue


def deleteTestQueues(testRequest, testResponse):
    messageHeaderResponse = {'__TypeId__': 'com.dell.cpsd.rcm.definition.service.rcm.definition.inserted'}
    messageHeaderRequest = {'__TypeId__': 'com.dell.cpsd.rcm.definition.service.insert.rcm.definition'}

    af_support_tools.rmq_purge_queue(host=hostTLS, port=portTLS, ssl_enabled=True, queue=testRequest)
    af_support_tools.rmq_purge_queue(host=hostTLS, port=portTLS, ssl_enabled=True, queue=testResponse)
    af_support_tools.rmq_delete_queue(host=hostTLS, port=portTLS, ssl_enabled=True, queue=testRequest)
    af_support_tools.rmq_delete_queue(host=hostTLS, port=portTLS, ssl_enabled=True, queue=testResponse)


def insertDummyRCMRequest(payLoad, requestFile, responseFile):
    messageHeaderResponse = {'__TypeId__': 'com.dell.cpsd.rcm.definition.service.rcm.definition.inserted'}
    messageHeaderRequest = {'__TypeId__': 'com.dell.cpsd.rcm.definition.service.insert.rcm.definition'}

    af_support_tools.rmq_bind_queue(host=hostTLS, port=portTLS, ssl_enabled=True,
                                    queue='testInsertRCMDefinitionsRequest',
                                    exchange='exchange.dell.cpsd.rfds.rcm.definition.request', routing_key='#')
    af_support_tools.rmq_bind_queue(host=hostTLS, port=portTLS, ssl_enabled=True,
                                    queue='testInsertRCMDefinitionsResponse',
                                    exchange='exchange.dell.cpsd.rfds.rcm.definition.response', routing_key='#')

    af_support_tools.rmq_publish_message(host=hostTLS, port=portTLS, ssl_enabled=True,
                                         exchange="exchange.dell.cpsd.rfds.rcm.definition.request",
                                         routing_key="dell.cpsd.rfds.rcm.definition.request",
                                         headers=messageHeaderRequest, payload=payLoad, payload_type='json')

    time.sleep(2)
    my_request_body = af_support_tools.rmq_consume_message(host=hostTLS, port=portTLS, ssl_enabled=True,
                                                           queue='testInsertRCMDefinitionsRequest')
    my_response_body = af_support_tools.rmq_consume_message(host=hostTLS, port=portTLS, ssl_enabled=True,
                                                            queue='testInsertRCMDefinitionsResponse')

    af_support_tools.rmq_payload_to_file(my_request_body, path + requestFile)
    af_support_tools.rmq_payload_to_file(my_response_body, path + responseFile)

    time.sleep(1)


def verifyPublishedAttributes(filename, eolDate, numContents, train, version, family, model, option):
    requestData = {}

    print("\nStarting to verify attributes published....\n")

    with open(filename, 'r') as data_file:
        requestData = json.load(data_file)

    print("Name of file: %s\n" % data_file.name)

    print("Routing key: %s" % requestData["routingKey"])

    if requestData["correlationId"] != "":
        # if requestData["correlationId"].find('-') == -1
        assert requestData["correlationId"].find('-') != -1, "Unexpected correlationID format found."
        print("Correlation ID: %s" % requestData["correlationId"])
    if requestData["rcmDetails"]["endOfLifeDate"] != "":
        assert requestData["rcmDetails"]["endOfLifeDate"] == eolDate, "Unexpected endOfLifeDate format found."
        print("End of Life Date: % s" % requestData["rcmDetails"]["endOfLifeDate"])
    if requestData["rcmDetails"]["rcmContents"] != '':
        assert (len(
            requestData["rcmDetails"]["rcmContents"])) == numContents, "Unexpected number of content entries found."
    assert requestData["rcmDetails"]["rcmTrain"] == train, "Unexpected rcmTrain found."
    assert requestData["rcmDetails"]["rcmVersion"] == version, "Unexpected rcmVersion found."
    assert requestData["rcmDetails"]["systemProductFamily"] == family, "Unexpected system family found."
    assert requestData["rcmDetails"]["systemModelFamily"] == model, "Unexpected system model found."
    assert requestData["rcmDetails"]["viewOption"] == option, "Unexpected system model found."
    assert requestData["routingKey"] == "dell.cpsd.rfds.rcm.definition.request", "Unexpected routing key found."

    print("\nAll verification steps executed successfully.....")


def verifyConsumedAttributes(filename, expectedResult, train, version, family, model, option):
    responseData = {}
    uuid_count = 0
    # dictUUID = dict()

    print("\nStarting to verify attributes consumed....\n")
    data_response = open(filename, 'rU')
    responseData = json.load(data_response)

    if responseData["correlationId"] != "":
        if responseData["insertSuccessful"] != "":
            print("Correlation ID: %s" % responseData["correlationId"])
            # print(responseData["insertSuccessful"])
            print("UUID: %s" % responseData["insertSuccessful"]["rcmDetails"]["uuid"])
            print("Model: %s" % responseData["insertSuccessful"]["rcmDetails"]["systemModelFamily"])
            print("Train: %s" % responseData["insertSuccessful"]["rcmDetails"]["rcmTrain"])
            print("Version: %s" % responseData["insertSuccessful"]["rcmDetails"]["rcmVersion"])
            print("Option: %s" % responseData["insertSuccessful"]["rcmDetails"]["viewOption"])
            # print(responseData["insertSuccessful"]["uuid"])
            # print(responseData["insertSuccessful"])
            if 'uuid' in responseData["insertSuccessful"]["rcmDetails"]:
                uuid_count += 1
            assert uuid_count == 1, "More than the one expected RCM returned."
            assert (responseData["insertSuccessful"]["rcmDetails"]["rcmTrain"]) == train
            assert (responseData["insertSuccessful"]["rcmDetails"]["rcmVersion"]) == version
            assert (responseData["insertSuccessful"]["rcmDetails"]["systemProductFamily"]) == family
            assert (responseData["insertSuccessful"]["rcmDetails"]["systemModelFamily"]) == model
            assert (responseData["insertSuccessful"]["rcmDetails"]["viewOption"]) == option
            assert len(
                responseData["insertSuccessful"]["rcmDetails"]["rcmContents"]) > 0, "Unexpected insert result found."

            dictUUID.update({responseData["correlationId"]: responseData["insertSuccessful"]["rcmDetails"]["uuid"]})
            # print(dictUUID)

    print("\nAll verification steps executed successfully.....")
    return dictUUID


def verifyCorrectCorrelationID(requestFile, responseFile):
    requestData = {}
    responseData = {}
    print("\nStarting to verify reply returns the correct correlation ID in message body.\n")

    data_request = open(requestFile, 'r')
    requestData = json.load(data_request)

    data_response = open(responseFile, 'r')
    responseData = json.load(data_response)

    if requestData["correlationId"] != "":
        if responseData["correlationId"] != "":
            print("Request ID: %s" % requestData["correlationId"])
            print("Response ID: %s" % responseData["correlationId"])
            assert requestData["correlationId"] == responseData[
                "correlationId"], "Correlation ID on response message does not match."

    print("\nAll verification steps executed successfully.....")


def verifyUniqueUUIDinResponse():
    responseUUIDs = ()
    responseCorrID = ()

    responseUUIDs = dictUUID.values()
    responseCorrID = dictUUID.keys()

    print("\nStarting to verify response attributes are unique....\n")

    print("\nAll returned CorrelationIDs:")
    print(responseCorrID)
    print("\nAll returned UUIDs:")
    print(responseUUIDs)

    assert (len(responseCorrID)) == len(set(responseCorrID)), "Non-unique Correlation IDs returned."
    assert (len(responseUUIDs)) == len(set(responseUUIDs)), "Non-unique UUIDs returned."

    print("\nAll verification steps executed successfully.....")


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes1():
    verifyPublishedAttributes(path + 'insertRCMRequest1.json', "March 2019", 66, "1.2", "1.2.33", "Vblock", "340",
                              "MANUFACTURING")

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes2():
    verifyPublishedAttributes(path + 'insertRCMRequest2.json', "March 2019", 66, "1.2", "1.2.33", "VxBlock", "340",
                              "MANUFACTURING")

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes3():
    verifyPublishedAttributes(path + 'insertRCMRequest3.json', "March 2020", 66, "1.2", "1.2.33.1", "Vblock", "340",
                              "ADDENDUM")

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes4():
    verifyPublishedAttributes(path + 'insertRCMRequest4.json', "June 2021", 66, "1.2", "1.2.33.2", "Vblock", "340",
                              "ADDENDUM")

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes5():
    verifyPublishedAttributes(path + 'insertRCMRequest5.json', "Sept 2022", 66, "1.2", "1.2.33.3", "Vblock", "340",
                              "ADDENDUM")

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes6():
    verifyPublishedAttributes(path + 'insertRCMRequest6.json', "June 2020", 66, "1.2", "1.2.33.1", "VxBlock", "340",
                              "ADDENDUM")

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes7():
    verifyPublishedAttributes(path + 'insertRCMRequest7.json', "March 2019", 66, "1.2", "1.2.33", "Vblock", "340",
                              "ORIGINAL")

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes8():
    verifyPublishedAttributes(path + 'insertRCMRequest8.json', "March 2019", 66, "1.2", "1.2.33", "VxBlock", "340",
                              "ORIGINAL")

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes9():
    verifyPublishedAttributes(path + 'insertRCMRequest9.json', "September 2018", 37, "9.2", "9.2.1", "VxRack", "1000 FLEX",
                              "ORIGINAL")

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes10():
    verifyPublishedAttributes(path + 'insertRCMRequest10.json', "September 2018", 37, "9.2", "9.2.1", "VxRack", "1000 FLEX",
                              "MANUFACTURING")

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes11():
    verifyPublishedAttributes(path + 'insertRCMRequest11.json', "January 2019", 37, "9.2", "9.2.1.1", "VxRack", "1000 FLEX",
                              "ADDENDUM")

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes12():
    verifyPublishedAttributes(path + 'insertRCMRequest12.json', "January 2020", 37, "9.2", "9.2.1.2", "VxRack", "1000 FLEX",
                              "ADDENDUM")

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes13():
    verifyPublishedAttributes(path + 'insertRCMRequest13.json', "September 2019", 48, "9.2", "9.2.2", "VxRack", "1000 FLEX",
                              "ORIGINAL")

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes14():
    verifyPublishedAttributes(path + 'insertRCMRequest14.json', "September 2018", 36, "9.2", "9.2.3", "VxRack", "1000 FLEX",
                              "ORIGINAL")


# @pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_verifyCorrectCorrelationID1():
    verifyCorrectCorrelationID(path + 'insertRCMRequest1.json', path + 'insertRCMResponse1.json')


# @pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_verifyCorrectCorrelationID2():
    verifyCorrectCorrelationID(path + 'insertRCMRequest2.json', path + 'insertRCMResponse2.json')


# @pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_verifyCorrectCorrelationID3():
    verifyCorrectCorrelationID(path + 'insertRCMRequest3.json', path + 'insertRCMResponse3.json')


# @pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_verifyCorrectCorrelationID4():
    verifyCorrectCorrelationID(path + 'insertRCMRequest4.json', path + 'insertRCMResponse4.json')


# @pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_verifyCorrectCorrelationID5():
    verifyCorrectCorrelationID(path + 'insertRCMRequest5.json', path + 'insertRCMResponse5.json')


# @pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_verifyCorrectCorrelationID6():
    verifyCorrectCorrelationID(path + 'insertRCMRequest6.json', path + 'insertRCMResponse6.json')


# @pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_verifyCorrectCorrelationID7():
    verifyCorrectCorrelationID(path + 'insertRCMRequest7.json', path + 'insertRCMResponse7.json')


# @pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_verifyCorrectCorrelationID8():
    verifyCorrectCorrelationID(path + 'insertRCMRequest8.json', path + 'insertRCMResponse8.json')


# @pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_verifyCorrectCorrelationID9():
    verifyCorrectCorrelationID(path + 'insertRCMRequest9.json', path + 'insertRCMResponse9.json')


# @pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_verifyCorrectCorrelationID10():
    verifyCorrectCorrelationID(path + 'insertRCMRequest10.json', path + 'insertRCMResponse10.json')


# @pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_verifyCorrectCorrelationID11():
    verifyCorrectCorrelationID(path + 'insertRCMRequest11.json', path + 'insertRCMResponse11.json')


# @pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_verifyCorrectCorrelationID12():
    verifyCorrectCorrelationID(path + 'insertRCMRequest12.json', path + 'insertRCMResponse12.json')


# @pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_verifyCorrectCorrelationID13():
    verifyCorrectCorrelationID(path + 'insertRCMRequest13.json', path + 'insertRCMResponse13.json')

# @pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_verifyCorrectCorrelationID14():
    verifyCorrectCorrelationID(path + 'insertRCMRequest14.json', path + 'insertRCMResponse14.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes1():
    verifyConsumedAttributes(path + 'insertRCMResponse1.json', True, "1.2", "1.2.33", "Vblock", "340", "MANUFACTURING")


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes2():
    verifyConsumedAttributes(path + 'insertRCMResponse2.json', True, "1.2", "1.2.33", "VxBlock", "340", "MANUFACTURING")


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes3():
    verifyConsumedAttributes(path + 'insertRCMResponse3.json', True, "1.2", "1.2.33.1", "Vblock", "340", "ADDENDUM")


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes4():
    verifyConsumedAttributes(path + 'insertRCMResponse4.json', True, "1.2", "1.2.33.2", "Vblock", "340", "ADDENDUM")


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes5():
    verifyConsumedAttributes(path + 'insertRCMResponse5.json', True, "1.2", "1.2.33.3", "Vblock", "340", "ADDENDUM")


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes6():
    verifyConsumedAttributes(path + 'insertRCMResponse6.json', True, "1.2", "1.2.33.1", "VxBlock", "340", "ADDENDUM")


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes7():
    verifyConsumedAttributes(path + 'insertRCMResponse7.json', True, "1.2", "1.2.33", "Vblock", "340", "ORIGINAL")


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes8():
    verifyConsumedAttributes(path + 'insertRCMResponse8.json', True, "1.2", "1.2.33", "VxBlock", "340", "ORIGINAL")

@pytest.mark.daily_status
@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes9():
    verifyConsumedAttributes(path + 'insertRCMResponse9.json', True, "9.2", "9.2.1", "VxRack", "1000 FLEX", "ORIGINAL")

@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes10():
    verifyConsumedAttributes(path + 'insertRCMResponse10.json', True, "9.2", "9.2.1", "VxRack", "1000 FLEX",
                             "MANUFACTURING")

@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes11():
    verifyConsumedAttributes(path + 'insertRCMResponse11.json', True, "9.2", "9.2.1.1", "VxRack", "1000 FLEX", "ADDENDUM")

@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes12():
    verifyConsumedAttributes(path + 'insertRCMResponse12.json', True, "9.2", "9.2.1.2", "VxRack", "1000 FLEX", "ADDENDUM")

@pytest.mark.daily_status
@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes13():
    verifyConsumedAttributes(path + 'insertRCMResponse13.json', True, "9.2", "9.2.2", "VxRack", "1000 FLEX", "ORIGINAL")

@pytest.mark.daily_status
@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes14():
    verifyConsumedAttributes(path + 'insertRCMResponse14.json', True, "9.2", "9.2.3", "VxRack", "1000 FLEX", "ORIGINAL")

@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_verifyUniqueUUIDinResponse():
    verifyUniqueUUIDinResponse()
