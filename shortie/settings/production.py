# flake8: noqa
import json
import os

from .base import *

secret_file_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '.prod_shortie_secret'
)

with open(secret_file_path, 'r') as f:
    secret = json.load(f).get('secret')

SHORTIE_SECRET = secret
