# Copyright © 2017 Dell Inc. or its subsidiaries.  All Rights Reserved
import af_support_tools
import os
import pytest
import subprocess
import requests
import json
import socket
import time

@pytest.fixture(autouse=True, scope='session')
def cpsd_common_properties():
    # Update env.ini file with cpsd common properties at runtime
    my_data_file = os.environ.get('AF_RESOURCES_PATH') + '/cpsd-common/cpsd_common.properties'
    af_support_tools.set_config_file_property_by_data_file(my_data_file)

#@pytest.fixture(autouse=True, scope='session')
#def get_tls_certs():
#    hostname = socket.gethostname()
#    print('Getting tls certs from tls_service')
#    tls_file = '/usr/local/share/ca-certificates/' + hostname + '.ca.crt'
#    if os.path.isfile(tls_file):
#        print('TLS Certs exist already')
#    else:
#        ex = subprocess.Popen('chmod +x tls_enable.sh', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#        ex = ex.wait()
#        p = subprocess.check_output('./test_suites/tls_enable.sh')
#        print(p)
#
#    print('Creating test user in Rabbitmq')
#    r = requests.put("https://pam-service.cpsd.dell:7002/pam-service/v1/amqp/users", cert=(
#        '/usr/local/share/ca-certificates/' + hostname + '.crt',
#        '/usr/local/share/ca-certificates/' + hostname + '.key'),
#                     verify='/usr/local/share/ca-certificates/cpsd.dell.ca.crt')
#
#    assert r.status_code == 200, "Error---Rabbitmq credentials for test not created"

@pytest.fixture(autouse=True, scope='session')
def scomm_deployment():
    """
    Function designed to demonstrate a function that requires scomm
    Example: my_return_value = scomm_required()
    """
    try:
        env_file = 'env.ini'
        my_hostname = af_support_tools.get_config_file_property(env_file, 'Base_OS', 'hostname')
        my_username = af_support_tools.get_config_file_property(env_file, 'Base_OS', 'username')
        my_password = af_support_tools.get_config_file_property(env_file, 'Base_OS', 'password')
        my_taf_username = 'autouser'
        my_taf_password = 'Password01!'

        #my_command = 'docker ps --filter name=taf-scomm --format \'{{.Status}}\' | awk \'{print $1}\''
        #docker_up = send_ssh_command(host=my_hostname, port=22, username=my_username, password=my_password, command=my_command, return_output=True)
        #docker_up = docker_up.strip()
        deploy_scomm = True
        try:
            url = 'http://' + my_hostname + ':19720/scomm-status'
            scomm_status = requests.get(url)
            if scomm_status.status_code == 200:
                deploy_scomm = False
        except Exception as e:
            print(e)
            deploy_scomm = True

        if deploy_scomm == True:
            # Deploy SCOMM
            print('Deploy SCOMM')
            my_command = 'systemctl start docker'
            ssh_return_value = af_support_tools.send_ssh_command(host=my_hostname, port=22, username=my_username, password=my_password, command=my_command, return_output=True)
            my_command = 'mkdir -p /root/images'
            ssh_return_value = af_support_tools.send_ssh_command(host=my_hostname, port=22, username=my_username, password=my_password, command=my_command, return_output=True)
            my_command = 'docker rm -f $(docker ps -a -q  --filter ancestor=cpsd-taf-scomm)'
            ssh_return_value = af_support_tools.send_ssh_command(host=my_hostname, port=22, username=my_username, password=my_password, command=my_command, return_output=True)
            my_command = 'docker rmi -f cpsd-taf-scomm'
            ssh_return_value = af_support_tools.send_ssh_command(host=my_hostname, port=22, username=my_username, password=my_password, command=my_command, return_output=True)
            my_command = 'curl -o /root/images/cpsd-taf-scomm http://artifactory.mpe.lab.vce.com:8080/artifactory/docker-dev-local/tar_files/cpsd-taf-scomm'
            ssh_return_value = af_support_tools.send_ssh_command(host=my_hostname, port=22, username=my_username, password=my_password, command=my_command, return_output=True)
            my_command = 'docker load -i /root/images/cpsd-taf-scomm'
            ssh_return_value = af_support_tools.send_ssh_command(host=my_hostname, port=22, username=my_username, password=my_password, command=my_command, return_output=True)
            my_command = 'docker run -d -h taf-scomm.cpsd.dell --dns=172.17.0.1 -p 2223:22 -p 19720:19720 --name cpsd-taf-scomm cpsd-taf-scomm'
            ssh_return_value = af_support_tools.send_ssh_command(host=my_hostname, port=22, username=my_username, password=my_password, command=my_command, return_output=True)
            time.sleep(15)
            my_command = '. scomm_env.sh;nohup python $SCOMM_BASE_PATH/scomm_api.py &'
            ssh_return_value = af_support_tools.send_ssh_command(host=my_hostname, port=2223, username=my_taf_username, password=my_taf_password, command=my_command, return_output=False)
            time.sleep(15)
            # This should be replaced with an API call
            # Run tls_enable.sh
            my_command = '. $SCOMM_BASE_PATH/libs/tls_enable.sh'
            ssh_return_value = af_support_tools.send_ssh_command(host=my_hostname, port=2223, username=my_taf_username, password=my_taf_password, command=my_command, return_output=True)
            print(ssh_return_value)
        else:
            # SCOMM already deployed
            print('SCOMM already deployed')
            return

        return
    except Exception as e:
        print(e)
        raise ValueError('A very specific bad thing happened.')
