#!/usr/bin/python
# Author:
# Revision:
# Code Reviewed by:
# Description: This is a setup scrip that will configure Symphony for DNE with a valid system definition file
#
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information

import af_support_tools
import os
import pytest
import json
import time
import requests


@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    import cpsd
    global cpsd

    # Update config ini files at runtime
    my_data_file = os.environ.get('AF_RESOURCES_PATH') + '/continuous-integration-deploy-suite/symphony-sds.properties'
    af_support_tools.set_config_file_property_by_data_file(my_data_file)

    # Update setup_config.ini file at runtime
    my_data_file = os.environ.get('AF_RESOURCES_PATH') + '/continuous-integration-deploy-suite/setup_config.properties'
    af_support_tools.set_config_file_property_by_data_file(my_data_file)


@pytest.fixture()
def setup():
    parameters = {}
    env_file = 'env.ini'

    ipaddress = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')
    cli_user = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='username')
    cli_password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                             property='password')

    parameters['IP'] = ipaddress
    parameters['user'] = cli_user
    parameters['password'] = cli_password

    # RackHD VM IP & Creds details. These will be used to register the Endpoints
    setup_config_file = 'continuous-integration-deploy-suite/setup_config.ini'
    setup_config_header = 'config_details'

    rackHD_IP = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                          heading=setup_config_header, property='rackhd_dne_ipaddress')

    rackHD_username = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                heading=setup_config_header, property='rackhd_username')

    rackHD_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                heading=setup_config_header, property='rackhd_password')

    # Vcenter VM IP & Creds details.
    vcenter_IP = af_support_tools.get_config_file_property(config_file=setup_config_file, heading=setup_config_header,
                                                           property='vcenter_dne_ipaddress_customer')

    vcenter_username = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                 heading=setup_config_header,
                                                                 property='vcenter_username')

    vcenter_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                 heading=setup_config_header,
                                                                 property='vcenter_password_fra')

    # ScaleIO VM IP & Creds details.
    scaleIO_IP = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                           heading=setup_config_header,
                                                           property='scaleio_integration_ipaddress')

    scaleIO_username = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                 heading=setup_config_header,
                                                                 property='scaleio_username')

    scaleIO_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                 heading=setup_config_header,
                                                                 property='scaleio_password')

    parameters['rackHD_IP'] = rackHD_IP
    parameters['rackHD_username'] = rackHD_username
    parameters['rackHD_password'] = rackHD_password
    parameters['rackHD_body'] = ':32080/ui/'
    parameters['vcenter_IP'] = vcenter_IP
    parameters['vcenter_username'] = vcenter_username
    parameters['vcenter_password'] = vcenter_password
    parameters['vcenter_port'] = '443'
    parameters['scaleIO_IP'] = scaleIO_IP
    parameters['scaleIO_username'] = scaleIO_username
    parameters['scaleIO_password'] = scaleIO_password

    return parameters


#####################################################################

@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_dne_setup_system(setup):
    """
    Description:    This script will configure a System with a json file.
    Parameters:     None
    Returns:        None
    """
    # Install dell-cpsd-amqp-rest-api
    time.sleep(2)
    assert install_amqpapi(setup), 'failed to install amqpapi'

    payload_file = 'continuous-integration-deploy-suite/symphony-sds.ini'
    payload_header = 'payload'
    payload_property_sys = 'sys_payload_node_exp'

    # Get the payload data from the config symphony-sds.ini file.
    the_payload = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                            property=payload_property_sys)

    assert api_addsystem(setup, the_payload), 'Error, System cont configured correctly'


@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_dne_RegisterRackHD(setup):
    assert registerRackHD(setup), 'Error: unable to register the RackHD endpoint'


@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_dne_RegisterVcenter(setup):
    assert registerVcenter(setup), 'Error: unable to register the vCenter endpoint'


@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_dne_RegisterScaleIO(setup):
    assert registerScaleIO(setup), 'Error: unable to register the ScaleIO endpoint'


#####################################################################

def install_amqpapi(setup):
    err = []

    amqpapi = "dell-cpsd-amqp-rest-api"

    sendcommand_install = "yum install -y " + amqpapi
    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                         password=setup['password'],
                                                         command=sendcommand_install, return_output=True)

    rpm_check = af_support_tools.check_for_installed_rpm(host=setup['IP'], username=setup['user'],
                                                         password=setup['password'],
                                                         rpm_name=amqpapi)

    if rpm_check != True:
        err.append(amqpapi + " did not install properly")
    # assert not err

    if err == []:
        return 1
    else:
        return 0


