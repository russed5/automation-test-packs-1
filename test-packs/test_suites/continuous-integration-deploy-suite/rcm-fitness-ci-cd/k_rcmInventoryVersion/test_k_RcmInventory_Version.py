#!/usr/bin/env python
import json
import pika
import sys
import logging
import requests
import pytest
import os
import re
import af_support_tools
from collections import Counter


@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    global path
    path = "/home/autouser/PycharmProjects/auto-framework/test_suites/continuous-integration-deploy-suite/rcm-fitness-ci-cd/restLevelTests/rcmInventory/"
    ensurePathExists(path)
    purgeOldOutput(path, "rcmDef")

    global ssl_options
    ssl_options = {"ca_certs":"/etc/rabbitmq/certs/testca/cacert.pem","certfile":"/etc/rabbitmq/certs/certs/client/cert.pem","keyfile":"/etc/rabbitmq/certs/certs/client/key.pem","cert_reqs":"ssl.CERT_REQUIRED","ssl_version":"ssl.PROTOCOL_TLSv1_2"}

    # Set config ini file name
    global env_file
    env_file = 'env.ini'

    global host
    host = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')

    ensurePathExists(path)
    purgeOldOutput(path, "rcmInventoryVer")

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


def getAvailableRCMs(family, model, train, version):
        # print(data)
    combo = str(family + "/" + model + "/" + train + "/" + version)
    href = []
    method = []
    rel = []
    option = "ORIGINAL"
    optionAdd = "ADDENDUM"
    optionManu = "MANUFACTURING"

    exception = "No rcm definitions for system family"
    # url = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/rcm/inventory/' + family + "/" + model + "/" + train + "/" + version + "/"
    urlSec = 'https://' + host + ':19080/rcm-fitness-api/api/rcm/inventory/' + family + "/" + model + "/" + train + "/" + version + "/"
    # resp = requests.get(url)
    resp = requests.get(urlSec, verify=False)
    data = json.loads(resp.text)
    rcm = data["rcmInventoryItems"]

    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    if data != "":
        if data["message"] == None:
            with open(path + 'rcmInventoryVersion.json', 'w') as outfile:
                json.dump(data, outfile, sort_keys=True, indent=4, ensure_ascii=False)

            assert len(rcm) > 0
            lastRCM = len(rcm)
            midRCM = (len(rcm))/2
            midRCM = int(midRCM)
            assert rcm[0]["rcmVersion"] == version
            assert rcm[(lastRCM-1)]["rcmVersion"] == version
            assert rcm[0]["rcmTrain"] == train
            assert rcm[(lastRCM-1)]["rcmTrain"] == train
            assert rcm[0]["systemModelFamily"] == model
            assert rcm[(lastRCM-1)]["systemModelFamily"] == model
            assert rcm[0]["systemProductFamily"] == family
            assert rcm[(lastRCM-1)]["systemProductFamily"] == family
            assert (rcm[0]["viewOption"] == option) or (rcm[0]["viewOption"] == optionAdd) or (rcm[0]["viewOption"] == optionManu)
            assert (rcm[(lastRCM-1)]["viewOption"] == option) or (rcm[(lastRCM-1)]["viewOption"] == optionAdd) or (rcm[(lastRCM-1)]["viewOption"] == optionManu)

            assert len(rcm[0]["links"]) > 0, "Empty list of Links returned."
            lenLinks = len(rcm[0]["links"])
            linkIndex = 0
            while linkIndex < lenLinks:
                href.append(rcm[0]["links"][linkIndex]["href"])
                method.append(rcm[0]["links"][linkIndex]["method"])
                rel.append(rcm[0]["links"][linkIndex]["rel"])
                assert rcm[0]["links"][linkIndex]["rel"] == "self" or "content", "Unexpected Rel value returned in link."
                assert rcm[0]["links"][linkIndex]["method"] == "GET", "Unexpected Method value returned in link."
                assert "/rcm/" in rcm[0]["links"][linkIndex]["href"], "Unexpected Href value returned in link."
                linkIndex += 1

            assert len(href) == len(set(href)), "Href links failed uniqueness check."
            assert len(method) != len(set(method)), "Method links failed uniqueness check."
            assert len(rel) == len(set(rel)), "Rel links failed uniqueness check."
            return

    assert False, "No rcm details returned: %s" % combo

