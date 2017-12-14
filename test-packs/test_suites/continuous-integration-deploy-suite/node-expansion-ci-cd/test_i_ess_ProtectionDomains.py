#!/usr/bin/python
# Author: russed5
# Revision: 1.0
# Code Reviewed by:
# Description: Testing the ability to change the state of nodes in the Node disocvery postgres DB
#
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information
#

import af_support_tools
import json
import os
import pytest
import time

@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    import cpsd
    global cpsd

    global FIXTURES_PATH
    FIXTURES_PATH = "/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/essProtectionDomains/"
    
##############################################################################################

@pytest.mark.daily_status
@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_requestNoWarnings():
    """ Verify that a request message which prompts no warnings is handled correctly"""

    # ARRANGE
    #
    filePath = os.environ[
        'AF_TEST_SUITE_PATH'] + FIXTURES_PATH + 'requestNoWarnings.json'
    with open(filePath) as fixture:
        request_body = json.loads(fixture.read())

    # Create & bind the test queue called testQueue to the ESS response queue
    bindQueues("exchange.dell.cpsd.service.ess.response", "ess.service.response.#")

    error_list = []

    # ACT
    # query the ESS and consume the response
    sendRequestMessageToESS(request_body)
    time.sleep(5)
    essRsp = consumeResponseMessageFromESS()

    print('********** test_requestNoWarnings *******************')
    print(essRsp)
    print('*****************************************************')

    # ASSERT
    # verify the response data, the order of the data is critical
    if essRsp['validProtectionDomains'][0]['protectionDomainID'] != "d0000000001":
        error_list.append("Error :wrong PD identified")
    if (essRsp['validProtectionDomains'][0]['recommendedMessages']):
        error_list.append("Error :wrong recommendation given for  d0000000001")
    if essRsp['validProtectionDomains'][0]['warningMessages']:
        error_list.append("Error :wrong warning given for  d0000000001")

    if essRsp['validProtectionDomains'][1]['protectionDomainID'] != "d0000000002":
        error_list.append("Error :wrong PD identified")
    if (essRsp['validProtectionDomains'][1]['recommendedMessages']):
        error_list.append("Error :wrong recommendation given for  d0000000002")
    if essRsp['validProtectionDomains'][1]['warningMessages']:
        error_list.append("Error :wrong warning given for  d0000000002")

    if essRsp['validProtectionDomains'][2]['protectionDomainID'] != "d0000000003":
        error_list.append("Error :wrong PD identified")
    if (essRsp['validProtectionDomains'][2]['recommendedMessages']):
        error_list.append("Error :wrong recommendation given for  d0000000003")
    if essRsp['validProtectionDomains'][2]['warningMessages']:
        error_list.append("Error :wrong warning given for  d0000000003")

    assert not error_list

##############################################################################################

@pytest.mark.daily_status
@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_requestBreaksReq1():
    """ Verify that a request message with a pd already identified returns an error """

    # ARRANGE
    #
    filePath = os.environ[
        'AF_TEST_SUITE_PATH'] + FIXTURES_PATH + 'requestBreaksReq1.json'
    with open(filePath) as fixture:
        request_body = json.loads(fixture.read())

    # Create & bind the test queue called testQueue to the ESS response queue
    bindQueues("exchange.dell.cpsd.service.ess.response", "ess.service.response.#")

    error_list = []

    # ACT
    # query the ESS and consume the response
    sendRequestMessageToESS(request_body)
    time.sleep(5)
    essRsp = consumeResponseMessageFromESS()

    print('********** test_requestBreaksReq1 *******************')
    print(essRsp)
    print('*****************************************************')

    # ASSERT
    # verify the response data, the order of the data is critical
    if "REQUIRED" not in essRsp['errorMessage']['message']:
        error_list.append("Error : An error message should have been raised")
    if essRsp['validProtectionDomains']:
        error_list.append("Error : No PDs should be valid")

        assert not error_list

##############################################################################################

@pytest.mark.dne_paqx_parent_mvp_extended
def test_requestBreaksWarn1():
    """ Verify that a request message which breaks the rule for warning #1 is handled correctly
         1e. protection domian has nodes of a different type to the query node"""

    # ARRANGE
    #
    filePath = os.environ[
        'AF_TEST_SUITE_PATH'] + FIXTURES_PATH + 'requestBreaksWarn1.json'
    with open(filePath) as fixture:
        request_body = json.loads(fixture.read())

    # Create & bind the test queue called testQueue to the ESS response queue
    bindQueues("exchange.dell.cpsd.service.ess.response", "ess.service.response.#")

    error_list = []

    # ACT
    # query the ESS and consume the response
    sendRequestMessageToESS(request_body)
    time.sleep(5)
    essRsp = consumeResponseMessageFromESS()

    print('********** test_requestBreaksWarn1 *******************')
    print(essRsp)
    print('*****************************************************')

    # ASSERT
    # verify the response data, the order of the data is critical
    if essRsp['validProtectionDomains'][0]['protectionDomainID'] != "d0000000001":
        error_list.append("Error :wrong PD identified")
    if (essRsp['validProtectionDomains'][0]['recommendedMessages']):
        error_list.append("Error :wrong recommendation given for  d0000000001")
    if essRsp['validProtectionDomains'][0]['warningMessages']:
        error_list.append("Error :wrong warning given for  d0000000001")

    if essRsp['validProtectionDomains'][1]['protectionDomainID'] != "d0000000003":
        error_list.append("Error :wrong PD identified")
    if (essRsp['validProtectionDomains'][1]['recommendedMessages']):
        error_list.append("Error :wrong recommendation given for  d0000000003")
    if essRsp['validProtectionDomains'][1]['warningMessages']:
        error_list.append("Error :wrong warning given for  d0000000003")

    if essRsp['validProtectionDomains'][2]['protectionDomainID'] != "d0000000002":
        error_list.append("Error :wrong PD identified")
    if (essRsp['validProtectionDomains'][2]['recommendedMessages']):
        error_list.append("Error :wrong recommendation given for  d0000000002")
    if "must be of the same type" not in  essRsp['validProtectionDomains'][2]['warningMessages'][0]['message']:
        error_list.append("Error :wrong warning given for  d0000000002")

    assert not error_list

