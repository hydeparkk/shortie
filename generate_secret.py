import binascii
import json
import os

secret_file_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'shortie',
    'settings',
    '.prod_shortie_secret'
)

if not os.path.isfile(secret_file_path):
    with open(secret_file_path, 'w') as f:
        json.dump(
            {'secret': binascii.hexlify(os.urandom(24)).decode('utf-8')}, f
        )
