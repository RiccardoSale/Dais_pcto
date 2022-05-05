# -*- coding: utf-8 -*-
"""Application configuration."""
import os
from datetime import timedelta


class Config(object):
    """Base configuration."""

    SECRET_KEY = "put_secret_key_here"
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    #CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProdConfig(Config):
    """Production configuration."""

    ENV = 'prod'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL',
                                             "postgresql://postgres:postgres@localhost:5432/dais_pcto")


class DevConfig(Config):
    """Development configuration."""

    #ENV = 'dev'
    DEBUG = True
    #DB_NAME = 'dev.db'
    # Put the db file in project root
    #DB_PATH = os.path.join(Config.PROJECT_ROOT, DB_NAME)
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:1234@localhost:5432/dais_pcto'
    #CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.