#######################################################################################

@pytest.mark.daily_status
@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_requestBreaksWarn2():
    """ Verify that a request message which breaks the rule for warning #2 is handled correctly
        ie. protection domain has less then 10 nodes"""

    # ARRANGE
    #
    filePath = os.environ[
        'AF_TEST_SUITE_PATH'] + FIXTURES_PATH + 'requestBreaksWarn2.json'
    with open(filePath) as fixture:
        request_body = json.loads(fixture.read())

    # Create & bind the test queue called testQueue to the ESS response queue
    bindQueues("exchange.dell.cpsd.service.ess.response", "ess.service.response.#")

    error_list = []

    # ACT
    # query the ESS and consume the response
    sendRequestMessageToESS(request_body)
    time.sleep(5)
    essRsp = consumeResponseMessageFromESS()

    print('********** test_requestBreaksWarn2 *******************')
    print(essRsp)
    print('*****************************************************')

    # ASSERT
    # verify the response data, the order of the data is critical
    if essRsp['validProtectionDomains'][0]['protectionDomainID'] != "d0000000002":
        error_list.append("Error :wrong PD identified")
    if (essRsp['validProtectionDomains'][0]['recommendedMessages']):
        error_list.append("Error :wrong recommendation given for  d0000000002")
    if essRsp['validProtectionDomains'][0]['warningMessages']:
        error_list.append("Error :wrong warning given for  d0000000002")

    if essRsp['validProtectionDomains'][1]['protectionDomainID'] != "d0000000003":
        error_list.append("Error :wrong PD identified")
    if (essRsp['validProtectionDomains'][1]['recommendedMessages']):
        error_list.append("Error :wrong recommendation given for  d0000000003")
    if essRsp['validProtectionDomains'][1]['warningMessages']:
        error_list.append("Error :wrong warning given for  d0000000003")

    if essRsp['validProtectionDomains'][2]['protectionDomainID'] != "d0000000001":
        error_list.append("Error :wrong PD identified")
    if (essRsp['validProtectionDomains'][2]['recommendedMessages']):
        error_list.append("Error :wrong recommendation given for  d0000000001")
    if "No Less than 10 nodes" not in  essRsp['validProtectionDomains'][2]['warningMessages'][0]['message']:
        error_list.append("Error :wrong warning given for  d0000000001")

    assert not error_list

#######################################################################################

@pytest.mark.dne_paqx_parent_mvp_extended
def test_requestBreaksWarn3():
    """ Verify that a request message which breaks the rule for warning #3 is handled correctly
        ie. protection domain has more then 30 nodes"""

    # ARRANGE
    #
    filePath = os.environ[
        'AF_TEST_SUITE_PATH'] + FIXTURES_PATH + 'requestBreaksWarn3.json'
    with open(filePath) as fixture:
        request_body = json.loads(fixture.read())

    # Create & bind the test queue called testQueue to the ESS response queue
    bindQueues("exchange.dell.cpsd.service.ess.response", "ess.service.response.#")

    error_list = []

    # ACT
    # query the ESS and consume the response
    sendRequestMessageToESS(request_body)
    time.sleep(5)
    essRsp = consumeResponseMessageFromESS()

    print('********** test_requestBreaksWarn3 *******************')
    print(essRsp)
    print('*****************************************************')

    # ASSERT
    # verify the response data, the order of the data is critical
    if essRsp['validProtectionDomains'][0]['protectionDomainID'] != "d0000000001":
        error_list.append("Error :wrong PD identified")
    if (essRsp['validProtectionDomains'][0]['recommendedMessages']):
        error_list.append("Error :wrong recommendation given for  d0000000001")
    if essRsp['validProtectionDomains'][0]['warningMessages']:
        error_list.append("Error :wrong warning given for  d0000000001")

    if essRsp['validProtectionDomains'][1]['protectionDomainID'] != "d0000000002":
        error_list.append("Error :wrong PD identified")
    if (essRsp['validProtectionDomains'][1]['recommendedMessages']):
        error_list.append("Error :wrong recommendation given for  d0000000002")
    if essRsp['validProtectionDomains'][1]['warningMessages']:
        error_list.append("Error :wrong warning given for  d0000000002")

    if essRsp['validProtectionDomains'][2]['protectionDomainID'] != "d0000000003":
        error_list.append("Error :wrong PD identified")
    if (essRsp['validProtectionDomains'][2]['recommendedMessages']):
        error_list.append("Error :wrong recommendation given for  d0000000003")
    if "No more than 30 nodes" not in  essRsp['validProtectionDomains'][2]['warningMessages'][0]['message']:
        error_list.append("Error :wrong warning given for  d0000000003")

    assert not error_list

