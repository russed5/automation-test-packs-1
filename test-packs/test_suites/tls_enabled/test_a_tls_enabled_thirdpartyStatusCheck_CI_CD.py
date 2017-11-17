#!/usr/bin/python
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information
# Author -Catherine Hurley

import af_support_tools
import pytest


@pytest.fixture(scope="session",
                params=["vault", "postgres", "consul","rabbitmq"])
def thirdparty_container(setup, request):
    ''' Fixture to get names of third party containers'''

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
def test_thirdparty_containerup(setup, thirdparty_container):
    """
    Title: Verify Third Party containers are UP
    Description: This test verifies that each core service container is up
    Params: List of Core service names
    Returns: None

    """

    print(test_thirdparty_containerup.__doc__)
    assert thirdparty_container, "container name not found"

    sendcommand = "docker ps --filter name=" + thirdparty_container + "  --format '{{.Status}}' | awk '{print $1}'"
    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                         password=setup['password'],
                                                         command=sendcommand, return_output=True)
    assert "Up" in my_return_status, " %s is not up" % thirdparty_container



@pytest.mark.tls_enabled_stop_start
@pytest.mark.core_services_mvp_extended
def test_core_stop(thirdparty_container, setup):
    """
        Title: Verify Third Part containers can be restarted with docker stop/start
        Description: This test verifies that each core service container can restart
        Params: List of Core service names
        Returns: None

    """
    print(test_core_stop.__doc__)
    assert thirdparty_container, "container name not found, test fails immediately"
    sendcommand = "docker ps --filter name=" + thirdparty_container + "  --format '{{.Status}}' | awk '{print $1}'"

    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                         password=setup['password'],
                                                         command=sendcommand, return_output=True)

    assert "Up" in my_return_status, "%s is not running so can't be stopped" % thirdparty_container

    cmd = "docker stop " + thirdparty_container

    response = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                 password=setup['password'],
                                                 command=cmd, return_output=False)

    assert response == 0, "docker stop did not execute correctly"

    cmd2 = "docker ps -a --filter name=" + thirdparty_container + "  --format '{{.Status}}' | awk '{print $1}'"

    response2 = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                  password=setup['password'],
                                                  command=cmd2, return_output=True)

    assert "Exited" in response2, "%s did not stop or container has been removed" % thirdparty_container


@pytest.mark.tls_enabled_stop_start
@pytest.mark.core_services_mvp_extended
def test_thirdparty_start(thirdparty_container, setup):
    """
            Title: Verify Third Part containers can be restarted with docker stop/start
            Description: This test verifies that each core service container can restart
            Params: List of Core service names
            Returns: None

        """
    print(test_thirdparty_start.__doc__)

    assert thirdparty_container, "container name not found, test fails immediately"

    sendcommand = "docker ps -a --filter name=" + thirdparty_container + "  --format '{{.Status}}' | awk '{print $1}'"

    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                         password=setup['password'],
                                                         command=sendcommand, return_output=True)
    assert "Exited" in my_return_status, "container is not in exited state, cannot start"

    cmd4 = "docker start " + thirdparty_container

    response = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                 password=setup['password'],
                                                 command=cmd4, return_output=False)
    assert response == 0, "docker start did not execute correctly"

    cmd3 = "docker ps -a --filter name=" + thirdparty_container + "  --format '{{.Status}}' | awk '{print $1}'"

    response3 = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                  password=setup['password'],
                                                  command=cmd3, return_output=True)
    assert "Up" in response3, "%s did not start correctly" % thirdparty_container
