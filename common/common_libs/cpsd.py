# Copyright © 2017 Dell Inc. or its subsidiaries.  All Rights Reserved
import af_support_tools
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_der_public_key
import datetime
import json
import time
import requests

class props(object):
    # Set env.ini file name
    env_file = 'env.ini'
    
    # Set CPSD common global vars
    # Base OS    
    base_hostname = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')
    base_username = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='username')
    base_password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='password')


def get_rmq_credentials():

    r = requests.put("https://pam-service.cpsd.dell:7002/pam-service/v1/amqp/users",
                     cert=('/usr/local/share/ca-certificates/taf.cpsd.dell.crt',
                           '/usr/local/share/ca-certificates/taf.cpsd.dell.key'),
                     verify='/usr/local/share/ca-certificates/cpsd.dell.ca.crt')

    assert r.status_code == 200, "Error---Rabbitmq credentials not returned"
    data = json.loads(r.text)
    rmq_user =data['response']['amqp']['username']    

    return {'rmq_user': rmq_user}


def cs_encrypt_credential_elements(my_json):
    '''
    Function designed to find all credential elements and encrypt the username, password and community values 
    '''
    try:
        # Set CPSD Props
        props()
        
        # Get CS Public Key
        my_public_key = cs_get_public_key()          

        # Ensure proper dictionary/json format
        if type(my_json) is not dict:
            my_json = json.loads(my_json)
    
        # Find Credential Elements objects
        my_credential_elements = find_in_obj(my_json, 'credentialElements', path=None)
        credential_elements = False
        
        # Step through Credential Elements objects
        for item in my_credential_elements:
            credential_elements = True
            print('Credential Elements Found')
            print('Credential Elements Path: %s' % item)
            my_return_value = get_item_value(my_json, item)
            print('Credential Elements: %s' % my_return_value)
      
            # Update 'username'
            my_return_value = get_item_value(my_json, item)
            if 'username' in my_return_value:
                new_item = item[:]
                new_item.append('username')
                my_return_value = get_item_value(my_json, new_item)
                print('Username: %s' % my_return_value)
                encrypted_username = cs_encrypt_text(my_return_value, my_public_key)
                print('Username: %s' % encrypted_username)

                val = my_json
                keys = new_item
                for key in keys[0:-1]:
                    val = val[key]
                val[keys[-1]] = encrypted_username

            # Update 'password'
            my_return_value = get_item_value(my_json, item)
            if 'password' in my_return_value:
                new_item = item[:]
                new_item.append('password')
                my_return_value = get_item_value(my_json, new_item)
                print('Password: %s' % my_return_value)
                encrypted_password = cs_encrypt_text(my_return_value, my_public_key)
                print('Password: %s' % encrypted_password)

                val = my_json
                keys = new_item
                for key in keys[0:-1]:
                    val = val[key]
                val[keys[-1]] = encrypted_password

            # Update 'community'
            my_return_value = get_item_value(my_json, item)            
            if 'community' in my_return_value:
                new_item = item[:]
                new_item.append('community')
                my_return_value = get_item_value(my_json, new_item)
                print('Community: %s' % my_return_value)
                encrypted_community = cs_encrypt_text(my_return_value, my_public_key)
                print('Community: %s' % encrypted_community)

                val = my_json
                keys = new_item
                for key in keys[0:-1]:
                    val = val[key]
                val[keys[-1]] = encrypted_community

        if credential_elements == False:
            print('No Credential Elements Found')
        
        my_json = json.dumps(my_json)
        
        return(my_json)
    except Exception as e:
        print(e)
        return   

def find_in_obj(obj, condition, path=None):
    '''
    Function designed to find full path to a nested dictionary key when the key is at an unknown level
    '''
    if path is None:
        path = []

    # In case this is a list
    if isinstance(obj, list):
        for index, value in enumerate(obj):
            new_path = list(path)
            new_path.append(index)
            for result in find_in_obj(value, condition, path=new_path):
                yield result

    # In case this is a dictionary
    if isinstance(obj, dict):
        for key, value in obj.items():
            new_path = list(path)
            new_path.append(key)
            for result in find_in_obj(value, condition, path=new_path):
                yield result

            if condition == key:
                new_path = list(path)
                new_path.append(key)
                yield new_path

