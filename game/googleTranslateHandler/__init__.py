# -*- coding: utf-8 -*-
"""
@author: Vladya
"""

import logging
import urllib2
from os import path
from .web_handler import WebHandler

__author__ = "Vladya"
__version__ = "1.0"

logging.basicConfig()
LOGGER = logging.getLogger("GoogleTranslateModule")
LOGGER.setLevel(logging.DEBUG)

url_opener = WebHandler(logger=LOGGER)

DATABASE_FOLDER = path.abspath(
    path.join(
        path.expanduser(u'~'),
        u"vladya's projects database",
        u"GoogleTranslateModule",
        u'.'.join(__version__.split('.')[:2])
    )
)


base_url = urllib2.urlparse.urlparse("https://translate.google.com")
translate_url = urllib2.urlparse.urlparse(
    "https://translate.google.com/translate_a/single"
)
