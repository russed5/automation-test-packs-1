#!/usr/bin/python
# Copyright Â© 01 April 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
#
# Author: russed5
# Revision: 1.0
# Code Reviewed by: olearj10
# Description: see https://wiki.ent.vce.com/display/VSE/Endpoint+Registry+Testing

import pytest
import requests
import json
import time
import af_support_tools
from conftest import NoMessageConsumedException


@pytest.fixture(scope="module", autouse=True)
def load_test_data(hostIpAddress):

    global consulHost
    consulHost = 'consul.cpsd.dell'
    #print("jk ",consulHost)

    global endpointExchange
    endpointExchange = "exchange.dell.cpsd.endpoint.registration.event"
# *******************************************************************************************
#

@pytest.mark.tls_enabled
@pytest.mark.core_services_mvp_extended
def test_registerServiceWithNoAddress(rabbitMq):
    with pytest.raises(NoMessageConsumedException):
        # Testing that even tho Consul accepts a registration with no Address field, the Endpoint Registry
        # does not advertise its existence

        # setup, delete any lingering AMQP testQueue and create a new one before any messaging starts
        #TA## print(rmq_connection)
        service_id="testService1"
        cleanup(service_id)
        rabbitMq.bind_queue_with_key(endpointExchange, 'testQueue', 'dell.cpsd.endpoint.discovered')


        #add service to consul
        test_serivce = {"ID": "testService1", "Name": "testService",
                        "Tags": ["testTag1"], "Check": {"HTTPS":  rabbitMq.connection.url, "Interval": "5s"}}
        status_code = registerServiceWithConsul(test_serivce)
        assert status_code == 200, "The Register Service task was unsuccessful"


        # check on the AMQP bus that a discovered endpoint event was NOT raised for this service
        rabbitMq.consume_message_from_queue('testQueue')
# # *******************************************************************************************
#
@pytest.mark.tls_enabled
@pytest.mark.core_services_mvp_extended
def test_registerServiceWithNoPort(rabbitMq):
    with pytest.raises(NoMessageConsumedException):
        # Testing that even tho Consul accepts a registration with no Address field, the Endpoint Registry
        # does not advertise its existence

        # setup, delete any lingering AMQP testQueue and create a new one before any messaging starts
        service_id="testService1"
        cleanup(service_id)
        rabbitMq.bind_queue_with_key(endpointExchange, 'testQueue', 'dell.cpsd.endpoint.discovered')

        #add service to consul
        test_service = {"ID": service_id, "Name": "testService", "Address": "1.2.3.4",
                        "Tags": ["testTag1"], "Check": {"HTTP":  rabbitMq.connection.url, "Interval": "5s"}}
        status_code = registerServiceWithConsul(test_service)
        assert status_code == 200, "The Register Service task was unsuccessful"


        # check on the AMQP bus that a discovered endpoint event was NOT raised for thsi service
        rabbitMq.consume_message_from_queue('testQueue')
# # *******************************************************************************************

@pytest.mark.tls_enabled
@pytest.mark.core_services_mvp_extended
def test_registerServiceWithNoHealthCheck(rabbitMq):
    with pytest.raises(NoMessageConsumedException):
        # Testing that even tho Consul accepts a registration with no Address field, the Endpoint Registry
        # does not advertise its existence

        # setup, delete any lingering AMQP testQueue and create a new one before any messaging starts
        service_id="testService1"
        cleanup(service_id)
        rabbitMq.bind_queue_with_key(endpointExchange, 'testQueue', 'dell.cpsd.endpoint.discovered')

        #add service to consul
        test_service = {"ID": service_id, "Name": "testService", "Address": "1.2.3.4", "Port": 200,
                        "Tags": ["testTag1"]}
        status_code = registerServiceWithConsul(test_service)
        assert status_code == 200, "The Register Service task was unsuccessful"

        # check on the AMQP bus that a discovered endpoint event was NOT raised for this service
        rabbitMq.consume_message_from_queue('testQueue')
