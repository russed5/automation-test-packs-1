#!/usr/bin/env python
import json
import requests
import pytest
import os
import re
import af_support_tools


@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    global path
    path = '/home/autouser/PycharmProjects/auto-framework/test_suites/continuous-integration-deploy-suite/rcm-fitness-ci-cd/restLevelTests/systemDefinition/'
    ensurePathExists(path)
    purgeOldOutput(path, "rcm")

    global ssl_options
    ssl_options = {"ca_certs": "/etc/rabbitmq/certs/testca/cacert.pem",
                   "certfile": "/etc/rabbitmq/certs/certs/client/cert.pem",
                   "keyfile": "/etc/rabbitmq/certs/certs/client/key.pem", "cert_reqs": "ssl.CERT_REQUIRED",
                   "ssl_version": "ssl.PROTOCOL_TLSv1_2"}

    # Set config ini file name
    global env_file
    env_file = 'env.ini'

    global hostTLS
    hostTLS = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')

    # getSystemDefinition()


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

def getSystemDefinition(identifier, system, product, family, model):
    # url = 'http://' + host + ':19080/rcm-fitness-api/api/system/definition/'
    urlSec = 'https://' + hostTLS + ':19080/rcm-fitness-api/api/system/definition/'
    # resp = requests.get(url)
    # resp = requests.get(urlSec, verify='/usr/local/share/ca-certificates/hennet1.cpsd.dell.ca.crt')
    resp = requests.get(urlSec, verify=False)
    data = json.loads(resp.text)

    groupIndex = linkIndex = totalGroups = 0
    totalEndpoints = totalSubSystems = totalComponents = totalLinks = 0

    print("GroupIndex: %d" % groupIndex)
    print("TotalSubSystems: %d" % totalSubSystems)

    print("Requesting UUID from System Definition....")
    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    if data != "":
        if data["systems"][0]["uuid"] != "":

            with open(path + 'rcmSystemDefinition-VxRack.json', 'w') as outfile:
                json.dump(data, outfile, sort_keys=True, indent=4, ensure_ascii=False)

            print("\nExtracting UUID from response....")
            global systemUUID
            systemUUID = data["systems"][0]["uuid"]
            print("Defined SystemUUID: %s" % systemUUID)
            print("Product Family: %s" % data["systems"][0]["definition"]["productFamily"])
            assert "uuid" in data["systems"][0], "Response not detail System UUID."
            assert "identity" in data["systems"][0], "Response not detail Identity."
            assert "definition" in data["systems"][0], "Response not detail Definition."
            assert "groups" in data["systems"][0], "Response not detail Groups."
            assert "endpoints" in data["systems"][0], "Response not detail Endpoints."
            assert "subSystems" in data["systems"][0], "Response not detail Subsystems."
            assert "components" in data["systems"][0], "Response not detail Components."
            assert "links" in data["systems"][0], "Response not detail Links."

            assert data["systems"][0]["definition"][
                       "productFamily"] == system, "Response details incorrect Product Family."
            assert data["systems"][0]["definition"]["product"] == product, "Response details incorrect Product."
            assert data["systems"][0]["definition"]["modelFamily"] == family, "Response details incorrect Model Family."
            assert data["systems"][0]["definition"]["model"] == model, "Response details incorrect Model."
            assert data["systems"][0]["identity"]["serialNumber"] != "", "Response details empty Serial Number."
            assert data["systems"][0]["identity"]["identifier"] == identifier, "Response details empty Identifier."
            assert model in data["systems"][0]["definition"]["model"], "Response details incorrect Model."

            totalLinks = len(data["systems"][0]["links"])
            assert totalLinks > 0, "Empty list of Links returned."

            while linkIndex < totalLinks:
                print("Defined groupUUID: %s" % data["systems"][0]["links"][linkIndex]["href"])
                assert data["systems"][0]["links"][linkIndex]["href"] != "", "Empty links returned in HREF field."
                linkIndex += 1

            if len(data["systems"]) > 1:

                global secondSystemUUID
                secondSystemUUID = data["systems"][1]["uuid"]
                print("Defined SystemUUID: %s" % secondSystemUUID)
                print("Product Family: %s" % data["systems"][1]["definition"]["productFamily"])
                assert "uuid" in data["systems"][1], "Response not detail System UUID."
                assert "identity" in data["systems"][1], "Response not detail Identity."
                assert "definition" in data["systems"][1], "Response not detail Definition."
                assert "groups" in data["systems"][1], "Response not detail Groups."
                assert "endpoints" in data["systems"][1], "Response not detail Endpoints."
                assert "subSystems" in data["systems"][1], "Response not detail Subsystems."
                assert "components" in data["systems"][1], "Response not detail Components."
                assert "links" in data["systems"][1], "Response not detail Links."

                assert data["systems"][1]["definition"][
                           "productFamily"] == system, "Response details incorrect Product Family."
                assert data["systems"][1]["definition"]["product"] == product, "Response details incorrect Product."
                assert data["systems"][1]["definition"][
                           "modelFamily"] == family, "Response details incorrect Model Family."
                assert data["systems"][1]["definition"]["model"] == model, "Response details incorrect Model."
                assert data["systems"][1]["identity"]["serialNumber"] != "", "Response details empty Serial Number."
                assert data["systems"][1]["identity"]["identifier"] == identifier, "Response details empty Identifier."
                assert model in data["systems"][1]["definition"]["model"], "Response details incorrect Model."

                totalLinks = len(data["systems"][1]["links"])
                assert totalLinks > 0, "Empty list of Links returned."

                while linkIndex < totalLinks:
                    print("Second defined groupUUID: %s" % data["systems"][1]["links"][linkIndex]["href"])
                    assert data["systems"][1]["links"][linkIndex]["href"] != "", "Empty links returned in HREF field."
                    linkIndex += 1
        else:
            print("\nNo System UUID returned in REST response")
            print(data["message"])

    return systemUUID

