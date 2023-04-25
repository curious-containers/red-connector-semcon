import json
import os
import sys
import jsonschema
from functools import wraps
from urllib.parse import urljoin

import requests


CONNECT_TIMEOUT = 12.05
READ_TIMEOUT = 1000
DEFAULT_TIMEOUT = (CONNECT_TIMEOUT, READ_TIMEOUT)

OAUTH_ENDPOINT = '/oauth/token'
OAUTH_GRANTTYPE = 'client_credentials'


class ListingError(Exception):
    pass


def graceful_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except jsonschema.exceptions.ValidationError as e:
            if hasattr(e, 'context'):
                print('{}:{}Context: {}'.format(repr(e), os.linesep, e.context), file=sys.stderr)
                exit(1)

            print(repr(e), file=sys.stderr)
            exit(2)

        except Exception as e:
            print('{}:{}{}'.format(repr(e), os.linesep, e), file=sys.stderr)
            exit(3)

    return wrapper


def http_method_func(access, default):
    http_method = access.get('method', default).lower()

    if http_method == 'get':
        return requests.get
    if http_method == 'put':
        return requests.put
    if http_method == 'post':
        return requests.post

    raise Exception('Invalid HTTP method: {}'.format(http_method))


def oauth_token(access, verify, default_scope='read'):
    if not access.get('auth'):
        return None
    
    url = urljoin(access['url'], OAUTH_ENDPOINT)
    auth = access['auth']
    
    client_id = auth['username']
    client_secret = auth['password']
    scope = auth.get('scope', default_scope)
    
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": OAUTH_GRANTTYPE,
        "scope": scope
    }
    
    r = requests.post(
        url,
        json=data,
        verify=verify,
        stream=True,
        timeout=(CONNECT_TIMEOUT, READ_TIMEOUT)
    )
    r.raise_for_status()
    
    access_token = r.json().get('access_token')
    return access_token

def bearer_auth_header(access_token):
    if access_token is None:
        return None
    
    headers = {
        'Authorization': f"Bearer {access_token}"
    }
    return headers


def fetch_file(file_path, url, http_method, headers, params, verify=True, data_key=None):
    """
    Fetches the given file. Assumes that the directory in which this file is stored is already present in the local
    filesystem.

    :param file_path: The path where the file content should be stored
    :param url: The url from where to fetch the file
    :param http_method: An function object, which returns a requests result,
    if called with (url, headers=headers, params=params, verify=verify, stream=True)
    :param headers: The request headers, which will be send with the http request.
    :param params: The parameters, which will be send with the http request.
    :param verify: A boolean indicating if SSL Certification should be used.
    :param data_key: The key to index the json data. If None no key will be used.

    :raise requests.exceptions.HTTPError: If the HTTP requests could not be resolved correctly.
    """

    r = http_method(
        url,
        headers=headers,
        params=params,
        verify=verify,
        stream=True,
        timeout=(CONNECT_TIMEOUT, READ_TIMEOUT)
    )
    r.raise_for_status()
    
    data = r.json()
    
    if data_key is not None:
        if 'data' in data:
            data = data['data']
        if 'content' in data:
            data = data['content']
        if isinstance(data, dict):
            data = data[data_key]
        else:
            raise InvalidDataException('Data key can only be fetched from a dictonary.')

    with open(file_path, 'w') as f:
        if isinstance(data, str) and not file_path.endswith('.json'):  # dump strings as plain files. Not as json.
            f.write(data)
        else:
            json.dump(data, f)

    r.raise_for_status()


def build_path(base_path, listing, key):
    """
    Builds a list of string representing urls, which are build by the base_url and the subfiles and subdirectories
    inside the listing. The resulting urls are written to the listing with the key 'complete_url'

    :param base_path: A string containing the base path
    :param listing: A dictionary containing information about the directory structure of the given base_url
    :param key: The key under which the complete url is stored
    """

    for sub in listing:
        path = os.path.join(base_path, sub['basename'])
        sub[key] = path
        if sub['class'] == 'Directory':
            if 'listing' in sub:
                build_path(path, sub['listing'], key)


class InvalidDataException(Exception):
    pass
