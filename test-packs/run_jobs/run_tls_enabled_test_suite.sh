TEST_SUITE_NAME='TLS ENABLED MVP'
REPORT_NAME='tls_enabled_mvp_report'
SEARCH_PATH=$AF_TEST_SUITE_PATH/
MARKER='tls_enabled'

. $HOME/af_env.sh
py3clean .
export AF_TEST_SUITE_NAME=$TEST_SUITE_NAME
py.test $SEARCH_PATH -m "$MARKER" --html $AF_REPORTS_PATH/all/$REPORT_NAME.html --self-contained-html --json $AF_REPORTS_PATH/all/$REPORT_NAME.json --junit-xml $AF_REPORTS_PATH/all/$REPORT_NAME.xml
py.test $SEARCH_PATH -m "tls_enabled_stop_start" --html $AF_REPORTS_PATH/all/$REPORT_NAME.html --self-contained-html --json $AF_REPORTS_PATH/all/$REPORT_NAME.json --junit-xml $AF_REPORTS_PATH/all/$REPORT_NAME.xml
export AF_TEST_SUITE_NAME='Test Suite Name Not Set'