def getSystemDefinitionByUUID(identifier, system, product, family, model, sysUUID):
    # url = 'http://' + host + ':19080/rcm-fitness-api/api/system/definition/' + sysUUID
    urlSec = 'https://' + hostTLS + ':19080/rcm-fitness-api/api/system/definition/' + sysUUID
    # resp = requests.get(url)
    # resp = requests.get(urlSec, verify='/usr/local/share/ca-certificates/hennet1.cpsd.dell.ca.crt')
    resp = requests.get(urlSec, verify=False)
    data = json.loads(resp.text)

    groupIndex = endptIndex = linkIndex = componentIndex = 0
    totalGroups = totalEndpoints = totalSubSystems = totalComponents = totalLinks = 0

    print("Requesting a systems specific details ....")
    # assert resp.status_code == 200, "Request has not been acknowledged as expected."

    if data != "":
        if data["system"]["uuid"] != "":
            print("Here now....1")
            with open(path + 'rcmSystemDefinitionByUUID-VxRack.json', 'w') as outfile:
                json.dump(data, outfile, sort_keys=True, indent=4, ensure_ascii=False)

            print("Defined SystemUUID: %s" % sysUUID)
            print("Product Family: %s" % data["system"]["definition"]["productFamily"])
            assert "uuid" in data["system"], "Response not detail System UUID."
            assert "identity" in data["system"], "Response not detail Identity."
            assert "definition" in data["system"], "Response not detail Definition."
            assert "groups" in data["system"], "Response not detail Groups."
            assert "endpoints" in data["system"], "Response not detail Endpoints."
            assert "subSystems" in data["system"], "Response not detail Subsystems."
            assert "components" in data["system"], "Response not detail Components."
            assert "links" in data["system"], "Response not detail Links."

            assert data["system"]["definition"]["productFamily"] == system, "Response details incorrect Product Family."
            assert data["system"]["definition"]["product"] == product, "Response details incorrect Product."
            assert data["system"]["definition"]["modelFamily"] == family, "Response details incorrect Model Family."
            assert data["system"]["identity"]["serialNumber"] != "", "Response details empty Serial Number."
            assert data["system"]["identity"]["identifier"] == identifier, "Response details empty Identifier."
            assert model in data["system"]["definition"]["model"], "Response details incorrect Model."

            totalGroups = len(data["system"]["groups"])
            totalEndpoints = len(data["system"]["endpoints"])
            # totalSubSystems = len(data["system"]["subSystems"])
            totalComponents = len(data["system"]["components"])
            totalLinks = len(data["system"]["links"])

            assert totalGroups > 0, "Empty list of Groups returned."
            assert totalEndpoints > 0, "Empty list of Endpoints returned."
            # assert totalSubSystems > 0, "Empty list of SubSystems returned."
            assert totalComponents > 0, "Empty list of Components returned."
            assert totalLinks > 0, "Empty list of Links returned."

            print("\nTotal groups: %d" % totalGroups)
            print("\nExtracting groupUUID from response....\n")
            while groupIndex < totalGroups:
                if data["system"]["groups"][groupIndex]["type"] == type:
                    print("Here now....2")
                    global groupUUID
                    groupUUID = data["system"]["groups"][groupIndex]["uuid"]
                    print("Total Groups: %d" % totalGroups)
                    print("Defined groupUUID: %s" % groupUUID)
                    print("Group Name: %s" % data["system"]["groups"][groupIndex]["name"])
                groupIndex += 1

            print("\nTotal endpts: %d" % totalEndpoints)
            print("\nExtracting endptUUID from response....\n")
            while endptIndex < totalEndpoints:
                if data["system"]["endpoints"][endptIndex]["uuid"] != "":
                    print("Here now....3")
                    global endptUUID
                    endptUUID = data["system"]["endpoints"][endptIndex]["uuid"]
                    print("Total Endpts: %d" % totalEndpoints)
                    print("Defined endptUUID: %s" % endptUUID)
                    print("Endpt Address: %s" % data["system"]["endpoints"][endptIndex]["address"])
                endptIndex += 1

            print("\nTotal components: %d" % totalComponents)
            print("\nExtracting componentUUID from response....\n")
            while componentIndex < totalComponents:
                if data["system"]["components"][componentIndex]["uuid"] != "":
                    print("Here now....4")
                    global componentUUID
                    componentUUID = data["system"]["components"][componentIndex]["uuid"]
                    print("Total Components: %d" % totalComponents)
                    print("Defined componentUUID: %s" % componentUUID)
                    # print("Endpt Address: %s" % data["system"][0]["components"][componentIndex]["address"])
                    assert data["system"]["components"][componentIndex][
                               "identity"] != "", "Component Identity details reeturned are empty."
                    assert data["system"]["components"][componentIndex][
                               "definition"] != "", "Component Definition details reeturned are empty."
                    assert data["system"]["components"][componentIndex][
                               "endpoints"] != "", "Component Endpts details reeturned are empty."
                    assert data["system"]["components"][componentIndex][
                               "parentGroupUuids"] != "", "Component Parent Group details reeturned are empty."
                componentIndex += 1

            while linkIndex < totalLinks:
                print("Defined groupUUID: %s" % data["system"]["links"][linkIndex]["href"])
                assert data["system"]["links"][linkIndex]["href"] != "", "Empty links returned in HREF field."
                linkIndex += 1
        else:
            print("\nNo System UUID returned in REST response")
            print(data["message"])

