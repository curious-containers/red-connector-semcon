import json
from argparse import ArgumentParser

import jsonschema

from red_connector_semcon.commons.schemas import SCHEMA
from red_connector_semcon.commons.helpers import http_method_func, oauth_token, bearer_auth_header, fetch_file, graceful_error,\
    DEFAULT_TIMEOUT

RECEIVE_FILE_DESCRIPTION = 'Receive input file from semantic container.'
RECEIVE_FILE_VALIDATE_DESCRIPTION = 'Validate access data for receive-file.'

SEND_FILE_DESCRIPTION = 'Send output file to semantic container.'
SEND_FILE_VALIDATE_DESCRIPTION = 'Validate access data for send-file.'


def _receive_file(access, local_file_path):
    with open(access) as f:
        access = json.load(f)

    verify = True
    if access.get('disableSSLVerification'):
        verify = False

    http_method = http_method_func(access, 'GET')
    access_token = oauth_token(access, verify)
    headers = bearer_auth_header(access_token)
    
    url = access['url']
    data_key = None
    params = {}
    
    if access.get('resource'):
        resource = access['resource']
        
        if resource.get('key'):
            data_key = resource['key']
        
        if resource.get('id'):
            url = url.strip('/') + f"/{resource['id']}"
            params['p'] = 'id'
        elif resource.get('dri'):
            url = url.strip('/') + f"/{resource['dri']}"
            params['p'] = 'dri'
        else:
            if resource.get('schemaDri'):
                params['schema_dri'] = resource['schemaDri']
            if resource.get('tableName'):
                params['table'] = resource['tableName']
        
        params['f'] = resource.get('format', 'plain')

    fetch_file(local_file_path, url, http_method, headers, params, verify, data_key)


def _receive_file_validate(access):
    with open(access) as f:
        access = json.load(f)

    jsonschema.validate(access, SCHEMA)


def _send_file(access, local_file_path):
    with open(access) as f:
        access = json.load(f)

    verify = True
    if access.get('disableSSLVerification'):
        verify = False

    http_method = http_method_func(access, 'POST')
    access_token = oauth_token(access, verify)
    headers = bearer_auth_header(access_token)
    
    data_key = None
    write_data = {}
    
    if access.get('resource'):
        resource = access['resource']
        
        if resource.get('key'):
            data_key = resource['key']
        
        if resource.get('dri'):
            write_data['dri'] = resource['dri']
        if resource.get('schemaDri'):
            write_data['schema_dri'] = resource['schemaDri']
        if resource.get('tableName'):
            write_data['table_name'] = resource['tableName']
    
    
    with open(local_file_path, 'rb') as f:
        content = json.loads(f.read())
        if data_key is None:
            write_data['content'] = content
        else:
            write_data['content'] = {
                data_key: content
            }
    print(write_data)
    
    r = http_method(
        access['url'],
        json=write_data,
        headers=headers,
        verify=verify,
        timeout=DEFAULT_TIMEOUT
    )
    r.raise_for_status()


def _send_file_validate(access):
    with open(access) as f:
        access = json.load(f)
    
    jsonschema.validate(access, SCHEMA)


@graceful_error
def receive_file():
    parser = ArgumentParser(description=RECEIVE_FILE_DESCRIPTION)
    parser.add_argument(
        'access', action='store', type=str, metavar='ACCESSFILE',
        help='Local path to ACCESSFILE in JSON format.'
    )
    parser.add_argument(
        'local_file_path', action='store', type=str, metavar='LOCALFILE',
        help='Local input file path.'
    )
    args = parser.parse_args()
    _receive_file(**args.__dict__)


@graceful_error
def receive_file_validate():
    parser = ArgumentParser(description=RECEIVE_FILE_VALIDATE_DESCRIPTION)
    parser.add_argument(
        'access', action='store', type=str, metavar='ACCESSFILE',
        help='Local path to ACCESSFILE in JSON format.'
    )
    args = parser.parse_args()
    _receive_file_validate(**args.__dict__)


@graceful_error
def send_file():
    parser = ArgumentParser(description=SEND_FILE_DESCRIPTION)
    parser.add_argument(
        'access', action='store', type=str, metavar='ACCESSFILE',
        help='Local path to ACCESSFILE in JSON format.'
    )
    parser.add_argument(
        'local_file_path', action='store', type=str, metavar='LOCALFILE',
        help='Local output file path.'
    )
    args = parser.parse_args()
    _send_file(**args.__dict__)


@graceful_error
def send_file_validate():
    parser = ArgumentParser(description=SEND_FILE_VALIDATE_DESCRIPTION)
    parser.add_argument(
        'access', action='store', type=str, metavar='ACCESSFILE',
        help='Local path to ACCESSFILE in JSON format.'
    )
    args = parser.parse_args()
    _send_file_validate(**args.__dict__)