#
# # # **************************************************************************************
@pytest.mark.skip(reason="Waiting for new API to be developed")
@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_registerServiceSuccess(rabbitMq):
    # This test verifies that a succful service register in Consul prompts the Endpoint Registry
    # to publish an endpoint.discovered event to the AMQP bus


    #reset consul and testQueue
    service_id = "testService1"
    cleanup(service_id)
    rabbitMq.bind_queue_with_key(endpointExchange, 'testQueue', 'dell.cpsd.endpoint.discovered')


    #add service to consul
    test_service = {"ID": service_id, "Name": "testService", "Address": "1.2.3.4", "Port": 200,
                    "Tags": ["testTag1"], "Check": {"HTTP":  rabbitMq.connection.url, "Interval": "2s"}}
    status_code = registerServiceWithConsul(test_service)
    assert status_code == 200, "The Register Service task was unsuccessful"
    data_check = verifyServiceWasRegisteredSuccessfully(test_service["Name"], test_service["ID"], test_service["Address"], test_service["Tags"][0])
    assert data_check == "Success", "The new Service is not correctly registered in Consul"


    #get endpoint event raised when service added to consul
    message = rabbitMq.consume_message_from_queue('testQueue')
    errors_list = []
    if test_service["Name"] not in message['endpoint']['type']:
        errors_list.append("Service Name on the AMQP Bus is incorrect")
    if test_service["Address"] not in message['endpoint']['instances'][0]['url']:
        errors_list.append("Service Address on the AMQP Bus is incorrect")
    if test_service["Tags"][0] not in message['endpoint']['instances'][0]['tags'][0]:
        errors_list.append("Service Tag on the AMQP Bus is incorrect")
    assert not errors_list
# #
# # # **************************************************************************************
@pytest.mark.skip(reason="Waiting for new API to be developed")
@pytest.mark.core_services_mvp_extended
def test_registerTwoServicesSameName(rabbitMq):
    # this test verifies that the same service can be registered twice, but with differing endpoints

    cleanup("duplicateService1")
    cleanup("duplicateService2")

    time.sleep(20)

    rabbitMq.bind_queue_with_key(endpointExchange, 'testQueue', 'dell.cpsd.endpoint.discovered')

    # perform initial registration
    regData1 = {"ID": "duplicateService1", "Name": "duplicateService","Address": "3.3.3.3", "Port": 300,
                "Tags": ["duplicate1"], "Check": {"HTTP":  rabbitMq.connection.url, "Interval": "2s"}}
    status_code = registerServiceWithConsul(regData1)
    assert status_code == 200, "The Register Service task was unsuccessful"

    data_check = verifyServiceWasRegisteredSuccessfully("duplicateService", "duplicateService1", "3.3.3.3", "duplicate1")
    assert data_check == "Success", "The new Service is not correctly registered in Consul"

    message = rabbitMq.consume_message_from_queue('testQueue')
    errors_list = []
    if 'duplicateService' not in message['endpoint']['type']:
        errors_list.append("Service Name on the AMQP Bus is incorrect")
    if '3.3.3.3' not in message['endpoint']['instances'][0]['url']:
        errors_list.append("Service Address on the AMQP Bus is incorrect")
    if 'duplicate1' not in message['endpoint']['instances'][0]['tags'][0]:
        errors_list.append("Service Tag on the AMQP Bus is incorrect")

    assert not errors_list

    time.sleep(20)    # necessary whilst ER uses pollinginstead of 'watch'


    # add a second service, duplicate name
    rabbitMq.bind_queue_with_key(endpointExchange, 'testQueue', 'dell.cpsd.endpoint.discovered')
    regData2 = {"ID": "duplicateService2", "Name": "duplicateService","Address": "4.4.4.4", "Port": 301,
                "Tags": ["duplicate2"], "Check": {"HTTP":  rabbitMq.connection.url, "Interval": "2s"}}
    status_code = registerServiceWithConsul(regData2)
    assert status_code == 200, "The Register Service task was unsuccessful"

    data_check = verifyServiceWasRegisteredSuccessfully("duplicateService", "duplicateService2", "4.4.4.4", "duplicate2")
    assert data_check == "Success", "The new Service is not correctly registered in Consul"

    # april 4th - 2 events are recieved when second service added. The first indicates a change to first service
    # we don't examine the first.
    # the second details the second service added, that is the one that we check
    rabbitMq.consume_message_from_queue('testQueue')
    message = rabbitMq.consume_message_from_queue('testQueue')
    errors_list = []
    if 'duplicateService' not in message['endpoint']['type']:
        errors_list.append("Service Name on the AMQP Bus is incorrect")
    if '3.3.3.3' not in message['endpoint']['instances'][0]['url']:
        errors_list.append("Service Address on the AMQP Bus is incorrect")
    if '4.4.4.4' not in message['endpoint']['instances'][1]['url']:
        errors_list.append("Service Address on the AMQP Bus is incorrect")
    if 'duplicate1' not in message['endpoint']['instances'][0]['tags'][0]:
        errors_list.append("Service Tag on the AMQP Bus is incorrect")
    if 'duplicate2' not in message['endpoint']['instances'][1]['tags'][0]:
        errors_list.append("Service Tag on the AMQP Bus is incorrect")

    assert not errors_list