def api_addsystem(setup, the_payload):
    err = []

    api_url = 'http://' + setup['IP'] + ':5500/v1/amqp/system-definition/'

    # the_payload = af_support_tools.get_config_file_property(config_file=payload_file, heading= payload_header,
    #                                                       property= payload_property_amqp )

    sysadd = json.loads(the_payload)

    time.sleep(10)
    header = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    r = requests.post(api_url, headers=header, data=the_payload)
    resp = json.loads(r.text)

    ## Validating contents of json file and message returned from Rest API
    if resp == None:
        err.append("Error---System not added successfully")
    assert not err

    if sysadd["body"]["convergedSystem"]["identity"]["serialNumber"] != resp["body"]["convergedSystem"]["identity"][
        "serialNumber"]:
        err.append("Error---Correct Serial number not returned")
    assert not err

    if (sysadd["body"]["convergedSystem"]["components"][0] != resp["body"]["convergedSystem"]["components"][0] and
                sysadd["body"]["convergedSystem"]["components"][1] != resp["body"]["convergedSystem"]["components"][
                1] and
                sysadd["body"]["convergedSystem"]["components"][2] != resp["body"]["convergedSystem"]["components"][
                2] and
                sysadd["body"]["convergedSystem"]["components"][3] != resp["body"]["convergedSystem"]["components"][3]):
        err.append("Error---All Components are not added successfully")
    assert not err

    if err == []:
        return 1
    else:
        return 0


def registerRackHD(setup):
    # Until consul is  working properly & integrated with the rackhd adapter in the same environment we need to register
    # it manually by sending this message.  This test is a prerequisite to getting the full list of

    cleanup('test.controlplane.rackhd.response')
    cleanup('test.endpoint.registration.event')
    bindQueues('exchange.dell.cpsd.controlplane.rackhd.response', 'test.controlplane.rackhd.response')
    bindQueues('exchange.dell.cpsd.endpoint.registration.event', 'test.endpoint.registration.event')

    time.sleep(2)

    af_support_tools.rmq_purge_queue(host='amqp', port=5671, ssl_enabled=True,
                                     queue='test.controlplane.rackhd.response')

    af_support_tools.rmq_purge_queue(host='amqp', port=5671, ssl_enabled=True,
                                     queue='test.endpoint.registration.event')

    the_payload = '{"messageProperties":{"timestamp":"2017-06-14T12:00:00Z","correlationId":"manually-reg-rackhd-3fb0-9696-3f7d28e17f72"},"registrationInfo":{"address":"http://' + \
                  setup['rackHD_IP'] + setup['rackHD_body'] + '","username":"' + setup[
                      'rackHD_username'] + '","password":"' + setup['rackHD_password'] + '"}}'

    af_support_tools.rmq_publish_message(host='amqp', port=5671, ssl_enabled=True,
                                         exchange='exchange.dell.cpsd.controlplane.rackhd.request',
                                         routing_key='controlplane.rackhd.endpoint.register',
                                         headers={
                                             '__TypeId__': 'com.dell.cpsd.rackhd.registration.info.request'},
                                         payload=the_payload)

    # Verify the RackHD account can be validated
    assert waitForMsg('test.controlplane.rackhd.response'), 'Error: No RackHD validation message received'
    return_message = af_support_tools.rmq_consume_message(host='amqp', port=5671, ssl_enabled=True,
                                                          queue='test.controlplane.rackhd.response',
                                                          remove_message=True)

    return_json = json.loads(return_message, encoding='utf-8')
    print(return_json)
    assert return_json['responseInfo']['message'] == 'SUCCESS', 'ERROR: RackHD validation failure'

    # Verify that an event to register the rackHD with endpoint registry is triggered
    assert waitForMsg('test.endpoint.registration.event'), 'Error: No message to register with Consul sent by system'
    return_message = af_support_tools.rmq_consume_message(host='amqp', port=5671, ssl_enabled=True,
                                                          queue='test.endpoint.registration.event',
                                                          remove_message=True)

    return_json = json.loads(return_message, encoding='utf-8')
    print(return_json)

    endpointType = return_json['endpoint']['type']
    timeout = 0
    
    # We need to check that we received the registration msg for rackHd and not something else 
    while endpointType != 'rackhd' and timeout < 20:
        assert waitForMsg(
            'test.endpoint.registration.event'), 'Error: No message to register with Consul sent by system'
        return_message = af_support_tools.rmq_consume_message(host='amqp', port=5671, ssl_enabled=True,
                                                              queue='test.endpoint.registration.event',
                                                              remove_message=True)
        return_json = json.loads(return_message, encoding='utf-8')
        print(return_json)
        endpointType = return_json['endpoint']['type']
        timeout += 1

    assert return_json['endpoint']['type'] == 'rackhd', 'rackhd not registered with endpoint'
    cleanup('test.controlplane.rackhd.response')
    cleanup('test.endpoint.registration.event')

    print('rackHD registerd')

    time.sleep(3)
    return 1


