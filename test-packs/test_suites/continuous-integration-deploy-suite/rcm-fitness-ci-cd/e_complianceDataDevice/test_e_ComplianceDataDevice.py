#!/usr/bin/env python
# Copyright © 2017 Dell Inc. or its subsidiaries.  All Rights Reserved
import json
import requests
import pytest
import os
import re
import af_support_tools
import datetime
import time


@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    global path
    path = '/home/autouser/PycharmProjects/auto-framework/test_suites/continuous-integration-deploy-suite/rcm-fitness-ci-cd/e_complianceDataDevice'
    global ssl_options
    ssl_options = {"ca_certs": "/etc/rabbitmq/certs/testca/cacert.pem",
                   "certfile": "/etc/rabbitmq/certs/certs/client/cert.pem",
                   "keyfile": "/etc/rabbitmq/certs/certs/client/key.pem", "cert_reqs": "ssl.CERT_REQUIRED",
                   "ssl_version": "ssl.PROTOCOL_TLSv1_2"}

    # Set config ini file name
    global env_file
    env_file = 'env.ini'

    global host
    host = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')

    ensurePathExists(path)
    purgeOldOutput(path, "complianceDataDevice")

    # initUrl = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/about'
    # resp = requests.get(initUrl)
    time.sleep(15)
    getSystemDefinition()


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


def getSystemDefinition():
    # url = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/system/definition/'
    # urlSec = 'https://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/system/definition/'
    urlSec = 'https://' + host + ':19080/rcm-fitness-api/api/system/definition/'
    # resp = requests.get(url)
    # resp = requests.get(urlSec, verify='/usr/local/share/ca-certificates/taf.cpsd.dell.ca.crt')
    resp = requests.get(urlSec, verify=False)

    data = json.loads(resp.text)
    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    if data != "":
        if data["systems"][0]["uuid"] != "":
            with open(path + 'rcmSystemDefinition-VxRack.json', 'w') as outfile:
                json.dump(data, outfile, sort_keys=True, indent=4, ensure_ascii=False)

            global systemUUID
            global secondSystemUUID
            systemUUID = data["systems"][0]["uuid"]
            if len(data["systems"]) > 1:
                secondSystemUUID = data["systems"][1]["uuid"]
    return systemUUID