#######################################################################################

@pytest.mark.dne_paqx_parent_mvp_extended
def test_requestBreaksRec1():
    """ Verify that a request message which breaks the rule for recomendation #1 is handled correctly
        ie. protection domain has 25 nodes"""

    # ARRANGE
    #
    filePath = os.environ[
        'AF_TEST_SUITE_PATH'] + FIXTURES_PATH + 'requestBreaksRec1.json'
    with open(filePath) as fixture:
        request_body = json.loads(fixture.read())

    # Create & bind the test queue called testQueue to the ESS response queue
    bindQueues("exchange.dell.cpsd.service.ess.response", "ess.service.response.#")

    error_list = []

    # ACT
    # query the ESS and consume the response
    sendRequestMessageToESS(request_body)
    time.sleep(5)
    essRsp = consumeResponseMessageFromESS()

    print('********** test_requestBreaksRec1 *******************')
    print(essRsp)
    print('*****************************************************')

    # ASSERT
    # verify the response data, the order of the data is critical
    if essRsp['validProtectionDomains'][0]['protectionDomainID'] != "d0000000002":
        error_list.append("Error :wrong PD identified")
    if (essRsp['validProtectionDomains'][0]['recommendedMessages']):
        error_list.append("Error :wrong recommendation given for  d0000000002")
    if essRsp['validProtectionDomains'][0]['warningMessages']:
        error_list.append("Error :wrong warning given for  d0000000002")

    if essRsp['validProtectionDomains'][1]['protectionDomainID'] != "d0000000003":
        error_list.append("Error :wrong PD identified")
    if (essRsp['validProtectionDomains'][1]['recommendedMessages']):
        error_list.append("Error :wrong recommendation given for  d0000000003")
    if essRsp['validProtectionDomains'][1]['warningMessages']:
        error_list.append("Error :wrong warning given for  d0000000003")

    if essRsp['validProtectionDomains'][2]['protectionDomainID'] != "d0000000001":
        error_list.append("Error :wrong PD identified")
    if "16 nodes per protection domain" not in (essRsp['validProtectionDomains'][2]['recommendedMessages'][0]['message']):
        error_list.append("Error :wrong recommendation given for  d0000000001")
    if essRsp['validProtectionDomains'][2]['warningMessages']:
        error_list.append("Error :wrong warning given for  d0000000001")

    assert not error_list

#######################################################################################

@pytest.mark.dne_paqx_parent_mvp_extended
def test_requestBreaksReq1Warn1Single():
    """ Verify that a request message which breaks req#1 (no pd already) assigned
        and breaks warn #1 (wrong type) is handled correctly """

    # ARRANGE
    #
    filePath = os.environ[
        'AF_TEST_SUITE_PATH'] + FIXTURES_PATH + 'requestBreaksReq1Warn1Single.json'
    with open(filePath) as fixture:
        request_body = json.loads(fixture.read())

    # Create & bind the test queue called testQueue to the ESS response queue
    bindQueues("exchange.dell.cpsd.service.ess.response", "ess.service.response.#")

    error_list = []

    # ACT
    # query the ESS and consume the response
    sendRequestMessageToESS(request_body)
    time.sleep(5)
    essRsp = consumeResponseMessageFromESS()

    print('********** test_requestBreaksReq1Warn1Single *******************')
    print(essRsp)
    print('*****************************************************')

    # ASSERT
    # verify the response data, the order of the data is critical
    if "REQUIRED" not in essRsp['errorMessage']['message']:
        error_list.append("Error : An error message should have been raised")
    if essRsp['validProtectionDomains']:
        error_list.append("Error : No PDs should be valid")

    assert not error_list

#######################################################################################

@pytest.mark.dne_paqx_parent_mvp_extended
def test_requestBreaksWarn1Warn2Single():
    """ Verify that a request message which breaks rwarn#1 (nwrong type) assigned
        and breaks warn #2 (less then 10 nodes) is handled correctly """

    # ARRANGE
    #
    filePath = os.environ[
        'AF_TEST_SUITE_PATH'] + FIXTURES_PATH + 'requestBreaksWarn1Warn2Single.json'
    with open(filePath) as fixture:
        request_body = json.loads(fixture.read())

    # Create & bind the test queue called testQueue to the ESS response queue
    bindQueues("exchange.dell.cpsd.service.ess.response", "ess.service.response.#")

    error_list = []

    # ACT
    # query the ESS and consume the response
    sendRequestMessageToESS(request_body)
    time.sleep(5)
    essRsp = consumeResponseMessageFromESS()

    print('********** test_requestBreaksWarn1Warn2Single *******************')
    print(essRsp)
    print('*****************************************************')

    # ASSERT
    # verify the response data, the order of the data is critical
    if essRsp['validProtectionDomains'][0]['protectionDomainID'] != "d0000000001":
        error_list.append("Error :wrong PD identified")
    if (essRsp['validProtectionDomains'][0]['recommendedMessages']):
        error_list.append("Error :wrong recommendation given for  d0000000001")
    if "No Less than 10 nodes" not in essRsp['validProtectionDomains'][0]['warningMessages'][0]['message']:
        error_list.append("Error :wrong warning given for  d0000000001")
    if "must be of the same type" not in essRsp['validProtectionDomains'][0]['warningMessages'][1]['message']:
        error_list.append("Error :wrong warning given for  d0000000001")

    assert not error_list

