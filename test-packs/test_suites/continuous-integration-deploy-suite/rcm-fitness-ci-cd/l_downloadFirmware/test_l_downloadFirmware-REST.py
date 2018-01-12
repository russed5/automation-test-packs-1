#!/usr/bin/python
import pika
import json
import time
import af_support_tools
import pytest
import os
import re
import datetime
import sys
import logging
import requests


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

    ensurePathExists(path)
    purgeOldOutput(path, "rest")


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


def deletePreviousDownloadFiles(filename, filepath):
    sendCommand = "find /opt/dell/cpsd -name downloads"
    dirStatus = af_support_tools.send_ssh_command(host=host, username=cli_username, password=cli_password,
                                                  command=sendCommand, return_output=True)

    if dirStatus is not "":
        dirStatus = dirStatus.rstrip() + "/"
    else:
        print("Downloads directory is missing.")

    if filepath in dirStatus:
        sendCommand = "rm -rf " + dirStatus + "*"
        fileDelete = af_support_tools.send_ssh_command(host=host, username=cli_username, password=cli_password,
                                                       command=sendCommand, return_output=True)
        sendCommand = 'find / -name "' + filename + '"'
        fileStatus = af_support_tools.send_ssh_command(host=host, username=cli_username, password=cli_password,
                                                       command=sendCommand, return_output=True)
        assert filepath not in fileStatus, "File was not removed successfully."
    else:
        print(filename + "not found in the repo directory.")


def resetTestQueues():
    # credentials = pika.PlainCredentials(rmq_username, rmq_password)
    # parameters = pika.ConnectionParameters(host, port, '/', credentials)
    # connection = pika.BlockingConnection(parameters)
    # channel = connection.channel()

    af_support_tools.rmq_purge_queue(host=hostTLS, port=portTLS, queue='testDownloadFWRequest',
                                     ssl_enabled=True)
    af_support_tools.rmq_purge_queue(host=hostTLS, port=portTLS,
                                     queue='testDownloadFWResponse', ssl_enabled=True)
    af_support_tools.rmq_purge_queue(host=hostTLS, port=portTLS,
                                     queue='testCredentialsRequest', ssl_enabled=True)
    af_support_tools.rmq_purge_queue(host=hostTLS, port=portTLS,
                                     queue='testCredentialsResponse', ssl_enabled=True)

    time.sleep(0.5)
    print("Old test queues successfully purged.")

    af_support_tools.rmq_bind_queue(host=hostTLS, port=portTLS,
                                    queue='testDownloadFWRequest',
                                    exchange='exchange.dell.cpsd.prepositioning.downloader.request',
                                    routing_key='#', ssl_enabled=True)
    af_support_tools.rmq_bind_queue(host=hostTLS, port=portTLS,
                                    queue='testDownloadFWResponse',
                                    exchange='exchange.dell.cpsd.prepositioning.downloader.response',
                                    routing_key='#', ssl_enabled=True)
    af_support_tools.rmq_bind_queue(host=hostTLS, port=portTLS,
                                    queue='testCredentialsRequest', exchange='exchange.dell.cpsd.esrs.request',
                                    routing_key='#', ssl_enabled=True)
    af_support_tools.rmq_bind_queue(host=hostTLS, port=portTLS,
                                    queue='testCredentialsResponse', exchange='exchange.dell.cpsd.esrs.response',
                                    routing_key='#', ssl_enabled=True)
    print("New test queues successfully initialized.")


