# Copyright © 2017 Dell Inc. or its subsidiaries.  All Rights Reserved
import json
import requests
import pytest
import af_support_tools


@pytest.fixture(scope="module", autouse=True)
def load_test_data():
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

@pytest.fixture()
def sys():
    # url = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/system/definition/'
    # response = requests.get(url)
    urlSec = 'https://' + host + ':19080/rcm-fitness-api/api/system/definition/'
    response = requests.get(urlSec, verify=False)
    assert response.status_code == 200, "Request has not been acknowledged as expected."
    data = response.json()

    assert data["systems"][0]["uuid"] != ""
    print("\nExtracting systemUUID from response....\n")
    uuidlist = []
    for k, v in data.items():
        if isinstance(v, list):
            for system in v:
                uuidlist.append(system["uuid"])
                print(uuidlist)

    return uuidlist

@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.parametrize(("train", "version", "type", "model", "identifier"), [
    ("9.2", "9.2.1", "iDRAC", "630", "Integrated Remote Access Controller"),
    ("9.2", "9.2.1", "NIC", "630", "Intel(R) Gigabit 4P X520/I350 rNDC -"),
    ("9.2", "9.2.1", "NIC", "630", "Intel(R) Ethernet 10G 2P X520 Adapter -"),
    ("9.2", "9.2.1", "BIOS", "630", "BIOS"),
    ("9.2", "9.2.1", "NonRAID", "630", "Dell HBA330 Mini"),
    ("9.2", "9.2.1", "iDRAC", "730", "Integrated Remote Access Controller"),
    ("9.2", "9.2.1", "NIC", "730", "Intel(R) Ethernet 10G 4P X520/I350 rNDC -"),
    ("9.2", "9.2.1", "NIC", "730", "Intel(R) Ethernet 10G 2P X520 Adapter -"),
    ("9.2", "9.2.1", "BIOS", "730", "BIOS"),
    ("9.2", "9.2.1", "ESXI", "VCENTER", "lab.vce.com"),
    ("9.2", "9.2.1", "RAID", "730", "PERC H730 Mini"),
    ("9.2", "9.2.1", "VCENTER", "VCENTER-APPLIANCE", "VCENTER-APPLIANCE"),
    ("9.2", "9.2.1", "VCENTER", "VCENTER-WINDOWS", "VCENTER-WINDOWS"),
    ("9.2", "9.2.2", "BIOS", "630", "BIOS"),
    ("9.2", "9.2.3", "BIOS", "630", "BIOS"),
    ("9.2", "9.2.2", "BIOS", "730", "BIOS"),
    ("9.2", "9.2.3", "BIOS", "730", "BIOS"),
    ("9.2", "9.2.2", "RAID", "730", "PERC H730 Mini"),
    ("9.2", "9.2.3", "RAID", "730", "PERC H730 Mini"),
    ("9.2", "9.2.2", "ESXI", "VCENTER", "lab.vce.com"),
    ("9.2", "9.2.3", "ESXI", "VCENTER", "lab.vce.com"),
    ("3.2", "3.2.1", "BIOS", "630", "BIOS"),
    ("3.2", "3.2.1", "BIOS", "730", "BIOS"),
    ("3.2", "3.2.1", "NIC", "630", "Intel(R) Gigabit 4P X520/I350 rNDC -"),
    ("3.2", "3.2.1", "NIC", "630", "Intel(R) Ethernet 10G 2P X520 Adapter -"),
    ("3.2", "3.2.1", "iDRAC", "630", "Integrated Remote Access Controller"),
    ("3.2", "3.2.1", "ESXI", "VCENTER", "lab.vce.com"),
    ("3.2", "3.2.1", "SUB_ESXI", "VCENTER", "ixgbe"),
    ("3.2", "3.2.1", "VCENTER", "VCENTER-APPLIANCE", "VCENTER-APPLIANCE"),
    ("3.2", "3.2.1", "VCENTER", "VCENTER-WINDOWS", "VCENTER-WINDOWS"),
    ("3.2", "3.2.1", "RAID", "730", "PERC H730 Mini"),
    ("3.2", "3.2.1", "NonRAID", "630", "Dell HBA330 Mini"),
    ("3.2", "3.2.1", "PERCCLI", "R730XD", "PercCli SAS Customization Utility"),
    ("3.2", "3.2.1", "PERCCLI", "R630", "PercCli SAS Customization Utility"),
    ("3.2", "3.2.1", "SVM", "SCALEIO", "TB1"),
    ("3.2", "3.2.1", "SVM", "SCALEIO", "Manager2"),
    ("3.2", "3.2.1", "SCALEIO", "SCALEIO", "SCALEIO-1"),
    ("3.2", "3.2.1", "SVM", "SCALEIO", "lab.vce.com"),
    # ("3.2", "3.2.1", "SUB_ESXI", "VCENTER-APPLIANCE", "i40e"),
    # ("3.2", "3.2.1", "SUB_ESXI", "VCENTER-WINDOWS", "ScaleIO VM"),
    ("3.2", "3.2.2", "BIOS", "630", "BIOS"),
    ("3.2", "3.2.2", "BIOS", "730", "BIOS"),
    ("3.2", "3.2.2", "NIC", "630", "Intel(R) Gigabit 4P X520/I350 rNDC -"),
    ("3.2", "3.2.2", "NIC", "630", "Intel(R) Ethernet 10G 2P X520 Adapter -"),
    ("3.2", "3.2.2", "iDRAC", "630", "Integrated Remote Access Controller"),
    ("3.2", "3.2.2", "ESXI", "VCENTER", "lab.vce.com"),
    ("3.2", "3.2.2", "SUB_ESXI", "VCENTER", "ixgbe"),
    ("3.2", "3.2.2", "VCENTER", "VCENTER-APPLIANCE", "VCENTER-APPLIANCE"),
    ("3.2", "3.2.2", "VCENTER", "VCENTER-WINDOWS", "VCENTER-WINDOWS"),
    ("3.2", "3.2.2", "RAID", "730", "PERC H730 Mini"),
    ("3.2", "3.2.2", "NonRAID", "630", "Dell HBA330 Mini"),
    ("3.2", "3.2.2", "PERCCLI", "R730XD", "PercCli SAS Customization Utility"),
    ("3.2", "3.2.2", "PERCCLI", "R630", "PercCli SAS Customization Utility"),
    ("3.2", "3.2.2", "SVM", "SCALEIO", "TB1"),
    ("3.2", "3.2.2", "SVM", "SCALEIO", "Manager2"),
    ("3.2", "3.2.2", "SCALEIO", "SCALEIO", "SCALEIO-1"),
    ("3.2", "3.2.2", "SVM", "SCALEIO", "lab.vce.com"),
    # ("3.2", "3.2.2", "SUB_ESXI", "VCENTER-WINDOWS", "ScaleIO VM"),
    ("3.2", "3.2.3", "BIOS", "630", "BIOS"),
    ("3.2", "3.2.3", "BIOS", "730", "BIOS"),
    ("3.2", "3.2.3", "NIC", "630", "Intel(R) Gigabit 4P X520/I350 rNDC -"),
    ("3.2", "3.2.3", "NIC", "630", "Intel(R) Ethernet 10G 2P X520 Adapter -"),
    ("3.2", "3.2.3", "iDRAC", "630", "Integrated Remote Access Controller"),
    ("3.2", "3.2.3", "ESXI", "VCENTER", "lab.vce.com"),
    ("3.2", "3.2.3", "SUB_ESXI", "VCENTER", "ixgbe"),
    ("3.2", "3.2.3", "VCENTER", "VCENTER-APPLIANCE", "VCENTER-APPLIANCE"),
    ("3.2", "3.2.3", "VCENTER", "VCENTER-WINDOWS", "VCENTER-WINDOWS"),
    ("3.2", "3.2.3", "SVM", "SCALEIO", "TB1"),
    ("3.2", "3.2.3", "SVM", "SCALEIO", "Manager2"),
    ("3.2", "3.2.3", "SCALEIO", "SCALEIO", "SCALEIO-1"),
    ("3.2", "3.2.3", "SVM", "SCALEIO", "lab.vce.com"),
    ("3.2", "3.2.3", "NonRAID", "630", "Dell HBA330 Mini"),
    ("3.2", "3.2.3", "PERCCLI", "R730XD", "PercCli SAS Customization Utility"),
    ("3.2", "3.2.3", "PERCCLI", "R630", "PercCli SAS Customization Utility"),
    # ("3.2", "3.2.1", "SWITCH", "3172TQ", "KatSwitch"),
    # ("3.2", "3.2.2", "SWITCH", "3172TQ", "KatSwitch"),
    # ("3.2", "3.2.3", "SWITCH", "3172TQ", "KatSwitch"),
    ("3.2", "3.2.3", "RAID", "730", "PERC H730 Mini")])
    # ("3.2", "3.2.3", "SUB_ESXI", "VCENTER-WINDOWS", "ScaleIO VM")])
