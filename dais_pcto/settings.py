# -*- coding: utf-8 -*-
"""Application configuration."""
import os
from datetime import timedelta

# Configurazione base
class Config(object):
    """Base configuration."""

    SECRET_KEY = "put_secret_key_here"
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# Configurazione di produzione
class ProdConfig(Config):
    """Production configuration."""

    ENV = 'prod'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL',
                                             "postgresql://postgres:postgres@localhost:5432/dais_pcto")

# Configurazione di sviluppo
class DevConfig(Config):
    """Development configuration."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:1234@localhost:5432/dais_pcto'