def verifyRESTdownloadInvalidFileRequest(rcmUUID, compUUID):
    resetTestQueues()
    deletePreviousDownloadFiles("100mbfiletest.zip",
                                "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader-service/repository/downloads/")

    timeout = 0
    # url = 'http://' + host + ':19080/rcm-fitness-api/api/download/firmware/'
    urlSec = 'https://' + host + ':19080/rcm-fitness-api/api/download/firmware/'
    payload = {'rcmUuid': rcmUUID, 'componentUuid': compUUID}
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    resp = requests.post(urlSec, data=json.dumps(payload), headers=headers, verify=False)
    # resp = requests.post(urlSec, data=json.dumps(payload), headers=headers, verify='/usr/local/share/ca-certificates/taf.cpsd.dell.ca.crt')

    statusResp = json.loads(resp.text)
    assert resp.status_code == 200 or 400, "Request has not been acknowledged as expected."

    if statusResp != "":
        while statusResp["state"] != "ERROR":
            timeout += 1
            time.sleep(0.5)
            statusURL = data["link"]["href"]
            statusData = requests.get(statusURL, verify=False)
            statusResp = json.loads(statusData.text)
            if timeout > 60:
                assert False, "Expected error state not returned in timely manner."

        if statusResp["state"] == "ERROR":
            print(statusResp)
            if rcmUUID == "" and compUUID == "":
                assert "RFCA1045E The [rcmUuid] can not be null or empty" in statusResp[
                    "message"], "Unexpected error message for empty values returned."
                return
            if rcmUUID == "" and compUUID != "":
                assert "RFCA1045E The [rcmUuid] can not be null or empty" in statusResp[
                    "message"], "Unexpected error message for empty values returned."
                return
            if rcmUUID != "" and compUUID == "":
                assert "RFCA1045E The [rcmComponentUuid] can not be null or empty" in statusResp[
                    "message"], "Unexpected error message for empty values returned."
                # assert "does not have any associated files" in statusResp["jobMessage"], "Unexpected error string returned."
                return
            else:
                assert compUUID in statusResp["message"], "Unexpected error message for empty values returned."
                assert rcmUUID in statusResp["message"], "Unexpected error message for empty values returned."
                assert "RFCA1046E The Component" in statusResp[
                    "message"], "Unexpected error message for empty values returned."
                assert "does not have any associated files" in statusResp[
                    "message"], "Unexpected error message for empty values returned."
                # assert "does not have any associated files" in statusResp["jobMessage"], "Unexpected error string returned."
                return

                # return
    assert False, ("Initial REST update request not complete.")