def getComplianceData(product, family, model, identifier, deviceProduct, deviceType, filename, sysUUID, minSubCount, maxSubCount):
    compIndex = 0
    groupIndex = 0
    i = 0

    urlSec = 'https://' + host + ':19080/rcm-fitness-api/api/system/definition/' + sysUUID + '/component/'
    resp = requests.get(urlSec, verify=False)

    data = json.loads(resp.text)
    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    urlSec = 'https://' + host + ':19080/rcm-fitness-api/api/system/definition/' + sysUUID

    resp = requests.get(urlSec, verify=False)

    sysData = json.loads(resp.text)

    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    totalComponents = len(data["components"])
    if data != "":
        print("1")
        while compIndex < totalComponents:
            print("2")
            print(data["components"][compIndex]["identity"]["identifier"])
            print(data["components"][compIndex]["definition"]["model"])
            if identifier in data["components"][compIndex]["identity"]["identifier"] and \
                            data["components"][compIndex]["definition"]["model"] == model:
                print("3")
                # if data["components"][compIndex]["identity"]["identifier"] == "VCENTER-APPLIANCE-CUSTOMER":
                #     global compUUID
                #     compUUID = data["components"][compIndex]["uuid"]
                #     print(compUUID)
                # else:
                global compUUID
                compUUID = data["components"][compIndex]["uuid"]
                print(compUUID)

                newComp = compUUID[:8]
                compURLSec = 'https://' + host + ':19080/rcm-fitness-api/api/compliance/data/device/' + compUUID

                compResp = requests.get(compURLSec, verify=False)
                compData = json.loads(compResp.text)
                print(compData)
                assert compResp.status_code == 200, "Request has not been acknowledged as expected."

                totalSubComponents = len(compData["subComponents"])
                print(totalSubComponents)
                assert totalSubComponents == minSubCount or maxSubCount, "Unexpected number of subcomponents returned."

                with open(filename, 'a') as outfile:
                    json.dump(compData, outfile, sort_keys=True, indent=4, ensure_ascii=False)

                if compData["device"]["uuid"] != "":
                    if compData["device"]["uuid"] != data["components"][i]["uuid"]:
                        i += 1
                        continue
                    if compData["device"]["uuid"] == data["components"][i]["uuid"]:
                        assert compData["device"]["uuid"] == data["components"][i][
                            "uuid"], "response does not detail Component UUID."

                        assert "parentGroupUuids" in compData["device"], "Response not detail Parent Group UUID."
                        assert compData["device"]["parentGroupUuids"] == data["components"][i][
                            "parentGroupUuids"], "Response not detail Parent Group UUID."

                        assert "elementData" in compData["device"], "Response not detail Element Data."
                        assert "auditData" in compData["device"], "Response not detail Audit Data."
                        assert "versionDatas" in compData["device"], "Response not detail Version Datas."
                        assert "modelFamily" in compData["device"]["elementData"], "Response not detail Family."
                        assert compData["device"]["elementData"]["modelFamily"] == \
                               data["components"][i]["definition"]["modelFamily"], "Response not detail Family."

                        assert "model" in compData["device"]["elementData"], "Response not detail Model."
                        assert compData["device"]["elementData"]["model"] == model, "Response not detail Model."
                        assert compData["device"]["elementData"]["model"] == data["components"][i]["definition"][
                            "model"], "Response not detail Model."

                        assert "productFamily" in compData["device"]["elementData"], "Response not detail Model."
                        assert compData["device"]["elementData"][
                                   "productFamily"] == deviceProduct, "Response not detail Model."
                        assert compData["device"]["elementData"]["productFamily"] == \
                               data["components"][i]["definition"]["productFamily"], "Response not detail Model."

                        assert "elementType" in compData["device"][
                            "elementData"], "Response not detail Element Type."
                        assert compData["device"]["elementData"][
                                   "elementType"] == deviceType, "Response not detail Type."
                        assert compData["device"]["elementData"]["elementType"] == \
                               data["components"][i]["identity"]["elementType"], "Response not detail Type."

                        assert "identifier" in compData["device"]["elementData"], "response not detail Identifier."
                        assert compData["device"]["elementData"]["identifier"] == data["components"][i]["identity"][
                            "identifier"], "Response not detail Identifier."

                        assert "collectedTime" in compData["device"][
                            "auditData"], "Response not detail Collected Time."
                        assert "collectionSentTime" in compData["device"][
                            "auditData"], "Response not detail Collection Sent Time."
                        assert "messageReceivedTime" in compData["device"][
                            "auditData"], "Response not detail Received Time."

                        while groupIndex < len(sysData["system"]["groups"]):
                            if compData["groups"][0]["uuid"] != sysData["system"]["groups"][groupIndex]["uuid"]:
                                groupIndex += 1
                                continue
                            if compData["groups"][0]["uuid"] == sysData["system"]["groups"][groupIndex]["uuid"]:
                                assert "uuid" in compData["groups"][0], "Response not detail component Groups."
                                assert compData["groups"][0]["uuid"] == sysData["system"]["groups"][groupIndex][
                                    "uuid"], "Response not detail component Groups."

                                assert "parentGroupUuids" in compData["groups"][0], "Response not detail Parent Groups."
                                assert compData["groups"][0]["parentGroupUuids"] == sysData["system"]["groups"][groupIndex][
                                    "parentGroupUuids"], "Response not detail Parent Group."

                                assert "parentSystemUuids" in compData["groups"][0], "Response not detail Parent System."
                                assert compData["groups"][0]["parentSystemUuids"][0] == \
                                       sysData["system"]["groups"][groupIndex]["parentSystemUuids"][
                                           0], "Response not detail Parent System."

                                assert "type" in compData["groups"][0], "Response not detail component Groups."
                                assert compData["groups"][0]["type"] == sysData["system"]["groups"][groupIndex][
                                    "type"], "Response not detail Type."
                                groupIndex += 1

                        assert "systemUuid" in compData["systems"][0], "Response not detail System UUID."
                        assert compData["systems"][0]["systemUuid"] == sysData["system"][
                            "uuid"], "Response not detail Type."

                        assert "product" in compData["systems"][0], "Response not detail System UUID."
                        assert compData["systems"][0]["product"] == product, "1 Response not detail Product."
                        assert compData["systems"][0]["product"] == sysData["system"]["definition"][
                            "product"], "2 Response not detail Product."

                        assert "modelFamily" in compData["systems"][0], "Response not detail System UUID."
                        assert compData["systems"][0]["modelFamily"] == family, "Response not detail Family."
                        assert compData["systems"][0]["modelFamily"] == sysData["system"]["definition"][
                            "modelFamily"], "Response not detail Family."

                        assert "model" in compData["systems"][0], "Response not detail System UUID."
                        assert compData["systems"][0]["model"] == sysData["system"]["definition"][
                            "model"], "Response not detail Model."

                        assert "identifier" in compData["systems"][0], "Response not detail System UUID."
                        assert compData["systems"][0]["identifier"] == sysData["system"]["identity"][
                            "identifier"], "Response not detail Identifier."

                        assert "serialNumber" in compData["systems"][0], "Response not detail System UUID."
                        assert compData["systems"][0]["serialNumber"] == sysData["system"]["identity"][
                            "serialNumber"], "Response not detail Serial Number."

                        assert compData["device"]["elementData"]["elementType"] == deviceType
                        i += 1
                return
            compIndex += 1
        compIndex = 0

    assert False, "No component details returned for System Def request."

