#!/usr/bin/python
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information
# Author -Ted Whooley

import af_support_tools
import pytest



@pytest.mark.tls_enabled_stop_start
def test_endpoint_uninstall(setup):
    """
    Title: Verify the endpoint service can be uninstalled
    Description: This test verifies that the endpoint service can be uninstalled successfully
    Params: dell-cpsd-core-endpoint-registration-service
    Returns: None

    """
    service = "dell-cpsd-core-endpoint-registration-service"

    print(test_endpoint_uninstall.__doc__)

    sendcommand = "yum -y remove " + service

    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                             password=setup['password'],
                                                             command=sendcommand, return_output=False)

    print(my_return_status)

    assert my_return_status == 0, "endpoint is not uninstalled"

@pytest.mark.tls_enabled_stop_start
def test_endpoint_install(setup):
    #this test is working (TW)
    """
    Title: Verify the endpoint service can be installed
    Description: This test verifies that the endpoint service can be installed successfully
    Params: dell-cpsd-core-endpoint-registration-service
    Returns: None

    """
    service = "dell-cpsd-core-endpoint-registration-service"

    print(test_endpoint_install.__doc__)

    expirecache = "yum clean expire-cache"
    makecache = "yum makecache fast"
    sendcommand = "yum install -y " + service

    af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                         password=setup['password'],
                                                         command=expirecache, return_output=True)

    af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                         password=setup['password'],
                                                         command=makecache, return_output=True)


    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                             password=setup['password'],
                                                             command=sendcommand, return_output=False)
    assert my_return_status == 0, "endpoint did not install"


@pytest.mark.tls_enabled
def test_endpoint_serviceup(setup):
    """
    Title: Verify the endpoint services containers are UP
    Description: This test verifies that the endpoint container is up
    Params: dell-cpsd-core-endpoint-registration-service
    Returns: None

    """
    service = "dell-cpsd-core-endpoint-registration-service"

    print(test_endpoint_serviceup.__doc__)

    assert service, "container name not found"

    sendcommand = "docker ps --filter name=" + service + "  --format '{{.Status}}' | awk '{print $1}'"

    print(sendcommand)

    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                         password=setup['password'],
                                                         command=sendcommand, return_output=True)

    assert "Up" in my_return_status, " %s is not up" % service