#######################################################################################

@pytest.mark.dne_paqx_parent_mvp_extended
def test_requestBreaksWarn1Rec1Single():
    """ Verify that a request message which breaks warn#1 (nwrong type assigned)
        and breaks rec #1 (25 nodes cuirrently) is handled correctly """

    # ARRANGE
    #
    filePath = os.environ[
        'AF_TEST_SUITE_PATH'] + FIXTURES_PATH + 'requestBreaksWarn1Rec1Single.json'
    with open(filePath) as fixture:
        request_body = json.loads(fixture.read())

    # Create & bind the test queue called testQueue to the ESS response queue
    bindQueues("exchange.dell.cpsd.service.ess.response", "ess.service.response.#")

    error_list = []

    # ACT
    # query the ESS and consume the response
    sendRequestMessageToESS(request_body)
    time.sleep(5)
    essRsp = consumeResponseMessageFromESS()

    print('********** test_requestBreaksWarn1Rec1Single *******************')
    print(essRsp)
    print('*****************************************************')

    # ASSERT
    # verify the response data, the order of the data is critical
    if essRsp['validProtectionDomains'][0]['protectionDomainID'] != "d0000000001":
        error_list.append("Error :wrong PD identified")
    if "16 nodes per protection domain" not in (essRsp['validProtectionDomains'][0]['recommendedMessages'][0]['message']):
        error_list.append("Error :wrong recommendation given for  d0000000001")
    if "must be of the same type" not in essRsp['validProtectionDomains'][0]['warningMessages'][0]['message']:
        error_list.append("Error :wrong warning given for  d0000000001")

    assert not error_list

#######################################################################################

@pytest.mark.dne_paqx_parent_mvp_extended
def test_requestBreaksWarn1Warn3Single():
    """ Verify that a request message which breaks warn#1 (wrong type assigned)
        and breaks warn #3 (more then 30 nodes) is handled correctly """

    # ARRANGE
    #
    filePath = os.environ[
        'AF_TEST_SUITE_PATH'] + FIXTURES_PATH + 'requestBreaksWarn1Warn3Single.json'
    with open(filePath) as fixture:
        request_body = json.loads(fixture.read())

    # Create & bind the test queue called testQueue to the ESS response queue
    bindQueues("exchange.dell.cpsd.service.ess.response", "ess.service.response.#")

    error_list = []

    # ACT
    # query the ESS and consume the response
    sendRequestMessageToESS(request_body)
    time.sleep(5)
    essRsp = consumeResponseMessageFromESS()

    print('********** test_requestBreaksWarn1Warn3Single *******************')
    print(essRsp)
    print('*****************************************************')

    # ASSERT
    # verify the response data, the order of the data is critical
    if essRsp['validProtectionDomains'][0]['protectionDomainID'] != "d0000000001":
        error_list.append("Error :wrong PD identified")
    if (essRsp['validProtectionDomains'][0]['recommendedMessages']):
        error_list.append("Error :wrong recommendation given for  d0000000001")
    if "No more than 30 nodes" not in essRsp['validProtectionDomains'][0]['warningMessages'][0]['message']:
        error_list.append("Error :wrong warning given for  d0000000001")
    if "must be of the same type" not in essRsp['validProtectionDomains'][0]['warningMessages'][1]['message']:
        error_list.append("Error :wrong warning given for  d0000000001")

    assert not error_list

#######################################################################################

@pytest.mark.dne_paqx_parent_mvp_extended
def test_requestBreaksWarn1Warn2Multi():
    """ Verify that a request message which breaks warn#1 (wrong type assigned) for PD1
        and breaks warn #3 (more then 30 nodes) for PD2 is handled correctly """

    # ARRANGE
    #
    filePath = os.environ[
        'AF_TEST_SUITE_PATH'] + FIXTURES_PATH + 'requestBreaksWarn1Warn2Multi.json'
    with open(filePath) as fixture:
        request_body = json.loads(fixture.read())

    # Create & bind the test queue called testQueue to the ESS response queue
    bindQueues("exchange.dell.cpsd.service.ess.response", "ess.service.response.#")

    error_list = []

    # ACT
    # query the ESS and consume the response
    sendRequestMessageToESS(request_body)
    time.sleep(5)
    essRsp = consumeResponseMessageFromESS()

    print('********** test_requestBreaksWarn1Warn2Multi *******************')
    print(essRsp)
    print('*****************************************************')

    # ASSERT
    # verify the response data, the order of the data is critical
    if essRsp['validProtectionDomains'][0]['protectionDomainID'] != "d0000000001":
        error_list.append("Error :wrong PD identified")
    if (essRsp['validProtectionDomains'][0]['recommendedMessages']):
        error_list.append("Error :wrong recommendation given for  d0000000001")
    if "must be of the same type" not in essRsp['validProtectionDomains'][0]['warningMessages'][0]['message']:
        error_list.append("Error :wrong warning given for  d0000000001")

    if essRsp['validProtectionDomains'][1]['protectionDomainID'] != "d0000000002":
        error_list.append("Error :wrong PD identified")
    if (essRsp['validProtectionDomains'][1]['recommendedMessages']):
        error_list.append("Error :wrong recommendation given for  d0000000002")
    if "No Less than 10 nodes" not in essRsp['validProtectionDomains'][1]['warningMessages'][0]['message']:
        error_list.append("Error :wrong warning given for  d0000000002")

    assert not error_list