def verifyRESTdownloadSingleFileRequestSTATUS(filename, train, version):
    contentIndex = 0
    fileIndex = 0
    resetTestQueues()
    deletePreviousDownloadFiles("100mbfiletest.zip",
                                "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader-service/repository/downloads/")

    urlInventorySec = 'https://' + host + ':19080/rcm-fitness-api/api/rcm/inventory/vxrack/1000 FLEX/' + train + '/' + version + '/'
    respInventory = requests.get(urlInventorySec, verify=False)
    # urlInventorySec = 'https://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/rcm/inventory/vxrack/1000 FLEX/' + train + '/' + version + '/'
    # respInventory = requests.get(urlInventorySec, verify='/usr/local/share/ca-certificates/taf.cpsd.dell.ca.crt')

    dataInventory = json.loads(respInventory.text)
    rcmUUID = dataInventory["rcmInventoryItems"][0]["uuid"]

    compInventorySec = 'https://' + host + ':19080/rcm-fitness-api/api/rcm/definition/' + rcmUUID + '/'
    respComp = requests.get(compInventorySec, verify=False)
    # compInventorySec = 'https://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/rcm/definition/' + rcmUUID + '/'
    # respComp = requests.get(compInventorySec, verify='/usr/local/share/ca-certificates/taf.cpsd.dell.ca.crt')
    dataComp = json.loads(respComp.text)

    if dataComp != "":
        while contentIndex < len(dataComp["rcmDefinition"]["rcmContents"]):
            if len(dataComp["rcmDefinition"]["rcmContents"][contentIndex]["remediationFiles"]) == 0:
                contentIndex += 1
                continue
            if len(dataComp["rcmDefinition"]["rcmContents"][contentIndex]["remediationFiles"]) > 0:
                if filename in dataComp["rcmDefinition"]["rcmContents"][contentIndex]["remediationFiles"][fileIndex][
                    "cdnPath"]:
                    compUUID = dataComp["rcmDefinition"]["rcmContents"][contentIndex]["uuid"]
            contentIndex += 1

    # url = 'http://' + host + ':19080/rcm-fitness-api/api/download/firmware/'
    urlSec = 'https://' + host + ':19080/rcm-fitness-api/api/download/firmware/'
    payload = {'rcmUuid': rcmUUID, 'componentUuid': compUUID}
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    # resp = requests.post(url, data=json.dumps(payload), headers=headers)
    # resp = requests.post(urlSec, data=json.dumps(payload), headers=headers, verify='/usr/local/share/ca-certificates/taf.cpsd.dell.ca.crt')
    resp = requests.post(urlSec, data=json.dumps(payload), headers=headers, verify=False)
    data = json.loads(resp.text)
    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    if "REQUESTED" in data["state"]:
        assert "19080/rcm-fitness-api/api/download/firmware/status/" in data["link"][
            "href"], "No URL included in response to query subsequent progress."
        statusURL = data["link"]["href"]
        assert data["link"]["rel"] == "status", "Unexpected REL value returned."
        assert data["link"]["method"] == "GET", "Unexpected method value returned."
        time.sleep(1)
        statusData = requests.get(statusURL, verify=False)
        statusResp = json.loads(statusData.text)
        assert statusResp["state"] == "COMPLETE" or "RUNNING", "Unexpected initial state returned."
        assert len(statusResp["uuid"]) > 16, "No valid request UUID returned."
        assert statusResp["uuid"] in statusResp["link"]["href"], "Request UUID not found in returned HREF link."
        assert statusResp["link"]["method"] == "GET", "Unexpected method returned in response."
        assert "19080/rcm-fitness-api/api/download/firmware/status/" in statusResp["link"][
            "href"], "No URL included in response to query subsequent progress."
        assert statusResp["link"]["rel"] == "status", "Unexpected REL value returned."
        assert "REQUESTED" in data["tasks"][0]["state"], "Unexpected state in Tasks detail"
        assert "RFCA1064I Download operation" in data["tasks"][0]["message"], "Unexpected message in Tasks detail"
        assert len(data["tasks"][0]["errors"]) == 0, "Expected an empty list of errors."
        assert data["tasks"][0]["file"] is None, "File details should be NULL."

        # i = 0

        while statusResp["state"] != "COMPLETE":
            i = 0
            assert statusResp["state"] == "IN_PROGRESS" or "RUNNING", "Unexpected initial state returned."
            assert len(statusResp["uuid"]) > 16, "No valid request UUID returned."
            assert statusResp["uuid"] in statusResp["link"]["href"], "Request UUID not found in returned HREF link."
            assert statusResp["link"]["method"] == "GET", "Unexpected method returned in response."
            assert "19080/rcm-fitness-api/api/download/firmware/status/" in statusResp["link"][
                "href"], "No URL included in response to query subsequent progress."
            assert statusResp["link"]["rel"] == "status"
            # print(fileCount)
            print(len(statusResp["tasks"][i]["file"]))
            while i < len(statusResp["tasks"]):
                assert statusResp["tasks"][i]["file"]["downloadedSize"] >= 0, "Unexpected download size returned."
                assert statusResp["tasks"][i]["file"]["size"] != 0, "Unexpected file size returned."
                if statusResp["tasks"][i]["file"]["size"] == statusResp["tasks"][i]["file"]["downloadedSize"]:
                    assert statusResp["tasks"][i]["file"]["url"] is not None, "Unexpected url returned."
                else:
                    assert statusResp["tasks"][i]["file"]["url"] is None, "Unexpected url returned."
                    assert statusResp["tasks"][i]["file"]["hashVal"] is None, "Unexpected hashval returned."
                    assert statusResp["tasks"][i]["file"]["error"] is "", "Unexpected error returned."
                print("Progressing ...")
                i += 1
            # assert statusResp["error"] is "", "Unexpected error returned."

            time.sleep(0.5)
            statusURL = statusResp["link"]["href"]
            statusData = requests.get(statusURL, verify=False)
            statusResp = json.loads(statusData.text)

            if statusResp["state"] == "RUNNING":
                time.sleep(0.5)
                statusURL = statusResp["link"]["href"]
                statusData = requests.get(statusURL, verify=False)
                statusResp = json.loads(statusData.text)
                continue

        if statusResp["state"] == "COMPLETE":
            i = 0
            assert statusResp["state"] == "COMPLETE", "Unexpected initial state returned."
            assert len(statusResp["uuid"]) > 16, "No valid request UUID returned."
            assert statusResp["uuid"] in statusResp["link"]["href"], "Request UUID not found in returned HREF link."
            assert statusResp["link"]["method"] == "GET", "Unexpected method returned in response."
            assert "19080/rcm-fitness-api/api/download/firmware/status/" in statusResp["link"][
                "href"], "No URL included in response to query subsequent progress."
            assert statusResp["link"]["rel"] == "status"

            while i < len(statusResp["tasks"]):
                assert statusResp["tasks"][i]["state"] == "COMPLETE", "Unexpected state in task list."
                assert "RFCA1064I Download operation" in statusResp["tasks"][i][
                    "message"], "Unexpected message in Tasks detail"
                assert filename in statusResp["tasks"][i]["file"][
                    "url"], "Expected filename not included in returned URL."
                assert len(statusResp["tasks"][i]["file"]["hashVal"]) > 32, "HashVal not the expected length."
                assert statusResp["tasks"][i]["file"]["downloadedSize"] != 0, "Unexpected download size returned."
                assert statusResp["tasks"][i]["file"]["size"] != 0, "Unexpected file size returned."
                assert statusResp["tasks"][i]["file"]["downloadedSize"] == statusResp["tasks"][i]["file"][
                    "size"], "Download size is reported as larger than expected size."
                assert statusResp["tasks"][i]["file"]["error"] is "", "Unexpected error returned."
                i += 1

            # assert statusResp["error"] is "", "Unexpected error returned."
            return

        if statusResp["state"] != "COMPLETE":
            if statusResp["state"] != "IN_PROGRESS":
                assert False, "Invalid status reported."
                return
        assert False, "Initial REST update request not complete."


