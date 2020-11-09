# -*- coding: utf-8 -*-
"""
@author: Vladya
"""

import logging
from os import path
from .web_handler import WebHandler
from .utils import UrlGetter

__author__ = "Vladya"
__version__ = "2.0.0"


logging.basicConfig()
LOGGER = logging.getLogger("GoogleTranslateModule")
LOGGER.setLevel(logging.DEBUG)

_database_struct_version = u"1.1"
DATABASE_FOLDER = path.abspath(
    path.join(
        path.expanduser(u'~'),
        u"vladya's projects database",
        u"GoogleTranslateModule",
        _database_struct_version
    )
)

_url_getter = UrlGetter(logger=LOGGER)
_url_opener = WebHandler(logger=LOGGER)
