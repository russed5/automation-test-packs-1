#!/usr/bin/python
# Copyright © 2017 Dell Inc. or its subsidiaries.  All Rights Reserved
import logging
import af_support_tools
import pika
import json
import pytest
import time
import os
import re


@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    global path
    path = "/home/autouser/PycharmProjects/auto-framework/test_suites/continuous-integration-deploy-suite/rcm-fitness-ci-cd/c_listRCMDefinitions/"
    global ssl_options
    ssl_options = {"ca_certs": "/etc/rabbitmq/certs/testca/cacert.pem",
                   "certfile": "/etc/rabbitmq/certs/certs/client/cert.pem",
                   "keyfile": "/etc/rabbitmq/certs/certs/client/key.pem", "cert_reqs": "ssl.CERT_REQUIRED",
                   "ssl_version": "ssl.PROTOCOL_TLSv1_2"}

    # Update config ini files at runtime
    my_data_file = os.environ.get('AF_RESOURCES_PATH') + '/continuous-integration-deploy-suite/listRCMInputs.properties'
    af_support_tools.set_config_file_property_by_data_file(my_data_file)
    logging.getLogger('pika').setLevel(logging.DEBUG)
    # Set config ini file name
    global env_file
    env_file = 'env.ini'

    global hostTLS
    hostTLS = "amqp"
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
    payload_file = 'continuous-integration-deploy-suite/listRCMInputs.ini'
    global payload_header
    payload_header = 'payload'
    global payload_dataVersion
    payload_dataVersion = 'dataversion'
    global payload_dataTrain
    payload_dataTrain = 'datatrain'
    global payload_dataModel
    payload_dataModel = 'datamodel'
    global payload_dataFamily
    payload_dataFamily = 'datafamily'
    global payload_dataVxRackVersion1
    payload_dataVxRackVersion1 = 'datavxrackversion1'
    global payload_dataVxRackVersion2
    payload_dataVxRackVersion2 = 'datavxrackversion2'
    global payload_dataVxRackVersion3
    payload_dataVxRackVersion3 = 'datavxrackversion3'
    global payload_dataVxRackVersion4
    payload_dataVxRackVersion4 = 'datavxrackversion4'
    global payload_dataVxRackTrain
    payload_dataVxRackTrain = 'datavxracktrain'
    global payload_dataVxRackModel
    payload_dataVxRackModel = 'datavxrackmodel'
    global payload_dataVxRackFamily
    payload_dataVxRackFamily = 'datavxrackfamily'
    global payload_dataInvalid1
    payload_dataInvalid1 = 'datainvalid1'
    global payload_dataInvalid2
    payload_dataInvalid2 = 'datainvalid2'
    global payload_dataInvalid3
    payload_dataInvalid3 = 'datainvalid3'
    global payload_dataInvalid4
    payload_dataInvalid4 = 'datainvalid4'
    global payload_dataInvalid5
    payload_dataInvalid5 = 'datainvalid5'
    global payload_dataInvalid6
    payload_dataInvalid6 = 'datainvalid6'
    global payload_dataInvalid7
    payload_dataInvalid7 = 'datainvalid7'
    global payload_dataInvalid8
    payload_dataInvalid8 = 'datainvalid8'

    messageVersion = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                               property=payload_dataVersion)
    messageTrain = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                             property=payload_dataTrain)
    messageModel = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                             property=payload_dataModel)
    messageFamily = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                              property=payload_dataFamily)
    messageInvalid1 = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                                property=payload_dataInvalid1)
    messageInvalid2 = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                                property=payload_dataInvalid2)
    messageInvalid3 = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                                property=payload_dataInvalid3)
    messageInvalid4 = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                                property=payload_dataInvalid4)
    messageInvalid5 = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                                property=payload_dataInvalid5)
    messageInvalid6 = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                                property=payload_dataInvalid6)
    messageInvalid7 = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                                property=payload_dataInvalid7)
    messageInvalid8 = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                                property=payload_dataInvalid8)
    messageVxRackVersion1 = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                                     property=payload_dataVxRackVersion1)
    messageVxRackVersion2 = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                                     property=payload_dataVxRackVersion2)
    messageVxRackVersion3 = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                                     property=payload_dataVxRackVersion3)
    messageVxRackVersion4 = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                                     property=payload_dataVxRackVersion4)
    messageVxRackTrain = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                                   property=payload_dataVxRackTrain)
    messageVxRackModel = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                                   property=payload_dataVxRackModel)
    messageVxRackFamily = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                                    property=payload_dataVxRackFamily)

    ensurePathExists(path)
    purgeOldOutput(path, "getRCMsRe")
    logging.getLogger('pika').setLevel(logging.DEBUG)

    insertListRequest(messageVersion, 'listRCMDefinitionRequest1.json', 'listRCMDefinitionResponse1.json')
    insertListRequest(messageTrain, 'listRCMDefinitionRequest2.json', 'listRCMDefinitionResponse2.json')
    insertListRequest(messageModel, 'listRCMDefinitionRequest3.json', 'listRCMDefinitionResponse3.json')
    insertListRequest(messageFamily, 'listRCMDefinitionRequest4.json', 'listRCMDefinitionResponse4.json')
    insertListRequest(messageInvalid1, 'listRCMDefinitionRequest5.json', 'listRCMDefinitionResponse5.json')
    insertListRequest(messageInvalid2, 'listRCMDefinitionRequest6.json', 'listRCMDefinitionResponse6.json')
    insertListRequest(messageInvalid3, 'listRCMDefinitionRequest7.json', 'listRCMDefinitionResponse7.json')
    insertListRequest(messageInvalid4, 'listRCMDefinitionRequest8.json', 'listRCMDefinitionResponse8.json')
    insertListRequest(messageInvalid5, 'listRCMDefinitionRequest9.json', 'listRCMDefinitionResponse9.json')
    insertListRequest(messageInvalid6, 'listRCMDefinitionRequest10.json', 'listRCMDefinitionResponse10.json')
    insertListRequest(messageInvalid7, 'listRCMDefinitionRequest11.json', 'listRCMDefinitionResponse11.json')
    insertListRequest(messageInvalid8, 'listRCMDefinitionRequest12.json', 'listRCMDefinitionResponse12.json')
    insertListRequest(messageVxRackVersion1, 'listRCMDefinitionRequest13.json', 'listRCMDefinitionResponse13.json')
    insertListRequest(messageVxRackVersion2, 'listRCMDefinitionRequest14.json', 'listRCMDefinitionResponse14.json')
    insertListRequest(messageVxRackVersion3, 'listRCMDefinitionRequest15.json', 'listRCMDefinitionResponse15.json')
    insertListRequest(messageVxRackVersion4, 'listRCMDefinitionRequest16.json', 'listRCMDefinitionResponse16.json')
    insertListRequest(messageVxRackTrain, 'listRCMDefinitionRequest17.json', 'listRCMDefinitionResponse17.json')
    insertListRequest(messageVxRackModel, 'listRCMDefinitionRequest18.json', 'listRCMDefinitionResponse18.json')
    insertListRequest(messageVxRackFamily, 'listRCMDefinitionRequest19.json', 'listRCMDefinitionResponse19.json')


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