# # **************************************************************************************
@pytest.mark.skip(reason="Waiting for new API to be developed")
@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_deregisterServiceSuccess(rabbitMq):
    # This test verifies that deregistering a service at Consul prompts the Endpoint Registry to publish
    # an endpoint.unavailable event
    service_id = "testService1"
    cleanup(service_id)
    rabbitMq.bind_queue_with_key(endpointExchange, 'testQueue', 'dell.cpsd.endpoint.discovered')
    time.sleep(20)

    #add service to consul
    test_service = {"ID": service_id, "Name": "testService", "Address": "1.2.3.4", "Port": 200,
                    "Tags": ["testTag1"], "Check": {"HTTP":  rabbitMq.connection.url, "Interval": "2s"}}
    status_code = registerServiceWithConsul(test_service)
    rabbitMq.consume_message_from_queue('testQueue')
    assert status_code == 200, "The Register Service task was unsuccessful"
    time.sleep(20)     # necessary whilst ER uses polling instead of 'watch'


    # setup a test queue for endpoint.unavailable
    rabbitMq.bind_queue_with_key(endpointExchange, 'testQueue', 'dell.cpsd.endpoint.unavailable')
    time.sleep(40)     # necessary whilst ER uses polling instead of 'watch'
    status_code = deregisterServiceFromConsul(test_service["ID"])
    assert status_code == 200, "The deRegister Service task was unsuccessful"


    # verify with Consul that the service is no longer listed
    data_check = verifyServiceNotRegistered(test_service["ID"])
    assert data_check == "True", "The Service is incorrectly still registered in Consul"

    message = rabbitMq.consume_message_from_queue('testQueue')
    assert test_service["Name"] in message['type'], "Service Name on the AMQP Bus is incorrect"

