# Copyright © 2017 Dell Inc. or its subsidiaries.  All Rights Reserved
import os
os.system('py.test $AF_TEST_SUITE_PATH/ -m "fru_mvp_extended" --html $AF_REPORTS_PATH/all/fru_mvp_extended_test_suite_report.html --self-contained-html --json $AF_REPORTS_PATH/all/fru_mvp_extended_test_suite_report.json --junit-xml $AF_REPORTS_PATH/all/fru_mvp_extended_test_suite_report.xml')