def getComponentBySystemUUID(family, series, type, tag, model, endpoints, sysUUID):
    # url = 'http://' + host + ':19080/rcm-fitness-api/api/system/definition/' + sysUUID + '/component'
    urlSec = 'https://' + hostTLS + ':19080/rcm-fitness-api/api/system/definition/' + sysUUID + '/component'
    # resp = requests.get(url)
    # resp = requests.get(urlSec, verify='/usr/local/share/ca-certificates/hennet1.cpsd.dell.ca.crt')
    resp = requests.get(urlSec, verify=False)
    data = json.loads(resp.text)

    compIndex = totalComponents = 0
    totalEndpts = endPts = 0

    print("Requesting a systems specific details ....")
    # assert resp.status_code == 200, "Request has not been acknowledged as expected."

    if data != "":
        if data["systemUuid"] != "":
            print("Here now....1")
            with open(path + 'rcmComponentBySystemUUID-VxRack.json', 'w') as outfile:
                json.dump(data, outfile, sort_keys=True, indent=4, ensure_ascii=False)

            assert data["systemUuid"] == sysUUID, "Response did not detail the expected system UUID."

            totalComponents = len(data["components"])
            assert totalComponents > 0, "Empty list of Components returned."

            print("\nTotal components: %d" % totalComponents)
            # print("\nExtracting groupUUID from response....\n")
            while compIndex < totalComponents:
                if series in data["components"][compIndex]["definition"]["modelFamily"] and \
                        data["components"][compIndex]["identity"]["identifier"] == tag:
                    print("Here now....2")
                    print(data)
                    assert data["components"][compIndex]["parentGroupUuids"][
                               0] != "", "Response includes unexpected group ID."
                    assert data["components"][compIndex]["definition"][
                               "productFamily"] == family, "Response includes unexpected Product Family."
                    assert data["components"][compIndex]["identity"][
                               "identifier"] != "", "Response includes unexpected Identifier."
                    assert data["components"][compIndex]["identity"][
                               "elementType"] == type, "Response includes unexpected Identifier."
                    assert model in data["components"][compIndex]["definition"][
                        "model"], "Response includes unexpected Model."
                    assert tag in data["components"][compIndex]["identity"][
                        "identifier"], "Response includes unexpected Identifier."
                    totalEndpts = len(data["components"][compIndex]["endpoints"])
                    print(data["components"][compIndex]["endpoints"])
                    assert totalEndpts == endpoints, "Empty list of Endpoints returned for this component."
                    print("\nComponent: %s" % data["components"][compIndex]["definition"]["modelFamily"])
                    print("Tag: %s" % data["components"][compIndex]["identity"]["identifier"])
                    print("UUID: %s" % data["components"][compIndex]["uuid"])
                    print("Total Endpts: %d" % totalEndpts)
                    # groupUUID = data["system"]["groups"][groupIndex]["groupUuid"]
                compIndex += 1
                endPts = 0

        else:
            print("\nNo system returned in REST response.")
            print(data["message"])