def get_item_value(response, path):
    for item in path:
        response = response[item]
    return response
    
def cs_get_public_key():
    #import cpsd
    print('Get Public Key')
    # Get Rabbit MQ Certs    
    af_support_tools.rmq_get_server_side_certs(host_hostname=props.base_hostname, host_username=props.base_username, host_password=props.base_password, host_port=22, rmq_certs_path=props.rmq_cert_path)
    # Set Payload
    the_payload = '{"messageProperties": {"timestamp": "' + datetime.datetime.now().isoformat() + '", "correlationId": "cpsd-getPublicKey", "replyTo": "dell.cpsd.com"}}'
    # Bind Queue
    my_return_value = af_support_tools.rmq_bind_queue(host=props.base_hostname, port=props.rmq_port, rmq_username=props.rmq_username, rmq_password=props.rmq_password, queue='queue.dell.cpsd.credential.public.key.response', exchange='exchange.dell.cpsd.cms.credentials.response', routing_key='dell.cpsd.credential.response.public.key|dell.cpsd.com', ssl_enabled=True)
    # Purge Queue
    my_return_value = af_support_tools.rmq_purge_queue(host=props.base_hostname, port=props.rmq_port, rmq_username=props.rmq_username, rmq_password=props.rmq_password, queue='queue.dell.cpsd.credential.public.key.response', ssl_enabled=props.rmq_ssl_enabled)
    # Publish Message Requesting Public Key
    my_return_value = af_support_tools.rmq_publish_message(host=props.base_hostname, port=props.rmq_port, rmq_username=props.rmq_username, rmq_password=props.rmq_password, exchange='exchange.dell.cpsd.cms.credentials.request', routing_key='dell.cpsd.credential.request.public.key', headers={'__TypeId__': 'com.dell.cpsd.credential.model.api.request.PublicKeyRequest'}, payload=the_payload, ssl_enabled=props.rmq_ssl_enabled)
    # Wait for Reply
    my_return_value = af_support_tools.rmq_wait_for_messages_in_queue(host=props.base_hostname, port=props.rmq_port, rmq_username=props.rmq_username, rmq_password=props.rmq_password, queue='queue.dell.cpsd.credential.public.key.response', number_of_messages=1, wait_time=300, check_interval=15, ssl_enabled=props.rmq_ssl_enabled)

    #Consume Message
    my_return_value = af_support_tools.rmq_consume_message(host=props.base_hostname, port=props.rmq_port, rmq_username=props.rmq_username, rmq_password=props.rmq_password, queue='queue.dell.cpsd.credential.public.key.response', ssl_enabled=props.rmq_ssl_enabled)
    # print('Public Key Response: %s' % my_return_value)
    # Convert the response string to json
    my_return_value = json.loads(my_return_value, encoding='utf-8')
    # Extract the Public Key from json
    my_public_key = my_return_value["encryptionParameters"]["publicKeyString"]
    print('Retrieved Public Key: %s' % my_public_key)

    # Return Public Key
    return(my_public_key)

def cs_generate_private_public_keys():
    my_private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend())
    my_public_key = my_private_key.public_key()

    return my_private_key, my_public_key
	
def cs_encrypt_text(my_text, my_public_key):
    # Encode Public Key
    keyBytes = base64.standard_b64decode(my_public_key)
    publicKey = load_der_public_key(keyBytes, backend=default_backend())
    # Encode Text
    my_text = my_text.encode('utf-8')
    # Encrypt Text
    ciphertext = publicKey.encrypt(my_text, padding.PKCS1v15())
    my_encrypted_text = base64.standard_b64encode(ciphertext)
    # Decode Text
    my_encrypted_text = my_encrypted_text.decode('utf-8')
    
    # Return Encrypted Text
    return(my_encrypted_text)
