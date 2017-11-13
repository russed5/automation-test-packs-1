#!/usr/bin/python
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information
# Author - Toqeer Akhtar


import af_support_tools
import pytest
import json
import requests
import socket


@pytest.fixture(scope="session", params=["core-pam-service"])

def core_container(setup, request):
    ''' Fixture to get names of core service containers'''

    service = request.param
    print(service)
    sendcommand_core = "cat /opt/dell/cpsd/" + service + "/install/docker-compose.yml | grep container_name| cut -f 2 -d ':'"
    my_return_status_core = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                              password=setup['password'], command=sendcommand_core,
                                                              return_output=True)

    if not my_return_status_core:
        print("Unable to find " + service)
    containername = my_return_status_core.strip()
    yield containername

    global consulHost
    consulHost = 'consul.cpsd.dell'


@pytest.mark.tls_enabled
@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended

def test_pam_serviceup(setup, core_container):

    """
    Title: Verify pam service container is UP
    Description: This test verifies that pam service container is up

    """

    print(test_pam_serviceup.__doc__)
    assert core_container, "container name not found"

    sendcommand = "docker ps --filter name=" + core_container + "  --format '{{.Status}}' | awk '{print $1}'"
    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                         password=setup['password'],
                                                         command=sendcommand, return_output=True)
    assert "Up" in my_return_status, " %s is not up" % core_container


@pytest.mark.tls_enabled
@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_pam_consulreg(setup):
    """
    Title: pam Registered in con
    Description: This test verify pam Services is registered with consul

    """
    print(test_pam_consulreg.__doc__)
    err = []
    consulHost = 'consul.cpsd.dell'


    consul_url = 'https://' + consulHost + ':8500/v1/catalog/services'
    resp = requests.get(consul_url, verify='/usr/local/share/ca-certificates/taf.cpsd.dell.ca.crt')
    data = json.loads(resp.text)

    assert resp.status_code == 200, "Request has not been acknowledged as expected."


    if 'pam-service' not in data:
        err.append("Error--- pam-service not registered in Consul")
    assert not err

    if 'postgres' not in data:
        err.append("Error--- Postgres not registered in Consul")
    assert not err


@pytest.mark.tls_enabled
@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_pam_createdb():

    """
        Title: Pam creating database
        Description: This test is to verfiy pam service creating a database using
         a simple put request

    """
    print(test_pam_createdb.__doc__)
    err = []


    r = requests.put("https://pam-service.cpsd.dell:7002/pam-service/v1/postgres/databases",
                     cert=('/usr/local/share/ca-certificates/taf.cpsd.dell.crt',
                           '/usr/local/share/ca-certificates/taf.cpsd.dell.key'),
                     verify='/usr/local/share/ca-certificates/cpsd.dell.ca.crt')
    data = json.loads(r.text)

    assert r.status_code == 200, "Error---Request has not been acknowledged as expected."

    if (data['status']['status_code'] != 201 and
            data['status']['status_message'] != "Created" and
                data['response']['postgres']['hostname'] != "postgres.cpsd.dell"):

        err.append("Error--- database not created successfully or wrong hostname")



@pytest.mark.tls_enabled
@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_pam_createRMQuser():

    """
        Title: Creating RMQ username and password
        Description: This test is to verfiy pam service creating a Rabbit MQ username and password using
         a simple put request

    """
    print(test_pam_createRMQuser.__doc__)
    err =[]
    hostname = socket.gethostname()

    r = requests.put("https://pam-service.cpsd.dell:7002/pam-service/v1/amqp/users",
                     cert=('/usr/local/share/ca-certificates/taf.cpsd.dell.crt',
                           '/usr/local/share/ca-certificates/taf.cpsd.dell.key'),
                     verify='/usr/local/share/ca-certificates/cpsd.dell.ca.crt')

    assert r.status_code == 200, "Error---Request has not been acknowledged as expected."
    
    data = json.loads(r.text)
    print (data)

    if (data['status']['status_code'] != 201 and
            data['status']['status_message'] != "Created" and
                data['response']['amqp']['username'] != hostname ):
        
        err.append("Error--- amqp username is not correct") 
        
        