def getComplianceDataDeviceSubComps(elementType, identifier, model, sysDefFilename, compDataFilename, sysUUID):
    subIndex = 0
    index = 0
    getSystemDefinition()

    # url = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/system/definition/' + sysUUID
    # urlSec = 'https://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/system/definition/' + sysUUID
    urlSec = 'https://' + host + ':19080/rcm-fitness-api/api/system/definition/' + sysUUID
    # resp = requests.get(url)
    # resp = requests.get(urlSec, verify='/usr/local/share/ca-certificates/taf.cpsd.dell.ca.crt')
    resp = requests.get(urlSec, verify=False)

    data = json.loads(resp.text)
    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    with open(sysDefFilename, 'w') as outfile:
        json.dump(data, outfile, sort_keys=True, indent=4, ensure_ascii=False)

    # url = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/system/definition/' + sysUUID + '/component'
    # urlSec = 'https://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/system/definition/' + sysUUID + '/component'
    urlSec = 'https://' + host + ':19080/rcm-fitness-api/api/system/definition/' + sysUUID + '/component'

    # sysCompResp = requests.get(url)
    sysCompResp = requests.get(urlSec, verify=False)
    sysCompData = json.loads(sysCompResp.text)

    assert sysCompResp.status_code == 200, "Request has not been acknowledged as expected."

    while index < len(sysCompData["components"]):
        if sysCompData["components"][index]["definition"]["model"] != model:
            index += 1
            continue
        if sysCompData["components"][index]["definition"]["model"] == model:
            if "CUSTOMER" in sysCompData["components"][index]["identity"]["identifier"]:
                print("CUSTOMER")
                componentID = sysCompData["components"][index]["uuid"]
                print(componentID)
                index += 1
                break
            else:
                print("ELSE")
                componentID = sysCompData["components"][index]["uuid"]
                print(componentID)
                index += 1
                # continue
                # componentID = sysCompData["components"][index]["uuid"]
                # print(componentID)
            print(componentID)


    # compURL = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/compliance/data/device/' + componentID
    # compURLSec = 'https://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/compliance/data/device/' + componentID
    compURLSec = 'https://' + host + ':19080/rcm-fitness-api/api/compliance/data/device/' + componentID
    compResp = requests.get(compURLSec, verify=False)
    compData = json.loads(compResp.text)

    print(compData)
    assert compResp.status_code == 200, "Request has not been acknowledged as expected."

    with open(compDataFilename, 'w') as outfile:
        json.dump(compData, outfile, sort_keys=True, indent=4, ensure_ascii=False)

    if len(compData["subComponents"]) != "":
        print("1")
        totalSubComponents = len(compData["subComponents"])
        while subIndex < totalSubComponents:
            print("2")
            if identifier not in compData["subComponents"][subIndex]["elementData"]["identifier"]:
                subIndex += 1
                continue
            if identifier in compData["subComponents"][subIndex]["elementData"]["identifier"]:
                print("3")
                assert "uuid" in compData["subComponents"][subIndex], "Response detailed an empty group UUID."
                assert "parentDeviceUuid" in compData["subComponents"][
                    subIndex], "Response not detail parent Group UUID."
                assert "elementType" in compData["subComponents"][subIndex][
                    "elementData"], "Response not detail Element Type."
                assert "identifier" in compData["subComponents"][subIndex][
                    "elementData"], "Response not detail Identifier."
                assert "modelFamily" in compData["subComponents"][subIndex][
                    "elementData"], "Response not detail Family."
                assert "model" in compData["subComponents"][subIndex]["elementData"], "Response not detail Model."
                assert "messageReceivedTime" in compData["subComponents"][subIndex][
                    "auditData"], "Response not detail Received Time."
                assert "type" in compData["subComponents"][subIndex]["versionDatas"][0], "Response not detail Type."
                assert "version" in compData["subComponents"][subIndex]["versionDatas"][
                    0], "Response not detail Version."

                assert compData["subComponents"][subIndex]["uuid"] != "", "Response not detail subcomponent UUID."
                assert compData["subComponents"][subIndex]["elementData"][
                           "elementType"] == elementType, "Response returns incorrect Type."
                assert compData["subComponents"][subIndex]["parentDeviceUuid"] == compData["device"][
                    "uuid"], "Response not detail parent Group UUID."
                assert compData["subComponents"][subIndex]["auditData"][
                           "messageReceivedTime"] != "", "No timestamp included."
                assert compData["subComponents"][subIndex]["versionDatas"][0]["type"] == "FIRMWARE" or "SOFTWARE"
                assert compData["subComponents"][subIndex]["versionDatas"][0]["version"] != ""
                if compData["subComponents"][subIndex]["elementData"]["elementType"] == "NIC":
                    macAddress = compData["subComponents"][subIndex]["elementData"]["identifier"]
                    countColon = macAddress.count(":")
                    assert countColon == 5, "Unexpected MAC address format returned in Identifier value."

                subIndex += 1
                return

    assert False, "Sub Comp details not included in discovered details response."

