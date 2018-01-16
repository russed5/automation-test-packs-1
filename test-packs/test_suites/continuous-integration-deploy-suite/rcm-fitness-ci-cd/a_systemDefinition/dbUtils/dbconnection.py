#!/usr/bin/python
# Author: Shivananda H R
# Revision: 1.0
# Code Reviewed by: Renukaprasad CB
# Description: Util file for system definition database connection establishment
#
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information


import pytest
import af_support_tools
#import socket
#import test_suites.config_files
#import configparser
#import os


@pytest.mark.db_test
def test_db(query,dbname):
    """
            Title: sds DB test
            Description: This test verify DB connection for SDS
            Params: query
            Returns: db Response
    """
    readFromCommand = query
    writetofilecmd = "echo \"" + readFromCommand + "\" > /tmp/sqlRead.txt"
    writetodockerfilecommand = 'docker cp /tmp/sqlRead.txt postgres:/tmp/sqlRead.txt'
    execSQLCommand = "docker exec -i postgres sh -c \'su - postgres sh -c \"psql \\\"dbname=" + dbname + " options=--search_path=public\\\" -t -f /tmp/sqlRead.txt\"\'"
    # Set config ini file name
    env_file = 'env.ini'
    # Test VM Details
    ipaddress = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',property='hostname')
    cli_username = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',property='username')
    cli_password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',property='password')
    try:

        af_support_tools.send_ssh_command(
            host=ipaddress,
            username=cli_username,
            password=cli_password,
            command=writetofilecmd,
            return_output=True)

        af_support_tools.send_ssh_command(
            host=ipaddress,
            username=cli_username,
            password=cli_password,
            command=writetodockerfilecommand,
            return_output=True)

        result = af_support_tools.send_ssh_command(
            host=ipaddress,
            username=cli_username,
            password=cli_password,
            command=execSQLCommand,
            return_output=True)

        print(result)

        return result

    except Exception as err:
        # Return code error
        print(err, '\n')
        raise Exception(err)