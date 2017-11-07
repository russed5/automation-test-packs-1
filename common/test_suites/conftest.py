# Copyright © 2017 Dell Inc. or its subsidiaries.  All Rights Reserved
import af_support_tools
import os
import pytest
import subprocess
import requests
import json
import socket


@pytest.fixture(autouse=True, scope='session')
def cpsd_common_properties():
    # Update env.ini file with cpsd common properties at runtime
    my_data_file = os.environ.get('AF_RESOURCES_PATH') + '/cpsd-common/cpsd_common.properties'
    af_support_tools.set_config_file_property_by_data_file(my_data_file)


# def get_certificates_for_tls():
#     result = subprocess.Popen('./tls-enable.sh', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#     result_status = result.wait()
#     print(result_status)


@pytest.fixture(autouse=True, scope='session')
def get_tls_certs():
    hostname = socket.gethostname()
    print('Getting tls certs from tls_service')
    tls_file = '/usr/local/share/ca-certificates/' + hostname + '.ca.crt'
    if os.path.isfile(tls_file):
        print('TLS Certs exist already')
    else:
        ex = subprocess.Popen('chmod +x tls_enable.sh', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        ex = ex.wait()
        o = subprocess.check_output('ls')
        with open(tls_file, 'w') as f:
            f.write(o.decode("utf-8"))
        print(o)
        p = subprocess.check_output('./test_suites/tls_enable.sh')
        # p = subprocess.Popen('./tls-enable.sh', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # p.wait()
        # out, err = p.communicate()
        print(p)
    print('Creating test user in Rabbitmq')
    r = requests.put("https://pam-service.cpsd.dell:7002/pam-service/v1/amqp/users", cert=(
        '/usr/local/share/ca-certificates/' + hostname + '.crt',
        '/usr/local/share/ca-certificates/' + hostname + '.key'),
                     verify='/usr/local/share/ca-certificates/cpsd.dell.ca.crt')

    assert r.status_code == 200, "Error---Rabbitmq credentials for test not created"
