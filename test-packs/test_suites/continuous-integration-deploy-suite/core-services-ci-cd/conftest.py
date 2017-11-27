#!/usr/bin/python
# Copyright © 2017 Dell Inc. or its subsidiaries.  All Rights Reserved
import pytest
import json
import af_support_tools


# class NoMessageConsumedException(Exception):
#     def __init__(self, message):
#         super().__init__(self, message)
#
#
# # class Connection:
# #     def __init__(self, ip_address, username, password):
# #         self.ipAddress = ip_address
# #         self.username = username
# #         self.password = password
# #
# #
# # class RmqConnection(Connection):
# #     def __init__(self, ip_address, username, password, port):
# #         super().__init__(ip_address, username, password)
# #         self.port = port
# #         self.url = "http://{}:15672".format(self.ipAddress)
#
#
# class Message:
#     def __init__(self, headers, payload, payload_type):
#         self.headers = headers;
#         self.payload = payload
#         self.payloadType = payload_type
#
#
# class JsonMessage(Message):
#     def __init__(self, headers, payload):
#         super().__init__(headers, payload, payload_type='json')


# class RabbitMq:
#     def __init__(self, connection):
#         self.connection = connection
#
#     def bind_queue_with_key(self, exchange, queue, routing_key):
#         self.delete_queue(queue)
#         print("INFO: binding queue {} to exchange {} with key {}".format(queue, exchange, routing_key))
#         af_support_tools.rmq_bind_queue(host=self.connection.ipAddress, port=self.connection.port,
#                                         rmq_username=self.connection.username,rmq_password=self.connection.password,
#                                         queue=queue, exchange=exchange, routing_key=routing_key, ssl_enabled=True)
#
#     def delete_queue(self, queue):
#         print("INFO: deleting queue", queue)
#         af_support_tools.rmq_delete_queue(self.connection.ipAddress, self.connection.port, self.connection.username,
#                                           self.connection.password, queue, ssl_enabled=True)
#
#     def consume_message_from_queue(self, queue):
#         message_found = af_support_tools.rmq_wait_for_messages_in_queue(host=self.connection.ipAddress, port=self.connection.port,
#                                                                        rmq_username=self.connection.username, rmq_password=self.connection.password,
#                                                                        queue=queue, wait_time=300, check_interval=5, ssl_enabled=True)
#         if message_found:
#             message = af_support_tools.rmq_consume_message(host=self.connection.ipAddress, port=self.connection.port,
#                                                            rmq_username=self.connection.username, rmq_password=self.connection.password,
#                                                            queue=queue, ssl_enabled=True)
#             print("INFO message consumed from queue {}: {}".format(queue, message))
#             return json.loads(message, encoding='utf-8')
#         else:
#             raise NoMessageConsumedException("failed to consume message from queue: \'{}\'".format(queue))
#
#     def publish_message(self, exchange, routing_key, message):
#         af_support_tools.rmq_publish_message(host=self.connection.ipAddress, port=self.connection.port,
#                                              rmq_username=self.connection.username, rmq_password=self.connection.password,
#                                              exchange=exchange, routing_key=routing_key,
#                                              headers=message.headers, payload=message.payload, payload_type=message.payloadType, ssl_enabled=True)
#
#





# @pytest.fixture(scope="session")
# def rabbitMq(hostIpAddress):
#     from common_libs import cpsd
# 
#     port = 5671
# 
#     rmq_connection = RmqConnection(port)
#     return RabbitMq(rmq_connection)


@pytest.fixture(scope="session")
def setup():
    parameters = {}
    env_file = 'env.ini'
    ipaddress = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                          property='hostname')
    parameters['IP'] = ipaddress
    cli_user = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                         property='username')
    parameters['user'] = cli_user
    cli_password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                             property='password')
    parameters['password'] = cli_password
    return parameters
