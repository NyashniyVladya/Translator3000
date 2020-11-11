# -*- coding: utf-8 -*-
"""
@author: Vladya
"""

import logging
import os
from os import path
import requests
from .web_handler import WebHandler
from .utils import (
    UrlGetter,
    _save_data_to_file
)

try:
    from renpy import (
        exports as renpy,
        config as renpy_config
    )
except ImportError:
    RUN_IN_RENPY = False
else:
    RUN_IN_RENPY = True

__author__ = "Vladya"
__version__ = "2.0.1"

_database_struct_version = u"1.1"
DATABASE_FOLDER = path.abspath(
    path.join(
        path.expanduser(u'~'),
        u"vladya's projects database",
        u"GoogleTranslateModule",
        _database_struct_version
    )
)


if RUN_IN_RENPY:

    TRANSLATOR_FOLDER = path.abspath(
        path.join(renpy_config.basedir, u"_translator3000Data")
    )
    TEMP_FOLDER = path.join(TRANSLATOR_FOLDER, u"temp")
    DEBUG_FOLDER = path.join(TRANSLATOR_FOLDER, u"debug")

    # Get cert from .rpa
    requests.utils.DEFAULT_CA_BUNDLE_PATH = path.join(
        TEMP_FOLDER,
        u"cacert.pem"
    )
    with renpy.file(u"requests/cacert.pem") as _cacert:
        _save_data_to_file(_cacert, requests.utils.DEFAULT_CA_BUNDLE_PATH)

    if not path.isdir(DEBUG_FOLDER):
        os.makedirs(DEBUG_FOLDER)
    for _dir, _, files in tuple(os.walk(DEBUG_FOLDER)):
        for _file in files:
            _file = path.abspath(path.join(_dir, _file))
            os.remove(_file)
    _handler = logging.FileHandler(path.join(DEBUG_FOLDER, u"lastLog.log"))
else:
    TRANSLATOR_FOLDER = DATABASE_FOLDER
    TEMP_FOLDER = path.join(TRANSLATOR_FOLDER, u"temp")
    DEBUG_FOLDER = path.join(TRANSLATOR_FOLDER, u"debug")
    _handler = logging.StreamHandler()
_handler.setFormatter(
    logging.Formatter("%(asctime)s::%(levelname)s::%(name)s\n%(message)s\n")
)

LOGGER = logging.getLogger("GoogleTranslateModule")
LOGGER.setLevel(logging.DEBUG)
LOGGER.addHandler(_handler)


_url_getter = UrlGetter(logger=LOGGER)
_url_opener = WebHandler(logger=LOGGER)