def resetTestQueues(testRequest, testResponse):
    messageReqHeader = {'__TypeId__': 'com.dell.cpsd.rfds.rcm.definition.service.list.rcm.definitions'}
    messageResHeader = {'__TypeId__': 'com.dell.cpsd.rcm.definition.service.rcm.definitions.summary'}

    af_support_tools.rmq_purge_queue(host=hostTLS, port=portTLS, ssl_enabled=True, queue=testRequest)
    af_support_tools.rmq_purge_queue(host=hostTLS, port=portTLS, ssl_enabled=True, queue=testResponse)

    af_support_tools.rmq_bind_queue(host=hostTLS, port=portTLS, ssl_enabled=True,
                                    queue='testListRCMDefinitionsRequest',
                                    exchange='exchange.dell.cpsd.rfds.rcm.definition.request', routing_key='#')
    af_support_tools.rmq_bind_queue(host=hostTLS, port=portTLS, ssl_enabled=True,
                                    queue='testListRCMDefinitionsResponse',
                                    exchange='exchange.dell.cpsd.rfds.rcm.definition.response', routing_key='#')


def insertListRequest(payLoad, requestFile, responseFile):
    messageReqHeader = {'__TypeId__': 'com.dell.cpsd.rfds.rcm.definition.service.list.rcm.definitions'}
    messageResHeader = {'__TypeId__': 'com.dell.cpsd.rcm.definition.service.rcm.definitions.summary'}

    resetTestQueues('testListRCMDefinitionsRequest', 'testListRCMDefinitionsResponse')
    time.sleep(2)
    global PAYLoad
    PAYLoad = payLoad
    print("Payload A: %s" % payLoad)

    af_support_tools.rmq_publish_message(host=hostTLS, port=portTLS, ssl_enabled=True,
                                         exchange="exchange.dell.cpsd.rfds.rcm.definition.request",
                                         routing_key="dell.cpsd.rfds.rcm.definition.request", headers=messageReqHeader,
                                         payload=payLoad, payload_type='json')
    time.sleep(2)
    my_request_body = af_support_tools.rmq_consume_message(host=hostTLS, port=portTLS, ssl_enabled=True,
                                                           queue='testListRCMDefinitionsRequest')
    my_response_body = af_support_tools.rmq_consume_message(host=hostTLS, port=portTLS, ssl_enabled=True,
                                                            queue='testListRCMDefinitionsResponse')

    af_support_tools.rmq_payload_to_file(my_request_body, path + requestFile)
    af_support_tools.rmq_payload_to_file(my_response_body, path + responseFile)
    time.sleep(1)

    resetTestQueues('testListRCMDefinitionsRequest', 'testListRCMDefinitionsResponse')


