# -*- coding: utf-8 -*-
"""Create an application instance."""
from flask.helpers import get_debug_flag

from dais_pcto.app import create_app
from dais_pcto.settings import DevConfig

CONFIG = DevConfig

app = create_app(CONFIG)