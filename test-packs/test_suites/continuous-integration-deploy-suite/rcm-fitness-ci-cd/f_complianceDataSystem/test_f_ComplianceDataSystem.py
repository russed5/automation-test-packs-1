#!/usr/bin/env python
# Copyright © 2017 Dell Inc. or its subsidiaries.  All Rights Reserved
import json
import requests
import pytest
import af_support_tools
import os
import re


@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    global path
    path = '/home/autouser/PycharmProjects/auto-framework/test_suites/continuous-integration-deploy-suite/rcm-fitness-ci-cd/f_complianceDataSystem/'
    ensurePathExists(path)
    purgeOldOutput(path, "complianceDataSystem")

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
    # resp = requests.get(url)
    urlSec = 'https://' + host + ':19080/rcm-fitness-api/api/system/definition/'
    print("urlSec:")
    print(urlSec)
    resp = requests.get(urlSec, verify=False)
    # resp = requests.get(urlSec, verify='/usr/local/share/ca-certificates/taf.cpsd.dell.ca.crt')

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

def getComplianceDataSystem(product, family, identifier, deviceFamily, deviceModel, deviceType, compDataFilename,sysUUID):
    compIndex = 0
    groupIndex = 0
    deviceIndex = 0
    i = 0

    urlSec = 'https://' + host + ':19080/rcm-fitness-api/api/system/definition/' + sysUUID
    resp = requests.get(urlSec, verify=False)
    # url = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/system/definition/' + sysUUID
    # resp = requests.get(url)
    # resp = requests.get(urlSec, verify='/usr/local/share/ca-certificates/taf.cpsd.dell.ca.crt')
    data = json.loads(resp.text)
    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    # url = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/system/definition/' + sysUUID + '/component/'
    # resp = requests.get(url)
    urlSec = 'https://' + host + ':19080/rcm-fitness-api/api/system/definition/' + sysUUID + '/component/'
    resp = requests.get(urlSec, verify=False)

    # resp = requests.get(urlSec, verify='/usr/local/share/ca-certificates/taf.cpsd.dell.ca.crt')
    deviceData = json.loads(resp.text)

    assert resp.status_code == 200, "Request has not been acknowledged as expected."
    print("Requesting system details from Compliance Data Service.\n")

    totalComponents = len(deviceData["components"])

    # compURL = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/compliance/data/system/' + sysUUID
    #
    # compResp = requests.get(compURL)
    compURLSec = 'https://' + host + ':19080/rcm-fitness-api/api/compliance/data/system/' + sysUUID

    compResp = requests.get(compURLSec, verify=False)

    # compResp = requests.get(compURLsec, verify='/usr/local/share/ca-certificates/taf.cpsd.dell.ca.crt')
    compData = json.loads(compResp.text)

    assert compResp.status_code == 200, "Request has not been acknowledged as expected."

    with open(compDataFilename, 'a') as outfile:
        json.dump(compData, outfile, sort_keys=True, indent=4, ensure_ascii=False)

    assert len(compData["devices"]) != "", "No devices discovered...."

    if len(compData["devices"]) != "":

        assert not compData["message"], "Expected message field to be NULL."
        assert compData["convergedSystem"]["systemUuid"] == deviceData[
            "systemUuid"] == systemUUID, "Response shows incorrect System UUID."
        assert compData["convergedSystem"]["product"] == product, "Response not detail Model."
        assert compData["convergedSystem"]["modelFamily"] == family, "Response not detail Family."
        assert compData["convergedSystem"]["identifier"] == identifier, "Response not detail Identifier."
        assert "serialNumber" in compData["convergedSystem"], "Response not detail Serial Number."

        assert compData["convergedSystem"]["model"] == data["system"]["definition"][
            "model"], "Unexpected Model returned."
        assert compData["convergedSystem"]["modelFamily"] == data["system"]["definition"][
            "modelFamily"], "Unexpected Model returned."
        assert compData["convergedSystem"]["product"] == data["system"]["definition"][
            "product"], "Unexpected Product returned."
        assert compData["convergedSystem"]["identifier"] == data["system"]["identity"][
            "identifier"], "Unexpected Identifier returned."
        assert compData["convergedSystem"]["serialNumber"] == data["system"]["identity"][
            "serialNumber"], "Unexpected Serial No. returned."
        assert len(compData["convergedSystem"]["links"]) > 0, "No link returned for Converged System."

        totalGroups = len(compData["groups"])
        assert totalGroups > 0, "response not including a list of Groups."
        totalDevices = len(compData["devices"])
        assert totalDevices > 0, "response not including a list of Devices."
        totalSubComponents = len(compData["subComponents"])
        assert totalSubComponents > 0, "response not including a list of Devices."

        while groupIndex < totalGroups:
            if compData["groups"][groupIndex]["uuid"] != data["system"]["groups"][i]["uuid"]:
                i += 1
                continue
            if compData["groups"][groupIndex]["uuid"] == data["system"]["groups"][i]["uuid"]:
                assert compData["groups"][groupIndex]["parentSystemUuids"][0] == systemUUID, "Response not detail parent System UUID."
                assert compData["groups"][groupIndex]["type"] == "STORAGE" or "NETWORK" or "COMPUTE"
                i += 1
                break
            groupIndex += 1
        while deviceIndex < totalDevices:
            while compIndex < len(deviceData["components"]):
                if deviceModel in compData["devices"][deviceIndex]["elementData"]["model"]:
                    if compData["devices"][deviceIndex]["uuid"] == deviceData["components"][compIndex]["uuid"]:
                        assert compData["devices"][deviceIndex]["parentGroupUuids"][0] == \
                               deviceData["components"][compIndex]["parentGroupUuids"][
                                   0], "Response not detail parent Group UUID."
                        assert "productFamily" in compData["devices"][deviceIndex][
                            "elementData"], "Response not detail Product Family."
                        assert "modelFamily" in compData["devices"][deviceIndex][
                            "elementData"], "Response not detail Model Family."
                        assert "model" in compData["devices"][deviceIndex]["elementData"], "Response not detail Model."
                        assert "identifier" in compData["devices"][deviceIndex][
                            "elementData"], "Response not detail Identifier."
                        assert "elementType" in compData["devices"][deviceIndex][
                            "elementData"], "Response not detail ElementType."
                        assert compData["devices"][deviceIndex]["auditData"][
                                   "collectedTime"] != "", "Response not detail Collection Time."
                        assert compData["devices"][deviceIndex]["auditData"][
                                   "collectionSentTime"] != "", "Response not detail Collection Sent Time."
                        assert compData["devices"][deviceIndex]["auditData"][
                                   "messageReceivedTime"] != "", "Response not detail Received Time."
                        if compData["devices"][deviceIndex]["elementData"]["model"] == deviceData["components"][compIndex]["definition"]["model"]:
                            assert compData["devices"][deviceIndex]["uuid"] == deviceData["components"][compIndex][
                                "uuid"], "Response detailed an empty group UUID."
                            assert compData["devices"][deviceIndex]["parentGroupUuids"][0] == \
                                   deviceData["components"][compIndex]["parentGroupUuids"][0], "Response not detail parent Group UUID."
                            assert compData["devices"][deviceIndex]["elementData"][
                                       "elementType"] == deviceType, "Response not detail Element Type."
                            assert compData["devices"][deviceIndex]["elementData"][
                                       "modelFamily"] == deviceFamily, "Response not detail Model."
                            assert compData["devices"][deviceIndex]["elementData"]["elementType"] == \
                                   deviceData["components"][compIndex]["identity"][
                                       "elementType"], "Response not detail Element Type."
                            assert compData["devices"][deviceIndex]["elementData"]["modelFamily"] == \
                                   deviceData["components"][compIndex]["definition"][
                                       "modelFamily"], "Response not detail Identifier."
                            assert compData["devices"][deviceIndex]["elementData"]["productFamily"] == \
                                   deviceData["components"][compIndex]["definition"][
                                       "productFamily"], "Response not detail Product Family."
                            assert compData["devices"][deviceIndex]["elementData"]["identifier"] == \
                                   deviceData["components"][compIndex]["identity"][
                                       "identifier"], "Response not detail Identifier."
                            macAddress = compData["devices"][deviceIndex]["elementData"]["identifier"]
                            if ":" in macAddress:
                                countColon = macAddress.count(":")
                                assert countColon == 5, "Unexpected MAC address format returned."
                            assert compData["devices"][deviceIndex]["auditData"][
                                       "collectedTime"] != "", "Response not detail Collection Time."
                            assert compData["devices"][deviceIndex]["auditData"][
                                       "collectionSentTime"] != "", "Response not detail Collection Sent Time."
                            assert compData["devices"][deviceIndex]["auditData"][
                                       "messageReceivedTime"] != "", "Response not detail Received Time."
                            return
                        else:
                            compIndex += 1
                            continue
                        compIndex += 1
                    else:
                        compIndex += 1
                        continue
                else:
                    deviceIndex += 1
                    continue
            deviceIndex += 1
    assert False, "No devices returned."

