#!/usr/bin/python
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information
#
import af_support_tools
import pytest

# Tests use the setup fixture in conftest.py

################################################
@pytest.mark.parametrize('service_name', ["dell-cpsd-dne-engineering-standards-service", "dell-cpsd-dne-node-expansion-service",
                                          "dell-cpsd-dne-node-discovery-service", "dell-cpsd-hal-vcenter-adapter",
                                          "dell-cpsd-hal-scaleio-adapter", "dell-cpsd-hal-rackhd-adapter",
                                          "dell-cpsd-core-api-gateway"])
@pytest.mark.daily_status
@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_dne_services_up(service_name, setup):
    """
    Title: Verify DNE services containers are UP
    Description: This test verifies that each DNE service containers are up
    Params: List of DNE service names
    Returns: None

    """
    print(test_dne_services_up.__doc__)

    err = []

    # for service_name in dne_dir:
    sendcommand = "docker ps --filter name=" + service_name + "  --format '{{.Status}}' | awk '{print $1}'"
    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['cli_user'],
                                                         password=setup['cli_password'],
                                                         command=sendcommand, return_output=True)
    my_return_status = my_return_status.strip()

    if "Up" not in my_return_status:
        err.append(service_name + " not running")

    print('\n' + service_name + ' Docker Container is:', my_return_status, '\n')
    assert my_return_status == 'Up', (service_name + " not running")

    assert not err


@pytest.mark.parametrize('service_name', ["dell-cpsd-dne-engineering-standards-service", "dell-cpsd-dne-node-expansion-service",
                                          "dell-cpsd-hal-vcenter-adapter", "dell-cpsd-hal-scaleio-adapter",
                                          "dell-cpsd-dne-node-discovery-service", "dell-cpsd-hal-rackhd-adapter"])
@pytest.mark.daily_status
@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_dne_amqpconnection_tls_port(service_name, setup):
    """
    Title: Verify DNE services containers are connected to Rabbitmq
    Description: This test verifies that each DNE service container is connected to rabbitmq
    Params: List of DNE service names
    Returns: None

    """
    print(test_dne_amqpconnection_tls_port.__doc__)

    err = []

    # Verify services are connected to port 5671 and only once
    cmd_1 = "docker exec " + service_name + " netstat -an 2>&1 | grep 5671 | awk '{print $6}'"
    response1 = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['cli_user'],
                                                  password=setup['cli_password'],
                                                  command=cmd_1, return_output=True)
    response1 = response1.splitlines()
    response_list_5671 = [response1]

    assert len(response1) == 1, 'Error: More than one connection to Port 5671'

    if any("ESTABLISHED" in s for s in response_list_5671):
        print(service_name + ": Rabbitmq connected within the container on Port 5671")
    else:
        err.append(service_name + " not connected to rabbitmq 5671")

    # Verify services are NOT connected to port 5672
    cmd2 = "docker exec " + service_name + " netstat -an 2>&1 | grep 5672 | awk '{print $6}'"
    response2 = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['cli_user'],
                                                  password=setup['cli_password'],
                                                  command=cmd2, return_output=True)
    response2 = response2.splitlines()
    response_list_5672 = [response2]

    if any("ESTABLISHED" in s for s in response_list_5672):
        err.append(service_name + " is connected to rabbitmq on Port 5672")
    else:
        print(service_name + ": Not connected to rabbitmq 5672")

    assert not err


@pytest.mark.parametrize('service_name', ["dell-cpsd-dne-engineering-standards-service", "dell-cpsd-dne-node-expansion-service",
                                          "dell-cpsd-dne-node-discovery-service", "dell-cpsd-hal-vcenter-adapter",
                                          "dell-cpsd-hal-scaleio-adapter", "dell-cpsd-hal-rackhd-adapter",
                                          "dell-cpsd-core-api-gateway"])
@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_dne_service_stop_start(service_name, setup):
    """
        Title: Verify Core services containers can be restarted with docker stop/start
        Description: This test verifies that each core service container can restart
        Params: List of Core service names
        Returns: None

    """
    print(test_dne_service_stop_start.__doc__)

    err = []

    sendcommand = "docker ps --filter name=" + service_name + "  --format '{{.Status}}' | awk '{print $1}'"
    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['cli_user'],
                                                         password=setup['cli_password'],
                                                         command=sendcommand, return_output=True)
    if "Up" not in my_return_status:
        err.append(service_name + " not running")
    else:

        cmd = "docker stop " + service_name
        response = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['cli_user'],
                                                     password=setup['cli_password'],
                                                     command=cmd, return_output=False)

        cmd2 = "docker ps -a --filter name=" + service_name + "  --format '{{.Status}}' | awk '{print $1}'"
        response2 = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['cli_user'],
                                                      password=setup['cli_password'],
                                                      command=cmd2, return_output=True)
        if "Exited" not in response2:
            err.append(service_name + " has not stopped or has been removed")

    sendcommand = "docker ps -a --filter name=" + service_name + "  --format '{{.Status}}' | awk '{print $1}'"
    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['cli_user'],
                                                         password=setup['cli_password'],
                                                         command=sendcommand, return_output=True)
    if "Exited" in my_return_status:
        cmd4 = "docker start " + service_name
        response = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['cli_user'],
                                                     password=setup['cli_password'],
                                                     command=cmd4, return_output=False)

        cmd3 = "docker ps -a --filter name=" + service_name + "  --format '{{.Status}}' | awk '{print $1}'"
        response3 = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['cli_user'],
                                                      password=setup['cli_password'],
                                                      command=cmd3, return_output=True)
    if "Up" not in response3:
        err.append(service_name + " has not started or has been removed")

    assert not err