def verifyRESTdownloadMultiFileRequest(filename, train, version, fileCount):
    contentIndex = 0
    fileIndex = 0
    resetTestQueues()
    print("Queues reset.")
    deletePreviousDownloadFiles("100mbfiletest.zip",
                                "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader-service/repository/downloads/")

    # urlInventory = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/rcm/inventory/vxrack/1000 FLEX/' + train + '/' + version + '/'
    urlInventorySec = 'https://' + host + ':19080/rcm-fitness-api/api/rcm/inventory/vxrack/1000 FLEX/' + train + '/' + version + '/'

    # respInventory = requests.get(urlInventory)
    respInventory = requests.get(urlInventorySec, verify=False)
    dataInventory = json.loads(respInventory.text)
    rcmUUID = dataInventory["rcmInventoryItems"][0]["uuid"]

    global tempRCMuuid
    tempRCMuuid = rcmUUID

    # compInventory = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/rcm/definition/' + rcmUUID + '/'
    compInventorySec = 'https://' + host + ':19080/rcm-fitness-api/api/rcm/definition/' + rcmUUID + '/'
    # respComp = requests.get(compInventorySec)
    respComp = requests.get(compInventorySec, verify=False)
    dataComp = json.loads(respComp.text)

    if dataComp != "":
        while contentIndex < len(dataComp["rcmDefinition"]["rcmContents"]):
            if len(dataComp["rcmDefinition"]["rcmContents"][contentIndex]["remediationFiles"]) == 0:
                contentIndex += 1
                continue
            if len(dataComp["rcmDefinition"]["rcmContents"][contentIndex]["remediationFiles"]) > 0:
                if filename in dataComp["rcmDefinition"]["rcmContents"][contentIndex]["remediationFiles"][fileIndex][
                    "cdnPath"]:
                    compUUID = dataComp["rcmDefinition"]["rcmContents"][contentIndex]["uuid"]
                    global tempCompUUID
                    tempCompUUID = compUUID
            contentIndex += 1

    # url = 'http://' + host + ':19080/rcm-fitness-api/api/download/firmware/'
    urlSec = 'https://' + host + ':19080/rcm-fitness-api/api/download/firmware/'
    payload = {'rcmUuid': rcmUUID, 'componentUuid': compUUID}
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    # resp = requests.post(url, data=json.dumps(payload), headers=headers)
    # resp = requests.post(urlSec, data=json.dumps(payload), headers=headers, verify='/usr/local/share/ca-certificates/taf.cpsd.dell.ca.crt')
    resp = requests.post(urlSec, data=json.dumps(payload), headers=headers, verify=False)

    data = json.loads(resp.text)
    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    if data != "":
        print("Initial download state:")
        print(data["state"])
        if "REQUESTED" in data["state"]:
            print("Found REQUESTED state.")
            assert "19080/rcm-fitness-api/api/download/firmware/status/" in data["link"][
                "href"], "No URL included in response to query subsequent progress."
            statusURL = data["link"]["href"]
            assert data["link"]["rel"] == "status", "Unexpected REL value returned."
            assert data["link"]["method"] == "GET", "Unexpected method value returned."
            assert "REQUESTED" in data["tasks"][0]["state"], "Unexpected state in Tasks detail"
            assert "RFCA1064I Download operation" in data["tasks"][0]["message"], "Unexpected message in Tasks detail"
            assert len(data["tasks"][0]["errors"]) == 0, "Expected an empty list of errors."
            assert data["tasks"][0]["file"] is None, "File details should be NULL."
            time.sleep(1)
            statusData = requests.get(statusURL, verify=False)
            statusResp = json.loads(statusData.text)
            assert statusResp["state"] == "COMPLETE" or "RUNNING", "Unexpected initial state returned."
            assert len(statusResp["uuid"]) > 16, "No valid request UUID returned."
            assert statusResp["uuid"] in statusResp["link"]["href"], "Request UUID not found in returned HREF link."
            assert statusResp["link"]["method"] == "GET", "Unexpected method returned in response."
            assert "19080/rcm-fitness-api/api/download/firmware/status/" in statusResp["link"][
                "href"], "No URL included in response to query subsequent progress."
            assert statusResp["link"]["rel"] == "status", "Unexpected REL value returned."

        i = 0

        while statusResp["state"] != "COMPLETE":
            assert statusResp["state"] == "IN_PROGRESS" or "RUNNING", "Unexpected initial state returned."
            assert len(statusResp["uuid"]) > 16, "No valid request UUID returned."
            assert statusResp["uuid"] in statusResp["link"]["href"], "Request UUID not found in returned HREF link."
            assert statusResp["link"]["method"] == "GET", "Unexpected method returned in response."
            assert "19080/rcm-fitness-api/api/download/firmware/status/" in statusResp["link"][
                "href"], "No URL included in response to query subsequent progress."
            assert statusResp["link"]["rel"] == "status"
            print(fileCount)
            print(len(statusResp["tasks"]))
            while i < len(statusResp["tasks"]):
                assert statusResp["tasks"][i]["file"]["downloadedSize"] >= 0, "Unexpected download size returned."
                assert statusResp["tasks"][i]["file"]["size"] != 0, "Unexpected file size returned."
                if statusResp["tasks"][i]["file"]["size"] == statusResp["tasks"][i]["file"]["downloadedSize"]:
                    assert statusResp["tasks"][i]["file"]["url"] is not None, "Unexpected url returned."
                else:
                    assert statusResp["tasks"][i]["file"]["url"] is None, "Unexpected url returned."
                    assert statusResp["tasks"][i]["file"]["hashVal"] is None, "Unexpected hashval returned."
                    assert statusResp["tasks"][i]["file"]["error"] is "", "Unexpected error returned."
                print("Progressing ...")
                i += 1
            # assert statusResp["error"] is "", "Unexpected error returned."

            time.sleep(0.5)
            statusURL = statusResp["link"]["href"]
            statusData = requests.get(statusURL, verify=False)
            statusResp = json.loads(statusData.text)

            if statusResp["state"] == "RUNNING":
                time.sleep(0.5)
                statusURL = statusResp["link"]["href"]
                statusData = requests.get(statusURL, verify=False)
                statusResp = json.loads(statusData.text)
                continue

        i = 0
        if statusResp["state"] == "COMPLETE":
            assert statusResp["state"] == "COMPLETE", "Unexpected initial state returned."
            assert len(statusResp["uuid"]) > 16, "No valid request UUID returned."
            assert statusResp["uuid"] in statusResp["link"]["href"], "Request UUID not found in returned HREF link."
            assert statusResp["link"]["method"] == "GET", "Unexpected method returned in response."
            assert "19080/rcm-fitness-api/api/download/firmware/status/" in statusResp["link"][
                "href"], "No URL included in response to query subsequent progress."
            assert statusResp["link"]["rel"] == "status"

            while i < len(statusResp["tasks"]):
                assert statusResp["tasks"][i]["state"] == "COMPLETE", "Unexpected state in task list."
                assert "RFCA1064I Download operation" in statusResp["tasks"][i][
                    "message"], "Unexpected message in Tasks detail"
                assert filename in statusResp["tasks"][i]["file"][
                    "url"], "Expected filename not included in returned URL."
                assert len(statusResp["tasks"][i]["file"]["hashVal"]) > 32, "HashVal not the expected length."
                assert statusResp["tasks"][i]["file"]["downloadedSize"] != 0, "Unexpected download size returned."
                assert statusResp["tasks"][i]["file"]["size"] != 0, "Unexpected file size returned."
                assert statusResp["tasks"][i]["file"]["downloadedSize"] == statusResp["tasks"][i]["file"][
                    "size"], "Download size is reported as larger than expected size."
                assert statusResp["tasks"][i]["file"]["error"] is "", "Unexpected error returned."
                i += 1

            return

        if statusResp["state"] != "COMPLETE":
            if statusResp["state"] != "IN_PROGRESS":
                assert False, "Invalid status reported."
                return
        assert False, "Initial REST update request not complete."