def getSystemDefinitionInvalidUUID(invalidSystemUUID):
    # invalidSystemUUID = systemUUID[:8]
    print(invalidSystemUUID)
    # url = 'http://' + host + ':19080/rcm-fitness-api/api/system/definition/' + invalidSystemUUID + '/'
    urlSec = 'https://' + hostTLS + ':19080/rcm-fitness-api/api/system/definition/' + invalidSystemUUID + '/'
    # resp = requests.get(url)
    # resp = requests.get(urlSec, verify='/usr/local/share/ca-certificates/hennet1.cpsd.dell.ca.crt')
    resp = requests.get(urlSec, verify=False)
    data = json.loads(resp.text)

    print(data["system"])
    print(data["message"])

    if not data["system"]:
        if ("message") in data.keys():
            print(data["message"])
            assert ('RFCA1017I') in (data["message"]), "Returned Error Message does not reflect expected Error Code."
            assert (invalidSystemUUID) in (
            data["message"]), "Returned Error Message does not reflect specified System UUID."

def getComponentByInvalidSystemUUID(invalidSystemUUID):
    # invalidSystemUUID = systemUUID[:8]
    print(invalidSystemUUID)
    # url = 'http://' + host + ':19080/rcm-fitness-api/api/system/definition/' + invalidSystemUUID + '/component/'
    urlSec = 'https://' + hostTLS + ':19080/rcm-fitness-api/api/system/definition/' + invalidSystemUUID + '/component/'
    # resp = requests.get(url)
    # resp = requests.get(urlSec, verify='/usr/local/share/ca-certificates/hennet1.cpsd.dell.ca.crt')
    resp = requests.get(urlSec, verify=False)
    data = json.loads(resp.text)

    print(data["components"])
    print(data["message"])

    if not data["components"]:
        if ("message") in data.keys():
            print(data["message"])
            assert ('RFCA1026E') in (data["code"]), "Returned Error does not reflect expected Error Code."
            assert ('SYSDEF2022W') in (data["message"]), "Returned Error Message does not reflect expected warning."

