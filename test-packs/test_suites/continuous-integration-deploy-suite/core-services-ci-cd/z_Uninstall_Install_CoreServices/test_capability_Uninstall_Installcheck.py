#!/usr/bin/python
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information
# Author - Toqeer Akhtar

import af_support_tools
import pytest



@pytest.mark.tls_enabled_stop_start
def test_cap_reg_uninstall(setup):
    """
    Title: Verify the capability Registry service can be uninstalled
    Description: This test verifies that the capability service can be uninstalled successfully
    Params: dell-cpsd-capability-registry-service
    Returns: None

    """
    service = "dell-cpsd-capability-registry-service"

    print(test_cap_reg_uninstall.__doc__)

    sendcommand = "yum -y remove " + service

    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                             password=setup['password'],
                                                             command=sendcommand, return_output=False)

    
    assert my_return_status == 0, "CapabilityReg service is not uninstalled"

@pytest.mark.tls_enabled_stop_start
def test_cap_reg_install(setup):
   
    """
    Title: Verify the sds service can be installed
    Description: This test verifies that the sds service can be installed successfully
    Params: dell-cpsd-capability-registry-service
    Returns: None

    """
    service = "dell-cpsd-capability-registry-service"

    print(test_cap_reg_install.__doc__)

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
    assert my_return_status == 0, "capability Reg did not install"


@pytest.mark.tls_enabled_stop_start
def test_cap_reg_serviceup(setup):
    """
    Title: Verify the Capability Reg service containers are UP
    Description: This test verifies that the capReg container is up
    Params: dell-cpsd-capability-registry-service
    Returns: None

    """
    service = "dell-cpsd-capability-registry-service"

    print(test_cap_reg_serviceup.__doc__)

    assert service, "container name not found"

    sendcommand = "docker ps --filter name=" + service + "  --format '{{.Status}}' | awk '{print $1}'"

    print(sendcommand)

    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                         password=setup['password'],
                                                         command=sendcommand, return_output=True)

    assert "Up" in my_return_status, " %s is not up" % service
