# Copyright © 2017 Dell Inc. or its subsidiaries.  All Rights Reserved
. $HOME/af_env.sh
py3clean .
export AF_TEST_SUITE_NAME='FRU MVP'
python $AF_RUN_JOBS_PATH/run_fru_mvp_test_suite.py
export AF_TEST_SUITE_NAME='Test Suite Name Not Set'