def registerVcenter(setup):
    # Until consul is  working properly & integrated with the vcenter adapter in the same environment we need to register
    # it manually by sending this message.

    cleanup('test.controlplane.vcenter.response')
    cleanup('test.endpoint.registration.event')
    bindQueues('exchange.dell.cpsd.controlplane.vcenter.response', 'test.controlplane.vcenter.response')
    bindQueues('exchange.dell.cpsd.endpoint.registration.event', 'test.endpoint.registration.event')

    time.sleep(2)

    af_support_tools.rmq_purge_queue(host='amqp', port=5671, ssl_enabled=True,
                                     queue='test.controlplane.vcenter.response')

    af_support_tools.rmq_purge_queue(host='amqp', port=5671, ssl_enabled=True,
                                     queue='test.endpoint.registration.event')

    the_payload = '{"messageProperties":{"timestamp":"2010-01-01T12:00:00Z","correlationId":"vcenter-registtration-corr-id","replyTo":"localhost"},"registrationInfo":{"address":"https://' + \
                  setup['vcenter_IP'] + ':' + setup['vcenter_port'] + '","username":"' + setup[
                      'vcenter_username'] + '","password":"' + setup['vcenter_password'] + '"}}'
    print(the_payload)
    af_support_tools.rmq_publish_message(host='amqp', port=5671, ssl_enabled=True,
                                         exchange='exchange.dell.cpsd.controlplane.vcenter.request',
                                         routing_key='controlplane.hypervisor.vcenter.endpoint.register',
                                         headers={
                                             '__TypeId__': 'com.dell.cpsd.vcenter.registration.info.request'},
                                         payload=the_payload)

    # Verify the vcenter is validated
    assert waitForMsg('test.controlplane.vcenter.response'), 'ERROR: No validation Message Returned'
    return_message = af_support_tools.rmq_consume_message(host='amqp', port=5671, ssl_enabled=True,
                                                          queue='test.controlplane.vcenter.response')
    return_json = json.loads(return_message, encoding='utf-8')
    print(return_json)
    assert return_json['responseInfo']['message'] == 'SUCCESS', 'ERROR: Vcenter validation failure'

    # Verify the system triggers a msg to register vcenter with consul
    assert waitForMsg('test.endpoint.registration.event'), 'ERROR: No message to register with Consul sent'
    return_message = af_support_tools.rmq_consume_message(host='amqp', port=5671, ssl_enabled=True,
                                                          queue='test.endpoint.registration.event',
                                                          remove_message=True)

    return_json = json.loads(return_message, encoding='utf-8')
    print(return_json)

    endpointType = return_json['endpoint']['type']
    timeout = 0

    # We need to check that we received the registration msg for vcenter and not something else 
    while endpointType != 'vcenter' and timeout < 20:
        assert waitForMsg(
            'test.endpoint.registration.event'), 'Error: No message to register with Consul sent by system'
        return_message = af_support_tools.rmq_consume_message(host='amqp', port=5671, ssl_enabled=True,
                                                              queue='test.endpoint.registration.event',
                                                              remove_message=True)
        return_json = json.loads(return_message, encoding='utf-8')
        print(return_json)
        endpointType = return_json['endpoint']['type']
        timeout += 1

    assert return_json['endpoint']['type'] == 'vcenter', 'vcenter not registered with endpoint'
    cleanup('test.controlplane.vcenter.response')
    cleanup('test.endpoint.registration.event')

    print('vcenter registerd')

    time.sleep(3)
    return 1