def getComplianceData_INVALID(compUUID):
    getSystemDefinition()
    # url = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/compliance/data/device/' + compUUID
    # urlSec = 'https://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/compliance/data/device/' + compUUID
    urlSec = 'https://' + host + ':19080/rcm-fitness-api/api/compliance/data/device/' + compUUID

    # resp = requests.get(url)
    # resp = requests.get(urlSec, verify='/usr/local/share/ca-certificates/taf.cpsd.dell.ca.crt')
    resp = requests.get(urlSec, verify=False)
    data = json.loads(resp.text)

    if not data["device"]:
        if "message" in data.keys():
            if ('RFCA1025E') in data["code"]:
                assert resp.status_code == 500, "Request has not been acknowledged as expected."
                assert ('RCDS1004E Error retrieving device compliance data') in (data["message"]), "Returned Error Message does not reflect expected Error Code."
                assert compUUID in (data["message"]), "Returned Error Message does not include expected compUUID."
                return

            if ('RFCA1024I') in data["code"]:
                assert resp.status_code == 200, "Request has not been acknowledged as expected."
                assert ('RFCA1024I No compliance data was found') in (data["message"]), "Returned Error Message does not reflect expected Error Code."
                assert compUUID in (data["message"]), "Returned Error Message does not include expected compUUID."
                return

    assert False, "Response not in expected format."

