# Copyright © 2017 Dell Inc. or its subsidiaries.  All Rights Reserved

TEST_SUITE_NAME='TLS test for System definition service'
REPORT_NAME='tls_enabled_sds_report'
SEARCH_PATH=$AF_TEST_SUITE_PATH/continuous-integration-deploy-suite/core-services-ci-cd/c_SystenDefinition/
MARKER='sds_tls_enabled'

. $HOME/af_env.sh
py3clean .
export AF_TEST_SUITE_NAME=$TEST_SUITE_NAME
py.test $SEARCH_PATH -m "$MARKER" --html $AF_REPORTS_PATH/all/$REPORT_NAME.html --self-contained-html --json $AF_REPORTS_PATH/all/$REPORT_NAME.json --junit-xml $AF_REPORTS_PATH/all/$REPORT_NAME.xml
py.test $SEARCH_PATH -m "tls_enabled_stop_start" --html $AF_REPORTS_PATH/all/$REPORT_NAME.html --self-contained-html --json $AF_REPORTS_PATH/all/$REPORT_NAME.json --junit-xml $AF_REPORTS_PATH/all/$REPORT_NAME.xml
export AF_TEST_SUITE_NAME='Test Suite Name Not Set'
