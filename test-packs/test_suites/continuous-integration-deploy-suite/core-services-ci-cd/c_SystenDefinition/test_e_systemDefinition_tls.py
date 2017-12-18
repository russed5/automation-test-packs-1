#!/usr/bin/python
# Author: Ragubathy Jayaraju
# Revision: 1.0
# Code Reviewed by: Azar
# Description: Testing the Converged System Components Rest API V's JSON input file
#
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information


import af_support_tools
import pytest
import requests
import json
import socket


@pytest.mark.sds_tls_enabled
def test_sds_consul():
    """
            Title: sds TLS test
            Description: This test verify SystemDefinition Services is running in TLS protocol
            Params: None
            Returns: None
        """    
    sysdef = 'system-definition-service.cpsd.dell'
    consul_url = 'https://' + sysdef + ':8080/about'
    print('Console URL : ' + consul_url)
    resp = af_support_tools.scomm_get_request(get_url=consul_url)
    print("---------------------------")
    print(resp[1])
    print("---------------------------")

    assert resp[0] == '200', "Request has not been acknowledged as expected."