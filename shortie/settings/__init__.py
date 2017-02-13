import os
import importlib

settings = importlib.import_module(
    os.getenv('SHORTIE_SETTINGS', '.development'),
    package='shortie.settings'
)