def getComplianceData_SPACES(compUUID):
    getSystemDefinition()

    # url = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/compliance/data/device/' + compUUID + '/'
    # urlSec = 'https://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/compliance/data/device/' + compUUID + '/'
    urlSec = 'https://' + host + ':19080/rcm-fitness-api/api/compliance/data/device/' + compUUID + '/'
    # resp = requests.get(url)
    # resp = requests.get(urlSec, verify='/usr/local/share/ca-certificates/taf.cpsd.dell.ca.crt')
    resp = requests.get(urlSec, verify=False)
    assert resp.status_code == 500, "Request has not been acknowledged as expected."

    assert 'RFCA1025E' in resp.text, "Returned Error Message does not reflect expected Error Code."
    assert ('[' + compUUID + ']') in resp.text, "Returned Error Message does not include expected compUUID."
    assert ('RCDS1004E Error retrieving device compliance data') in resp.text, "Returned Error Message does not include expected text."


def getComplianceData_NULL():
    # url = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/compliance/data/device/'
    # urlSec = 'https://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/compliance/data/device/'
    urlSec = 'https://' + host + ':19080/rcm-fitness-api/api/compliance/data/device/'
    # resp = requests.get(url)
    # resp = requests.get(urlSec, verify='/usr/local/share/ca-certificates/taf.cpsd.dell.ca.crt')
    resp = requests.get(urlSec, verify=False)
    assert resp.status_code == 404, "Request has not been acknowledged as expected."

    # url = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/compliance/data/device//'
    # urlSec = 'https://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/compliance/data/device//'
    urlSec = 'https://' + host + ':19080/rcm-fitness-api/api/compliance/data/device//'
    # resp = requests.get(url)
    # resp = requests.get(urlSec, verify='/usr/local/share/ca-certificates/taf.cpsd.dell.ca.crt')
    resp = requests.get(urlSec, verify=False)
    assert resp.status_code == 404, "Request has not been acknowledged as expected."


@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice1():
    getComplianceData("VXRACK", "FLEX", "R730XD", ":", "POWEREDGE", "SERVER", path + "complianceDataDevicePOWEREDGE.json",
                      systemUUID, 5, 5)