def verifyRESTrepositoryStatus(filepath, filename):
    url = 'https://' + host + ':8888/downloads/' + filepath
    repoStatus = requests.get(url, verify=False)
    # urlSec = 'https://' + host + ':8888/downloads/' + filepath
    # repoStatus = requests.get(urlSec, verify='/usr/local/share/ca-certificates/taf.cpsd.dell.ca.crt')

    assert repoStatus.status_code == 200, "Request has not been acknowledged as expected."

    content = repoStatus.content.decode('utf-8')
    if repoStatus.content != "":
        assert filepath in content, "Response does not include file path."
        assert filename in content, "Response does not include file name."
        return
    assert False, "Failing....."


@pytest.mark.daily_status
@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.rcm_fitness_mvp
def test_verifyRESTdownloadSingleFileRequest1():
    verifyRESTdownloadMultiFileRequest(
        "RCM/3.2.1/VxRack_1000_FLEX/Component/Controller_Firmware/SAS-RAID_Firmware_VH28K_WN64_25.4.0.0017_A06.EXE",
        "3.2", "3.2.1", 1)


@pytest.mark.daily_status
@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.rcm_fitness_mvp
def test_verifyRESTdownloadSingleFileRequestSTATUS1():
    verifyRESTdownloadSingleFileRequestSTATUS(
        "RCM/3.2.1/VxRack_1000_FLEX/Component/Controller_Firmware/SAS-RAID_Firmware_VH28K_WN64_25.4.0.0017_A06.EXE",
        "3.2", "3.2.1")