def getSystemDefinitionNullUUID(identifier, system, product, family, model):
    # url = 'http://' + host + ':19080/rcm-fitness-api/api/system/definition//'
    urlSec = 'https://' + hostTLS + ':19080/rcm-fitness-api/api/system/definition//'
    # resp = requests.get(url)
    # resp = requests.get(urlSec, verify='/usr/local/share/ca-certificates/hennet1.cpsd.dell.ca.crt')
    resp = requests.get(urlSec, verify=False)
    data = json.loads(resp.text)

    groupIndex = linkIndex = totalGroups = 0
    totalEndpoints = totalSubSystems = totalComponents = totalLinks = 0

    print("GroupIndex: %d" % groupIndex)
    print("TotalSubSystems: %d" % totalSubSystems)

    print("Requesting UUID from System Definition....")
    print(resp.status_code)
    print(data)
    # assert resp.status_code == 200, "Request has not been acknowledged as expected."

    if data != "":
        if data["systems"][0]["uuid"] != "":
            # with open(path + 'rcmSystemDefinition-VxRack.json', 'w') as outfile:
            #     json.dump(data, outfile, sort_keys=True, indent=4, ensure_ascii=False)
            global systemUUID
            systemUUID = data["systems"][0]["uuid"]
            assert data["systems"][0]["definition"][
                       "productFamily"] == system, "Response details incorrect Product Family."
            assert data["systems"][0]["definition"]["product"] == product, "Response details incorrect Product."
            assert data["systems"][0]["definition"]["modelFamily"] == family, "Response details incorrect Model Family."
            assert data["systems"][0]["definition"]["model"] == model, "Response details incorrect Model."
            assert data["systems"][0]["identity"]["serialNumber"] != "", "Response details empty Serial Number."
            assert data["systems"][0]["identity"]["identifier"] == identifier, "Response details empty Identifier."
            assert model in data["systems"][0]["definition"]["model"], "Response details incorrect Model."

            totalLinks = len(data["systems"][0]["links"])
            assert totalLinks > 0, "Empty list of Links returned."

        else:
            print("\nNo System UUID returned in REST response")
            print(data["message"])