def verifyPublishedAttributes(filename):
    countInstances = 0
    # insertListRequest(payload, 'listRCMDefinitionRequest1.json', 'listRCMDefinitionResponse1.json')
    with open(filename, "rU") as dataFile:
        dataInput = json.load(dataFile)

    print(dataInput.keys())
    print ("\nName of file: %s" % dataFile.name)

    assert ("correlationId") in dataInput.keys(), "Correlation ID not included in published attributes."
    assert ("hostname") in dataInput.keys(), "Hostname not included in published attributes."
    assert ("rcmTrain") in dataInput.keys(), "Train not included in published attributes."
    assert ("rcmVersion") in dataInput.keys(), "Version not included in published attributes."
    assert ("routingKey") in dataInput.keys(), "Routing Key not included in published attributes."
    assert ("systemProductFamily") in dataInput.keys(), "Product not included in published attributes."
    assert ("systemModelFamily") in dataInput.keys(), "Model not included in published attributes."
    assert ("timestamp") in dataInput.keys(), "Timestamp not included in published attributes."

    countInstances += 1

    return dataInput


def verifyConsumedAttributesVersion(requestFile, responseFile):
    numRCMs = 0
    # x = 0
    i = 0
    # UUIDList = []
    # viewOption = []
    # RCMVersions = []
    #
    # dataInput = {}
    # data = {}
    # countInstances = 0

    requestData = open(requestFile, "rU")
    dataInput = json.load(requestData)

    dataFile = open(responseFile, "rU")
    data = json.load(dataFile)
    print(data.keys())
    print ("\nName of file: %s" % dataFile.name)

    if ("errorCode") in data.keys():
        print(data["errorCode"])
        if ("errorMessage") in data.keys():
            print(data["errorMessage"])
            assert (data["errorCode"][:-2]) in (
            data["errorMessage"]), "Returned Error Code not included in Error Message."
            assert ('orrelation') or ('uid') in (
            data["errorMessage"]), "Returned Error Message does not reflect missing correlation ID."

    if ("rcms") in data.keys():
        numRCMs = len(data["rcms"])
        if numRCMs == 0:
            print("\nNo RCMs found based on the requested details.")
            print("\nRCM details shown: %s" % (data["rcms"]))

        if numRCMs > 0:
            while i < numRCMs:
                print("\nNumber of RCMs returned: %d" % numRCMs)
                print(data["rcms"][i]["systemModelFamily"])
                print(dataInput['rcmTrain'][:-2])
                print(data["rcms"][i]["rcmTrain"])
                print(data["rcms"][i]["rcmVersion"])
                print(dataInput["systemProductFamily"])
                print(data["rcms"][i]["systemProductFamily"])
                # print(dataInput['uuid'])
                assert (dataInput['correlationId']) == (
                data["correlationId"]), "Correlation Ids on request and response do not match."
                assert (dataInput['rcmTrain'][:-2]) == (data["rcms"][i]["rcmTrain"]), "Train does not match."
                assert (dataInput['rcmTrain'][:-2]) in (data["rcms"][i]["rcmVersion"]), "Version does not match."
                assert data["rcms"][i]["systemModelFamily"] == (dataInput["systemModelFamily"]), "Model does not match."
                assert data["rcms"][i]["systemProductFamily"] == (
                dataInput["systemProductFamily"]), "Product does not match."
                i += 1

                # if numRCMs == 1:
                # assert data["rcms"][0]["uuid"] == dataInput['uuid'], "Not the single RCM returned as expected."

        print("Response attributes match those defined in request.")


