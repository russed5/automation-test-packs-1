import af_support_tools
import pytest
import requests
import socket
import json

@pytest.mark.demo_test
def test_sysdef_serviceup(setup):
    """
    Title: Verify the sds services containers are UP
    Description: This test verifies that the sd container is up
    Params: dell-cpsd-core-system-definition-service
    Returns: None
    """
    service = "dell-cpsd-core-system-definition-service"

    print(test_sysdef_serviceup.__doc__)

    assert service, "container name not found"

    sendcommand = "docker ps --filter name=" + service + "  --format '{{.Status}}' | awk '{print $1}'"

    print (setup['IP'])
    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                         password=setup['password'],
                                                         command=sendcommand, return_output=True)

    assert "Up" in my_return_status, " %s is not up" % service

#@pytest.mark.ta_test
#def test_pam_createRMQuser():
#
#     """
#         Title: Creating RMQ username and password
#         Description: This test is to verfiy pam service creating a Rabbit MQ username and password using
#          a simple put request
#     """
#     print(test_pam_createRMQuser.__doc__)
#     err =[]
#     hostname = socket.gethostname()
#
#     r = requests.put("https://pam-service.cpsd.dell:7002/pam-service/v1/amqp/users",
#                      cert=('/usr/local/share/ca-certificates/taf.cpsd.dell.crt',
#                            '/usr/local/share/ca-certificates/taf.cpsd.dell.key'),
#                      verify='/usr/local/share/ca-certificates/cpsd.dell.ca.crt')
#
#     assert r.status_code == 200, "Error---Request has not been acknowledged as expected."
#
#     data = json.loads(r.text)
#     print(data)
#
#     if (data['status']['status_code'] != 201 and
#                 data['status']['status_message'] != "Created" and
#                 data['response']['amqp']['username'] != hostname):
#         err.append("Error--- amqp username is not correct")

@pytest.mark.demo_test
def test_bindrmq_queue(setup):

    af_support_tools.rmq_bind_queue(host='amqp' , port=5671, ssl_enabled=True, queue='test.TA.system.list.request',
                                    exchange='exchange.dell.cpsd.syds.system.definition.request',
                                    routing_key='#')
    assert True , 'Failed'
@pytest.mark.demo_test
def test_deletermq_queue():
        af_support_tools.rmq_delete_queue(host='amqp', port=5671, ssl_enabled=True, queue='test.TA.system.list.request')

        assert True, 'Delet queue failed'