#  **************************************************************************************
@pytest.mark.skip(reason="Waiting for new API to be developed")
@pytest.mark.core_services_mvp_extended
def test_deregisterOneOfTwoSameServices(rabbitMq):
    # This test verifies what happens if there is a service with 2 instances registered and
    # one of those services deregisters. An 'endpoint.discovered' event is published listing just details of the
    # remaining instance

    errors_list = []
    cleanup("duplicateService1")
    cleanup("duplicateService2")
    rabbitMq.bind_queue_with_key(endpointExchange, 'testQueue', 'dell.cpsd.endpoint.discovered')

    # perform initial registration
    regData1 = {"ID": "duplicateService1", "Name": "duplicateService","Address": "3.3.3.3", "Port": 300,
                "Tags": ["duplicate1"], "Check": {"HTTP":  rabbitMq.connection.url, "Interval": "2s"}}
    status_code = registerServiceWithConsul(regData1)
    assert status_code == 200, "The Register Service task was unsuccessful"

    time.sleep(12)     # necessary whilst ER uses pollinginstead of 'watch'

    # add a second service, duplicate name
    rabbitMq.bind_queue_with_key(endpointExchange, 'testQueue', 'dell.cpsd.endpoint.discovered')
    regData2 = {"ID": "duplicateService2", "Name": "duplicateService","Address": "4.4.4.4", "Port": 402,
                "Tags": ["duplicate2"], "Check": {"HTTP":  rabbitMq.connection.url, "Interval": "2s"}}
    status_code = registerServiceWithConsul(regData2)
    assert status_code == 200, "The Register Service task was unsuccessful"

    time.sleep(12)     # necessary whilst ER uses pollinginstead of 'watch'

    # deregister one of the services
    rabbitMq.bind_queue_with_key(endpointExchange, 'testQueue', 'dell.cpsd.endpoint.discovered')
    status_code = deregisterServiceFromConsul("duplicateService1")
    assert status_code == 200, "The deRegister Service task was unsuccessful"

    data_check = verifyServiceNotRegistered("duplicateService1")
    assert data_check == "True", "The Service is incorrectly still registered in Consul"

    message = rabbitMq.consume_message_from_queue('testQueue')

    if 'duplicateService' not in message['endpoint']['type']:
        errors_list.append("Service Name on the AMQP Bus is incorrect")
    if '4.4.4.4' not in message['endpoint']['instances'][0]['url']:
        errors_list.append("Service Address on the AMQP Bus is incorrect")
    if 'duplicate2' not in message['endpoint']['instances'][0]['tags'][0]:
        errors_list.append("Service Tag on the AMQP Bus is incorrect")

    assert not errors_list

    data_check = verifyServiceWasRegisteredSuccessfully("duplicateService", "duplicateService2", "4.4.4.4", "duplicate2")
    assert data_check == "Success", "The remaining Service, duplicate2, should still be registered in Consul"

    cleanup("duplicateService1")
    cleanup("duplicateService2")
# # *****************************************************************************************************
@pytest.mark.skip(reason="Waiting for new API to be developed")
@pytest.mark.core_services_mvp_extended
def test_deregisterTwoOfTwoSameServices(rabbitMq):
# This test verifies what happens when all instances of a service (in this case 2) are deregistered
    # An 'endpoint.unavailable' event is expected listing the service.

    errors_list = []
    cleanup("duplicateService1")
    cleanup("duplicateService2")
    rabbitMq.bind_queue_with_key(endpointExchange, 'testQueue', 'dell.cpsd.endpoint.discovered')

    # perform initial registration to setup the first instance
    regData1 = {"ID": "duplicateService1", "Name": "duplicateService", "Address": "3.3.3.3", "Port": 300,
                "Tags": ["duplicate1"], "Check": {"HTTP": rabbitMq.connection.url, "Interval": "2s"}}
    status_code = registerServiceWithConsul(regData1)
    rabbitMq.consume_message_from_queue('testQueue')
    assert status_code == 200, "The Register Service task was unsuccessful"

    time.sleep(12)

    # add a second instance, duplicate name
    rabbitMq.bind_queue_with_key(endpointExchange, 'testQueue', 'dell.cpsd.endpoint.discovered')
    regData2 = {"ID": "duplicateService2", "Name": "duplicateService","Address": "4.4.4.4", "Port": 403,
                "Tags": ["duplicate2"], "Check": {"HTTP": rabbitMq.connection.url, "Interval": "2s"}}
    status_code = registerServiceWithConsul(regData2)
    rabbitMq.consume_message_from_queue('testQueue')
    assert status_code == 200, "The Register Service task was unsuccessful"

    time.sleep(12)     # necessary whilst ER uses pollinginstead of 'watch'

    # deregister instance 1
    rabbitMq.bind_queue_with_key(endpointExchange, 'testQueue', 'dell.cpsd.endpoint.discovered')
    status_code = deregisterServiceFromConsul("duplicateService1")
    assert status_code == 200, "The deRegister Service task was unsuccessful for duplicateService1"
    data_check = verifyServiceNotRegistered("duplicateService1")
    assert data_check == "True", "The Service is incorrectly still registered in Consul"
    message = rabbitMq.consume_message_from_queue('testQueue')

    if 'duplicateService' not in message['endpoint']['type']:
        errors_list.append("Service Name on the AMQP Bus is incorrect")
    if '4.4.4.4' not in message['endpoint']['instances'][0]['url']:
        errors_list.append("Service Address on the AMQP Bus is incorrect")
    if 'duplicate2' not in message['endpoint']['instances'][0]['tags'][0]:
        errors_list.append("Service Tag on the AMQP Bus is incorrect")

    assert not errors_list

    time.sleep(10)     # necessary whilst ER uses pollinginstead of 'watch'

    # deregisterinstance 2
    rabbitMq.bind_queue_with_key(endpointExchange, 'testQueue', 'dell.cpsd.endpoint.unavailable')
    status_code = deregisterServiceFromConsul("duplicateService2")
    assert status_code == 200, "The deRegister Service task was unsuccessful for duplicateService2"
    data_check = verifyServiceNotRegistered("duplicateService2")
    assert data_check == "True", "The Service is incorrectly still registered in Consul"
    message = rabbitMq.consume_message_from_queue('testQueue')
    assert "duplicateService" in message['type'],        "Service Name on the AMQP Bus is incorrect"

    cleanup("duplicateService1")
    cleanup("duplicateService2")