def verifyConsumedAttributesTrain(requestFile, responseFile):
    numRCMs = 0
    i = 0

    requestData = open(requestFile, "rU")
    dataInput = json.load(requestData)

    dataFile = open(responseFile, "rU")
    data = json.load(dataFile)
    print(data.keys())
    print ("\nName of file: %s" % dataFile.name)

    if ("errorCode") in data.keys():
        print(data["errorCode"])
        if ("errorMessage") in data.keys():
            print(data["errorMessage"])
            assert (data["errorCode"][:-2]) in (
            data["errorMessage"]), "Returned Error Code not included in Error Message."
            assert ('orrelation') or ('uid') in (
            data["errorMessage"]), "Returned Error Message does not reflect missing correlation ID."

    if ("rcms") in data.keys():
        numRCMs = len(data["rcms"])
        if numRCMs == 0:
            print("\nNo RCMs found based on the requested details.")
            print("\nRCM details shown: %s" % (data["rcms"]))

        if numRCMs > 0:
            while i < numRCMs:
                print("\nNumber of RCMs returned: %d" % numRCMs)
                print(data["rcms"][i]["systemModelFamily"])
                print(dataInput['rcmTrain'][:-2])
                print(data["rcms"][i]["rcmTrain"])
                print(data["rcms"][i]["rcmVersion"])
                print(dataInput["systemProductFamily"])
                print(data["rcms"][i]["systemProductFamily"])
                assert (dataInput['correlationId']) == (
                data["correlationId"]), "Correlation Ids on request and response do not match."
                assert (dataInput['rcmTrain'][:-2]) == (data["rcms"][i]["rcmTrain"]), "Train does not match."
                assert (dataInput['rcmTrain'][:-2]) in (data["rcms"][i]["rcmVersion"]), "Version does not match."
                assert data["rcms"][i]["systemModelFamily"] == (dataInput["systemModelFamily"]), "Model does not match."
                assert data["rcms"][i]["systemProductFamily"] == (
                dataInput["systemProductFamily"]), "Product does not match."
                i += 1

        print("Response attributes match those defined in request.")


def verifyConsumedAttributesModel(requestFile, responseFile):
    numRCMs = 0
    i = 0

    requestData = open(requestFile, "rU")
    dataInput = json.load(requestData)

    dataFile = open(responseFile, "rU")
    data = json.load(dataFile)
    print(data.keys())
    print ("\nName of file: %s" % dataFile.name)

    if ("errorCode") in data.keys():
        print(data["errorCode"])
        if ("errorMessage") in data.keys():
            print(data["errorMessage"])
            assert (data["errorCode"][:-2]) in (
            data["errorMessage"]), "Returned Error Code not included in Error Message."
            assert ('orrelation') or ('uid') in (
            data["errorMessage"]), "Returned Error Message does not reflect missing correlation ID."

    if ("rcms") in data.keys():
        numRCMs = len(data["rcms"])
        if numRCMs == 0:
            print("\nNo RCMs found based on the requested details.")
            print("\nRCM details shown: %s" % (data["rcms"]))

        if numRCMs > 0:
            while i < numRCMs:

                print("\nNumber of RCMs returned: %d" % numRCMs)
                print(data["rcms"][i]["systemModelFamily"])
                print(dataInput['rcmTrain'][:-2])
                print(data["rcms"][i]["rcmTrain"])
                print(data["rcms"][i]["rcmVersion"])
                print(dataInput["systemProductFamily"])
                print(data["rcms"][i]["systemProductFamily"])
                assert (dataInput['correlationId']) == (
                data["correlationId"]), "Correlation Ids on request and response do not match."
                if not ((dataInput["systemModelFamily"]) == "" or (dataInput["systemModelFamily"]) == " "):
                    assert data["rcms"][i]["systemModelFamily"] == (
                    dataInput["systemModelFamily"]), "Model does not match."
                assert data["rcms"][i]["systemProductFamily"] == (
                dataInput["systemProductFamily"]), "Product does not match."
                i += 1

                # if numRCMs == 1:
                # assert data["rcms"][0]["uuid"] == dataInput['uuid'], "Not the single RCM returned as expected."

        print("Response attributes match those defined in request.")


