# Copyright © 2017 Dell Inc. or its subsidiaries.  All Rights Reserved
. $HOME/af_env.sh
py3clean .
export AF_TEST_SUITE_NAME='System definition service test'
pytest $AF_TEST_SUITE_PATH/continuous-integration-deploy-suite/core-services-ci-cd/c_SystenDefinition/test_e_systemDefinition_tls.py
