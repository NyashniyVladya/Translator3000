# -*- coding: utf-8 -*-
"""
@author: Vladya
"""

import os
import json
import copy
import threading
from os import path
from . import utils


class TranslatorAbstract(object):

    __author__ = "Vladya"
    __version__ = "1.1.0"

    LOGGER = None
    DATABASE_FN = None
    LOCAL_DATABASE_FN = None

    def __init__(self):

        self._database_lock = threading.RLock()
        self._hdd_lock = threading.RLock()

        self._database = {}
        self._local_db = {}
        if path.isfile(self.DATABASE_FN):
            with open(self.DATABASE_FN, "rb") as _db_file:
                _global_database = json.load(_db_file)
            self._database.update(copy.deepcopy(_global_database))

        if path.isfile(self.LOCAL_DATABASE_FN):
            with open(self.LOCAL_DATABASE_FN, "rb") as _db_file:
                _local_database = json.load(_db_file)
            self._database.update(copy.deepcopy(_local_database))
            self._local_db.update(copy.deepcopy(_local_database))

        self.backup_database()

    def backup_database(self):

        with self._hdd_lock:

            self.LOGGER.debug("Database backup has been requested.")

            with self._database_lock:
                database_dump_bytes = json.dumps(
                    self._database,
                    ensure_ascii=False
                )
                l_database_dump_bytes = json.dumps(
                    self._local_db,
                    ensure_ascii=False
                )

            if isinstance(database_dump_bytes, unicode):
                database_dump_bytes = database_dump_bytes.encode("utf_8")

            if isinstance(l_database_dump_bytes, unicode):
                l_database_dump_bytes = l_database_dump_bytes.encode("utf_8")

            utils.save_data_to_file(database_dump_bytes, self.DATABASE_FN)
            utils.save_data_to_file(
                l_database_dump_bytes,
                self.LOCAL_DATABASE_FN
            )
            self.LOGGER.debug("Backup has been created.")

    def add_translate_to_local_database(self, text, dest, src, tr, _upd=True):

        with self._database_lock:

            _lang_db = self._local_db.setdefault(src, {})
            _text_db = _lang_db.setdefault(text, {})

            if dest not in _text_db:
                _text_db[dest] = tr
                if _upd:
                    self.backup_database()

    def clear_cache(self, local=True):

        with self._hdd_lock:

            with self._database_lock:

                if not local:
                    self.LOGGER.debug("Full cache cleanup requested.")
                    self._database.clear()
                    self._local_db.clear()
                    if path.isfile(self.LOCAL_DATABASE_FN):
                        os.remove(self.LOCAL_DATABASE_FN)
                    if path.isfile(self.DATABASE_FN):
                        os.remove(self.DATABASE_FN)
                    self.LOGGER.debug("Cache cleared.")
                    return

                self.LOGGER.debug("Local cache cleanup requested.")

                for lang, texts in self._local_db.iteritems():
                    if lang not in self._database:
                        continue
                    for text, dest_langs in texts.iteritems():
                        if text not in self._database[lang]:
                            continue
                        for dest_lang in dest_langs.iterkeys():
                            self._database[lang][text].pop(dest_lang, None)
                            if not self._database[lang][text]:
                                self._database[lang].pop(text, None)
                            if not self._database[lang]:
                                self._database.pop(lang, None)

                self._local_db.clear()
                if path.isfile(self.LOCAL_DATABASE_FN):
                    os.remove(self.LOCAL_DATABASE_FN)

                self.backup_database()
                self.LOGGER.debug("Local cache is cleared.")

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