def verifyConsumedAttributesFamily(requestFile, responseFile):
    numRCMs = 0
    i = 0

    requestData = open(requestFile, "rU")
    dataInput = json.load(requestData)

    dataFile = open(responseFile, "rU")
    data = json.load(dataFile)
    print(data.keys())
    print ("\nName of file: %s" % dataFile.name)

    if ("errorCode") in data.keys():
        print(data["errorCode"])
        if ("errorMessage") in data.keys():
            print(data["errorMessage"])
            assert (data["errorCode"][:-2]) in (
            data["errorMessage"]), "Returned Error Code not included in Error Message."
            assert ('orrelation') or ('uid') in (
            data["errorMessage"]), "Returned Error Message does not reflect missing correlation ID."

    if ("rcms") in data.keys():
        numRCMs = len(data["rcms"])
        if numRCMs == 0:
            print("\nNo RCMs found based on the requested details.")
            print("\nRCM details shown: %s" % (data["rcms"]))

        if numRCMs > 0:
            while i < numRCMs:

                print("\nNumber of RCMs returned: %d" % numRCMs)
                print(data["rcms"][i]["systemModelFamily"])
                print(dataInput['rcmTrain'][:-2])
                print(data["rcms"][i]["rcmTrain"])
                print(data["rcms"][i]["rcmVersion"])
                print(dataInput["systemProductFamily"])
                (dataInput["systemProductFamily"]) = (dataInput["systemProductFamily"]).lower()
                (data["rcms"][i]["systemProductFamily"]) = (data["rcms"][i]["systemProductFamily"]).lower()
                print(dataInput["systemProductFamily"])
                print(data["rcms"][i]["systemProductFamily"])
                # print(dataInput['uuid'])
                assert (dataInput['correlationId']) == (
                data["correlationId"]), "Correlation Ids on request and response do not match."

                if not ((dataInput["systemModelFamily"]) == "" or (dataInput["systemModelFamily"]) == " "):
                    assert data["rcms"][i]["systemModelFamily"] == (
                    dataInput["systemModelFamily"]), "Model does not match."
                if not ((dataInput["systemProductFamily"]) == "" or (dataInput["systemProductFamily"]) == " "):
                    assert data["rcms"][i]["systemProductFamily"] == (
                    dataInput["systemProductFamily"]), "Product does not match."
                i += 1

        print("Response attributes match those defined in request.")


def verifyCorrectCorrelationID(requestFile, responseFile):
    requestData = {}
    responseData = {}
    # print("\nStarting to verify reply returns the correct correlation ID in message body.")

    data_request = open(requestFile, 'r')
    requestData = json.load(data_request)

    data_response = open(responseFile, 'r')
    responseData = json.load(data_response)

    print("Input: %s" % requestData["correlationId"])
    print("Output: %s" % responseData["correlationId"])

    if requestData["correlationId"] != "":
        if responseData["correlationId"] != "":
            assert requestData["correlationId"] == responseData[
                "correlationId"], "Correlation ID on response message does not match."

    print("All verification steps executed successfully.....")


