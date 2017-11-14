#!/usr/bin/python
# Author: Shane McGowan
# Revision: 1.0
# Code Reviewed by: Toqeer Akhtar
# Description: Testing the Converged System Components Rest API V's JSON input file
#
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information

import time
import sys
import af_support_tools
import pytest
import string
import requests
import json
import os



@pytest.mark.sds_tls_enabled
def test_sds_consul():
    """
            Title: sds Registered in con
            Description: This test verify SystemDefinition Services is running in TLS protocol
            Params: None
            Returns: None
        """
    err = []


    consul_url = 'https://ragu89.mpe.lab.vce.com:8088/about'
    resp = requests.get(consul_url, verify= '/usr/local/share/ca-certificates/system-definition-service.cpsd.dell.crt')
    data = json.loads(resp.text)

    assert resp.status_code == 200, "Request has not been acknowledged as expected."

