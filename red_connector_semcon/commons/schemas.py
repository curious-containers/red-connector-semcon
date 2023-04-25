from copy import deepcopy


_HTTP_METHODS = ['Get', 'Put', 'Post']
_HTTP_METHODS_ENUMS = deepcopy(_HTTP_METHODS) + [m.lower() for m in _HTTP_METHODS] + [m.upper() for m in _HTTP_METHODS]

_OUTPUT_FORMAT_ENUMS = ['plain', 'full', 'meta', 'validation']

SCHEMA = {
    'type': 'object',
    'properties': {
        'url': {'type': 'string'},
        'method': {'enum': _HTTP_METHODS_ENUMS},
        'auth': {
            'type': 'object',
            'properties': {
                'username': {'type': 'string'},
                'password': {'type': 'string'},
                'scope': {'type': 'string'}
            },
            'additionalProperties': False,
            'required': ['username', 'password']
        },
        'resource': {
            'type': 'object',
            'properties': {
                'id': {'type': 'string'},
                'dri': {'type': 'string'},
                'schemaDri': {'type': 'string'},
                'tableName': {'type': 'string'},
                'key': {'type': 'string'},
                'format': {'enum': _OUTPUT_FORMAT_ENUMS}
            },
            'additionalProperties': False
        },
        'disableSSLVerification': {'type': 'boolean'}
    },
    'additionalProperties': False,
    'required': ['url']
}
