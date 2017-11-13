#!/usr/bin/python
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information
# Author -Catherine Hurley

import af_support_tools
import pytest


@pytest.fixture(scope="session",
                params=["system-definition-service", "credential-service", "hal-orchestrator-service",
                        "identity-service",
                        "capability-registry-service", "endpoint-registration-service", "vcenter-adapter",
                        "vcenter-compute",
                        "poweredge-compute", "rackhd-adapter", "scaleio-adapter", "core-tls-service",
                        "core-pam-service", "api-gateway",
                        ])
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


# @pytest.mark.core_services_mvp
# @pytest.mark.core_services_mvp_extended
# def test_coreamqpconnection(core_container, setup):
#     """
#     Title: Verify Core services containers are connected to Rabbitmq
#     Description: This test verifies that each core service container is connected to rabbitmq
#     Params: List of Core service names
#     Returns: None
#
#     """
#     print(test_coreamqpconnection.__doc__)
#     assert core_container, "container name not found, test fails"
#
#     cmd_1 = "docker exec " + core_container + " netstat -an 2>&1 | grep 5672 | awk '{print $6}'"
#     response1 = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
#                                                   password=setup['password'],
#                                                   command=cmd_1, return_output=True)
#     response1 = response1.splitlines()
#     if "ESTABLISHED" in response1:
#         print(core_container + " connected on port 5672")
#
#     cmd2 = "docker exec " + core_container + " netstat -an 2>&1 | grep 5671 | awk '{print $6}'"
#     response2 = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
#                                                   password=setup['password'],
#                                                   command=cmd2, return_output=True)
#     response2 = response2.splitlines()
#     if "ESTABLISHED" in response2:
#         print(core_container + " connected on port 5671")
#
#     response_list = [response1, response2]
#
#     assert any("ESTABLISHED" in s for s in response_list), " %s is not connected to amqp" % core_container
#
#
# @pytest.mark.skip(reason="Disabled until every service uses port 5671")
# @pytest.mark.core_services_mvp
# @pytest.mark.core_services_mvp_extended
# def test_coreamqptls(core_services, setup):
#     """
#     Title: Verify Core services containers are connected to TLS port for Rabbit
#     Description: This test verifies that each core service container is connected to rabbitmq TLS Port
#     Params: List of Core service names
#     Returns: None
#
#     """
#     print(test_coreamqptls.__doc__)
#     err = []
#     for service in core_services:
#
#         sendcommand_amqp = "docker exec " + service + " netstat -an 2>&1 | grep 5671 | awk '{print $6}'"
#         response = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
#                                                      password=setup['password'],
#                                                      command=sendcommand_amqp, return_output=True)
#         if "ESTABLISHED" not in response:
#             err.append(service + " Rabbit not connected on TLS Port")
#
#     assert not err


# @pytest.mark.core_services_mvp_extended
# def test_core_stop(core_container, setup):
#     """
#         Title: Verify Core services containers can be restarted with docker stop/start
#         Description: This test verifies that each core service container can restart
#         Params: List of Core service names
#         Returns: None
#
#     """
#     print(test_core_stop.__doc__)
#     assert core_container, "container name not found, test fails immediately"
#     sendcommand = "docker ps --filter name=" + core_container + "  --format '{{.Status}}' | awk '{print $1}'"
#     my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
#                                                          password=setup['password'],
#                                                          command=sendcommand, return_output=True)
#     assert "Up" in my_return_status, "%s is not running so can't be stopped" % core_container
#
#     cmd = "docker stop " + core_container
#     response = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
#                                                  password=setup['password'],
#                                                  command=cmd, return_output=False)
#
#     assert response == 0, "docker stop did not execute correctly"
#
#     cmd2 = "docker ps -a --filter name=" + core_container + "  --format '{{.Status}}' | awk '{print $1}'"
#     response2 = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
#                                                   password=setup['password'],
#                                                   command=cmd2, return_output=True)
#
#     assert "Exited" in response2, "%s did not stop or container has been removed" % core_container
#
#
# @pytest.mark.core_services_mvp_extended
# def test_core_start(core_container, setup):
#     """
#             Title: Verify Core services containers can be restarted with docker stop/start
#             Description: This test verifies that each core service container can restart
#             Params: List of Core service names
#             Returns: None
#
#         """
#     print(test_core_start.__doc__)
#
#     assert core_container, "container name not found, test fails immediately"
#
#     sendcommand = "docker ps -a --filter name=" + core_container + "  --format '{{.Status}}' | awk '{print $1}'"
#     my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
#                                                          password=setup['password'],
#                                                          command=sendcommand, return_output=True)
#     assert "Exited" in my_return_status, "container is not in exited state, cannot start"
#
#     cmd4 = "docker start " + core_container
#     response = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
#                                                  password=setup['password'],
#                                                  command=cmd4, return_output=False)
#     assert response == 0, "docker start did not execute correctly"
#
#     cmd3 = "docker ps -a --filter name=" + core_container + "  --format '{{.Status}}' | awk '{print $1}'"
#     response3 = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
#                                                   password=setup['password'],
#                                                   command=cmd3, return_output=True)
#     assert "Up" in response3, "%s did not start correctly" % core_container
