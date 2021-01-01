# -*- coding: utf-8 -*-
"""
@author: Vladya
"""

import json
import threading
from os import path
from . import utils


class TranslatorAbstract(object):

    __author__ = "Vladya"
    __version__ = "1.0.3"

    LOGGER = None
    DATABASE_FN = None

    def __init__(self):

        self._database_lock = threading.Lock()
        self._hdd_lock = threading.Lock()

        self._database = {}
        if path.isfile(self.DATABASE_FN):
            with open(self.DATABASE_FN, "rb") as _db_file:
                self._database = json.load(_db_file)

    def backup_database(self):

        with self._hdd_lock:

            self.LOGGER.debug("Database backup has been requested.")

            with self._database_lock:
                database_dump_bytes = json.dumps(
                    self._database,
                    ensure_ascii=False
                )

            if isinstance(database_dump_bytes, unicode):
                database_dump_bytes = database_dump_bytes.encode("utf_8")

            utils.save_data_to_file(database_dump_bytes, self.DATABASE_FN)
            self.LOGGER.debug("Backup has been created.")

    @staticmethod
    def get_parts_from_text(text):
        if not isinstance(text, basestring):
            raise TypeError("'text' should be a string.")
        if not isinstance(text, unicode):
            text = text.decode("utf_8")
        for t in text.split(u'\n'):
            yield t

    @staticmethod
    def join_parts_to_text(parts):
        parts = tuple(parts)
        return u'\n'.join(parts)

    def translate(self, text, dest, src, _update_on_hdd=True):
        raise NotImplementedError("Should be redefined.")

    def get_lang_code(self, data):
        raise NotImplementedError("Should be redefined.")

    def get_lang_name(self, data):
        raise NotImplementedError("Should be redefined.")

    def get_all_lang_codes(self):
        raise NotImplementedError("Should be redefined.")