# print (" [x] Sent JSON data to RabbitMQ......")


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes1():
    verifyPublishedAttributes(path + "listRCMDefinitionRequest1.json")


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes2():
    verifyPublishedAttributes(path + "listRCMDefinitionRequest2.json")


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes3():
    verifyPublishedAttributes(path + 'listRCMDefinitionRequest3.json')


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes4():
    verifyPublishedAttributes(path + 'listRCMDefinitionRequest4.json')


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes5():
    verifyPublishedAttributes(path + 'listRCMDefinitionRequest5.json')


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes6():
    verifyPublishedAttributes(path + 'listRCMDefinitionRequest6.json')


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes7():
    verifyPublishedAttributes(path + 'listRCMDefinitionRequest7.json')


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes8():
    verifyPublishedAttributes(path + 'listRCMDefinitionRequest8.json')


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes9():
    verifyPublishedAttributes(path + 'listRCMDefinitionRequest9.json')


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes10():
    verifyPublishedAttributes(path + 'listRCMDefinitionRequest10.json')


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes11():
    verifyPublishedAttributes(path + 'listRCMDefinitionRequest11.json')


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes12():
    verifyPublishedAttributes(path + 'listRCMDefinitionRequest12.json')


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes13():
    verifyPublishedAttributes(path + 'listRCMDefinitionRequest13.json')


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes14():
    verifyPublishedAttributes(path + 'listRCMDefinitionRequest14.json')


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes15():
    verifyPublishedAttributes(path + 'listRCMDefinitionRequest15.json')


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes16():
    verifyPublishedAttributes(path + 'listRCMDefinitionRequest16.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes17():
    verifyPublishedAttributes(path + 'listRCMDefinitionRequest17.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes18():
    verifyPublishedAttributes(path + 'listRCMDefinitionRequest18.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyPublishedAttributes19():
    verifyPublishedAttributes(path + 'listRCMDefinitionRequest19.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes1():
    verifyConsumedAttributesVersion(path + "listRCMDefinitionRequest1.json", path + "listRCMDefinitionResponse1.json")


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes2():
    verifyConsumedAttributesTrain(path + 'listRCMDefinitionRequest2.json', path + 'listRCMDefinitionResponse2.json')


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes3():
    verifyConsumedAttributesModel(path + 'listRCMDefinitionRequest3.json', path + 'listRCMDefinitionResponse3.json')


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes4():
    verifyConsumedAttributesFamily(path + 'listRCMDefinitionRequest4.json', path + 'listRCMDefinitionResponse4.json')


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes5():
    verifyConsumedAttributesFamily(path + 'listRCMDefinitionRequest5.json', path + 'listRCMDefinitionResponse5.json')


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes6():
    verifyConsumedAttributesFamily(path + 'listRCMDefinitionRequest6.json', path + 'listRCMDefinitionResponse6.json')


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes7():
    verifyConsumedAttributesFamily(path + 'listRCMDefinitionRequest7.json', path + 'listRCMDefinitionResponse7.json')


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes8():
    verifyConsumedAttributesFamily(path + 'listRCMDefinitionRequest8.json', path + 'listRCMDefinitionResponse8.json')


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes9():
    verifyConsumedAttributesFamily(path + 'listRCMDefinitionRequest9.json', path + 'listRCMDefinitionResponse9.json')


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes10():
    verifyConsumedAttributesFamily(path + 'listRCMDefinitionRequest10.json', path + 'listRCMDefinitionResponse10.json')


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes11():
    verifyConsumedAttributesFamily(path + 'listRCMDefinitionRequest11.json', path + 'listRCMDefinitionResponse11.json')


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes12():
    verifyConsumedAttributesFamily(path + 'listRCMDefinitionRequest12.json', path + 'listRCMDefinitionResponse12.json')


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes13():
    verifyConsumedAttributesFamily(path + 'listRCMDefinitionRequest13.json', path + 'listRCMDefinitionResponse13.json')


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes14():
    verifyConsumedAttributesFamily(path + 'listRCMDefinitionRequest14.json', path + 'listRCMDefinitionResponse14.json')


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes15():
    verifyConsumedAttributesFamily(path + 'listRCMDefinitionRequest15.json', path + 'listRCMDefinitionResponse15.json')


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes16():
    verifyConsumedAttributesFamily(path + 'listRCMDefinitionRequest16.json', path + 'listRCMDefinitionResponse16.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes17():
    verifyConsumedAttributesFamily(path + 'listRCMDefinitionRequest17.json', path + 'listRCMDefinitionResponse17.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes18():
    verifyConsumedAttributesFamily(path + 'listRCMDefinitionRequest18.json', path + 'listRCMDefinitionResponse18.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes19():
    verifyConsumedAttributesFamily(path + 'listRCMDefinitionRequest19.json', path + 'listRCMDefinitionResponse19.json')


# #connection.close()