def registerScaleIO(setup):
    # Until consul is  working properly & integrated with the vcenter adapter in the same environment we need to register
    # it manually by sending this message.

    cleanup('test.controlplane.scaleio.response')
    cleanup('test.endpoint.registration.event')
    bindQueues('exchange.dell.cpsd.controlplane.scaleio.response', 'test.controlplane.scaleio.response')
    bindQueues('exchange.dell.cpsd.endpoint.registration.event', 'test.endpoint.registration.event')

    time.sleep(2)

    af_support_tools.rmq_purge_queue(host='amqp', port=5671, ssl_enabled=True,
                                     queue='test.controlplane.scaleio.response')

    af_support_tools.rmq_purge_queue(host='amqp', port=5671, ssl_enabled=True,
                                     queue='test.endpoint.registration.event')

    the_payload = '{"messageProperties":{"timestamp":"2010-01-01T12:00:00Z","correlationId":"scaleio-full-abcd-abcdabcdabcd"},"registrationInfo":{"address":"https://' + \
                  setup['scaleIO_IP'] + '","username":"' + setup['scaleIO_username'] + '","password":"' + setup[
                      'scaleIO_password'] + '"}}'
    print(the_payload)

    af_support_tools.rmq_publish_message(host='amqp', port=5671, ssl_enabled=True,
                                         exchange='exchange.dell.cpsd.controlplane.scaleio.request',
                                         routing_key='dell.cpsd.scaleio.consul.register.request',
                                         headers={
                                             '__TypeId__': 'com.dell.cpsd.scaleio.registration.info.request'},
                                         payload=the_payload)

    # Verify the vcenter is validated
    assert waitForMsg('test.controlplane.scaleio.response'), 'ERROR: No validation Message Returned'
    return_message = af_support_tools.rmq_consume_message(host='amqp', port=5671, ssl_enabled=True,
                                                          queue='test.controlplane.scaleio.response',
                                                          remove_message=True)
    return_json = json.loads(return_message, encoding='utf-8')
    print(return_json)
    assert return_json['responseInfo']['message'] == 'SUCCESS', 'ERROR: ScaleIO validation failure'

    # Verify the system triggers a msg to register vcenter with consul
    assert waitForMsg('test.endpoint.registration.event'), 'ERROR: No message to register with Consul sent'
    return_message = af_support_tools.rmq_consume_message(host='amqp', port=5671, ssl_enabled=True,
                                                          queue='test.endpoint.registration.event',
                                                          remove_message=True)

    return_json = json.loads(return_message, encoding='utf-8')
    print(return_json)
    endpointType = return_json['endpoint']['type']
    timeout = 0

    # We need to check that we received the registration msg for scaleio and not something else 
    while endpointType != 'scaleio' and timeout < 20:
        assert waitForMsg(
            'test.endpoint.registration.event'), 'Error: No message to register with Consul sent by system'
        return_message = af_support_tools.rmq_consume_message(host='amqp', port=5671, ssl_enabled=True,
                                                              queue='test.endpoint.registration.event',
                                                              remove_message=True)
        return_json = json.loads(return_message, encoding='utf-8')
        print(return_json)
        endpointType = return_json['endpoint']['type']
        timeout += 1

    assert return_json['endpoint']['type'] == 'scaleio', 'scaleio not registered with endpoint'
    cleanup('test.controlplane.scaleio.response')
    cleanup('test.endpoint.registration.event')

    print('scaleio registerd')

    time.sleep(3)
    return 1


#####################################################################

def bindQueues(exchange, queue):
    af_support_tools.rmq_bind_queue(host='amqp', port=5671, ssl_enabled=True,
                                    queue=queue,
                                    exchange=exchange,
                                    routing_key='#')


def cleanup(queue):
    af_support_tools.rmq_delete_queue(host='amqp', port=5671, ssl_enabled=True,
                                      queue=queue)


def waitForMsg(queue):
    # This function keeps looping untill a message is in the specified queue. We do need it to timeout and throw an error
    # if a message never arrives. Once a message appears in the queue the function is complete and main continues.

    # The length of the queue, it will start at 0 but as soon as we get a response it will increase
    q_len = 0

    # Represents the number of seconds that have gone by since the method started
    timeout = 0

    # Max number of seconds to wait
    max_timeout = 500

    # Amount of time in seconds that the loop is going to wait on each iteration
    sleeptime = 1

    while q_len < 1:
        time.sleep(sleeptime)
        timeout += sleeptime

        q_len = af_support_tools.rmq_message_count(host='amqp', port=5671, ssl_enabled=True,
                                                   queue=queue)

        if timeout > max_timeout:
            print('ERROR: Message took too long to return. Something is wrong')
            return False

    return True
