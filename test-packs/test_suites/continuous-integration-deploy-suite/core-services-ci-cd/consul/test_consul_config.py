#!/usr/bin/python
# Author: cullia
# Revision: 1.1
# Refactorr by : Toqeer Akhtar
# Code Reviewed by:
# Description: Testing services registered with consul.
#
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information

import pytest
import requests
import af_support_tools
import socket
import json

@pytest.fixture(scope="session", params=["amqp", "api-gateway", "capability-registry-service", "credential-service",
                                        "endpoint-registration-service", "identity-service", "pam-service", "postgres"])
def service_name(setup, request):
    ''' Fixture to get Service names expected to register in Consul'''

    service = request.param
    print(service)
    yield service


@pytest.mark.daily_status
@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_consul_status(setup):
    """
    Test Case Title :       Verify Consul Service is running
    Description     :       This method tests that consul docker container is running
                            It will fail if :
                                The the container is not running
    Parameters      :       none
    Returns         :       None
    """
    service_name = 'consul'

    ssh_command = "docker ps --filter name=" + service_name + "  --format '{{.Status}}' | awk '{print $1}'"
    my_return_status = af_support_tools.send_ssh_command(host = setup['IP'], username= setup['user'], password=setup['password'],
                                                             command=ssh_command, return_output=True)
    my_return_status = my_return_status.strip()
    print('\nDocker Container is:', my_return_status, '\n')
    assert my_return_status == 'Up', (service_name + " not running")


@pytest.mark.daily_status
@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended

def test_service_is_registered_with_consul(service_name):
    """
    Test Case Title :       Verify consul, CoreServices and hdp adapters are registered with Consul
    Description     :       This method tests that above services is registered in the Consul API http://{SymphonyIP}:8500/v1/agent/services
                            It will fail if :
                                The line 'Service: "consul"' is not present
    Parameters      :       none
    Returns         :       None

    """
    print (test_consul_status.__doc__)
    consulHost = 'consul.cpsd.dell'
    hostname = socket.gethostname()
    err = []

    consul_url = 'https://' + consulHost + ':8500/v1/catalog/services'
    print('sending GET request:', consul_url)
    response = requests.get(consul_url, verify= '/usr/local/share/ca-certificates/' + hostname + '.ca.crt')
    data = json.loads(response.text)


    assert response.status_code == 200, "Error---Request has not been acknowledged as expected"
    assert service_name in data, 'ERROR--- Service is not Registered in Consul\n'
    assert "consul" in data, 'ERROR--- consul is not Registered in Consul\n'


@pytest.mark.daily_status
@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_service_status_is_healthy_in_consul(service_name):
    """
    Test Case Title :       Verify all services listed in the fixture are Passing in Consul
    Description     :       This method tests that vault has a passing status in the Consul API http://{SymphonyIP}:8500/v1/health/checks/vault
                            It will fail if :
                                The line '"Status": "passing"' is not present
    Parameters      :       none
    Returns         :       None
    """

    print(test_service_status_is_healthy_in_consul.__doc__)
    consulHost = 'consul.cpsd.dell'
    hostname = socket.gethostname()

    consul_url = 'https://' + consulHost + ':8500/v1/health/checks/' + service_name
    print('GET:', consul_url)

    response = requests.get(consul_url, verify='/usr/local/share/ca-certificates/' + hostname + '.ca.crt')
    service_status = '"Status":"passing"'

    assert response.status_code == 200, "Error---Request has not been acknowledged as expected"
    assert service_status in response.text, ('ERROR:', service_name, 'is not Passing in Consul\n')
