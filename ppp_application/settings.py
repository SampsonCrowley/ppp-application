# -*- coding: utf-8 -*-
"""Application configuration.

Most configuration is set via environment variables.

For local development, use a .env file to set
environment variables.
"""
from environs import Env
import re

env = Env()
env.read_env()

ENV = env.str("FLASK_ENV", default="production")
DEBUG = ENV == "development"
# SQLALCHEMY_DATABASE_URI = env.str("DATABASE_URL")
SECRET_KEY = env.str("SECRET_KEY")
RECAPTCHA_PUBLIC_KEY= "6Lc2HiYaAAAAAEZk-cVOh0KB1X_gK2LQvbkYo7b-"
RECAPTCHA_PRIVATE_KEY = env.str("RECAPTCHA_PRIVATE_KEY")
SEND_FILE_MAX_AGE_DEFAULT = env.int("SEND_FILE_MAX_AGE_DEFAULT")
BCRYPT_LOG_ROUNDS = env.int("BCRYPT_LOG_ROUNDS", default=13)
DEBUG_TB_ENABLED = DEBUG
DEBUG_TB_INTERCEPT_REDIRECTS = False
CACHE_TYPE = "simple"  # Can be "memcached", "redis", etc.
# SQLALCHEMY_TRACK_MODIFICATIONS = False

# File upload configuration
ALLOWED_FILE_EXTENSIONS = ["PDF", "JPG", "JPEG", "PNG", "TIF"]
ALLOWED_MIME_TYPES = re.compile("^(application/pdf|image/[^\\\/]+)$")
MAX_FILE_SIZE = 5 * 1024 * 1024