#######################################################################################

@pytest.mark.dne_paqx_parent_mvp_extended
def test_requestBreaksWarn1Rec1Multi():
    """ Verify that a request message which breaks warn#1 (wrong type assigned) for PD1
        and breaks rec#1 (count = 25 nodes) for PD2 is handled correctly """

    # ARRANGE
    #
    filePath = os.environ[
        'AF_TEST_SUITE_PATH'] + FIXTURES_PATH + 'requestBreaksWarn1Rec1Multi.json'
    with open(filePath) as fixture:
        request_body = json.loads(fixture.read())

    # Create & bind the test queue called testQueue to the ESS response queue
    bindQueues("exchange.dell.cpsd.service.ess.response", "ess.service.response.#")

    error_list = []

    # ACT
    # query the ESS and consume the response
    sendRequestMessageToESS(request_body)
    time.sleep(5)
    essRsp = consumeResponseMessageFromESS()

    print('********** test_requestBreaksWarn1Rec1Multi *******************')
    print(essRsp)
    print('*****************************************************')

    # ASSERT
    # verify the response data, the order of the data is critical
    if essRsp['validProtectionDomains'][0]['protectionDomainID'] != "d0000000002":
        error_list.append("Error :wrong PD identified")
    if "16 nodes per protection domain" not in (essRsp['validProtectionDomains'][0]['recommendedMessages'][0]['message']):
        error_list.append("Error :wrong recommendation given for  d0000000002")
    if essRsp['validProtectionDomains'][0]['warningMessages']:
        error_list.append("Error :wrong warning given for  d0000000002")

    if essRsp['validProtectionDomains'][1]['protectionDomainID'] != "d0000000001":
        error_list.append("Error :wrong PD identified")
    if (essRsp['validProtectionDomains'][1]['recommendedMessages']):
        error_list.append("Error :wrong recommendation given for  d0000000001")
    if "must be of the same type" not in (essRsp['validProtectionDomains'][1]['warningMessages'][0]['message']):
        error_list.append("Error :wrong warning given for  d0000000001")

    assert not error_list

#######################################################################################

@pytest.mark.dne_paqx_parent_mvp_extended
def test_requestBreaksWarn1Warn3Multi():
    """ Verify that a request message which breaks warn#1 (wrong type assigned) for PD1
        and breaks warn #3 (more then 30 nodes) for PD2 is handled correctly """

    # ARRANGE
    #
    filePath = os.environ[
        'AF_TEST_SUITE_PATH'] + FIXTURES_PATH + 'requestBreaksWarn1Warn3Multi.json'
    with open(filePath) as fixture:
        request_body = json.loads(fixture.read())

    # Create & bind the test queue called testQueue to the ESS response queue
    bindQueues("exchange.dell.cpsd.service.ess.response", "ess.service.response.#")

    error_list = []

    # ACT
    # query the ESS and consume the response
    sendRequestMessageToESS(request_body)
    time.sleep(5)
    essRsp = consumeResponseMessageFromESS()

    print('********** test_requestBreaksWarn1Warn3Multi *******************')
    print(essRsp)
    print('*****************************************************')

    # ASSERT
    # verify the response data, the order of the data is critical
    if essRsp['validProtectionDomains'][0]['protectionDomainID'] != "d0000000001":
        error_list.append("Error :wrong PD identified")
    if essRsp['validProtectionDomains'][0]['recommendedMessages']:
        error_list.append("Error :wrong recommendation given for  d0000000001")
    if "must be of the same type" not in (essRsp['validProtectionDomains'][0]['warningMessages'][0]['message']):
        error_list.append("Error :wrong warning given for  d0000000001")

    if essRsp['validProtectionDomains'][1]['protectionDomainID'] != "d0000000002":
        error_list.append("Error :wrong PD identified")
    if (essRsp['validProtectionDomains'][1]['recommendedMessages']):
        error_list.append("Error :wrong recommendation given for  d0000000002")
    if "No more than 30 nodes" not in (essRsp['validProtectionDomains'][1]['warningMessages'][0]['message']):
        error_list.append("Error :wrong warning given for  d0000000002")

    assert not error_list

#######################################################################################

