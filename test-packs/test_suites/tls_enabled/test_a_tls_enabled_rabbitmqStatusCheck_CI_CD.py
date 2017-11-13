#!/usr/bin/python
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information
# Author -Catherine Hurley

import af_support_tools
import pytest


# @pytest.fixture(scope="session",
#                 params=["system-definition-service", "credentials", "hal-orchestrator-service", "identity-service",
#                         "capability-registry-service", "endpoint-registration-service", "vcenter-adapter",
#                         "hdp-poweredge-compute", "coprhd-adapter", "rackhd-adapter", "scaleio-adapter",
#                         "hal-data-provider-vcenter"])

@pytest.fixture(scope="session",
                params=["credential-service", "endpoint-registration-service"])
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


@pytest.mark.tls_enabled
@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_coreamqpconnection(core_container, setup):
    """
    Title: Verify Core services containers are connected to Rabbitmq
    Description: This test verifies that each core service container is connected to rabbitmq
    Params: List of Core service names
    Returns: None

    """
    print(test_coreamqpconnection.__doc__)
    assert core_container, "container name not found, test fails"

    cmd_1 = "docker exec " + core_container + " netstat -an 2>&1 | grep 5672 | awk '{print $6}'"
    response1 = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                  password=setup['password'],
                                                  command=cmd_1, return_output=True)
    response1 = response1.splitlines()
    if "ESTABLISHED" in response1:
        print(core_container + " connected on port 5672")

    cmd2 = "docker exec " + core_container + " netstat -an 2>&1 | grep 5671 | awk '{print $6}'"
    response2 = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                  password=setup['password'],
                                                  command=cmd2, return_output=True)
    response2 = response2.splitlines()
    if "ESTABLISHED" in response2:
        print(core_container + " connected on port 5671")

    response_list = [response1, response2]

    assert any("ESTABLISHED" in s for s in response_list), " %s is not connected to amqp" % core_container


@pytest.mark.skip(reason="Disabled until every service uses port 5671")
@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_coreamqptls(core_services, setup):
    """
    Title: Verify Core services containers are connected to TLS port for Rabbit
    Description: This test verifies that each core service container is connected to rabbitmq TLS Port
    Params: List of Core service names
    Returns: None

    """
    print(test_coreamqptls.__doc__)

    err = []
    for service in core_services:

        sendcommand_amqp = "docker exec " + service + " netstat -an 2>&1 | grep 5671 | awk '{print $6}'"
        response = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                     password=setup['password'],
                                                     command=sendcommand_amqp, return_output=True)
        if "ESTABLISHED" not in response:
            err.append(service + " Rabbit not connected on TLS Port")

    assert not err