def getComplianceDataSystemSubComps(model, elementType, identifier, sysDefFilename, compDataFilename, sysUUID):
    getSystemDefinition()
    urlSec = 'https://' + host + ':19080/rcm-fitness-api/api/system/definition/' + sysUUID
    resp = requests.get(urlSec, verify=False)
    # resp = requests.get(urlSec, verify='/usr/local/share/ca-certificates/taf.cpsd.dell.ca.crt')
    data = json.loads(resp.text)

    assert resp.status_code == 200, "Request has not been acknowledged as expected."
    with open(sysDefFilename, 'w') as outfile:
        json.dump(data, outfile, sort_keys=True, indent=4, ensure_ascii=False)

    compURLSec = 'https://' + host + ':19080/rcm-fitness-api/api/compliance/data/system/' + sysUUID
    compResp = requests.get(compURLSec, verify=False)

    compData = json.loads(compResp.text)

    assert compResp.status_code == 200, "Request has not been acknowledged as expected."

    with open(compDataFilename, 'w') as outfile:
        json.dump(compData, outfile, sort_keys=True, indent=4, ensure_ascii=False)

    index = 0
    assert len(compData["devices"]) != "", "No devices discovered......"

    if len(compData["devices"]) != "":
        totalSubComponents = len(compData["subComponents"])
        assert len(compData["subComponents"]) != "", "No subcomponents discovered ...."
        subIndex = 0
        while subIndex < totalSubComponents:
            if identifier in compData["subComponents"][subIndex]["elementData"]["identifier"] and model in compData["subComponents"][subIndex]["elementData"]["model"]:
                while index < len(compData["devices"]):
                    if compData["subComponents"][subIndex]["parentDeviceUuid"] == compData["devices"][index]["uuid"]:
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
                        assert identifier in compData["subComponents"][subIndex]["elementData"][
                            "identifier"], "Response returns incorrect Identifier."
                        assert compData["subComponents"][subIndex]["parentDeviceUuid"] == compData["devices"][index][
                            "uuid"], "Response not detail parent Group UUID."
                        assert compData["subComponents"][subIndex]["auditData"][
                                   "messageReceivedTime"] != "", "No timestamp included."
                        assert compData["subComponents"][subIndex]["versionDatas"][0]["type"] == "FIRMWARE" or "SOFTWARE"
                        assert compData["subComponents"][subIndex]["versionDatas"][0]["version"] != ""
                        if compData["subComponents"][subIndex]["elementData"]["elementType"] == "NIC":
                            macAddress = compData["subComponents"][subIndex]["elementData"]["identifier"]
                            countColon = macAddress.count(":")
                            assert countColon == 5, "Unexpected MAC address format returned in Identifier value."
                        return

                    index += 1
                index = 0
            subIndex += 1

        assert False, "Unexpected Identifier in response."
    assert False, "No devices returned."

