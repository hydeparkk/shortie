import os

DEBUG = bool(os.getenv('SHORTIE_DEBUG', False))

MONGO_URL = os.getenv('SHORTIE_MONGO_URL', 'mongodb://mongodb:27017')
DATABASE = os.getenv('SHORTIE_DATABASE', 'shortie')

SHORTIE_SECRET = 'change_me!!!'

# time in seconds
SESSION_LENGTH = 3600
