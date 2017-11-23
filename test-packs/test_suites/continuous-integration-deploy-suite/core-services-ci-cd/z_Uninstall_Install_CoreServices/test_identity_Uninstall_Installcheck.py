#!/usr/bin/python
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information
# Author - Toqeer Akhtar

import af_support_tools
import pytest



@pytest.mark.tls_enabled_stop_start
def test_identity_service_uninstall(setup):
    """
    Title: Verify the Identityservice can be uninstalled
    Description: This test verifies that the Identity service can be uninstalled successfully
    Params: dell-cpsd-core-identity-service
    Returns: None

    """
    service = "dell-cpsd-core-identity-service"

    print(test_identity_service_uninstall.__doc__)

    sendcommand = "yum -y remove " + service

    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                             password=setup['password'],
                                                             command=sendcommand, return_output=False)

    
    assert my_return_status == 0, "Identity service is not uninstalled"

@pytest.mark.tls_enabled_stop_start
def test_identity_service_install(setup):
   
    """
    Title: Verify the Identity service can be installed
    Description: This test verifies that the Identity service can be installed successfully
    Params: dell-cpsd-core-identity-service
    Returns: None

    """
    service = "dell-cpsd-core-identity-service"

    print(test_identity_service_install.__doc__)

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
    assert my_return_status == 0, "Identity did not install"


@pytest.mark.tls_enabled_stop_start
def test_cap_reg_serviceup(setup):
    """
    Title: Verify the Identity service containers are UP
    Description: This test verifies that the Identity container is up
    Params: dell-cpsd-core-identity-service
    Returns: None

    """
    service = "dell-cpsd-core-identity-service"

    print(test_cap_reg_serviceup.__doc__)

    assert service, "container name not found"

    sendcommand = "docker ps --filter name=" + service + "  --format '{{.Status}}' | awk '{print $1}'"

    print(sendcommand)

    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                         password=setup['password'],
                                                         command=sendcommand, return_output=True)

    assert "Up" in my_return_status, " %s is not up" % service