def getComplianceDataSystem_INVALID(sysUUID):
    getSystemDefinition()
    # url = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/compliance/data/system/' + sysUUID
    #
    # resp = requests.get(url)
    urlSec = 'https://' + host + ':19080/rcm-fitness-api/api/compliance/data/system/' + sysUUID
    resp = requests.get(urlSec, verify=False)
    # resp = requests.get(urlSec, verify='/usr/local/share/ca-certificates/taf.cpsd.dell.ca.crt')
    data = json.loads(resp.text)

    if not data["convergedSystem"]:
        if "message" in data.keys():
            if ('RFCA1003E') in data["code"]:
                assert resp.status_code == 500, "Request has not been acknowledged as expected."
                assert ('RCDS1006E Error retrieving system compliance data') in (
                data["message"]), "Returned Error Message text not as expected."
                assert (sysUUID) in (data["message"]), "Returned Error Message does not include expected compUUID."

            if ('RFCA1005I') in (data["code"]):
                assert resp.status_code == 200, "Request has not been acknowledged as expected."
                print("Message: %s" % data["message"])
                assert ('RFCA1005I No compliance data was found') in (
                data["message"]), "Returned Error Message text not as expected."
                assert (sysUUID) in (data["message"]), "Returned Error Message does not include expected compUUID."

def getComplianceDataSystem_NULL():
    print("Verifying 404 returned if no component UUID provided.")

    # url = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/compliance/data/system/'
    # resp = requests.get(url)
    urlSec = 'https://' + host + ':19080/rcm-fitness-api/api/compliance/data/system/'
    resp = requests.get(urlSec, verify=False)
    # resp = requests.get(urlSec, verify='/usr/local/share/ca-certificates/taf.cpsd.dell.ca.crt')
    assert resp.status_code == 404, "Request has not been acknowledged as expected."

    # url = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/compliance/data/system//'
    # resp = requests.get(url)
    urlSec = 'https://' + host + ':19080/rcm-fitness-api/api/compliance/data/system//'
    resp = requests.get(urlSec, verify=False)
    # resp = requests.get(urlSec, verify='/usr/local/share/ca-certificates/taf.cpsd.dell.ca.crt')
    assert resp.status_code == 404, "Request has not been acknowledged as expected."


