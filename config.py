#!/usr/bin/env python3
import os

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """
    APP_ID = os.environ.get("MICROSOFT_APP_ID", "")
    APP_PASSWORD = os.environ.get("MICROSOFT_APP_PASSWORD", "")
