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


@pytest.mark.parametrize('service, directory', [("dell-cpsd-hal-vcenter-adapter", "vcenter-adapter"),
                                                ("dell-cpsd-hal-rackhd-adapter", "rackhd-adapter"),
                                                ("dell-cpsd-hal-scaleio-adapter", "scaleio-adapter"),
                                                ("dell-cpsd-dne-node-expansion-service", "node-expansion-service"),
                                                ("dell-cpsd-dne-engineering-standards-service", "engineering-standards-service"),
                                                ("dell-cpsd-dne-node-discovery-service", "node-discovery-service")])
@pytest.mark.daily_status
@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_dne_services_log_files_exceptions(service, directory, setup):
    """
    Description     :       This method tests that the ESS log files exist and contain no Exceptions.
                            It will fail:
                                If the the error and/or info log files do not exists
                                If the error log file contains AuthenticationFailureException, RuntimeException or NullPointerException.
    Parameters      :       None
    Returns         :       None
    """

    filePath = '/opt/dell/cpsd/' + directory + '/logs/'

    infoLogFile = directory + '-info.log'

    # Need this exception as the node-discovery-paqx log file format is different to the others
    if filePath == '/opt/dell/cpsd/engineering-standards-service/logs/':
        filePath = '/opt/dell/cpsd/dne/engineering-standards-service/logs/'
        infoLogFile = 'ess-info.log'

    if filePath == '/opt/dell/cpsd/node-expansion-service/logs/':
        filePath = '/opt/dell/cpsd/dne/node-expansion-service/logs/'

    if filePath == '/opt/dell/cpsd/node-discovery-service/logs/':
        filePath = '/opt/dell/cpsd/dne/node-discovery-service/logs/'
        infoLogFile = 'node-discovery-info.log'


    # Verify the log files exist
    sendCommand = 'docker ps | grep ' + service + ' | awk \'{system("docker exec -i "$1" ls ' + filePath + '") }\''

    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['cli_user'],
                                                         password=setup['cli_password'],
                                                         command=sendCommand, return_output=True)
    print(my_return_status)
    error_list = []

    if (infoLogFile not in my_return_status):
        error_list.append(infoLogFile)

    excep1 = 'AuthenticationFailureException'
    excep2 = 'RuntimeException'
    excep3 = 'NullPointerException'
    excep4 = 'BeanCreationException'
    excep5 = 'java.net.SocketException: Socket is closed'

    # Verify there are no Authentication errors
    sendCommand = 'docker ps | grep ' + service + ' | awk \'{system("docker exec -i "$1" cat ' + filePath + infoLogFile + ' | grep ' + excep1 + '")}\''
    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['cli_user'],
                                                         password=setup['cli_password'],
                                                         command=sendCommand, return_output=True)
    if (excep1 in my_return_status):
        error_list.append(excep1)

    # Verify there are no RuntimeException errors
    sendCommand = 'docker ps | grep ' + service + ' | awk \'{system("docker exec -i "$1" cat ' + filePath + infoLogFile + ' | grep ' + excep2 + '")}\''
    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['cli_user'],
                                                         password=setup['cli_password'],
                                                         command=sendCommand, return_output=True)
    if (excep2 in my_return_status):
        error_list.append(excep2)

    # Verify there are no NullPointerException errors
    sendCommand = 'docker ps | grep ' + service + ' | awk \'{system("docker exec -i "$1" cat ' + filePath + infoLogFile + ' | grep ' + excep3 + '")}\''
    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['cli_user'],
                                                         password=setup['cli_password'],
                                                         command=sendCommand, return_output=True)
    if (excep3 in my_return_status):
        error_list.append(excep3)

    # Verify there are no BeanCreationException errors
    sendCommand = 'docker ps | grep ' + service + ' | awk \'{system("docker exec -i "$1" cat ' + filePath + infoLogFile + ' | grep ' + excep4 + '")}\''
    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['cli_user'],
                                                         password=setup['cli_password'],
                                                         command=sendCommand, return_output=True)
    if (excep4 in my_return_status):
        error_list.append(excep4)

    # Verify there are no BeanCreationException errors
    sendCommand = 'docker ps | grep ' + service + ' | awk \'{system("docker exec -i "$1" cat ' + filePath + infoLogFile + ' | grep ' + excep5 + '")}\''
    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['cli_user'],
                                                         password=setup['cli_password'],
                                                         command=sendCommand, return_output=True)
    if (excep4 in my_return_status):
        error_list.append(excep5)

    assert not error_list, 'Exceptions in log files, Review the ' + infoLogFile + ' file'

    print(
        '\nNo Authentication, RuntimeException, BeanCreationException, SocketException or NullPointerException in log files\n')