# #
# *****************************************************************************************************
#  Helper functions
def registerServiceWithConsul(apidata):
    # request Consul to register a new service
    apipath = "/v1/agent/service/register"
    apiheaders = {"content-type": "application/json"}
    url = 'https://' + consulHost + ':8500' + apipath
    resp = requests.put(url, data=json.dumps(apidata), headers = apiheaders,verify='/usr/local/share/ca-certificates/taf.cpsd.dell.ca.crt')
    return resp.status_code


def verifyServiceWasRegisteredSuccessfully(service_name, service_id, service_host, service_tag_1):
    # check the contents stored for the service in Consul
    apipath = "/v1/agent/services"
    url = 'https://' + consulHost + ':8500' + apipath
    #resp = requests.get(url)
    resp = requests.get(url, verify='/usr/local/share/ca-certificates/taf.cpsd.dell.ca.crt')
    data = json.loads(resp.text)
    assert service_name in data[service_id]['Service']
    assert service_id in data[service_id]['ID']
    assert service_host in data[service_id]['Address']
    assert service_tag_1 in data[service_id]['Tags']
    return "Success"


def verifyServiceNotRegistered(service_id):
    # check the contents stored for the service in Consul
    apipath = "/v1/agent/services"
    url = 'https://' + consulHost + ':8500' + apipath
    #resp = requests.get(url)
    resp = requests.put(url, verify='/usr/local/share/ca-certificates/taf.cpsd.dell.ca.crt')
    data = json.loads(resp.text)
    assert service_id not in data, "The Service should not be registered at this time"
    return "True"


def deregisterServiceFromConsul(serviceID):
    # deregister the service at consul
    apipath = "/v1/agent/service/deregister/" + serviceID
    url = 'https://' + 'consul.cpsd.dell' + ':8500' + apipath
    print("jk consul url ",url)
    resp = requests.put(url, verify='/usr/local/share/ca-certificates/taf.cpsd.dell.ca.crt')
    #resp = requests.put(url, verify='/home/autouser/PycharmProjects/auto-framework/test_suites/continuous-integration-deploy-suite/core-services-ci-cd/z_endpoint-registration-service/certs/taf.cpsd.dell.ca.crt')
    return resp.status_code


def cleanup(service_id):
    # deregister the service at Consul ?
    deregisterServiceFromConsul(service_id)
    time.sleep(10)
