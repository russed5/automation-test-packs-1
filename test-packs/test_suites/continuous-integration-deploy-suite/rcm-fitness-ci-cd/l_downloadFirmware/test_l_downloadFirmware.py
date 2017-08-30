#!/usr/bin/python
import pika
import json
import time
import af_support_tools
import pytest
import os
import re
import datetime


@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    global path
    path = "/home/autouser/PycharmProjects/auto-framework/test_suites/continuous-integration-deploy-suite/rcm-fitness-ci-cd/l_downloadFirmware/"
    global ssl_options
    ssl_options = {"ca_certs": "/etc/rabbitmq/certs/testca/cacert.pem",
                   "certfile": "/etc/rabbitmq/certs/certs/client/cert.pem",
                   "keyfile": "/etc/rabbitmq/certs/certs/client/key.pem", "cert_reqs": "ssl.CERT_REQUIRED",
                   "ssl_version": "ssl.PROTOCOL_TLSv1_2"}

    # Update config ini files at runtime
    # my_data_file = 'listRCMs.properties'
    my_data_file = os.environ.get(
        'AF_RESOURCES_PATH') + '/continuous-integration-deploy-suite/downloadInputs.properties'
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
    payload_file = 'continuous-integration-deploy-suite/downloadInputs.ini'
    global payload_header
    payload_header = 'payload'
    global payload_message
    payload_message = 'first_download'
    global payload_messageSec
    payload_messageSec = 'second_download'
    global payload_messageThird
    payload_messageThird = 'third_download'
    global payload_messageInvalidFile
    payload_messageInvalidFile = 'invalid_file'
    global payload_messageInvalidReplyTo
    payload_messageInvalidReplyTo = 'invalid_replyto'
    global payload_messageInvalidSwid
    payload_messageInvalidSwid = 'invalid_swid'
    global payload_messageInvalidAll
    payload_messageInvalidAll = 'invalid_all'
    global payload_messageNoFile
    payload_messageNoFile = 'no_file'
    global payload_messageNoReplyTo
    payload_messageNoReplyTo = 'no_replyto'
    global payload_messageNoSwid
    payload_messageNoSwid = 'no_swid'
    global payload_messageNoAll
    payload_messageNoAll = 'no_all'

    global ipaddress
    ipaddress = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')
    global cli_username
    cli_username = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                             property='username')
    global cli_password
    cli_password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                             property='password')

    ensurePathExists(path)
    purgeOldOutput(path, "loadFW")
    purgeOldOutput(path, "invalid")
    purgeOldOutput(path, "no")

    global message
    message = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header, property=payload_message)
    global messageSec
    messageSec = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                           property=payload_messageSec)
    global messageThird
    messageThird = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                             property=payload_messageThird)
    global messageInvalidFile
    messageInvalidFile = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                               property=payload_messageInvalidFile)
    global messageInvalidReplyTo
    messageInvalidReplyTo = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                               property=payload_messageInvalidReplyTo)
    global messageInvalidSwid
    messageInvalidSwid = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                               property=payload_messageInvalidSwid)
    global messageInvalidAll
    messageInvalidAll = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                               property=payload_messageInvalidAll)
    global messageNoFile
    messageNoFile = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                               property=payload_messageNoFile)
    global messageNoReplyTo
    messageNoReplyTo = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                               property=payload_messageNoReplyTo)
    global messageNoSwid
    messageNoSwid = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                               property=payload_messageNoSwid)
    global messageNoAll
    messageNoAll = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                               property=payload_messageNoAll)


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


def resetTestQueues():
    # messageReqHeader = {'__TypeId__': 'com.dell.cpsd.esrs.service.download.credentials.requested'}
    # messageResHeaderComplete = {'__TypeId__': 'com.dell.cpsd.prepositioning.downloader.file.download.completed'}
    # messageResHeaderProgress = {'__TypeId__': 'com.dell.cpsd.prepositioning.downloader.file.download.progress'}

    credentials = pika.PlainCredentials(rmq_username, rmq_password)
    parameters = pika.ConnectionParameters(host, port, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    af_support_tools.rmq_purge_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username, queue='testDownloadFWRequest',
                                     ssl_enabled=False)
    af_support_tools.rmq_purge_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                     queue='testDownloadFWResponse', ssl_enabled=False)
    af_support_tools.rmq_purge_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                     queue='testCredentialsRequest', ssl_enabled=False)
    af_support_tools.rmq_purge_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                     queue='testCredentialsResponse', ssl_enabled=False)

    time.sleep(0.5)
    print("Old test queues successfully purged.")

    af_support_tools.rmq_bind_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                    queue='testDownloadFWRequest', exchange='exchange.dell.cpsd.prepositioning.downloader.request',
                                    routing_key='#', ssl_enabled=False)
    af_support_tools.rmq_bind_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                    queue='testDownloadFWResponse',
                                    exchange='exchange.dell.cpsd.prepositioning.assetmanager.response',
                                    routing_key='#', ssl_enabled=False)
    af_support_tools.rmq_bind_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                    queue='testCredentialsRequest', exchange='exchange.dell.cpsd.esrs.request',
                                    routing_key='#', ssl_enabled=False)
    af_support_tools.rmq_bind_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                    queue='testCredentialsResponse', exchange='exchange.dell.cpsd.esrs.response',
                                    routing_key='#', ssl_enabled=False)
    print("New test queues successfully initialized.")


