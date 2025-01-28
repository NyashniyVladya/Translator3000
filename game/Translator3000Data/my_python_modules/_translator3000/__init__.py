# -*- coding: utf-8 -*-
"""
@author: Vladya
"""

import logging
from . import (
    utils,
    web_handler,
    _logging,
    _paths
)

__author__ = "Vladya"
__version__ = "1.0.11"

utils.remove_dir(_paths.TEMP_FOLDER)
utils.remove_dir(_paths.DEBUG_FOLDER)

LOGGER = _logging.Logger.getLogger("translator3000")
LOGGER.setLevel(logging.DEBUG)


current_session = web_handler.WebHandler(logger_object=LOGGER)