@pytest.mark.daily_status
@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem1():
    getComplianceDataSystem("VXRACK", "FLEX", "VXRACKFLEX", "730", "R730XD", "SERVER",
                            path + "complianceDataSystemPOWEREDGE.json", systemUUID)

@pytest.mark.daily_status
@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem2():
    getComplianceDataSystemSubComps("R730XD", "NIC", "Ethernet 10G 2P", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataSystemPOWEREDGE.json", systemUUID)


@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem3():
    getComplianceDataSystemSubComps("R730XD", "NIC", "Ethernet 10G 4P", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataSystemPOWEREDGE.json", systemUUID)


@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem4():
    getComplianceDataSystemSubComps("R730XD", "BIOS", "BIOS", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataSystemPOWEREDGE.json", systemUUID)


@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem5():
    getComplianceDataSystemSubComps("R730XD", "iDRAC", "Remote Access", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataSystemPOWEREDGE.json", systemUUID)


@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem6():
    getComplianceDataSystemSubComps("R730XD", "RAID", "PERC H730", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataSystemPOWEREDGE.json", systemUUID)

@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem6():
    getComplianceDataSystemSubComps("R730XD", "PERCCLI", "PercCli SAS Customization Utility", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataSystemPOWEREDGE.json", systemUUID)

@pytest.mark.daily_status
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem7():
    getComplianceDataSystem("VXRACK", "FLEX", "VXRACKFLEX", "630", "R630", "SERVER",
                            path + "complianceDataSystemPOWEREDGE.json", systemUUID)

@pytest.mark.daily_status
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem8():
    getComplianceDataSystemSubComps("R630", "NIC", "Ethernet 10G 2P", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataSystemPOWEREDGE.json", systemUUID)


@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem9():
    getComplianceDataSystemSubComps("R630", "NIC", "Gigabit 4P", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataSystemPOWEREDGE.json", systemUUID)


@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem10():
    getComplianceDataSystemSubComps("R630", "BIOS", "BIOS", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataSystemPOWEREDGE.json", systemUUID)


@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem11():
    getComplianceDataSystemSubComps("R630", "iDRAC", "Remote Access", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataSystemPOWEREDGE.json", systemUUID)


@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem12():
    getComplianceDataSystemSubComps("R630", "NonRAID", "Dell HBA330", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataSystemPOWEREDGE.json", systemUUID)

@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem12a():
    getComplianceDataSystemSubComps("R630", "PERCCLI", "PercCli SAS Customization Utility", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataSystemPOWEREDGE.json", systemUUID)

@pytest.mark.daily_status
@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem13():
    getComplianceDataSystem("VXRACK", "FLEX", "VXRACKFLEX", "VCENTER", "VCENTER-WINDOWS", "VCENTER",
                            path + "complianceDataSystemVCENTER.json", systemUUID)

@pytest.mark.daily_status
@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem14():
    getComplianceDataSystem("VXRACK", "FLEX", "VXRACKFLEX", "VCENTER", "VCENTER-APPLIANCE", "VCENTER",
                            path + "complianceDataSystemVCENTER.json", systemUUID)

@pytest.mark.daily_status
@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem15():
    getComplianceDataSystemSubComps("VCENTER-WINDOWS", "ESXI", "lab.vce.com", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataSystemVCENTER.json", systemUUID)

@pytest.mark.daily_status
@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem15a():
    getComplianceDataSystemSubComps("VCENTER-APPLIANCE", "SUB_ESXI", "ixgbe", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataSystemVCENTER.json", systemUUID)

@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem16():
    getComplianceDataSystem_INVALID(systemUUID[:8])


@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem17():
    getComplianceDataSystem_INVALID("----")


@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem18():
    getComplianceDataSystem_INVALID(" ")


@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem19():
    getComplianceDataSystem_NULL()

@pytest.mark.daily_status
@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem20():
    getComplianceDataSystem("VXRACK", "FLEX", "VXRACKFLEX", "730", "R730XD", "SERVER",
                            path + "complianceDataSystemPOWEREDGE.json", systemUUID)

@pytest.mark.daily_status
@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem21():
    getComplianceDataSystemSubComps("SCALEIO", "SVM", "Manager2", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataSystemPOWEREDGE.json", systemUUID)

@pytest.mark.daily_status
@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem22():
    getComplianceDataSystemSubComps("SCALEIO", "SVM", "lab.vce.com-ESX", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataSystemPOWEREDGE.json", systemUUID)

@pytest.mark.daily_status
@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem23():
    getComplianceDataSystemSubComps("SCALEIO", "SVM", "Manager1", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataSystemPOWEREDGE.json", systemUUID)

@pytest.mark.daily_status
@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem24():
    getComplianceDataSystemSubComps("SCALEIO", "SVM", "TB1", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataSystemPOWEREDGE.json", systemUUID)