@pytest.mark.daily_status
@pytest.mark.rcm_fitness_mvp_extended
def test_verifyRESTrepositoryStatus1():
    verifyRESTrepositoryStatus("RCM/3.2.1/VxRack_1000_FLEX/Component/Controller_Firmware/",
                               "SAS-RAID_Firmware_VH28K_WN64_25.4.0.0017_A06.EXE")


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyRESTdownloadSingleFileRequest2():
    verifyRESTdownloadMultiFileRequest(
        "RCM/3.2.3/VxRack_1000_FLEX/Component/Controller_Firmware/SAS-RAID_Firmware_2H45F_WN64_25.5.0.0018_A08.EXE",
        "3.2", "3.2.3", 1)


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyRESTdownloadSingleFileRequestSTATUS2():
    verifyRESTdownloadSingleFileRequestSTATUS(
        "RCM/3.2.3/VxRack_1000_FLEX/Component/Controller_Firmware/SAS-RAID_Firmware_2H45F_WN64_25.5.0.0018_A08.EXE",
        "3.2", "3.2.3")


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyRESTrepositoryStatus2():
    verifyRESTrepositoryStatus("RCM/3.2.3/VxRack_1000_FLEX/Component/Controller_Firmware/",
                               "SAS-RAID_Firmware_2H45F_WN64_25.5.0.0018_A08.EXE")


