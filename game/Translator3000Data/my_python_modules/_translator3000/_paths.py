# -*- coding: utf-8 -*-
"""
@author: Vladya
"""


from os import path
from . import utils


DATABASE_FOLDER = path.abspath(
    path.join(
        path.expanduser(u'~'),
        u"vladya's projects database",
        u"translator3000"
    )
)

if utils.renpy:
    _translator_data_folder = path.abspath(
        path.join(utils.renpy.config.basedir, u"_translator3000Data")
    )
    LOCAL_DATABASE_FOLDER = path.abspath(
        path.join(utils.renpy.config.basedir, u"local translations")
    )
else:
    _translator_data_folder = path.join(DATABASE_FOLDER, u"_AppData")
    LOCAL_DATABASE_FOLDER = path.join(
        _translator_data_folder,
        u"local translations"
    )

TEMP_FOLDER = path.join(_translator_data_folder, u"temp")
DEBUG_FOLDER = path.join(_translator_data_folder, u"debug")
_logfile = path.join(DEBUG_FOLDER, u"lastLog.log")
