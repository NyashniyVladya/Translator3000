# -*- coding: utf-8 -*-
"""
@author: Vladya
"""

import requests
import logging
from os import path
from . import (
    utils,
    web_handler,
    _logging,
    _paths
)

__author__ = "Vladya"
__version__ = "1.0.2"

utils.remove_dir(_paths.TEMP_FOLDER)
utils.remove_dir(_paths.DEBUG_FOLDER)

LOGGER = _logging.Logger.getLogger("translator3000")
LOGGER.setLevel(logging.DEBUG)


if utils.renpy:
    # Get cert from .rpa
    requests.utils.DEFAULT_CA_BUNDLE_PATH = path.join(
        _paths.TEMP_FOLDER,
        u"cacert.pem"
    )
    with utils.renpy.file(u"requests/cacert.pem") as _cacert:
        utils.save_data_to_file(_cacert, requests.utils.DEFAULT_CA_BUNDLE_PATH)

current_session = web_handler.WebHandler(logger_object=LOGGER)