def getAvailableRCMs_Invalid(family, model, train, version):
    # url = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/rcm/inventory/' + family + "/" + model + "/" + train + "/" + version + "/"
    # resp = requests.get(url)
    urlSec = 'https://' + host + ':19080/rcm-fitness-api/api/rcm/inventory/' + family + "/" + model + "/" + train + "/" + version + "/"
    resp = requests.get(urlSec, verify=False)
    data = json.loads(resp.text)
    rcm = data["rcmInventoryItems"]

    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    if not rcm:
        if ("message") in data.keys():
            assert ('RFCA1021I') in (data["message"]), "Returned Error Message does not reflect expected Error Code."
            assert (family) in (data["message"]), "Returned Error Message does not include expected Family."
            assert (model) in (data["message"]), "Returned Error Message does not include expected Model."
            assert (train) in (data["message"]), "Returned Error Message does not include expected Train."
            assert (version) in (data["message"]), "Returned Error Message does not include expected Version."


def getAvailableRCMs_Null(family, model, train, version):
    # url = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/rcm/inventory/' + family + "/" + model + "/" + train + '/' + version + '/'
    # resp = requests.get(url)
    urlSec = 'https://' + host + ':19080/rcm-fitness-api/api/rcm/inventory/' + family + "/" + model + "/" + train + '/' + version
    resp = requests.get(urlSec, verify=False)

    if family == "" and model == "" and train == "" and version == "":
        assert resp.status_code == 404, "Request has not been acknowledged as expected."
    elif family == "" and version != "":
        assert resp.status_code == 200, "Request has not been acknowledged as expected."
        data = json.loads(resp.text)
        assert "RFCA1019I No RCM definitions for system family" in data["message"], "Unexpected error response returned."
    elif family != "" and version == "":
        assert resp.status_code == 200, "Request has not been acknowledged as expected."
        data = json.loads(resp.text)
        assert len(data["rcmInventoryItems"]) >= 1, "Returned RCM items should be one or more."
        assert data["message"] is None, "Unexpected error response returned."
    else:
        assert resp.status_code == 200, "Request has not been acknowledged as expected."
        data = json.loads(resp.text)
        assert data["rcmInventoryItems"] is None, "Returned RCM items should be null."
        assert "RFCA1019I No RCM definitions for system family" in data["message"], "Unexpected error response returned."


@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.rcm_fitness_mvp
def test_getRCM1():
    getAvailableRCMs("VxRack", "1000 FLEX", "9.2", "9.2.1")
@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.rcm_fitness_mvp
def test_getRCM2():
    getAvailableRCMs("VxRack", "1000 FLEX", "9.2", "9.2.2")
@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.rcm_fitness_mvp
def test_getRCM3():
    getAvailableRCMs("VxRack", "1000 FLEX", "9.2", "9.2.3")
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCM4():
    getAvailableRCMs("VxRack", "1000 FLEX", "9.2", "9.2.1.1")
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCM5():
    getAvailableRCMs_Invalid("VxRack", "1000 FLEX", "9.2", "9.2.99")
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCM6():
    getAvailableRCMs_Invalid("VxRack", "1000 FLEX", "9.9", "9.2.1")
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCM7():
    getAvailableRCMs_Invalid("VxRack", "999", "9.2", "9.2.1")
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCM8():
    getAvailableRCMs_Null("VxRack", "1000 FLEX", "9.2", "")
# @pytest.mark.rcm_fitness_mvp_extended
# def test_getRCM9():
#     getAvailableRCMs_Null("VxRack", "1000 FLEX", "", "9.2.1")
# @pytest.mark.rcm_fitness_mvp_extended
# def test_getRCM10():
#     getAvailableRCMs_Null("VxRack", "", "9.2", "9.2.1")
# @pytest.mark.rcm_fitness_mvp_extended
# def test_getRCM11():
#     getAvailableRCMs_Null("", "1000 FLEX", "9.2", "9.2.1")
# @pytest.mark.rcm_fitness_mvp_extended
# def test_getRCM12():
#     getAvailableRCMs_Null("", "", "", "")
#@pytest.mark.TC546560_Empty
#def test_getRCM7():
#    getAvailableRCMs_Invalid("", "", "")
