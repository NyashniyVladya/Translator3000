# -*- coding: utf-8 -*-
"""
@author: Vladya
"""

from os import path
from .. import _paths

_database_struct_version = u"1.5"
DATABASE_FOLDER = path.join(
    _paths.DATABASE_FOLDER,
    u"Google",
    _database_struct_version
)
LOCAL_DATABASE_FOLDER = path.join(
    _paths.LOCAL_DATABASE_FOLDER,
    u"Google",
    _database_struct_version
)
