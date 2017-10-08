from common_libs import cpsd
import pytest

@pytest.mark.tls_test
def test_rmq_creds():
    print("About to get creds....")
    creds = cpsd.get_rmq_credentials()
    print("RabbitMQ User is ", creds['rmq_user'])
    print("RabbitMQ Password is", creds['rmq_password'])
    assert creds['rmq_user'], "rmq user not returned"
    assert creds['rmq_password'], "rmq password not returned"