@pytest.mark.dne_paqx_parent_mvp_extended
def test_requestBreaksWarn2Warn3Multi():
    """ Verify that a request message which breaks warn#2 (less then 10 nodes) for PD1
        and breaks warn #3 (more then 30 nodes) for PD2 is handled correctly """

    # ARRANGE
    #
    filePath = os.environ[
        'AF_TEST_SUITE_PATH'] + FIXTURES_PATH + 'requestBreaksWarn2Warn3Multi.json'
    with open(filePath) as fixture:
        request_body = json.loads(fixture.read())

    # Create & bind the test queue called testQueue to the ESS response queue
    bindQueues("exchange.dell.cpsd.service.ess.response", "ess.service.response.#")

    error_list = []

    # ACT
    # query the ESS and consume the response
    sendRequestMessageToESS(request_body)
    time.sleep(5)
    essRsp = consumeResponseMessageFromESS()

    print('********** test_requestBreaksWarn2Warn3Multi *******************')
    print(essRsp)
    print('*****************************************************')

    # ASSERT
    # verify the response data, the order of the data is critical
    if essRsp['validProtectionDomains'][0]['protectionDomainID'] != "d0000000001":
        error_list.append("Error :wrong PD identified")
    if essRsp['validProtectionDomains'][0]['recommendedMessages']:
        error_list.append("Error :wrong recommendation given for  d0000000001")
    if "No Less than 10 nodes" not in (essRsp['validProtectionDomains'][0]['warningMessages'][0]['message']):
        error_list.append("Error :wrong warning given for  d0000000001")

    if essRsp['validProtectionDomains'][1]['protectionDomainID'] != "d0000000002":
        error_list.append("Error :wrong PD identified")
    if (essRsp['validProtectionDomains'][1]['recommendedMessages']):
        error_list.append("Error :wrong recommendation given for  d0000000002")
    if "No more than 30 nodes" not in (essRsp['validProtectionDomains'][1]['warningMessages'][0]['message']):
        error_list.append("Error :wrong warning given for  d0000000002")

    assert not error_list

#######################################################################################

@pytest.mark.dne_paqx_parent_mvp_extended
def test_requestBreaksWarn2Rec1Multi():
    """ Verify that a request message which breaks warn#2 (less then 10 nodes) for PD1
        and breaks rec#1 (count = 25 nodes) for PD2 is handled correctly """

    # ARRANGE
    #
    filePath = os.environ[
        'AF_TEST_SUITE_PATH'] + FIXTURES_PATH + 'requestBreaksWarn2Rec1Multi.json'
    with open(filePath) as fixture:
        request_body = json.loads(fixture.read())

    # Create & bind the test queue called testQueue to the ESS response queue
    bindQueues("exchange.dell.cpsd.service.ess.response", "ess.service.response.#")

    error_list = []

    # ACT
    # query the ESS and consume the response
    sendRequestMessageToESS(request_body)
    time.sleep(5)
    essRsp = consumeResponseMessageFromESS()

    print('********** test_requestBreaksWarn2Rec1Multi *******************')
    print(essRsp)
    print('*****************************************************')

    # ASSERT
    # verify the response data, the order of the data is critical
    if essRsp['validProtectionDomains'][0]['protectionDomainID'] != "d0000000002":
        error_list.append("Error :wrong PD identified")
    if "16 nodes per protection domain" not in (essRsp['validProtectionDomains'][0]['recommendedMessages'][0]['message']):
        error_list.append("Error :wrong recommendation given for  d0000000002")
    if essRsp['validProtectionDomains'][0]['warningMessages']:
        error_list.append("Error :wrong warning given for  d0000000002")

    if essRsp['validProtectionDomains'][1]['protectionDomainID'] != "d0000000001":
        error_list.append("Error :wrong PD identified")
    if (essRsp['validProtectionDomains'][1]['recommendedMessages']):
        error_list.append("Error :wrong recommendation given for  d0000000001")
    if "No Less than 10 nodes" not in (essRsp['validProtectionDomains'][1]['warningMessages'][0]['message']):
        error_list.append("Error :wrong warning given for  d0000000001")

    assert not error_list

#######################################################################################

@pytest.mark.dne_paqx_parent_mvp_extended
def test_requestBreaksWarn3Rec1Multi():
    """ Verify that a request message which breaks warn#3 (more then 30 nodes) for PD1
        and breaks rec#1 (count = 25 nodes) for PD2 is handled correctly """

    # ARRANGE
    #
    filePath = os.environ[
        'AF_TEST_SUITE_PATH'] + FIXTURES_PATH + 'requestBreaksWarn3Rec1Multi.json'
    with open(filePath) as fixture:
        request_body = json.loads(fixture.read())

    # Create & bind the test queue called testQueue to the ESS response queue
    bindQueues("exchange.dell.cpsd.service.ess.response", "ess.service.response.#")

    error_list = []

    # ACT
    # query the ESS and consume the response
    sendRequestMessageToESS(request_body)
    time.sleep(5)
    essRsp = consumeResponseMessageFromESS()

    print('********** test_requestBreaksWarn3Rec1Multi *******************')
    print(essRsp)
    print('*****************************************************')

    # ASSERT
    # verify the response data, the order of the data is critical
    if essRsp['validProtectionDomains'][0]['protectionDomainID'] != "d0000000002":
        error_list.append("Error :wrong PD identified")
    if "16 nodes per protection domain" not in (essRsp['validProtectionDomains'][0]['recommendedMessages'][0]['message']):
        error_list.append("Error :wrong recommendation given for  d0000000002")
    if essRsp['validProtectionDomains'][0]['warningMessages']:
        error_list.append("Error :wrong warning given for  d0000000002")

    if essRsp['validProtectionDomains'][1]['protectionDomainID'] != "d0000000001":
        error_list.append("Error :wrong PD identified")
    if (essRsp['validProtectionDomains'][1]['recommendedMessages']):
        error_list.append("Error :wrong recommendation given for  d0000000001")
    if "No more than 30 nodes" not in (essRsp['validProtectionDomains'][1]['warningMessages'][0]['message']):
        error_list.append("Error :wrong warning given for  d0000000001")

    assert not error_list

