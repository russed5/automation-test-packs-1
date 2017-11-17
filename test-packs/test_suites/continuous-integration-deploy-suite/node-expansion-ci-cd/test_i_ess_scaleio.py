#!/usr/bin/python
# Author:
# Revision:
# Code Reviewed by:
# Description: Testing the ESS rules for ScaleIO Storage Pools.

#
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information
#

import af_support_tools
import pytest
import json
import time
import os
import uuid


##############################################################################################

@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    import cpsd
    global cpsd

    global my_routing_key
    my_routing_key = 'ess.service.request.' + str(uuid.uuid4())


#####################################################################
# These are the exepected rules
# Warnings:
# “The storage device {0} is already present in storage pool {1}.”
# Errors:
# “No storage pool assigned to device: {0}”,
# “No storage pool found containing all SSDs and disk count < 300.”,
# “No storage pool found containing all SSDs.”,
# “No storage pool found with disk count < 300."

#####################################################################

@pytest.mark.daily_status
@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_validateScaleIO_StoragePool_ESS_msg_1():
    '''
    2 Storage pools - 1 @ 300 & SSD; 1 @ 150 & SSD
    5 New Disks
    Expect: 5 Disks to be added to valid pool;
            1 Warning message

    :return:
    '''
    cleanupQ('test.ess.service.response')
    bindQueue('exchange.dell.cpsd.service.ess.response', 'test.ess.service.response')

    filePath = os.environ[
                   'AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/ess_StoragePools/ess_scaleioInfo_1.json'

    with open(filePath) as fixture:
        my_payload = fixture.read()

    print("Send validate ScaleIO request message ...\n")
    simulate_validateScaleIORequest_message(my_payload, my_routing_key);

    print("Consume validate scaleIO response message ...\n")
    responseMsg = consumeResponse()
    print(responseMsg)

    error_list = []
    if responseMsg['deviceToStoragePoolMap']['003']['storagePoolId'] != '74ff6005valid':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['003']['storagePoolName'] != 'Pool-2-Valid':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['003']['deviceId'] != '003':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['004']['storagePoolId'] != '74ff6005valid':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['004']['storagePoolName'] != 'Pool-2-Valid':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['004']['deviceId'] != '004':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['004']['deviceName'] != 'Device-4':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['005']['storagePoolId'] != '74ff6005valid':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['005']['storagePoolName'] != 'Pool-2-Valid':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['005']['deviceId'] != '005':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['006']['storagePoolId'] != '74ff6005valid':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['006']['storagePoolName'] != 'Pool-2-Valid':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['005']['deviceName'] != 'Device-5':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['006']['deviceId'] != '006':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['007']['storagePoolId'] != '74ff6005valid':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['007']['storagePoolName'] != 'Pool-2-Valid':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['007']['deviceId'] != '007':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['warnings'][0][
        'message'] != 'REQUIRED: The size of Pool-1-Invalid storage pool must be between 0 and 299 devices. -- StoragePool : Pool-1-Invalid with 300 devices failed rule checking.':
        error_list.append('Error :Warning returned')

    assert not error_list

    cleanupQ('test.ess.service.response')


@pytest.mark.daily_status
@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_validateScaleIO_StoragePool_ESS_msg_2():
    '''
    2 Storage pools - 1 @ 190 & HDD; 1 @ 150 & HDD
    5 New Disks
    Expect: No Disks to be added;
            No Warning message;
            Error 'No storage pool found containing all SSDs'

    :return:
    '''

    cleanupQ('test.ess.service.response')
    bindQueue('exchange.dell.cpsd.service.ess.response', 'test.ess.service.response')

    filePath = os.environ[
                   'AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/ess_StoragePools/ess_scaleioInfo_2.json'

    with open(filePath) as fixture:
        my_payload = fixture.read()

    print("Send validate ScaleIO request message ...\n")
    simulate_validateScaleIORequest_message(my_payload, my_routing_key);

    print("Consume validate scaleIO response message ...\n")
    responseMsg = consumeResponse()
    print(responseMsg)

    error_list = []
    if responseMsg['deviceToStoragePoolMap']:
        error_list.append('Error :wrong storage pool identified')

    if responseMsg['warnings']:
        error_list.append('Error :Unexpected Warning returned')

    if responseMsg['errors'][0]['message'] != 'No storage pool found containing all SSDs.':
        error_list.append('Error :Unexpected Error returned')

    assert not error_list

    cleanupQ('test.ess.service.response')


@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_validateScaleIO_StoragePool_ESS_msg_3():
    '''
    1 Storage pools - 1 @ 150 & SSD;
    5 New Disks; 1 Disk already assigned to current Storage Pool
    Expect: 4 Disks to be added to valid pool;
            1 Warning message

    :return:
    '''
    cleanupQ('test.ess.service.response')
    bindQueue('exchange.dell.cpsd.service.ess.response', 'test.ess.service.response')

    filePath = os.environ[
                   'AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/ess_StoragePools/ess_scaleioInfo_3.json'

    with open(filePath) as fixture:
        my_payload = fixture.read()

    print("Send validate ScaleIO request message ...\n")
    simulate_validateScaleIORequest_message(my_payload, my_routing_key);

    print("Consume validate scaleIO response message ...\n")
    responseMsg = consumeResponse()
    print(responseMsg)

    error_list = []
    if responseMsg['deviceToStoragePoolMap']['004']['storagePoolId'] != '74ff6005valid':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['004']['storagePoolName'] != 'Pool-1':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['004']['deviceId'] != '004':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['004']['deviceName'] != 'Device-4':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['005']['storagePoolId'] != '74ff6005valid':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['005']['storagePoolName'] != 'Pool-1':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['005']['deviceId'] != '005':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['006']['storagePoolId'] != '74ff6005valid':
        error_list.append('Error :wrong storage pool identified')
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['006']['storagePoolName'] != 'Pool-1':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['005']['deviceName'] != 'Device-5':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['006']['deviceId'] != '006':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['007']['storagePoolId'] != '74ff6005valid':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['007']['storagePoolName'] != 'Pool-1':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['007']['deviceId'] != '007':
        error_list.append('Error :wrong storage pool identified')

    if responseMsg['errors']:
        error_list.append('Error :Unexpected Warning returned')

    if responseMsg['warnings'][0][
        'message'] != 'The storage device Device-1 is already present in storage pool Pool-1.':
        error_list.append('Error :Unexpected Error returned')

    assert not error_list

    cleanupQ('test.ess.service.response')


@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_validateScaleIO_StoragePool_ESS_msg_4():
    '''
    0 Storage pools;
    5 New Disks;
    Expect: 0 Disks to be added to valid pool;
            0 Warning
            1 Error message

    :return:
    '''
    cleanupQ('test.ess.service.response')
    bindQueue('exchange.dell.cpsd.service.ess.response', 'test.ess.service.response')

    filePath = os.environ[
                   'AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/ess_StoragePools/ess_scaleioInfo_4.json'

    with open(filePath) as fixture:
        my_payload = fixture.read()

    print("Send validate ScaleIO request message ...\n")
    simulate_validateScaleIORequest_message(my_payload, my_routing_key);

    print("Consume validate scaleIO response message ...\n")
    responseMsg = consumeResponse()
    print(responseMsg)

    error_list = []

    if responseMsg['warnings']:
        error_list.append('Error :Unexpected Warning returned')

    if responseMsg['errors'][0]['message'] != 'No Storage pools or new devices found in the request.':
        error_list.append('Error :Unexpected Error returned')

    assert not error_list

    cleanupQ('test.ess.service.response')


@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_validateScaleIO_StoragePool_ESS_msg_5():
    '''
    1 Storage pools - 1 @ 298 & SSD;
    5 New Disks
    Expect: 2 Disks to be added to valid pool;
            1 Error message

    :return:
    '''
    cleanupQ('test.ess.service.response')
    bindQueue('exchange.dell.cpsd.service.ess.response', 'test.ess.service.response')

    filePath = os.environ[
                   'AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/ess_StoragePools/ess_scaleioInfo_5.json'

    with open(filePath) as fixture:
        my_payload = fixture.read()

    print("Send validate ScaleIO request message ...\n")
    simulate_validateScaleIORequest_message(my_payload, my_routing_key);

    print("Consume validate scaleIO response message ...\n")
    responseMsg = consumeResponse()
    print(responseMsg)

    error_list = []
    if responseMsg['deviceToStoragePoolMap']['003']['storagePoolId'] != '74ff6005valid':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['003']['storagePoolName'] != 'Pool-1':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['003']['deviceId'] != '003':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['004']['storagePoolId'] != '74ff6005valid':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['004']['storagePoolName'] != 'Pool-1':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['004']['deviceId'] != '004':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['004']['deviceName'] != 'Device-4':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['errors'][0]['message'] != 'No storage pool assigned to device: Device-5':
        error_list.append('Error :Unexpected Error returned')
    if responseMsg['errors'][1]['message'] != 'No storage pool assigned to device: Device-6':
        error_list.append('Error :Unexpected Error returned')
    if responseMsg['errors'][2]['message'] != 'No storage pool assigned to device: Device-7':
        error_list.append('Error :Unexpected Error returned')

    assert not error_list

    cleanupQ('test.ess.service.response')


@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_validateScaleIO_StoragePool_ESS_msg_6():
    '''
    3 Storage pools - 1 @ 300 & SSD, 1 @ 150 & HDD; 1 @ 150 & SSD ;
    4 New Disks
    Expect: 4 Disks to be added to the valid pool;
            0 Error message
            1 Warning about Pool 1's size

    :return:
    '''
    cleanupQ('test.ess.service.response')
    bindQueue('exchange.dell.cpsd.service.ess.response', 'test.ess.service.response')

    filePath = os.environ[
                   'AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/ess_StoragePools/ess_scaleioInfo_6.json'

    with open(filePath) as fixture:
        my_payload = fixture.read()

    print("Send validate ScaleIO request message ...\n")
    simulate_validateScaleIORequest_message(my_payload, my_routing_key);

    print("Consume validate scaleIO response message ...\n")
    responseMsg = consumeResponse()
    print(responseMsg)

    error_list = []
    if responseMsg['deviceToStoragePoolMap']['004']['storagePoolId'] != '74ff6007valid':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['004']['deviceName'] != 'Device-4':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['005']['storagePoolId'] != '74ff6007valid':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['005']['deviceName'] != 'Device-5':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['006']['storagePoolId'] != '74ff6007valid':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['007']['storagePoolId'] != '74ff6007valid':
        error_list.append('Error :wrong storage pool identified')

    if responseMsg['errors']:
        error_list.append('Error :Unexpected Warning returned')

    if responseMsg['warnings'][0][
        'message'] != 'REQUIRED: The size of Pool-1 storage pool must be between 0 and 299 devices. -- StoragePool : Pool-1 with 301 devices failed rule checking.':
        error_list.append('Error :Warning returned')

    assert not error_list

    cleanupQ('test.ess.service.response')


@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_validateScaleIO_StoragePool_ESS_msg_7():
    '''
    3 Storage pools - 3 @ 299 & SSD;
    3 New Disks
    Expect: 3 Disks to be added to the each valid pool;
            0 Error message
            0 Warning

    :return:
    '''
    cleanupQ('test.ess.service.response')
    bindQueue('exchange.dell.cpsd.service.ess.response', 'test.ess.service.response')

    filePath = os.environ[
                   'AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/ess_StoragePools/ess_scaleioInfo_7.json'

    with open(filePath) as fixture:
        my_payload = fixture.read()

    print("Send validate ScaleIO request message ...\n")
    simulate_validateScaleIORequest_message(my_payload, my_routing_key);

    print("Consume validate scaleIO response message ...\n")
    responseMsg = consumeResponse()
    print(responseMsg)

    error_list = []
    if responseMsg['deviceToStoragePoolMap']['004']['storagePoolId'] != '74ff6005valid':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['004']['deviceName'] != 'Device-4':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['005']['storagePoolId'] != '74ff6006valid':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['005']['deviceName'] != 'Device-5':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['006']['storagePoolId'] != '74ff6007valid':
        error_list.append('Error :wrong storage pool identified')

    if responseMsg['errors']:
        error_list.append('Error :Unexpected Warning returned')

    if responseMsg['warnings']:
        error_list.append('Error :Warning returned')

    assert not error_list

    cleanupQ('test.ess.service.response')


@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_validateScaleIO_StoragePool_ESS_msg_8():
    '''
    3 Storage pools - 1 @ 100 & SSD; 1 @ 199 & HDD: 1 @ 300 & SDD
    12 New Disks
    Expect: 12 Disks to be added to the each valid pool;
            0 Error message
            1 Warning about Pool-3

    :return:
    '''
    cleanupQ('test.ess.service.response')
    bindQueue('exchange.dell.cpsd.service.ess.response', 'test.ess.service.response')

    filePath = os.environ[
                   'AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/ess_StoragePools/ess_scaleioInfo_8.json'

    with open(filePath) as fixture:
        my_payload = fixture.read()

    print("Send validate ScaleIO request message ...\n")
    simulate_validateScaleIORequest_message(my_payload, my_routing_key);

    print("Consume validate scaleIO response message ...\n")
    responseMsg = consumeResponse()
    print(responseMsg)

    error_list = []
    if responseMsg['deviceToStoragePoolMap']['004']['storagePoolId'] != '74ff6005valid':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['004']['storagePoolName'] != 'Pool-1':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['004']['deviceId'] != '004':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['004']['deviceName'] != 'Device-4':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['005']['storagePoolId'] != '74ff6005valid':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['005']['storagePoolName'] != 'Pool-1':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['005']['deviceId'] != '005':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['005']['deviceName'] != 'Device-5':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['006']['storagePoolId'] != '74ff6005valid':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['006']['storagePoolName'] != 'Pool-1':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['006']['deviceId'] != '006':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['007']['storagePoolId'] != '74ff6005valid':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['007']['storagePoolName'] != 'Pool-1':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['007']['deviceId'] != '007':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['008']['storagePoolId'] != '74ff6005valid':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['008']['storagePoolName'] != 'Pool-1':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['008']['deviceId'] != '008':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['009']['storagePoolId'] != '74ff6005valid':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['009']['storagePoolName'] != 'Pool-1':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['009']['deviceId'] != '009':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['0010']['storagePoolId'] != '74ff6005valid':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['0010']['storagePoolName'] != 'Pool-1':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['0010']['deviceId'] != '0010':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['0015']['storagePoolId'] != '74ff6005valid':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['0015']['storagePoolName'] != 'Pool-1':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['0015']['deviceId'] != '0015':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['0016']['storagePoolId'] != '74ff6005valid':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['0016']['storagePoolName'] != 'Pool-1':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['0016']['deviceId'] != '0016':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['0017']['storagePoolId'] != '74ff6005valid':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['0017']['storagePoolName'] != 'Pool-1':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['0017']['deviceId'] != '0017':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['0018']['storagePoolId'] != '74ff6005valid':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['0018']['storagePoolName'] != 'Pool-1':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['0018']['deviceId'] != '0018':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['0019']['storagePoolId'] != '74ff6005valid':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['0019']['storagePoolName'] != 'Pool-1':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['0019']['deviceId'] != '0019':
        error_list.append('Error :wrong storage pool identified')

    if responseMsg['errors']:
        error_list.append('Error :Unexpected Warning returned')

    if responseMsg['warnings'][0][
        'message'] != 'REQUIRED: The size of Pool-3 storage pool must be between 0 and 299 devices. -- StoragePool : Pool-3 with 301 devices failed rule checking.':
        error_list.append('Error :Warning returned')

    assert not error_list

    cleanupQ('test.ess.service.response')


@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_validateScaleIO_StoragePool_ESS_msg_9():
    '''
    1 Storage pools - 1 @ 350 & SSD;
    3 New Disks
    Expect: 0 Disks to be added to the pool;
            1 Error message
            1 Warning about Pool-1

    :return:
    '''
    cleanupQ('test.ess.service.response')
    bindQueue('exchange.dell.cpsd.service.ess.response', 'test.ess.service.response')

    filePath = os.environ[
                   'AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/ess_StoragePools/ess_scaleioInfo_9.json'

    with open(filePath) as fixture:
        my_payload = fixture.read()

    print("Send validate ScaleIO request message ...\n")
    simulate_validateScaleIORequest_message(my_payload, my_routing_key);

    print("Consume validate scaleIO response message ...\n")
    responseMsg = consumeResponse()
    print(responseMsg)

    error_list = []

    if responseMsg['errors'][0]['message'] != 'No storage pool found with disk count < 300.':
        error_list.append('Error :Unexpected Error returned')

    if responseMsg['warnings'][0][
        'message'] != 'REQUIRED: The size of Pool-1 storage pool must be between 0 and 299 devices. -- StoragePool : Pool-1 with 350 devices failed rule checking.':
        error_list.append('Error :Warning returned')

    assert not error_list

    cleanupQ('test.ess.service.response')


@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_validateScaleIO_StoragePool_ESS_msg_10():
    '''
    1 Storage pools - 1 @ 300 & HDD;
    3 New Disks
    Expect: 0 Disks to be added to the pool;
            1 Error message
            1 Warning about Pool-1

    :return:
    '''
    cleanupQ('test.ess.service.response')
    bindQueue('exchange.dell.cpsd.service.ess.response', 'test.ess.service.response')

    filePath = os.environ[
                   'AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/ess_StoragePools/ess_scaleioInfo_10.json'

    with open(filePath) as fixture:
        my_payload = fixture.read()

    print("Send validate ScaleIO request message ...\n")
    simulate_validateScaleIORequest_message(my_payload, my_routing_key);

    print("Consume validate scaleIO response message ...\n")
    responseMsg = consumeResponse()
    print(responseMsg)

    error_list = []

    if responseMsg['errors'][0]['message'] != 'No storage pool found containing all SSDs.':
        error_list.append('Error :Unexpected Error returned')

    if responseMsg['warnings'][0][
        'message'] != 'REQUIRED: The size of Pool-1 storage pool must be between 0 and 299 devices. -- StoragePool : Pool-1 with 301 devices failed rule checking.':
        error_list.append('Error :Warning returned')

    assert not error_list

    cleanupQ('test.ess.service.response')


@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_validateScaleIO_StoragePool_ESS_msg_11():
    '''
    1 Storage pools - 1 @ 300 & HDD;
    3 New Disks
    Expect: 0 Disks to be added to the pool;
            1 Error message
            1 Warning about Pool-1

    :return:
    '''
    cleanupQ('test.ess.service.response')
    bindQueue('exchange.dell.cpsd.service.ess.response', 'test.ess.service.response')

    filePath = os.environ[
                   'AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/ess_StoragePools/ess_scaleioInfo_11.json'

    with open(filePath) as fixture:
        my_payload = fixture.read()

    print("Send validate ScaleIO request message ...\n")
    simulate_validateScaleIORequest_message(my_payload, my_routing_key);

    print("Consume validate scaleIO response message ...\n")
    responseMsg = consumeResponse()
    print(responseMsg)

    error_list = []

    if responseMsg['errors'][0]['message'] != 'No storage pool found containing all SSDs and disk count < 300.':
        error_list.append('Error :Unexpected Error returned')

    if responseMsg['warnings'][0][
        'message'] != 'REQUIRED: The size of Pool-1 storage pool must be between 0 and 299 devices. -- StoragePool : Pool-1 with 301 devices failed rule checking.':
        error_list.append('Error :Warning returned')

    assert not error_list

    cleanupQ('test.ess.service.response')


@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_validateScaleIO_StoragePool_ESS_msg_12():
    '''
    1 Storage pools - 1 @ 300 & HDD;
    3 New Disks
    Expect: 0 Disks to be added to the pool;
            1 Error message
            1 Warning about Pool-1

    :return:
    '''
    cleanupQ('test.ess.service.response')
    bindQueue('exchange.dell.cpsd.service.ess.response', 'test.ess.service.response')

    filePath = os.environ[
                   'AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/ess_StoragePools/ess_scaleioInfo_12.json'

    with open(filePath) as fixture:
        my_payload = fixture.read()

    print("Send validate ScaleIO request message ...\n")
    simulate_validateScaleIORequest_message(my_payload, my_routing_key);

    print("Consume validate scaleIO response message ...\n")
    responseMsg = consumeResponse()
    print(responseMsg)

    error_list = []

    if responseMsg['errors'][0]['message'] != 'No Storage pools or new devices found in the request.':
        error_list.append('Error :Unexpected Error returned')

    if responseMsg['warnings']:
        error_list.append('Error :Warning returned')

    assert not error_list

    cleanupQ('test.ess.service.response')


@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_validateScaleIO_StoragePool_ESS_msg_13():
    '''
    0 Storage pools;
    2 New Disks
    Expect: 2 Disks to be added to the pool;
            0 Error message
            0 Warning messages

    :return:
    '''
    cleanupQ('test.ess.service.response')
    bindQueue('exchange.dell.cpsd.service.ess.response', 'test.ess.service.response')

    filePath = os.environ[
                   'AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/ess_StoragePools/ess_scaleioInfo_13.json'

    with open(filePath) as fixture:
        my_payload = fixture.read()

    print("Send validate ScaleIO request message ...\n")
    simulate_validateScaleIORequest_message(my_payload, my_routing_key);

    print("Consume validate scaleIO response message ...\n")
    responseMsg = consumeResponse()
    print(responseMsg)

    error_list = []

    if responseMsg['deviceToStoragePoolMap']['004']['storagePoolId'] != '74ff6005valid':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['004']['storagePoolName'] != 'Pool-1':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['004']['deviceId'] != '004':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['004']['deviceName'] != 'Device-4':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['005']['storagePoolId'] != '74ff6005valid':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['005']['storagePoolName'] != 'Pool-1':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['005']['deviceId'] != '005':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['005']['deviceName'] != 'Device-5':
        error_list.append('Error :wrong storage pool identified')

    if responseMsg['errors']:
        error_list.append('Error :Unexpected Error returned')

    if responseMsg['warnings']:
        error_list.append('Error :Warning returned')

    assert not error_list

    cleanupQ('test.ess.service.response')


@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_validateScaleIO_StoragePool_ESS_msg_14():
    '''
    0 Storage pools;
    4 New Disks (1 is < 90Gb)
    Expect: 3 Disks to be added to the pool;
            0 Error message
            1 Warning messages

    :return:
    '''
    cleanupQ('test.ess.service.response')
    bindQueue('exchange.dell.cpsd.service.ess.response', 'test.ess.service.response')

    filePath = os.environ[
                   'AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/ess_StoragePools/ess_scaleioInfo_14.json'

    with open(filePath) as fixture:
        my_payload = fixture.read()

    print("Send validate ScaleIO request message ...\n")
    simulate_validateScaleIORequest_message(my_payload, my_routing_key);

    print("Consume validate scaleIO response message ...\n")
    responseMsg = consumeResponse()
    print(responseMsg)

    error_list = []

    if responseMsg['deviceToStoragePoolMap']['001']['storagePoolId'] != '74ff6005valid':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['001']['storagePoolName'] != 'Pool-1':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['005']['storagePoolId'] != '74ff6005valid':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['005']['storagePoolName'] != 'Pool-1':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['005']['deviceId'] != '005':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['005']['deviceName'] != 'Device-5':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['006']['storagePoolId'] != '74ff6005valid':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['006']['storagePoolName'] != 'Pool-1':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['006']['deviceId'] != '006':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['006']['deviceName'] != 'Device-6':
        error_list.append('Error :wrong storage pool identified')
    if responseMsg['deviceToStoragePoolMap']['006']['serialNumber'] != 'SN-6':
        error_list.append('Error :wrong storage pool identified')

    if responseMsg['errors']:
        error_list.append('Error :Unexpected Error returned')

    if responseMsg['warnings'][0][
        'message'] != 'Could not allocate storage pool to device : SN-4 with capacity less than 90 GB.':
        error_list.append('Error : Invalid Warning returned')

    assert not error_list

    cleanupQ('test.ess.service.response')


#######################################################################################################################

def simulate_validateScaleIORequest_message(my_payload, my_routing_key):
    print(" Publishing a scaleio request message .. ")

    print(my_payload)
    af_support_tools.rmq_publish_message(host='amqp', port=5671, ssl_enabled=True,
                                         exchange='exchange.dell.cpsd.service.ess.request',
                                         routing_key=my_routing_key,
                                         headers={
                                             '__TypeId__': 'com.dell.cpsd.service.engineering.standards.EssValidateStoragePoolRequestMessage'},
                                         payload=my_payload,
                                         payload_type='json')


####################################################################################################
def consumeResponse():
    """ Consume the next message received on the testqueue and return the message in json format"""

    waitForMsg('test.ess.service.response')

    return_message = af_support_tools.rmq_consume_message(host='amqp', port=5671, ssl_enabled=True,
                                                          queue='test.ess.service.response')

    return_message = json.loads(return_message, encoding='utf-8')

    return return_message


####################################################################################################


def cleanupQ(testqueue):
    """ Delete the passed-in queue."""

    af_support_tools.rmq_delete_queue(host='amqp', port=5671, ssl_enabled=True, queue=testqueue)


def bindQueue(exchange, testqueue):
    """ Bind 'testqueue' to 'exchange'."""
    af_support_tools.rmq_bind_queue(host='amqp', port=5671, ssl_enabled=True,
                                    queue=testqueue, exchange=exchange, routing_key='#')


def waitForMsg(queue):
    # This function keeps looping untill a message is in the specified queue. We do need it to timeout and throw an error
    # if a message never arrives. Once a message appears in the queue the function is complete and main continues.

    print('Waiting for message')
    # The length of the queue, it will start at 0 but as soon as we get a response it will increase
    q_len = 0

    # Represents the number of seconds that have gone by since the method started
    timeout = 0

    # Max number of seconds to wait
    max_timeout = 15

    # Amount of time in seconds that the loop is going to wait on each iteration
    sleeptime = 10

    while q_len < 1:
        time.sleep(sleeptime)
        timeout += sleeptime

        q_len = af_support_tools.rmq_message_count(host='amqp', port=5671, ssl_enabled=True, queue=queue)

        if timeout > max_timeout:
            print('ERROR: Message took too long to return. Something is wrong')
            cleanupQ(queue)
            break
