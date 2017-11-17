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
                params=["core-tls-service", "core-pam-service", "credential-service", "endpoint-registration-service", "system-definition-service"])
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
def test_core_serviceup(setup, core_container):
    """
    Title: Verify Core services containers are UP
    Description: This test verifies that each core service container is up
    Params: List of Core service names
    Returns: None

    """

    print(test_core_serviceup.__doc__)
    assert core_container, "container name not found"

    sendcommand = "docker ps --filter name=" + core_container + "  --format '{{.Status}}' | awk '{print $1}'"
    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                         password=setup['password'],
                                                         command=sendcommand, return_output=True)
    assert "Up" in my_return_status, " %s is not up" % core_container


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


@pytest.mark.tls_enabled_stop_start
@pytest.mark.core_services_mvp_extended
def test_core_stop(core_container, setup):
    """
        Title: Verify Core services containers can be restarted with docker stop/start
        Description: This test verifies that each core service container can restart
        Params: List of Core service names
        Returns: None

    """
    print(test_core_stop.__doc__)
    assert core_container, "container name not found, test fails immediately"
    sendcommand = "docker ps --filter name=" + core_container + "  --format '{{.Status}}' | awk '{print $1}'"
    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                         password=setup['password'],
                                                         command=sendcommand, return_output=True)
    assert "Up" in my_return_status, "%s is not running so can't be stopped" % core_container

    cmd = "docker stop " + core_container
    response = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                 password=setup['password'],
                                                 command=cmd, return_output=False)

    assert response == 0, "docker stop did not execute correctly"

    cmd2 = "docker ps -a --filter name=" + core_container + "  --format '{{.Status}}' | awk '{print $1}'"
    response2 = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                  password=setup['password'],
                                                  command=cmd2, return_output=True)

    assert "Exited" in response2, "%s did not stop or container has been removed" % core_container


@pytest.mark.tls_enabled_stop_start
@pytest.mark.core_services_mvp_extended
def test_core_start(core_container, setup):
    """
            Title: Verify Core services containers can be restarted with docker stop/start
            Description: This test verifies that each core service container can restart
            Params: List of Core service names
            Returns: None

        """
    print(test_core_start.__doc__)

    assert core_container, "container name not found, test fails immediately"

    sendcommand = "docker ps -a --filter name=" + core_container + "  --format '{{.Status}}' | awk '{print $1}'"
    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                         password=setup['password'],
                                                         command=sendcommand, return_output=True)
    assert "Exited" in my_return_status, "container is not in exited state, cannot start"

    cmd4 = "docker start " + core_container
    response = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                 password=setup['password'],
                                                 command=cmd4, return_output=False)
    assert response == 0, "docker start did not execute correctly"

    cmd3 = "docker ps -a --filter name=" + core_container + "  --format '{{.Status}}' | awk '{print $1}'"
    response3 = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                  password=setup['password'],
                                                  command=cmd3, return_output=True)
    assert "Up" in response3, "%s did not start correctly" % core_container


@pytest.mark.tls_enabled
@pytest.mark.core_services_mvp_extended
def test_core_version(core_container, setup):
    """
            Title: Verify Core services have a version associated with them
            Description: This test verifies that each core service container has a version
            Params: List of Core service names
            Returns: None

        """
    print(test_core_version.__doc__)

    assert core_container, "container name not found, test fails immediately"

    sendcommand = "docker image ls " + core_container + "|grep -v TAG | awk '{print $2}'"

    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                         password=setup['password'],
                                                         command=sendcommand, return_output=True)

    assert "." in my_return_status, "versioning is not present for this container"

