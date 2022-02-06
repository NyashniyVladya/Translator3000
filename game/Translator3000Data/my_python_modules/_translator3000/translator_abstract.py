# -*- coding: utf-8 -*-
"""
@author: Vladya
"""

import os
import json
import copy
import urllib
import threading
from os import path
from . import (
    utils,
    lang_codes,
    _paths
)


class TranslatorAbstract(object):

    __author__ = "Vladya"
    __version__ = "1.2.1"

    LOGGER = None
    DATABASE_FN = None
    LOCAL_DATABASE_FN = None

    SYMB_LIMIT = None
    TRANSLATOR_NAME = None

    FORCE_RPM = None

    def __init__(self):

        self._database_lock = threading.RLock()
        self._hdd_lock = threading.RLock()

        self._database = {}
        self._local_db = {}
        if path.isfile(self.DATABASE_FN):
            try:
                with open(self.DATABASE_FN, "rb") as _db_file:
                    _global_database = json.load(_db_file)
            except Exception as ex:
                broken_db_path = path.join(
                    _paths.DEBUG_FOLDER,
                    u"broken_global_database.json"
                )
                with open(self.DATABASE_FN, "rb") as _db_file:
                    utils.save_data_to_file(_db_file, broken_db_path)
                raise ex
            else:
                self._database.update(copy.deepcopy(_global_database))

        if path.isfile(self.LOCAL_DATABASE_FN):
            try:
                with open(self.LOCAL_DATABASE_FN, "rb") as _db_file:
                    _local_database = json.load(_db_file)
            except Exception as ex:
                broken_db_path = path.join(
                    _paths.DEBUG_FOLDER,
                    u"broken_local_database.json"
                )
                with open(self.LOCAL_DATABASE_FN, "rb") as _db_file:
                    utils.save_data_to_file(_db_file, broken_db_path)
                raise ex
            else:
                self._database.update(copy.deepcopy(_local_database))
                self._local_db.update(copy.deepcopy(_local_database))

        self.backup_database()

    @staticmethod
    def _urlencode(param_dict, space_is_plus=False):

        quote_func = (urllib.quote_plus if space_is_plus else urllib.quote)

        query = set()
        for k, v in param_dict.iteritems():
            if isinstance(k, unicode):
                k = k.encode("utf_8", "ignore")
            if isinstance(v, unicode):
                v = v.encode("utf_8", "ignore")
            k, v = map(quote_func, map(str, (k, v)))
            query.add("{}={}".format(k, v))

        return '&'.join(sorted(query))

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

    def translate(self, text, dest, src, _update_on_hdd=True):

        dest, src = map(self.get_lang_code, (dest, src))
        text = text.strip()

        if not text:
            return u""

        if not isinstance(text, unicode):
            text = text.decode("utf_8", "ignore")

        parts = tuple(self.get_parts_from_text(text))
        if len(parts) > 1:

            def _translate_child(txt):
                return self.translate(txt, dest, src, _update_on_hdd)

            return self.join_parts_to_text(map(_translate_child, parts))

        elif not parts:
            return u""

        text = parts[0]
        if self.SYMB_LIMIT is not None:
            if len(text) >= self.SYMB_LIMIT:
                text = u"{0}...".format(text[:(self.SYMB_LIMIT - 4)].strip())

        _text_for_log = text
        if len(_text_for_log) >= 100:
            _text_for_log = u"{0}...".format(_text_for_log[:96].strip())

        with self._database_lock:

            self.LOGGER.debug(
                "Start translating \"%s\" from %s to %s.",
                _text_for_log.encode("utf_8", "ignore"),
                self.get_lang_name(src).lower(),
                self.get_lang_name(dest).lower()
            )

            _lang_db = self._database.setdefault(src, {})
            _text_db = _lang_db.setdefault(text, {})

            if dest in _text_db:
                result = _text_db[dest]
                self.add_translate_to_local_database(
                    text,
                    dest,
                    src,
                    result,
                    _update_on_hdd
                )
                self.LOGGER.debug("Translation is available in database.")
                return result

            self.LOGGER.debug("Translation is not available in database.")

            result = self._web_translate(text, dest, src)
            self.LOGGER.debug("Successfully translated.")

            _text_db[dest] = result
            self.add_translate_to_local_database(
                text,
                dest,
                src,
                result,
                False
            )

            if _update_on_hdd:
                self.backup_database()

            return result

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

    def _web_translate(self, text, dest, src):
        raise NotImplementedError("Should be redefined.")

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

    def get_lang_code(self, data):
        return lang_codes.get_lang_code(data, self.TRANSLATOR_NAME)

    def get_lang_name(self, data):
        return lang_codes.get_lang_name(data)

    def get_all_lang_codes(self):
        return lang_codes.get_lang_codes_for_translator(self.TRANSLATOR_NAME)
