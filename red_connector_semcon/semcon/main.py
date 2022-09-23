from collections import OrderedDict

from red_connector_semcon.commons.cli_modes import cli_modes
from red_connector_semcon.version import VERSION

from red_connector_semcon.semcon.send_receive_file import receive_file, receive_file_validate
from red_connector_semcon.semcon.send_receive_file import RECEIVE_FILE_DESCRIPTION, RECEIVE_FILE_VALIDATE_DESCRIPTION
from red_connector_semcon.semcon.send_receive_file import send_file, send_file_validate
from red_connector_semcon.semcon.send_receive_file import SEND_FILE_DESCRIPTION, SEND_FILE_VALIDATE_DESCRIPTION


CLI_VERSION = '1'
SCRIPT_NAME = 'red-connector-semcon'
DESCRIPTION = 'RED Connector Semcon'
TITLE = 'modes'

MODES = OrderedDict([
    ('cli-version', {'main': lambda: print(CLI_VERSION), 'description': 'RED connector CLI version.'}),
    ('receive-file', {'main': receive_file, 'description': RECEIVE_FILE_DESCRIPTION}),
    ('receive-file-validate', {'main': receive_file_validate, 'description': RECEIVE_FILE_VALIDATE_DESCRIPTION}),
    ('send-file', {'main': send_file, 'description': SEND_FILE_DESCRIPTION}),
    ('send-file-validate', {'main': send_file_validate, 'description': SEND_FILE_VALIDATE_DESCRIPTION}),
])


def main():
    cli_modes(SCRIPT_NAME, TITLE, DESCRIPTION, MODES, VERSION)