#######################################################################################

@pytest.mark.daily_status
@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_requestBreaksWarn1Warn2Warn3Rec1Multi():
    """ Verify that a request message which breaks warn1 (wrong node type) for PD1,
        warn#2 (less then 10 nodes) for PD2
        and breaks warn #3 (more then 30 nodes) for PD3 is handled correctly """

    # ARRANGE
    #
    filePath = os.environ[
        'AF_TEST_SUITE_PATH'] + FIXTURES_PATH + 'requestBreaksWarn1Warn2Warn3Multi.json'
    with open(filePath) as fixture:
        request_body = json.loads(fixture.read())

    # Create & bind the test queue called testQueue to the ESS response queue
    bindQueues("exchange.dell.cpsd.service.ess.response", "ess.service.response.#")

    error_list = []

    # ACT
    # query the ESS and consume the response
    sendRequestMessageToESS(request_body)
    time.sleep(5)
    essRsp = consumeResponseMessageFromESS()

    print('********** test_requestBreaksWarn1Warn2Warn3Multi *******************')
    print(essRsp)
    print('*****************************************************')

    # ASSERT
    # verify the response data, the order of the data is critical
    if essRsp['validProtectionDomains'][0]['protectionDomainID'] != "d0000000001":
        error_list.append("Error :wrong PD identified")
    if essRsp['validProtectionDomains'][0]['recommendedMessages']:
        error_list.append("Error :wrong recommendation given for  d0000000001")
    if "must be of the same type" not in (essRsp['validProtectionDomains'][0]['warningMessages'][0]['message']):
        error_list.append("Error :wrong warning given for  d0000000001")

    if essRsp['validProtectionDomains'][1]['protectionDomainID'] != "d0000000002":
        error_list.append("Error :wrong PD identified")
    if (essRsp['validProtectionDomains'][1]['recommendedMessages']):
        error_list.append("Error :wrong recommendation given for  d0000000002")
    if "No Less than 10 nodes" not in (essRsp['validProtectionDomains'][1]['warningMessages'][0]['message']):
        error_list.append("Error :wrong warning given for  d0000000002")

    if essRsp['validProtectionDomains'][2]['protectionDomainID'] != "d0000000003":
        error_list.append("Error :wrong PD identified")
    if (essRsp['validProtectionDomains'][2]['recommendedMessages']):
        error_list.append("Error :wrong recommendation given for  d0000000003")
    if "No more than 30 nodes" not in (essRsp['validProtectionDomains'][2]['warningMessages'][0]['message']):
        error_list.append("Error :wrong warning given for  d0000000003")

    assert not error_list

#######################################################################################

@pytest.mark.daily_status
@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_requestBreaksWarn1Warn2Warn3Rec1Multi():
    """ Verify that a request message which breaks warn1 (wrong node type) for PD1,
        warn#2 (less then 10 nodes) for PD2,
        breaks warn #3 (more then 30 nodes) for PD3
        and triggers recommendation#1 (node count = 25) is handled correctly """

    # ARRANGE
    #
    filePath = os.environ[
        'AF_TEST_SUITE_PATH'] + FIXTURES_PATH + 'requestBreaksWarn1Warn2Warn3Rec1Multi.json'
    with open(filePath) as fixture:
        request_body = json.loads(fixture.read())

    # Create & bind the test queue called testQueue to the ESS response queue
    bindQueues("exchange.dell.cpsd.service.ess.response", "ess.service.response.#")

    error_list = []

    # ACT
    # query the ESS and consume the response
    sendRequestMessageToESS(request_body)
    time.sleep(5)
    essRsp = consumeResponseMessageFromESS()

    print('********** test_requestBreaksWarn1Warn2Warn3Rec1Multi *******************')
    print(essRsp)
    print('*****************************************************')

    # ASSERT
    # verify the response data, the order of the data is critical

    if essRsp['validProtectionDomains'][0]['protectionDomainID'] != "d0000000004":
        error_list.append("Error :wrong PD identified")
    if "16 nodes per protection domain" not in (essRsp['validProtectionDomains'][0]['recommendedMessages'][0]['message']):
        error_list.append("Error :wrong recommendation given for  d0000000004")
    if essRsp['validProtectionDomains'][0]['warningMessages']:
        error_list.append("Error :wrong warning given for  d0000000004")

    if essRsp['validProtectionDomains'][1]['protectionDomainID'] != "d0000000001":
        error_list.append("Error :wrong PD identified")
    if essRsp['validProtectionDomains'][1]['recommendedMessages']:
        error_list.append("Error :wrong recommendation given for  d0000000001")
    if "must be of the same type" not in (essRsp['validProtectionDomains'][1]['warningMessages'][0]['message']):
        error_list.append("Error :wrong warning given for  d0000000001")

    if essRsp['validProtectionDomains'][2]['protectionDomainID'] != "d0000000002":
        error_list.append("Error :wrong PD identified")
    if (essRsp['validProtectionDomains'][2]['recommendedMessages']):
        error_list.append("Error :wrong recommendation given for  d0000000002")
    if "No Less than 10 nodes" not in (essRsp['validProtectionDomains'][2]['warningMessages'][0]['message']):
        error_list.append("Error :wrong warning given for  d0000000002")

    if essRsp['validProtectionDomains'][3]['protectionDomainID'] != "d0000000003":
        error_list.append("Error :wrong PD identified")
    if (essRsp['validProtectionDomains'][3]['recommendedMessages']):
        error_list.append("Error :wrong recommendation given for  d0000000003")
    if "No more than 30 nodes" not in (essRsp['validProtectionDomains'][3]['warningMessages'][0]['message']):
        error_list.append("Error :wrong warning given for  d0000000003")

    assert not error_list