@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice2():
    getComplianceDataDeviceSubComps("NIC", "Ethernet 10G 2P", "R730XD", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataDevicePOWEREDGE.json", systemUUID)

@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice3():
    getComplianceDataDeviceSubComps("NIC", "Ethernet 10G 4P", "R730XD", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataDevicePOWEREDGE.json", systemUUID)

@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice4():
    getComplianceDataDeviceSubComps("BIOS", "BIOS", "R730XD", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataDevicePOWEREDGE.json", systemUUID)


@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice5():
    getComplianceDataDeviceSubComps("iDRAC", "Remote Access", "R730XD", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataDevicePOWEREDGE.json", systemUUID)


@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice6():
    getComplianceDataDeviceSubComps("RAID", "PERC H730", "R730XD", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataDevicePOWEREDGE.json", systemUUID)

@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice6a():
    getComplianceDataDeviceSubComps("PERCCLI", "PercCli SAS Customization Utility", "R730XD", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataDevicePOWEREDGE.json", systemUUID)

@pytest.mark.daily_status
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice7():
    getComplianceData("VXRACK", "FLEX", "R630", ":", "POWEREDGE", "SERVER", path + "complianceDataDevicePOWEREDGE.json",
                      systemUUID, 5, 5)

@pytest.mark.daily_status
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice8():
    getComplianceDataDeviceSubComps("NIC", "Ethernet 10G 2P", "R630", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataDevicePOWEREDGE.json", systemUUID)

@pytest.mark.daily_status
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice9():
    getComplianceDataDeviceSubComps("NIC", "Gigabit 4P X520", "R630", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataDevicePOWEREDGE.json", systemUUID)

@pytest.mark.daily_status
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice10():
    getComplianceDataDeviceSubComps("BIOS", "BIOS", "R630", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataDevicePOWEREDGE.json", systemUUID)

@pytest.mark.daily_status
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice11():
    getComplianceDataDeviceSubComps("iDRAC", "Remote Access", "R630", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataDevicePOWEREDGE.json", systemUUID)

@pytest.mark.daily_status
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice12():
    getComplianceDataDeviceSubComps("NonRAID", "Dell HBA330 Mini", "R630", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataDevicePOWEREDGE.json", systemUUID)

@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice12a():
    getComplianceDataDeviceSubComps("PERCCLI", "PercCli SAS Customization Utility", "R630", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataDevicePOWEREDGE.json", systemUUID)

@pytest.mark.daily_status
@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice13():
    getComplianceData("VXRACK", "FLEX", "VCENTER-WINDOWS", "WINDOWS", "VCENTER", "VCENTER", path + "complianceDataDeviceVCENTER.json",
                      systemUUID, 3, 18)

@pytest.mark.daily_status
@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice14():
    getComplianceData("VXRACK", "FLEX", "VCENTER-APPLIANCE", "APPLIANCE", "VCENTER", "VCENTER", path + "complianceDataDeviceVCENTER.json",
                      systemUUID, 3, 3)

@pytest.mark.daily_status
@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice15():
    getComplianceDataDeviceSubComps("ESXI", "lab.vce.com", "VCENTER-WINDOWS", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataDeviceVCENTER.json", systemUUID)

@pytest.mark.daily_status
@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice16():
    getComplianceDataDeviceSubComps("ESXI", "lab.vce.com", "VCENTER-APPLIANCE", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataDeviceVCENTER.json", systemUUID)

@pytest.mark.daily_status
@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice17():
    getComplianceDataDeviceSubComps("SUB_ESXI", "ixgbe", "VCENTER-APPLIANCE", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataDeviceVCENTER.json", systemUUID)


@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice18():
    getComplianceData_INVALID(compUUID[:8])


@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice19():
    getComplianceData_INVALID("----")


@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice20():
    getComplianceData_INVALID("0-0-0-0")


@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice21():
    getComplianceData_INVALID("<>")


@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice22():
    getComplianceData_INVALID("  ")


@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice23():
    getComplianceData_NULL()

#(product, family, model, deviceProduct, deviceType, filename, sysUUID, minSubCount, maxSubCount)
@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice24():
    getComplianceData("VXRACK", "FLEX", "SCALEIO", "SCALEIO-1", "SCALEIO", "SCALEIO", path + "complianceDataDevicePOWEREDGE.json",
                      systemUUID, 6, 6)
#elementType, identifier, model, sysDefFilename, compDataFilename, sysUUID
@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice25():
    getComplianceDataDeviceSubComps("SVM", "lab.vce.com-ESX", "SCALEIO", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataDevicePOWEREDGE.json", systemUUID)

#(product, family, model, identifier, deviceProduct, deviceType, filename, sysUUID, minSubCount, maxSubCount)
@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice26():
    getComplianceData("VXRACK", "FLEX", "VCENTER-APPLIANCE", "VCENTER", "VCENTER", "VCENTER", path + "complianceDataDevicePOWEREDGE.json",
                      systemUUID, 6, 6)

#elementType, identifier, model, sysDefFilename, compDataFilename, sysUUID
@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice27():
    getComplianceDataDeviceSubComps("ESXI", "lab.vce.com", "VCENTER-APPLIANCE", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataDevicePOWEREDGE.json", systemUUID)

@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice28():
    getComplianceDataDeviceSubComps("SUB_ESXI", "ixgbe", "VCENTER-APPLIANCE", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataDevicePOWEREDGE.json", systemUUID)

@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice29():
    getComplianceData("VXRACK", "FLEX", "VCENTER-WINDOWS", "CUSTOMER", "VCENTER", "VCENTER", path + "complianceDataDevicePOWEREDGE.json",
                      systemUUID, 6, 6)

#elementType, identifier, model, sysDefFilename, compDataFilename, sysUUID
@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice30():
    getComplianceDataDeviceSubComps("SUB_ESXI", "ScaleIO VM", "VCENTER-WINDOWS", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataDevicePOWEREDGE.json", systemUUID)

