#!/usr/bin/python
# Author: Shane McGowan
# Revision: 1.0
# Code Reviewed by: Toqeer Akhtar
# Description: Testing the Converged System Components Rest API V's JSON input file
#
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information


import pytest
import requests
import json



@pytest.mark.sds_tls_enabled
def test_sds_consul():
    """
            Title: sds Registered in con
            Description: This test verify SystemDefinition Services is running in TLS protocol
            Params: None
            Returns: None
        """
    err = []

    print('HHHHHHHHHH')
    consul_url = 'https://ragu89.mpe.lab.vce.com:8088/about'
    resp = requests.get(consul_url, verify= '/usr/local/share/ca-certificates/system-definition-service.cpsd.dell.crt')
    print("---------------------------")
    print(resp.text)
    data = json.loads(resp.text)
    print(data)
    print("---------------------------")

    assert resp.status_code == 200, "Request has not been acknowledged as expected."