def test_post_eval(sys, train, version, type, model, identifier):
    # url = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/rcm/inventory/VxRack/1000 FLEX/' + train + '/' + version + '/'
    urlSec = 'https://' + host + ':19080/rcm-fitness-api/api/rcm/inventory/VxRack/1000 FLEX/' + train + '/' + version + '/'
    response = requests.get(urlSec, verify=False)
    # response = requests.get(urlSec, verify='/usr/local/share/ca-certificates/taf.cpsd.dell.ca.crt')

    assert response.status_code == 200, "Request has not been acknowledged as expected."
    data = response.json()
    rcmid = data["rcmInventoryItems"][0]["uuid"]

    # url = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/rcm/evaluation/'
    urlSec = 'https://' + host + ':19080/rcm-fitness-api/api/rcm/evaluation/'
    body = {'systemUuid': sys[0], 'rcmUuid': rcmid}
    data_json = json.dumps(body)
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    response = requests.post(urlSec, data_json, headers=headers, verify=False)
    data = response.json()

    assert response.status_code == 200, "Request has not been acknowledged as expected."
    evals = len(data['rcmEvaluationResults'])
    assert evals != 0, "Unexpected number of evaluation results found, has Collectcomponentversion been executed??"
    results = 0
    instances = 0

    while results < evals:
        if model in data['rcmEvaluationResults'][results]['evaluatedVersionDatum']['definition']['model'] and identifier in data['rcmEvaluationResults'][results]['evaluatedVersionDatum']['identity']['identifier']:
            assert model in data['rcmEvaluationResults'][results]['evaluatedVersionDatum']['definition'][
                'model'], "Model"
            assert identifier in data['rcmEvaluationResults'][results]['evaluatedVersionDatum']['identity'][
                'identifier'], "Identifier"
            if type in data['rcmEvaluationResults'][results]['evaluatedVersionDatum']['identity']['elementType']:
                assert data['rcmEvaluationResults'][results]['evaluatedVersionDatum']['identity'][
                           'elementType'] == type, "Type"
                assert data['rcmEvaluationResults'][results]['evaluatedRcmDatum']['rcmUuid'] == rcmid
                assert data['rcmEvaluationResults'][results]['evaluatedRcmDatum']['rcmTrain'] == train
                assert data['rcmEvaluationResults'][results]['evaluatedRcmDatum']['rcmVersion'] == version
                assert data['rcmEvaluationResults'][results]['elementUuid'] == \
                       data['rcmEvaluationResults'][results]['evaluatedVersionDatum']['componentUuid']
                if 'serialNumber' in data['rcmEvaluationResults'][results]['evaluatedVersionDatum']['identity']:
                    assert type in data['rcmEvaluationResults'][results]['evaluatedVersionDatum']['identity']['serialNumber']
                assert data['rcmEvaluationResults'][results]['evaluatedRcmDatum']['productFamily'] == \
                       data['rcmEvaluationResults'][results]['evaluatedVersionDatum']['definition']['productFamily']
                assert data['rcmEvaluationResults'][results]['evaluatedRcmDatum']['product'] == \
                       data['rcmEvaluationResults'][results]['evaluatedVersionDatum']['definition']['product']
                mFamily = data['rcmEvaluationResults'][results]['evaluatedRcmDatum']['modelFamily']
                mFamily = mFamily[1:]
                modelM = data['rcmEvaluationResults'][results]['evaluatedRcmDatum']['model']
                modelM = modelM[2:-2]
                assert mFamily in data['rcmEvaluationResults'][results]['evaluatedVersionDatum']['definition']['modelFamily']
                assert modelM in data['rcmEvaluationResults'][results]['evaluatedVersionDatum']['definition']['model']
                assert data['rcmEvaluationResults'][results]['evaluatedVersionDatum']['versions'][0]['version'] == \
                       data['rcmEvaluationResults'][results]['actualValue']
                assert data['rcmEvaluationResults'][results]['evaluatedRcmDatum']['versions'][0] == \
                       data['rcmEvaluationResults'][results]['expectedValues'][0]
                actual = data['rcmEvaluationResults'][results]['actualValue']
                expected = data['rcmEvaluationResults'][results]['expectedValues'][0]
                if expected in actual:
                    assert (data['rcmEvaluationResults'][results]['evaluationResult']) == "match", "Expect a match"

                else:
                    assert (
                           data['rcmEvaluationResults'][results]['evaluationResult']) == "mismatch", "Expect a mismatch"

                stripActual = actual.strip("0")
                stripExpected = expected.strip("0")
                if stripExpected in stripActual:
                    assert (data['rcmEvaluationResults'][results]['evaluationResult']) == "match", "Expect a match"
                else:
                    assert (
                           data['rcmEvaluationResults'][results]['evaluationResult']) == "mismatch", "Expect a mismatch"

                return
            instances += 1
            results += 1
        else:
            results += 1
            # continue


    assert False, "No Evaluation for this component"