def downloadFWFileRequest(payLoad, requestFile, requestCredentials, responseFileComplete):
    messageReqHeader = {'__TypeId__': 'com.dell.cpsd.prepositioning.downloader.file.download.request'}
    messageResHeaderComplete = {'__TypeId__': 'com.dell.cpsd.prepositioning.downloader.file.download.completed'}
    messageResHeaderProgress = {'__TypeId__': 'com.dell.cpsd.prepositioning.downloader.file.download.progress'}

    credentials = pika.PlainCredentials(rmq_username, rmq_password)
    parameters = pika.ConnectionParameters(host, port, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    resetTestQueues()
    print("Queues reset.")

    time.sleep(2)
    deletePreviousDownloadFiles("BIOS_PFWCY_WN64_2.2.5.EXE",
                              "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads/")
    print("Previous downloads deleted.")
    time.sleep(2)

    af_support_tools.rmq_publish_message(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                         exchange="exchange.dell.cpsd.prepositioning.downloader.request",
                                         routing_key="dell.cpsd.prepositioning.downloader.request",
                                         headers=messageReqHeader, payload=payLoad, payload_type='json',
                                         ssl_enabled=False)

    print("Download request published.")

    time.sleep(2)
    q_len = 0
    timeout = 0

    while q_len < 1:
        time.sleep(1)
        timeout += 1

        q_len = af_support_tools.rmq_message_count(host=host, port=port,
                                                           rmq_username=rmq_username, rmq_password=rmq_username,
                                                           queue='testCredentialsResponse', ssl_enabled=False)

        # If the test queue doesn't get a message them something is wrong. Time out needs to be high as msg can take 3+ minutes
        if timeout > 60:
            print("ERROR: ESRS Credential response took too long to return.")
            break

    my_request_body = af_support_tools.rmq_consume_message(host=host, port=port,
                                                           rmq_username=rmq_username, rmq_password=rmq_username,
                                                           queue='testDownloadFWRequest',
                                                           ssl_enabled=False)
    af_support_tools.rmq_payload_to_file(my_request_body, path + requestFile)
    time.sleep(2)
    my_response_credentials_body = af_support_tools.rmq_consume_all_messages(host=host, port=port, rmq_username=rmq_username,
                                                                        rmq_password=rmq_username,
                                                                        queue='testCredentialsResponse',
                                                                        ssl_enabled=False)
    af_support_tools.rmq_payload_to_file(my_response_credentials_body, path + requestCredentials)

    print("Download request and credential response(s) consumed.")
    time.sleep(120)

    my_response_download_body = af_support_tools.rmq_consume_all_messages(host=host, port=port,
                                                                          rmq_username=rmq_username,
                                                                          rmq_password=rmq_username,
                                                                          queue='testDownloadFWResponse',
                                                                          ssl_enabled=False)
    af_support_tools.rmq_payload_to_file(my_response_download_body, path + responseFileComplete)

    print("Download response consumed.")

    time.sleep(1)


def downloadFWFileMulti(payLoad, secPayLoad, thirdPayLoad, requestFile, requestCredentials, responseFileComplete):
    resetTestQueues()
    messageReqHeader = {'__TypeId__': 'com.dell.cpsd.prepositioning.downloader.file.download.request'}
    time.sleep(2)
    print("Queues reset.")

    deletePreviousDownloadFiles("BIOS_PFWCY_WN64_2.2.5.EXE",
                                "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads/")

    print("Previous downloads deleted.")
    time.sleep(2)

    af_support_tools.rmq_publish_message(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                         exchange="exchange.dell.cpsd.prepositioning.downloader.request",
                                         routing_key="dell.cpsd.prepositioning.downloader.request",
                                         headers=messageReqHeader, payload=payLoad, payload_type='json',
                                         ssl_enabled=False)
    time.sleep(2)

    af_support_tools.rmq_publish_message(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                         exchange="exchange.dell.cpsd.prepositioning.downloader.request",
                                         routing_key="dell.cpsd.prepositioning.downloader.request",
                                         headers=messageReqHeader, payload=secPayLoad, payload_type='json',
                                         ssl_enabled=False)
    time.sleep(2)

    af_support_tools.rmq_publish_message(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                         exchange="exchange.dell.cpsd.prepositioning.downloader.request",
                                         routing_key="dell.cpsd.prepositioning.downloader.request",
                                         headers=messageReqHeader, payload=thirdPayLoad, payload_type='json',
                                         ssl_enabled=False)

    print("Three file download requests published.")

    time.sleep(2)
    q_len = 0
    timeout = 0

    while q_len < 3:
        time.sleep(1)
        timeout += 1

        q_len = af_support_tools.rmq_message_count(host=host, port=port,
                                                           rmq_username=rmq_username, rmq_password=rmq_username,
                                                           queue='testCredentialsResponse', ssl_enabled=False)

        # If the test queue doesn't get a message them something is wrong. Time out needs to be high as msg can take 3+ minutes
        if timeout > 60:
            print("ERROR: ESRS Credential response took too long to return.")
            break

    my_request_body = af_support_tools.rmq_consume_all_messages(host=host, port=port,
                                                           rmq_username=rmq_username, rmq_password=rmq_username,
                                                           queue='testDownloadFWRequest',
                                                           ssl_enabled=False)
    af_support_tools.rmq_payload_to_file(my_request_body, path + requestFile)
    time.sleep(10)
    my_response_credentials_body = af_support_tools.rmq_consume_all_messages(host=host, port=port, rmq_username=rmq_username,
                                                                        rmq_password=rmq_username,
                                                                        queue='testCredentialsResponse',
                                                                        ssl_enabled=False)
    af_support_tools.rmq_payload_to_file(my_response_credentials_body, path + requestCredentials)

    print("Download request and credential response(s) consumed.")
    time.sleep(60)

    my_response_download_body = af_support_tools.rmq_consume_all_messages(host=host, port=port,
                                                                          rmq_username=rmq_username,
                                                                          rmq_password=rmq_username,
                                                                          queue='testDownloadFWResponse',
                                                                          ssl_enabled=False)
    af_support_tools.rmq_payload_to_file(my_response_download_body, path + responseFileComplete)

    print("Download response consumed.")

    time.sleep(1)


def downloadFWFileRequestInvalid(payLoad, requestFile, requestCredentials, responseFileComplete):
    messageReqHeader = {'__TypeId__': 'com.dell.cpsd.prepositioning.downloader.file.download.request'}
    resetTestQueues()
    print("Queues reset.")
    time.sleep(2)
    deletePreviousDownloadFiles("BIOS_PFWCY_WN64_2.2.5.EXE",
                                "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads/")

    print("Previous downloads deleted.")

    # af_support_tools.rmq_publish_message(host=host, port=port, rmq_username=uname, rmq_password=password,
    #                                      exchange="exchange.dell.cpsd.esrs.request",
    #                                      routing_key="dell.cpsd.esrs.download.request",
    #                                      headers=messageReqHeader, payload=payLoad, ssl_enabled=False)

    af_support_tools.rmq_publish_message(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                         exchange="exchange.dell.cpsd.prepositioning.downloader.request",
                                         routing_key="dell.cpsd.prepositioning.downloader.request",
                                         headers=messageReqHeader, payload=payLoad, payload_type='json',
                                         ssl_enabled=False)
    print("Download request with invalid properties published.")
    time.sleep(2)
    q_len = 0
    timeout = 0

    while q_len < 1:
        time.sleep(1)
        timeout += 1

        q_len = af_support_tools.rmq_message_count(host=host, port=port,
                                                           rmq_username=rmq_username, rmq_password=rmq_username,
                                                           queue='testCredentialsResponse', ssl_enabled=False)

        # If the test queue doesn't get a message them something is wrong. Time out needs to be high as msg can take 3+ minutes
        if timeout > 60:
            print("ERROR: ESRS Credential response took too long to return.")
            break

    my_request_body = af_support_tools.rmq_consume_message(host=host, port=port,
                                                           rmq_username=rmq_username, rmq_password=rmq_username,
                                                           queue='testDownloadFWRequest', ssl_enabled=False)
    af_support_tools.rmq_payload_to_file(my_request_body, path + requestFile)


    my_response_credentials_body = af_support_tools.rmq_consume_message(host=host, port=port,
                                                                        rmq_username=rmq_username,
                                                                        rmq_password=rmq_username,
                                                                        queue='testCredentialsResponse',
                                                                        ssl_enabled=False)
    af_support_tools.rmq_payload_to_file(my_response_credentials_body, path + requestCredentials)
    print("Download request and credential response consumed.")

    time.sleep(2)
    my_response_download_body = af_support_tools.rmq_consume_all_messages(host=host, port=port,
                                                                     rmq_username=rmq_username,
                                                                     rmq_password=rmq_username,
                                                                     queue='testDownloadFWResponse', ssl_enabled=False)
    af_support_tools.rmq_payload_to_file(my_response_download_body, path + responseFileComplete)
    print("All download responses consumed.")
    time.sleep(1)


def verifyPublishedAttributes(filename):
    countInstances = 0
    with open(filename, "rU") as dataFile:
        dataInput = json.load(dataFile)

    print(dataInput.keys())
    print("\nName of file: %s" % dataFile.name)

    if len(dataInput["messageProperties"]) > 0:
        assert "timestamp" in dataInput["messageProperties"], "Timestamp not included in published attributes."
        assert "correlationId" in dataInput["messageProperties"], "Correlation Id not included in published attributes."
        assert "replyTo" in dataInput["messageProperties"], "Reply To not included in published attributes."
        assert "swid" in dataInput.keys(), "Swid not included in published attributes."
        # assert "url" in dataInput.keys(), "URL not included in published attributes."
        assert "fileName" in dataInput.keys(), "fileName not included in published attributes."
        return

    assert False, ("Unable to verify published attributes.")


def verifyMultiPublishedAttributes(filename):
    count = 0
    with open(filename, "rU") as dataFile:
        dataInput = json.load(dataFile)

    print(dataInput[count].keys())
    print("\nName of file: %s" % dataFile.name)

    assert len(dataInput) == 3, "Expected to find three published messages."
    if len(dataInput) > 0:
        while count < len(dataInput):
            assert "timestamp" in dataInput[count][
                "messageProperties"], "Timestamp not included in published attributes."
            assert "correlationId" in dataInput[count][
                "messageProperties"], "Correlation Id not included in published attributes."
            assert "replyTo" in dataInput[count]["messageProperties"], "Reply To not included in published attributes."
            assert "swid" in dataInput[count].keys(), "Swid not included in published attributes."
            # assert "url" in dataInput[count].keys(), "URL not included in published attributes."
            assert "fileName" in dataInput[count].keys(), "fileName not included in published attributes."
            assert dataInput[count]["swid"] == "VCEVISIONDEV01", "Unexpected SWID returned."
            assert dataInput[count]["messageProperties"]["replyTo"] == "dell.cpsd.prepositioning.downloader.completed"
            # assert dataInput[count]["url"] is "", "URL is not empty."
            count += 1
            return

    assert False, "Unable to verify published attributes."

def verifyConsumedAttributes(filename, requestFile, credentialsFile, responseFile, hashType, family, esrsURL):
    numRCMs = 0
    count = 0
    credCount = 0
    hashVal = []
    filepath = "file:///opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads"
    requestData = open(requestFile, "rU")
    dataInput = json.load(requestData)

    credentialsData = open(credentialsFile, "rU")
    dataCredentials = json.load(credentialsData)

    dataFile = open(responseFile, "rU")
    data = json.load(dataFile)
    print(data)
    print("\nName of file: %s" % dataFile.name)

    size = checkFileSize(filename, "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads/")
    # sizeMD5 = checkFileSize("VMW-ESX-6.0.0-lsi_mr3-6.903.85.00_MR-3818071.zip.md5",
    #                          "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads/")
    # sizeRAID = checkFileSize("VMW-ESX-6.0.0-lsi_mr3-6.903.85.00_MR-3818071.zip",
    #                          "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads/")

    maxCount = len(data)
    maxCreds = len(dataCredentials)
    print("Total messages consumed: %d" % maxCount)
    while count < maxCount:

        if ("errorCode") in data[count].keys():
            print(data[count]["errorCode"])
            if ("errorMessage") in data[count].keys():
                print(data[count]["errorMessage"])
                assert (data[count]["errorCode"][:-2]) in (
                    data[count]["errorMessage"]), "Returned Error Code not included in Error Message."
                assert ('orrelation') or ('uid') in (
                    data[count]["errorMessage"]), "Returned Error Message does not reflect missing correlation ID."



        for i in range(maxCount):
            if ("url") in data[i].keys():
                print("Count: %d" % i)
                print("HERE NOW")
                assert "timestamp" in data[i]["messageProperties"], "Timestamp not included in consumed attributes."
                assert "correlationId" in data[i][
                    "messageProperties"], "Correlation Id not included in consumed attributes."
                assert "replyTo" in data[i]["messageProperties"], "Reply To not included in consumed attributes."
                assert "hashType" in data[i].keys(), "Hash Type not included in consumed attributes."
                assert "hashVal" in data[i].keys(), "Hash not included in consumed attributes."
                assert "fileName" in data[i].keys(), "Swid not included in consumed attributes."
                assert "size" in data[i].keys(), "Size not included in consumed attributes."
                assert "fileUUID" in data[i].keys(), "File UUID not included in consumed attributes."
                assert filepath in data[i]["url"], "Download complete does not include expected URL."

                # assert data["swid"] == dataCredentials["swid"], "Swids don't match in consumed messages."
                # assert data[maxCount-1]["size"] == sizeNIC or sizeBIOS or sizeRAID, "Size not consistent with expected value."
                assert data[i]["size"] == size, "Size not consistent with expected value."
                assert dataInput["messageProperties"]["correlationId"] in data[i]["messageProperties"][
                    "correlationId"], "Corr Ids don't match in consumed messages."
                assert dataInput["messageProperties"]["replyTo"] == data[i]["messageProperties"][
                    "replyTo"], "Corr Ids don't match in consumed messages."
                assert data[i]["hashType"] == hashType, "Incorrect hashType detailed."

                hashVal.append(data[i]["hashVal"])
                while credCount < maxCreds:
                    if data[i]["size"] == dataCredentials[credCount]["size"]:
                        print(data[i]["size"])
                        print(dataCredentials[credCount]["size"])
                        assert filepath in data[i]["url"], "Unexpected URL returned."
                        assert data[i]["fileName"] in data[i]["url"], "Unexpected URL returned."
                        assert data[i]["fileUUID"] == dataCredentials[credCount]["fileUUID"], "FileUUIDs don't match in consumed messages."

                    credCount += 1

            else:
                print("Consumed download response message not a Complete.")

        for cred in range(maxCreds):
            print("Cred count: %d" % cred)
            print("Total creds: %d" % maxCreds)
            if dataCredentials[cred]["fileFound"] == True:
                if ("url") in dataCredentials[cred].keys():
                    assert dataInput["fileName"] in dataCredentials[cred]["fileName"], "File names are not consistent."
                    assert dataCredentials[cred]["swid"] in dataCredentials[cred]["url"], "Swid not included in Credential response URL."
                    assert dataCredentials[cred]["size"] == size, "Size not consistent with expected value."
                    assert dataInput["messageProperties"]["correlationId"] in dataCredentials[cred]["messageProperties"][
                        "correlationId"], "Corr Ids don't match in consumed messages."
                    assert dataInput["messageProperties"]["replyTo"] == dataCredentials[cred]["messageProperties"][
                        "replyTo"], "Corr Ids don't match in consumed messages."
                    assert dataCredentials[cred]["hashType"] == hashType, "Incorrect hashType detailed."
                    assert dataCredentials[cred]["size"] == size, "Size not consistent with expected value."
                    assert esrsURL in dataCredentials[cred]["url"], "Host and port details incorrect in returned URL"
                    assert dataCredentials[cred]["swid"] in dataCredentials[cred]["header"][
                        "authorization"], "Swid not included in Credential response URL authorization details."
                    assert family in dataCredentials[cred]["header"][
                        "authorization"], "Swid not included in Credential response URL authorization details."
                    # assert dataCredentials["header"][
                    #            "productFamily"] == family, "Product Family not included in Credential response URL authorization details."
                    assert dataCredentials[cred]["header"]["serialNumber"] == dataCredentials[cred][
                        "swid"], "Serial number not match Swid in Credential response URL authorization details."

                    assert dataCredentials[cred]["hashVal"] in hashVal, "Hash values do not match."
                    return

        count += 1


    assert False, "Consumed response messages not complete."


def verifyMultiConsumedAttributes(requestFile, credentialsFile, responseFile, hashType, family, esrsURL):
    count = 0

    filepath = "file:///opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads"
    requestData = open(requestFile, "rU")
    dataInput = json.load(requestData)

    credentialsData = open(credentialsFile, "rU")
    dataCredentials = json.load(credentialsData)

    dataFile = open(responseFile, "rU")
    data = json.load(dataFile)
    print(data)
    print("\nName of file: %s" % dataFile.name)
    print("Request count: %d" % len(dataInput))
    print("Credential count: %d" % len(dataCredentials))
    print("Response count: %d" % len(data))

    sizeBIOS = checkFileSize("BIOS_PFWCY_WN64_2.2.5.EXE",
                             "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads/")
    sizeDAS = checkFileSize("DAS_Cache_Linux_1.zip",
                            "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads/")
    sizeESX = checkFileSize("VMW-ESX-6.0.0-lsi_mr3-6.903.85.00_MR-3818071.zip",
                             "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads/")
    sizeMD5 = checkFileSize("VMW-ESX-6.0.0-lsi_mr3-6.903.85.00_MR-3818071.zip.md5",
                             "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads/")

    print("Total messages consumed: %d" % len(data))

    while count < len(data):
        if "errorCode" in data[count].keys():
            print(data[count]["errorCode"])
            if ("errorMessage") in data[count].keys():
                print(data[count]["errorMessage"])
                assert (data[count]["errorCode"][:-2]) in (
                    data[count]["errorMessage"]), "Returned Error Code not included in Error Message."
                assert ('orrelation') or ('uid') in (
                    data[count]["errorMessage"]), "Returned Error Message does not reflect missing correlation ID."
                print("0.1")
        print("Count: %d" % count)
        print(data[count].keys())
        if "url" in data[count].keys():
            print("HERE NOW")
            assert "timestamp" in data[count]["messageProperties"], "Timestamp not included in consumed attributes."
            assert "correlationId" in data[count][
                "messageProperties"], "Correlation Id not included in consumed attributes."
            assert "replyTo" in data[count]["messageProperties"], "Reply To not included in consumed attributes."
            assert "hashType" in data[count].keys(), "Hash Type not included in consumed attributes."
            assert "hashVal" in data[count].keys(), "Hash not included in consumed attributes."
            assert "swid" in data[count].keys(), "Swid not included in consumed attributes."
            assert "size" in data[count].keys(), "Size not included in consumed attributes."
            assert "fileUUID" in data[count].keys(), "File UUID not included in consumed attributes."
            assert filepath in data[count]["url"], "Download complete does not include expected URL."
            print("Expected Keys are included.")
            print("1.%d" % count)

            credCount = 0
            # assert data["fileName"] == dataInput["fileName"], "File names are not consistent."

            for respCount in range(len(data)):
                print("resp count: %d" % respCount)
                print("Total resps: %d" % len(data))
                print(data[respCount])
                if "url" not in data[respCount]:
                    continue
                if filepath in data[respCount]["url"]:
                    assert data[respCount]["hashType"] == hashType, "Incorrect hashtype detailed in complete message."
                    print("Hash value len: %d" % len(data[respCount]["hashVal"]))
                    print(data[respCount])
                    print(data[respCount]["messageProperties"]["replyTo"])
                    assert len(data[respCount]["hashVal"]) > 30, "Hash value in complete message not of the expected length"
                    assert "completed" in data[respCount]["messageProperties"]["replyTo"], "Incorrect replyTo value included in complete message."
                    print("2.1")

                    for credCount in range(len(dataCredentials)):
                        if data[respCount]["hashVal"] == dataCredentials[credCount]["hashVal"]:
                            assert data[respCount]["hashVal"] == dataCredentials[credCount]["hashVal"], "Hash values for file not consistent."
                            print("Final Corr ID: %s" % data[respCount]["messageProperties"]["correlationId"])
                            print("Cred Resp Corr ID: %s" % dataCredentials[credCount]["messageProperties"]["correlationId"])
                            #assert data[respCount]["swid"] == family, "Unexpected swid returned in consumed messages."
                            assert data[respCount]["messageProperties"]["correlationId"] == dataCredentials[credCount]["messageProperties"]["correlationId"], "Corr Ids don't match in consumed messages."
                            assert data[respCount]["messageProperties"]["replyTo"] == dataCredentials[credCount]["messageProperties"]["replyTo"], "Reply To values don't match in consumed messages."
                            assert data[respCount]["size"] == dataCredentials[credCount]["size"], "Size values don't match in comsumed messages."
                            assert data[respCount]["fileUUID"] == dataCredentials[credCount]["fileUUID"], "fileUUIDs don't match in consumed messages."
                            print("2.2")

            for credCount in range(len(dataCredentials)):
                print("Cred count: %d" % credCount)
                print("Total creds: %d" % len(dataCredentials))
                print(dataCredentials[credCount]["fileFound"])
                if dataCredentials[credCount]["fileFound"] == True:
                    assert dataCredentials[credCount]["swid"] == family, "Unexpected swid returned in credential response."
                    assert dataCredentials[credCount]["swid"] in dataCredentials[credCount]["url"], "Swids don't match in consumed messages."
                    assert dataCredentials[credCount]["hashType"] == hashType, "Incorrect hashType detailed."
                    print("URL: %s" % dataCredentials[credCount]["url"])
                    assert esrsURL in dataCredentials[credCount]["url"], "Download complete does not include expected URL."
                    assert dataCredentials[credCount]["swid"] == dataCredentials[credCount]["header"]["serialNumber"], "Swids don't match in consumed messages."
                    assert dataCredentials[credCount]["header"]["productFamily"] in dataCredentials[credCount]["header"]["authorization"], "Unexpected header values returned."
                    print("3.1")

                    for inCount in range(len(dataInput)):
                        if "fileName" not in dataCredentials[credCount]:
                            continue
                        if dataCredentials[credCount]["fileName"] == dataInput[inCount]["fileName"]:
                            print("Checking response messages.....A")
                            assert dataCredentials[credCount]["fileName"] == dataInput[inCount]["fileName"], "File names are not consistent."
                            print("Orig Corr ID: %s" % dataInput[inCount]["messageProperties"]["correlationId"])
                            print("Cred Resp Corr ID: %s" % dataCredentials[credCount]["messageProperties"]["correlationId"])
                            assert dataCredentials[credCount]["messageProperties"]["correlationId"] == dataInput[inCount]["messageProperties"]["correlationId"], "Corr Ids don't match in consumed messages."
                            assert dataCredentials[credCount]["messageProperties"]["replyTo"] == dataInput[inCount]["messageProperties"]["replyTo"], "Reply To don't match in consumed messages."
                            print("3.2")
                        # inCount += 1
                    print(len(data))
                    for respC in range(len(data)):
                        print(dataCredentials[credCount]["fileName"])
                        print(data[respC])
                        print(respC)
                        if "url" not in data[respC]:
                            continue
                        if dataCredentials[credCount]["fileName"] in data[respC]["url"]:
                            # assert dataCredentials[credCount]["fileName"] == data[respC]["fileName"], "File names are not consistent."
                            assert dataCredentials[credCount]["url"] != data[respC]["url"], "URLs don't match in consumed messages."
                            assert dataCredentials[credCount]["size"] == data[respC]["size"] or sizeMD5, "File sizes don't match in consumed messages."
                            assert dataCredentials[credCount]["messageProperties"]["correlationId"] == data[respC]["messageProperties"]["correlationId"], "Corr Ids don't match in consumed messages."
                            assert dataCredentials[credCount]["messageProperties"]["replyTo"] == data[respC]["messageProperties"]["replyTo"], "Reply To don't match in consumed messages."
                            assert dataCredentials[credCount]["hashType"] == hashType, "Incorrect hashType detailed."
                            print("3.3")
                        # respC += 1
                    credCount += 1
            print("Response attributes match those defined in request.")
            print("Downloaded BIOS file size: %s" % sizeBIOS)
            print("Downloaded ZIP file size: %s" % sizeDAS)
            print("Downloaded ESX file size: %s" % sizeESX)
        count += 1

        return

    assert False, "Consumed response messages not complete."


def verifyConsumedAttributesInvalid(requestFile, credentialsFile, responseFile, hashType, family):
    numRCMs = 0
    path = "file:///opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads"
    requestData = open(requestFile, "rU")
    dataInput = json.load(requestData)

    credentialsData = open(credentialsFile, "rU")
    dataCredentials = json.load(credentialsData)

    dataFile = open(responseFile, "rU")
    data = json.load(dataFile)
    # print(data.keys())
    print("\nName of file: %s" % dataFile.name)

    # checkFileSize("BIOS_PFWCY_WN64_2.2.5.EXE", "/rootfs/opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads/")
    maxCount = len(data)

    for count in range(maxCount):
        if ("errorCode") not in data[count].keys():
            continue
        if ("errorCode") in data[count].keys():
            print(data[count]["errorCode"])
            print(data[count])
            print(data[count].keys())
            print(data[count]["errorMessage"])
            assert dataInput["fileName"] in data[count]["errorMessage"], "Expeceted file name included in error message text."
            assert dataInput["messageProperties"]["correlationId"] in data[count]["messageProperties"][
                "correlationId"], "Corr Ids don't match in consumed messages."

            assert "errorMessage" in data[count].keys(), "Error Message not included in consumed attributes."
            assert "timestamp" in data[count]["messageProperties"], "Timestamp not included in consumed attributes."
            assert "correlationId" in data[count]["messageProperties"], "Correlation Id not included in consumed attributes."
            assert "replyTo" in data[count]["messageProperties"], "Reply To not included in consumed attributes."
            assert "hashType" in data[count].keys(), "Hash Type not included in consumed attributes."
            assert "size" in data[count].keys(), "Size not included in consumed attributes."
            assert "fileUUID" in data[count].keys(), "File UUID not included in consumed attributes."

            assert data[count]["size"] == 0, "Size of ZERO not returned in error."
            assert data[count]["errorMessage"] == dataCredentials["errorMessage"], "Error messages are not consistent."
            assert data[count]["fileUUID"] == dataCredentials["fileUUID"], "FileUUIDs are not consistent."
            assert data[count]["size"] == dataCredentials["size"], "File sizes don't match in consumed messages."
            assert dataInput["messageProperties"]["replyTo"] == data[count]["messageProperties"][
                "replyTo"], "Corr Ids don't match in consumed messages."
            assert data[count]["hashType"] == dataCredentials["hashType"], "Incorrect hashType detailed."
            print("Download response verified on failed request.")


            if dataCredentials["fileFound"] == False:
                assert "errorMessage" in dataCredentials.keys(), "No error message in credentials response."
                assert "replyTo" in dataCredentials["messageProperties"], "No message detailed in credentials response."
                assert dataInput["fileName"] in dataCredentials["errorMessage"], "No file name included in error message text."
                # assert dataCredentials["fileName"] == dataInput["fileName"], "File names are not consistent."
                assert dataCredentials["size"] == 0, "Size of ZERO not returned in error."
                assert dataInput["messageProperties"]["correlationId"] in dataCredentials["messageProperties"][
                    "correlationId"], "Corr Ids don't match in consumed messages."
                assert dataInput["messageProperties"]["replyTo"] == dataCredentials["messageProperties"][
                    "replyTo"], "ReplyTo values don't match in consumed messages."
                assert dataCredentials["hashType"] == hashType, "Incorrect hashType detailed."
                print("Header key count: %d" % len(dataCredentials["header"].keys()))
                assert len(dataCredentials["header"].keys()) == 0, "Header should not included authorization keys or similar."
                assert not dataCredentials["header"].keys(), "Header be an empty list."
                assert "authorization" not in dataCredentials["header"], "Header should not included authorization keys."
                print("Invalid request triggered expected Credentials response.")
                print("Credentials response verified on failed request.")

                return

    assert False, "Response attributes do not match those defined in request."


def verifyProgressMessage(requestFile, credentialsFile, responseFile):
    numRCMs = 0
    count = 0

    filepath = "file:///opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads"
    requestData = open(requestFile, "rU")
    dataInput = json.load(requestData)

    credentialsData = open(credentialsFile, "rU")
    dataCredentials = json.load(credentialsData)

    dataFile = open(responseFile, "rU")
    data = json.load(dataFile)
    print(data)
    print("\nName of file: %s" % dataFile.name)
    print("Request count: %d" % len(dataInput))
    print("Credential count: %d" % len(dataCredentials))
    print("Response count: %d" % len(data))

    # sizeBIOS = checkFileSize("BIOS_PFWCY_WN64_2.2.5.EXE",
    #                          "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads/")
    # sizePNG = checkFileSize("shai.png",
    #                         "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads/")
    # sizeESX = checkFileSize("VMW-ESX-6.0.0-lsi_mr3-6.903.85.00_MR-3818071.zip",
    #                          "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads/")
    # sizeMD5 = checkFileSize("VMW-ESX-6.0.0-lsi_mr3-6.903.85.00_MR-3818071.zip.md5",
    #                          "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads/")
    sizeDAS = checkFileSize("DAS_Cache_Linux_1.zip",
                             "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads/")


    credCount = len(dataCredentials)
    maxCount = len(data)
    print("Total messages consumed: %d" % maxCount)
    while count < maxCount:
        if ("totalSize") in data[count].keys():
            print("Count: %d" % count)
            assert "timestamp" in data[count]["messageProperties"], "Timestamp not included in consumed attributes."
            assert "correlationId" in data[count]["messageProperties"], "Correlation Id not included in consumed attributes."
            assert "downloadedSize" in data[count].keys(), "Hash Type not included in consumed attributes."
            assert "downloadSpeed" in data[count].keys(), "Hash not included in consumed attributes."
            # assert "swid" in data[count].keys(), "Swid not included in consumed attributes."
            # assert "size" in data[count].keys(), "Size not included in consumed attributes."
            assert "fileUUID" in data[count].keys(), "File UUID not included in consumed attributes."
            assert data[count]["totalSize"] > 0, "Unexpected file size expected."

            for cred in range(credCount):
                assert data[count]["fileUUID"] == dataCredentials[cred]["fileUUID"], "FileUUIDs don't match in consumed messages."
                assert data[count]["totalSize"] == dataCredentials[cred]["size"], "File sizes don't match in consumed messages."
                assert data[count]["totalSize"] != data[count]["downloadedSize"], "Progress message download size matches expected file size, unexpected."
                assert data[count]["totalSize"] == dataCredentials[cred]["size"], "Size not consistent in consumed messages."
                assert data[count]["totalSize"] == sizeDAS, "Size not consistent with expected value."
                #assert data[count]["totalSize"] == sizeNIC or sizePNG or sizeESX or sizeMD5 or sizeDAS, "Size not consistent with expected value."
                assert data[count]["downloadedSize"] >= 0, "No bytes downloaded as per progress message."
                assert data[count]["downloadSpeed"] >= 0, "No download speed returned as per progress message."
                assert dataInput["messageProperties"]["correlationId"] in data[count]["messageProperties"][
                    "correlationId"], "Corr Ids don't match in consumed messages."
                if data[count]["downloadSpeed"] > 0:
                    assert data[count]["downloadedSize"] > 1, "Progress message downloaded size not as expected."
                    assert data[count]["downloadedSize"] < data[count]["totalSize"], "Progress message download size equal or greater than expected size."
                return
        else:
            continue
        count += 1

    assert False, ("Progress message is not complete.")


def deletePreviousDownloadFiles(filename, filepath):
    sendCommand = "find /opt/dell/cpsd -name downloads"
    dirStatus = af_support_tools.send_ssh_command(host=host, username=cli_username, password=cli_password,
                                                  command=sendCommand, return_output=True)

    print("Directory status A: %s" % dirStatus)
    if dirStatus is not "":
        dirStatus = dirStatus.rstrip() + "/"
        # dirStatus = (dirStatus + "/").rstrip()
    else:
        print("Downloads directory is missing.")
    print("Directory status B: %s" % dirStatus)

    if filepath in dirStatus:
        sendCommand = "rm -rf " + dirStatus + "*"
        print(sendCommand)
        fileDelete = af_support_tools.send_ssh_command(host=host, username=cli_username, password=cli_password,
                                                       command=sendCommand, return_output=True)
        sendCommand = 'find / -name "' + filename + '"'
        fileStatus = af_support_tools.send_ssh_command(host=host, username=cli_username, password=cli_password,
                                                       command=sendCommand, return_output=True)
        print("Current Status: %s" % fileStatus)
        assert filepath not in fileStatus, "File was not removed successfully."
    else:
        print(filename + "not found in the repo directory.")


def checkFileSize(filename, filepath):
    sendCommand = "find /opt/dell/cpsd -name " + filename
    fileStatus = af_support_tools.send_ssh_command(host=host, username=cli_username, password=cli_password,
                                                   command=sendCommand, return_output=True)
    if fileStatus is not "":
        fileStatus = fileStatus.rstrip()
        if filepath in fileStatus:
            sendCommand = "ls -ltr " + fileStatus + " | awk \'FNR == 1 {print$5}\'"
            global fileSize
            fileSize = af_support_tools.send_ssh_command(host=host, username=cli_username, password=cli_password,
                                                         command=sendCommand, return_output=True)
            print("Size: %s" % fileSize)
            fileSize = int(fileSize.rstrip())
            print("Size: %d" % fileSize)
            print("File status: %s" % fileStatus)
            return fileSize

    assert False, ("Attempt to check File Size is unsuccessful.")


def profileESRSResponseTimes(payLoad):
    messageReqHeader = {'__TypeId__': 'com.dell.cpsd.prepositioning.downloader.file.download.request'}
    resetTestQueues()
    print("Queues reset.")
    time.sleep(0.5)
    deletePreviousDownloadFiles("BIOS_PFWCY_WN64_2.2.5.EXE",
                                "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads/")

    print("Previous downloads deleted.")
    count = 0
    t1 = 0
    t2 = 0
    timeDelta = 0
    averageDelta = 0
    sortedDelta = []
    listDelta = []

    while count < 200:
        af_support_tools.rmq_publish_message(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                             exchange="exchange.dell.cpsd.prepositioning.downloader.request",
                                             routing_key="dell.cpsd.prepositioning.downloader.request",
                                             headers=messageReqHeader, payload=payLoad, payload_type='json',
                                             ssl_enabled=False)
        print("Download request published.")
        print(datetime.datetime.utcnow())
        t1 = datetime.datetime.utcnow()
        time.sleep(0.1)
        q_len = 0
        timeout = 0

        while q_len < 1:

            q_len = af_support_tools.rmq_message_count(host=host, port=port,
                                                       rmq_username=rmq_username, rmq_password=rmq_username,
                                                       queue='testCredentialsResponse', ssl_enabled=False)
            timeout += 1
            time.sleep(1)
            if timeout > 60:
                print("ERROR: ESRS Credential response took too long to return.")
                break

        print (datetime.datetime.utcnow())
        t2 = datetime.datetime.utcnow()

        timeDelta = (t2 - t1).total_seconds()
        print(timeDelta)
        assert timeDelta < 5, "Significant delay in response from ESRS."
        listDelta.append(timeDelta)
        averageDelta = sum(listDelta[0:(len(listDelta)-1)])/(len(listDelta))
        count += 1
        print("\nCount: %d" % count)
        if len(listDelta) > 5:
            print(listDelta)
            sortedDelta = sorted(listDelta)
            sortedDelta = sortedDelta[-5:]
            print("Five longest response times: ")
            print(sortedDelta)

            print("Average delta: %0.3f" % averageDelta)
        else:
            continue

        return
    assert False, "No messages published to profile."



@pytest.mark.rcm_fitness_mvp_extended
def test_downloadFWFileRequestInvalid():
    downloadFWFileRequestInvalid(messageInvalidFile, 'invalidFileFWRequest.json', 'invalidFileFWCredentials.json',
                                 'invalidFileFWResponse.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes1():
    verifyConsumedAttributesInvalid(path + 'invalidFileFWRequest.json', path + 'invalidFileFWCredentials.json',
                                    path + 'invalidFileFWResponse.json', "SHA-256", "VCEVision")


# #@pytest.mark.rcm_fitness_mvp_extended
# def test_downloadFWFileRequestInvalid2():
#     downloadFWFileRequestInvalid(messageInvalidReplyTo, 'invalidReplyToFWRequest.json', 'invalidReplyToFWCredentials.json',
#                                  'invalidReplyToFWResponse.json')

# #@pytest.mark.rcm_fitness_mvp_extended
# def test_downloadFWFileRequestInvalid3():
#     downloadFWFileRequestInvalid(messageInvalidSwid, 'invalidSwidFWRequest.json', 'invalidSwidFWCredentials.json',
#                                  'invalidSwidFWResponse.json')
#
# def test_verifyConsumedAttributes3():
#     verifyConsumedAttributesInvalid(path + 'invalidSwidFWRequest.json', path + 'invalidSwidFWCredentials.json',
#                                     path + 'invalidSwidFWResponse.json', "SHA-256", "VCEVision")

@pytest.mark.rcm_fitness_mvp_extended
def test_downloadFWFileRequestInvalid4():
    downloadFWFileRequestInvalid(messageInvalidAll, 'invalidAllFWRequest.json', 'invalidAllFWCredentials.json',
                                 'invalidAllFWResponse.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes4():
    verifyConsumedAttributesInvalid(path + 'invalidAllFWRequest.json', path + 'invalidAllFWCredentials.json',
                                    path + 'invalidAllFWResponse.json', "SHA-256", "VCEVision")

@pytest.mark.rcm_fitness_mvp_extended
def test_downloadFWFileRequestInvalid5():
    downloadFWFileRequestInvalid(messageNoFile, 'noFileFWRequest.json', 'noFileFWCredentials.json',
                                 'noFileFWResponse.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes5():
    verifyConsumedAttributesInvalid(path + 'noFileFWRequest.json', path + 'noFileFWCredentials.json',
                                    path + 'noFileFWResponse.json', "SHA-256", "VCEVision")

# #@pytest.mark.rcm_fitness_mvp_extended
# def test_downloadFWFileRequestInvalid6():
#     downloadFWFileRequestInvalid(messageNoReplyTo, 'noReplyToFWRequest.json', 'noReplyToFWCredentials.json',
#                                  'noReplyToFWResponse.json')

# #@pytest.mark.rcm_fitness_mvp_extended
# def test_downloadFWFileRequestInvalid7():
#     downloadFWFileRequestInvalid(messageNoSwid, 'noSwidFWRequest.json', 'noSwidFWCredentials.json',
#                                  'noSwidFWResponse.json')
#
@pytest.mark.rcm_fitness_mvp_extended
def test_downloadFWFileRequestInvalid8():
    downloadFWFileRequestInvalid(messageNoAll, 'noAllFWRequest.json', 'noAllFWCredentials.json',
                                 'noAllFWResponse.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes8():
    verifyConsumedAttributesInvalid(path + 'noAllFWRequest.json', path + 'noAllFWCredentials.json',
                                    path + 'noAllFWResponse.json', "SHA-256", "VCEVision")

#
# # def test_verifyConsumedAttributes7():
# #     verifyConsumedAttributesInvalid(path + 'noSwidFWRequest.json', path + 'noSwidFWCredentials.json',
# #                                     path + 'noSwidFWResponse.json', "SHA-256", "VCEVision")
# #
@pytest.mark.rcm_fitness_mvp_extended
def test_profileESRSResponseTimes():
    profileESRSResponseTimes(message)

@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.rcm_fitness_mvp
def test_downloadFWFileRequest():
    downloadFWFileRequest(message, 'downloadFWRequest.json', 'downloadFWCredentials.json',
                          'downloadFWResponse.json')


@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.rcm_fitness_mvp
def test_verifyPublishedAttributes():
    verifyPublishedAttributes(path + 'downloadFWRequest.json')

@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.rcm_fitness_mvp
def test_verifyConsumedAttributes():
    verifyConsumedAttributes("BIOS_PFWCY_WN64_2.2.5.EXE", path + 'downloadFWRequest.json', path + 'downloadFWCredentials.json',
                             path + 'downloadFWResponse.json', "SHA-256", "BETA2ENG218", "https://10.234.100.5:9443/")

@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.rcm_fitness_mvp
def test_checkFileSize():
    checkFileSize("BIOS_PFWCY_WN64_2.2.5.EXE",
                  "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads/")

@pytest.mark.rcm_fitness_mvp_extended
def test_downloadFWFileRequest2():
    downloadFWFileRequest(messageSec, 'repeatDownloadFWRequest.json', 'repeatDownloadFWCredentials.json',
                          'repeatDownloadFWResponse.json')


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes2():
    verifyConsumedAttributes("DAS_Cache_Linux_1.zip", path + 'repeatDownloadFWRequest.json', path + 'repeatDownloadFWCredentials.json',
                             path + 'repeatDownloadFWResponse.json', "SHA-256", "BETA2ENG218", "https://10.234.100.5:9443/")


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyProgressMessage():
    verifyProgressMessage(path + 'repeatDownloadFWRequest.json', path + 'repeatDownloadFWCredentials.json',
                          path + 'repeatDownloadFWResponse.json')


@pytest.mark.rcm_fitness_mvp_extended
def test_checkFileSize2():
    checkFileSize("DAS_Cache_Linux_1.zip",
                  "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads/")

@pytest.mark.rcm_fitness_mvp_extended
def test_downloadFWFileMulti():
    downloadFWFileMulti(message, messageSec, messageThird, 'multiDownloadFWRequest.json',
                        'multiDownloadFWCredentials.json', 'multiDownloadFWResponse.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyMultiPublishedAttributes():
    verifyMultiPublishedAttributes(path + 'multiDownloadFWRequest.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyMultiConsumedAttributes():
    verifyMultiConsumedAttributes(path + 'multiDownloadFWRequest.json', path + 'multiDownloadFWCredentials.json',
                                  path + 'multiDownloadFWResponse.json', "SHA-256", "BETA2ENG218", "https://10.234.100.5:9443/")

@pytest.mark.rcm_fitness_mvp_extended
def test_downloadFWFileMulti2():
    downloadFWFileMulti(message, messageSec, messageThird, 'secMultiDownloadFWRequest.json',
                        'secMultiDownloadFWCredentials.json', 'secMultiDownloadFWResponse.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyMultiPublishedAttributes2():
    verifyMultiPublishedAttributes(path + 'secMultiDownloadFWRequest.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyMultiConsumedAttributes2():
    verifyMultiConsumedAttributes(path + 'secMultiDownloadFWRequest.json', path + 'secMultiDownloadFWCredentials.json',
                                  path + 'secMultiDownloadFWResponse.json', "SHA-256", "VCEVision", "https://10.234.100.5:9443/")
