# Copyright © 2017 Dell Inc. or its subsidiaries.  All Rights Reserved
. $HOME/af_env.sh
py3clean .
export AF_TEST_SUITE_NAME='System definition service test'
python /home/autouser/PycharmProjects/auto-framework/test_suites/system_definition_service/test_system_definition_a_ConvergedSystemAdditionRequestedAMQP_Negative.py