def getComponentByComponentUUID():
    subIndex = 0
    compIndex = 0
    versionIndex = 0
    compList = []
    # url = 'http://' + host + ':19080/rcm-fitness-api/api/system/definition/'
    urlSec = 'https://' + hostTLS + ':19080/rcm-fitness-api/api/system/definition/'
    # resp = requests.get(url)
    # resp = requests.get(urlSec, verify='/usr/local/share/ca-certificates/hennet1.cpsd.dell.ca.crt')
    resp = requests.get(urlSec, verify=False)
    data = json.loads(resp.text)

    groupIndex = linkIndex = totalGroups = 0
    totalEndpoints = totalSubSystems = totalComponents = totalLinks = 0

    print("Requesting UUID from System Definition....")
    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    # url = 'http://' + host + ':19080/rcm-fitness-api/api/system/definition/' + systemUUID + '/component/'
    urlSec = 'https://' + hostTLS + ':19080/rcm-fitness-api/api/system/definition/' + systemUUID + '/component/'

    # resp = requests.get(url)
    resp = requests.get(urlSec, verify=False)
    dataInput = json.loads(resp.text)

    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    totalComponents = len(dataInput["components"])

    try:
        if data != "" and totalComponents > 0:
            while compIndex < totalComponents:
                print("Here now....1")
                global compUUID
                global compList
                compUUID = dataInput["components"][compIndex]["uuid"]
                compList.append(compUUID)
                # print("Component UUID: %s" % compUUID)
                compIndex += 1
        print("\nComponent List length: %d" % len(compList))
        print("List of Component UUIDs:")
        for i in compList:
            print(i)
            # return compList

    except Exception as e:
        print("Unexpected error: " + str(e))
        # print(response)
        traceback.print_exc()
        raise Exception(e)

    assert ("components") in dataInput.keys(), "Components not included in published attributes."
    assert ("systemUuid") in dataInput.keys(), "System UUID not included in published attributes."
    compListIndex = 0

    while compListIndex < len(compList):
        compIndexUUID = 0
        # url = 'http://' + host + ':19080/rcm-fitness-api/api/system/definition/' + systemUUID + '/component/' + compList[compListIndex]
        urlSec = 'https://' + hostTLS + ':19080/rcm-fitness-api/api/system/definition/' + systemUUID + '/component/' + compList[compListIndex]
        # resp = requests.get(url)
        resp = requests.get(urlSec, verify=False)
        data = json.loads(resp.text)

        print("\nRequesting a systems specific details ....")
        print(urlSec)
        assert resp.status_code == 200, "Request has not been acknowledged as expected."

        if data != "":
            if data["systemUuid"] != "":
                print("Here now....2")
                with open(path + 'rcmComponentByComponentUUID-VxRack.json', 'w') as outfile:
                    json.dump(data, outfile, sort_keys=True, indent=4, ensure_ascii=False)

                assert data["systemUuid"] == systemUUID, "Response did not detail the expected system UUID."

                assert len(data["components"]) == 1, "Unexpected number of components listed."

                print("\nTotal components: %d" % len(data["components"]))
                print("UUID: %s" % data["components"][compIndexUUID]["uuid"])
                # print(data["components"][compIndexUUID]["parentGroupUuids"])
                # print(dataInput["components"][compListIndex]["parentGroupUuids"])
                # print("\n")
                # print("\nExtracting groupUUID from response....\n")

                # while compIndexUUID < len(data["components"]):
                #     print(compIndexUUID)
                #     #if data["components"][compIndex]["definition"]["modelFamily"] == series:
                assert data["components"][compIndexUUID]["parentGroupUuids"] == dataInput["components"][compListIndex][
                    "parentGroupUuids"], "Response includes unexpected group ID."
                print("System level Parent Group: %s" % data["components"][compIndexUUID]["parentGroupUuids"])
                print("Component level Parent Group: %s" % dataInput["components"][compListIndex]["parentGroupUuids"])
                assert data["components"][compIndexUUID]["definition"]["productFamily"] == \
                       dataInput["components"][compListIndex]["definition"][
                           "productFamily"], "Response includes unexpected Product Family."
                print(
                "System level Product Family: %s" % data["components"][compIndexUUID]["definition"]["productFamily"])
                print("Component level Product Family: %s" % dataInput["components"][compListIndex]["definition"][
                    "productFamily"])
                assert data["components"][compIndexUUID]["definition"]["modelFamily"] == \
                       dataInput["components"][compListIndex]["definition"][
                           "modelFamily"], "Response includes unexpected Model Family."
                print("System level Model Family: %s" % data["components"][compIndexUUID]["definition"]["modelFamily"])
                print("Component level Model Family: %s" % dataInput["components"][compListIndex]["definition"][
                    "modelFamily"])
                assert data["components"][compIndexUUID]["definition"]["model"] == \
                       dataInput["components"][compListIndex]["definition"][
                           "model"], "Response includes unexpected Model."
                print("System level Model: %s" % data["components"][compIndexUUID]["definition"]["model"])
                print("Component level Model: %s" % dataInput["components"][compListIndex]["definition"]["model"])
                assert data["components"][compIndexUUID]["identity"]["identifier"] == \
                       dataInput["components"][compListIndex]["identity"][
                           "identifier"], "Response includes unexpected Identifier."
                print("System level Identifier: %s" % data["components"][compIndexUUID]["identity"]["identifier"])
                print(
                "Component level Identifier: %s" % dataInput["components"][compListIndex]["identity"]["identifier"])
                assert data["components"][compIndexUUID]["identity"]["elementType"] == \
                       dataInput["components"][compListIndex]["identity"][
                           "elementType"], "Response includes unexpected Identifier."
                assert len(data["components"][compIndexUUID]["endpoints"]) == len(
                    dataInput["components"][compListIndex]["endpoints"]), "Response includes unexpected endpoints."

            else:
                print("\nNo system returned in REST response.")
                print(data["message"])
        compListIndex += 1
        compIndex += 1


