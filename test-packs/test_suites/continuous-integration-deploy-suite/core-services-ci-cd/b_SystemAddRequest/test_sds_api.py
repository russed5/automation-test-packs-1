#!/u#!/usr/bin/python
# Author: Toqeer Akhtar
# Revision: 1.0
# Code Reviewed by:
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
            Title: sds Registered in con
            Description: This test verify SystemDefinition Services is running in TLS protocol
            Params: None
            Returns: None
        """
    consulHost = 'consul.cpsd.dell'
    sysdef = 'system-definition-service.cpsd.dell'
    hostname = socket.gethostname()
    err = []

    print('HHHHHHHHHH')
    #consul_url = 'https://' + consulHost + ':8500/v1/catalog/services'
    #resp = requests.get(consul_url, verify= '/usr/local/share/ca-certificates/taf.cpsd.dell.ca.crt')

    consul_url = 'https://' + sysdef + ':8080/about'
    resp = requests.get(consul_url, cert=(
        '/usr/local/share/ca-certificates/' + hostname + '.crt',
        '/usr/local/share/ca-certificates/' + hostname + '.key'),
                     verify='/usr/local/share/ca-certificates/cpsd.dell.ca.crt')
    print("---------------------------")
    print(resp.text)
    #data = json.loads(resp.text)
    #print(data)
    print("---------------------------")

    assert resp.status_code == 200, "Request has not been acknowledged as expected."




