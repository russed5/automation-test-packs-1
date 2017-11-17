#!/usr/bin/python
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information
# Author - Toqeer Akhtar



import af_support_tools
import pytest



@pytest.mark.tls_enabled_stop_start
def test_sysdef_uninstall(setup):
    """
    Title: Verify the dell-cpsd-hal-vcenter-adapter service can be uninstalled
    Description: This test verifies that the dell-cpsd-hal-vcenter-adapter service can be uninstalled successfully
    Params: dell-cpsd-hal-vcenter-adapter
    Returns: None

    """
    service = "dell-cpsd-hal-vcenter-adapter"

    print(test_sysdef_uninstall.__doc__)

    sendcommand = "yum -y remove " + service

    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                             password=setup['password'],
                                                             command=sendcommand, return_output=False)

    
    assert my_return_status == 0, " %s did not uninstall" % service

@pytest.mark.tls_enabled_stop_start
def test_sysdef_install(setup):
    #this test is working (TW)
    """
    Title: Verify the dell-cpsd-hal-vcenter-adapter service can be installed
    Description: This test verifies that the dell-cpsd-hal-vcenter-adapter service can be installed successfully
    Params: dell-cpsd-hal-vcenter-adapter
    Returns: None

    """
    service = "dell-cpsd-hal-vcenter-adapter"

    print(test_sysdef_install.__doc__)

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
    assert my_return_status == 0, " %s did not install" % service
    



@pytest.mark.tls_enabled_stop_start
def test_sysdef_serviceup(setup):
    """
    Title: Verify the dell-cpsd-hal-vcenter-adapter service containers are UP
    Description: This test verifies that the dell-cpsd-hal-vcenter-adapter container is up
    Params: dell-cpsd-hal-vcenter-adapter
    Returns: None

    """
    service = "dell-cpsd-hal-vcenter-adapter"

    print(test_sysdef_serviceup.__doc__)

    assert service, "container name not found"

    sendcommand = "docker ps --filter name=" + service + "  --format '{{.Status}}' | awk '{print $1}'"
    

    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                         password=setup['password'],
                                                         command=sendcommand, return_output=True)

    assert "Up" in my_return_status, " %s is not up" % service