#
# def getComponentByInvalidComponentUUID():
#
# def getComponentNullUUID():
@pytest.mark.rcm_fitness_mvp_extended
def test_getSysDef1():
    getSystemDefinition("VXRACKFLEX", "VCESYSTEM", "VXRACK", "FLEX", "1000")

@pytest.mark.rcm_fitness_mvp_extended
def test_getSysDef2():
    getSystemDefinitionByUUID("VXRACKFLEX", "VCESYSTEM", "VXRACK", "FLEX", "1000", systemUUID)

@pytest.mark.rcm_fitness_mvp_extended
def test_getSysDef3():
    getComponentBySystemUUID("VCENTER", "VCENTER", "VCENTER", "VCENTER-WINDOWS", "VCENTER-WINDOWS", 1, systemUUID)

@pytest.mark.rcm_fitness_mvp_extended
def test_getSysDef4():
    getComponentBySystemUUID("VCENTER", "VCENTER", "VCENTER", "VCENTER-APPLIANCE-CUSTOMER", "VCENTER-WINDOWS", 2, systemUUID)

#family, series, type, tag, model, endpoints, sysUUID
@pytest.mark.rcm_fitness_mvp_extended
def test_getSysDef5():
    getComponentBySystemUUID("SCALEIO", "SCALEIO", "SCALEIO", "SCALEIO-1", "SCALEIO", 1, systemUUID)

@pytest.mark.rcm_fitness_mvp_extended
def test_getSysDef6():
    getComponentBySystemUUID("VCENTER", "VCENTER", "VCENTER", "VCENTER-APPLIANCE", "VCENTER-APPLIANCE", 1, systemUUID)

@pytest.mark.rcm_fitness_mvp_extended
def test_getSysDef7():
    getComponentBySystemUUID("POWEREDGE", "630", "SERVER", "0a:d8", "R630", 1, systemUUID)

@pytest.mark.rcm_fitness_mvp_extended
def test_getSysDef8():
    getComponentBySystemUUID("POWEREDGE", "730", "SERVER", "e0:b8", "R730XD", 1, systemUUID)

@pytest.mark.rcm_fitness_mvp_extended
def test_getSysDefInvalid9():
    getSystemDefinitionInvalidUUID(systemUUID[:8])

@pytest.mark.rcm_fitness_mvp_extended
def test_getSysDefInvalid10():
    getSystemDefinitionInvalidUUID("1111")

@pytest.mark.rcm_fitness_mvp_extended
def test_getCompByCompUUID10():
    getComponentByComponentUUID()

@pytest.mark.rcm_fitness_mvp_extended
def test_getSysDef11():
     getComponentBySystemUUID("NEXUS","N3K","SWITCH","SLB-TAF-3164A","3164Q",1,systemUUID)

@pytest.mark.rcm_fitness_mvp_extended
def test_getSysDef12():
    getComponentBySystemUUID("NEXUS", "N3K", "SWITCH", "SLB-TAF-3164B", "3164Q", 1, systemUUID)

@pytest.mark.rcm_fitness_mvp_extended
def test_getSysDef13():
    getComponentBySystemUUID("NEXUS", "N3K", "SWITCH", "SLB-TAF-3172TQ", "3172TQ", 1, systemUUID)

@pytest.mark.rcm_fitness_mvp_extended
def test_getSysDef14():
    getComponentBySystemUUID("NEXUS", "N3K", "SWITCH", "SLB-TAF-3132A", "3132QX", 1, systemUUID)

@pytest.mark.rcm_fitness_mvp_extended
def test_getSysDef15():
    getComponentBySystemUUID("NEXUS", "N3K", "SWITCH", "SLB-TAF-93180A", "93180YC-EX", 1, systemUUID)

@pytest.mark.rcm_fitness_mvp_extended
def test_getSysDef16():
    getComponentBySystemUUID("NEXUS", "N3K", "SWITCH", "SLB-TAF-9332A", "9332PQ", 1, systemUUID)