@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.rcm_fitness_mvp
def test_verifyRESTdownloadInvalidFileRequest3():
    verifyRESTdownloadInvalidFileRequest(tempRCMuuid[:8], tempCompUUID)


@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.rcm_fitness_mvp
def test_verifyRESTdownloadInvalidFileRequest4():
    verifyRESTdownloadInvalidFileRequest(tempRCMuuid[:8], tempCompUUID[:8])


@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.rcm_fitness_mvp
def test_verifyRESTdownloadInvalidFileRequest5():
    verifyRESTdownloadInvalidFileRequest(tempRCMuuid, tempCompUUID[:8])


@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.rcm_fitness_mvp
def test_verifyRESTdownloadInvalidFileRequest6():
    verifyRESTdownloadInvalidFileRequest(tempRCMuuid, "")


@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.rcm_fitness_mvp
def test_verifyRESTdownloadInvalidFileRequest7():
    verifyRESTdownloadInvalidFileRequest("", tempCompUUID)


@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.rcm_fitness_mvp
def test_verifyRESTdownloadInvalidFileRequest8():
    verifyRESTdownloadInvalidFileRequest("----", tempCompUUID)


@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.rcm_fitness_mvp
def test_verifyRESTdownloadInvalidFileRequest9():
    verifyRESTdownloadInvalidFileRequest(tempRCMuuid, "----")


@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.rcm_fitness_mvp
def test_verifyRESTdownloadInvalidFileRequest10():
    verifyRESTdownloadInvalidFileRequest("", "")


@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.rcm_fitness_mvp
def test_verifyRESTdownloadMultiFileRequest11():
    verifyRESTdownloadMultiFileRequest("RCM/3.2.2/VxRack_1000_FLEX/Component/ESXi/", "3.2", "3.2.2", 3)

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyRESTdownloadSingleFileRequestFor3kSwitch():
    verifyRESTdownloadMultiFileRequest("RCM/3.2.2/VxRack_1000_FLEX/Component/Cisco/Nexus3k/3172TQ/","3.2", "3.2.2", 2)

#
