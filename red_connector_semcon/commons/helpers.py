import os
import sys
import jsonschema
from functools import wraps
from shutil import which

import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth


CONNECT_TIMEOUT = 12.05
READ_TIMEOUT = 1000
DEFAULT_TIMEOUT = (CONNECT_TIMEOUT, READ_TIMEOUT)


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


def _get_working_executable(executables):
    """
    Returns the first executable that can be found in PATH.
    :param executables: A list of strings defining executables to test
    :return: A string defining a executable in executables
    :raise Exception: If no executable was found in PATH
    """
    for executable in executables:
        if which(executable):
            return executable

    raise Exception('One of the following executables must be present in PATH: {}'.format(
        executables
    ))


def http_method_func(access, default):
    http_method = access.get('method', default).lower()

    if http_method == 'get':
        return requests.get
    if http_method == 'put':
        return requests.put
    if http_method == 'post':
        return requests.post

    raise Exception('Invalid HTTP method: {}'.format(http_method))


def auth_method_obj(access):
    if not access.get('auth'):
        return None

    auth = access['auth']
    auth_method = auth.get('method', 'basic').lower()

    if auth_method == 'basic':
        return HTTPBasicAuth(
            auth['username'],
            auth['password']
        )
    if auth_method == 'digest':
        return HTTPDigestAuth(
            auth['username'],
            auth['password']
        )

    raise Exception('Invalid auth method: {}'.format(auth_method))


def fetch_file(file_path, url, http_method, auth_method, verify=True):
    """
    Fetches the given file. Assumes that the directory in which this file is stored is already present in the local
    filesystem.

    :param file_path: The path where the file content should be stored
    :param url: The url from where to fetch the file
    :param http_method: An function object, which returns a requests result,
    if called with (url, auth=auth_method, verify=verify, stream=True)
    :param auth_method: An auth_method, which can be used as parameter for requests.http_method
    :param verify: A boolean indicating if SSL Certification should be used.

    :raise requests.exceptions.HTTPError: If the HTTP requests could not be resolved correctly.
    """

    r = http_method(
        url,
        auth=auth_method,
        verify=verify,
        stream=True,
        timeout=(CONNECT_TIMEOUT, READ_TIMEOUT)
    )
    r.raise_for_status()

    with open(file_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=4096):
            if chunk:
                f.write(chunk)

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