#######################################################################################

@pytest.mark.dne_paqx_parent_mvp_extended
def test_requestPDListEmpty():
    """ Verify that a request message with no pd list included """

    # ARRANGE
    #
    filePath = os.environ[
        'AF_TEST_SUITE_PATH'] + FIXTURES_PATH + 'requestPDListEmpty.json'
    with open(filePath) as fixture:
        request_body = json.loads(fixture.read())

    # Create & bind the test queue called testQueue to the ESS response queue
    bindQueues("exchange.dell.cpsd.service.ess.response", "ess.service.response.#")

    error_list = []

    # ACT
    # query the ESS and consume the response
    sendRequestMessageToESS(request_body)
    time.sleep(5)
    essRsp = consumeResponseMessageFromESS()

    print('********** test_requestPDListEmpty *******************')
    print(essRsp)
    print('*****************************************************')

    # ASSERT
    # verify the response data, the order of the data is critical
    if (essRsp['validProtectionDomains']):
        error_list.append("Error : No valid protection domains should be listed as none were submitted")

    assert not error_list

#########################################################################################

@pytest.mark.dne_paqx_parent_mvp_extended
def test_requestNoNodesListed():
    """ Verify that a request message with no nodes in the PD list is handled correctly """

    # ARRANGE
    #
    filePath = os.environ[
        'AF_TEST_SUITE_PATH'] + FIXTURES_PATH + 'requestNoNodesListed.json'
    with open(filePath) as fixture:
        request_body = json.loads(fixture.read())

    # Create & bind the test queue called testQueue to the ESS response queue
    bindQueues("exchange.dell.cpsd.service.ess.response", "ess.service.response.#")

    error_list = []

    # ACT
    # query the ESS and consume the response
    sendRequestMessageToESS(request_body)
    time.sleep(5)
    essRsp = consumeResponseMessageFromESS()

    print('********** test_requestNoNodesListed *******************')
    print(essRsp)
    print('*****************************************************')

    # ASSERT
    # verify the response data, the order of the data is critical
    if essRsp['validProtectionDomains'][0]['protectionDomainID'] != "d0000000001":
        error_list.append("Error :wrong PD identified")
    if essRsp['validProtectionDomains'][0]['recommendedMessages']:
        error_list.append("Error :wrong recommendation given for  d0000000001")
    if "No Less than 10 nodes" not in (essRsp['validProtectionDomains'][0]['warningMessages'][0]['message']):
        error_list.append("Error :wrong warning given for  d0000000001")

    assert not error_list

#########################################################################################

def sendRequestMessageToESS(my_payload):
    """ Use the AMQP bus to send a Request message to the ESS.
    """

    my_exchange = "exchange.dell.cpsd.service.ess.request"
    my_routing_key = "ess.service.request"
    my_type_id = "com.dell.cpsd.list.protection.domain.validate.request"

    try:
        # publish the AMQP message
        af_support_tools.rmq_publish_message(host='amqp', port=5671, ssl_enabled=True,
                                         exchange=my_exchange,
                                         routing_key=my_routing_key,
                                         headers={'__TypeId__': my_type_id},
                                         payload=json.dumps(my_payload))
        return None

    except Exception as err:
        # Return code error
        print(err, '\n')
        raise Exception(err)

##############################################################################################

def consumeResponseMessageFromESS():
    """ Consume the ESS Response message """
    ess_response = ""
    ess_response = af_support_tools.rmq_consume_message(host='amqp', port=5671, ssl_enabled=True,
                                                          queue='testQueue')
    Qcleanup()

    if ess_response :
        # Convert the returned message to json format
        ess_message = json.loads(ess_response, encoding='utf-8')
        return ess_message
    else :
        return None

##############################################################################################

def bindQueues(exchangeName, routeName):
    """
    :param exchangeName:
    :param routeName:
    :return:
    Create & bind the test queue called testQueue"""

    af_support_tools.rmq_bind_queue(host='amqp', port=5671, ssl_enabled=True,
                                    queue='testQueue',
                                    exchange=exchangeName,
                                    routing_key=routeName)

##############################################################################################

def Qcleanup():
    """ Delete the test queue """
    print('Cleaning up testQueue...')
    af_support_tools.rmq_delete_queue(host='amqp', port=5671, ssl_enabled=True, queue='testQueue')

##############################################################################################

