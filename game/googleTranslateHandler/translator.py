# -*- coding: utf-8 -*-
"""
@author: Vladya
"""

import io
import os
import json
import threading
import urllib2
from os import path
from . import (
    DATABASE_FOLDER,
    LOGGER,
    url_opener,
    translate_url,
    token,
    consts
)


class JSONError(Exception):
    pass


class Translator(object):

    __author__ = "Vladya"
    translations_json_path = path.join(DATABASE_FOLDER, "translations.json")

    LOGGER = LOGGER.getChild("Translator")

    def __init__(self):

        self._token_generator = token.TokenGenerator()
        self.__hdd_lock = threading.Lock()
        self.__database_lock = threading.Lock()
        self.__database = {}
        if path.isfile(self.translations_json_path):
            with open(self.translations_json_path, "rb") as _file:
                self.__database = json.load(_file)

    def translate(self, text, dest, src, _update_on_hdd=True):

        dest, src = map(self._get_lang_code, (dest, src))

        self.LOGGER.debug("Start translate from %s to %s.", src, dest)

        if not text.strip():
            return u""

        if not isinstance(text, unicode):
            text = text.decode("utf_8", "ignore")

        with self.__database_lock:

            src_db = self.__database.setdefault(src, {})
            text_db = src_db.setdefault(text, {})

            if dest in text_db:
                self.LOGGER.debug("Translation in database.")
                return text_db[dest]

            self.LOGGER.debug("Translation not find. Send web request.")
            result_raw = self._translate_with_web(text, dest, src)
            result = u""
            for translate_data in result_raw[0]:
                phrase = translate_data[0]
                if isinstance(phrase, basestring):
                    result += phrase
            if not result.strip():
                return u""

            text_db[dest] = result

        if _update_on_hdd:
            self._backup_database()

        return result

    def _backup_database(self):

        with self.__hdd_lock:

            self.LOGGER.debug("Start creating backup on HDD.")

            with self.__database_lock:
                json_dump_bytes = json.dumps(
                    self.__database,
                    ensure_ascii=False
                )

            if isinstance(json_dump_bytes, unicode):
                json_dump_bytes = json_dump_bytes.encode("utf_8")
            json_dump_bytes = io.BytesIO(json_dump_bytes)

            directory = path.dirname(self.translations_json_path)
            if not path.isdir(directory):
                os.makedirs(directory)
            temp_fn = u"{0}.temp".format(self.translations_json_path)
            with open(temp_fn, "wb") as _file:
                while True:
                    chunk = json_dump_bytes.read((2 ** 20))
                    if not chunk:
                        break
                    _file.write(chunk)
            if path.isfile(self.translations_json_path):
                os.remove(self.translations_json_path)
            os.rename(temp_fn, self.translations_json_path)
            self.LOGGER.debug("Backup is created.")

    def _translate_with_web(self, text, dest, src):

        url = self.create_translate_url(text, dest, src)
        page = url_opener.open(url)
        result = ""
        while True:
            chunk = page.read((2 ** 20))
            if not chunk:
                break
            result += chunk
        try:
            result = json.loads(result)
        except Exception as ex:
            raise JSONError(ex.message)
        else:
            return result

    @staticmethod
    def _get_lang_code(language_data):

        def _format(t):
            return t.lower().strip().replace('-', '_')

        _language_data = _format(language_data)
        for code, _variants in consts.LANG_CODES.iteritems():

            variants = set()
            variants.add(_format(code))
            variants.update(map(_format, _variants))

            if _language_data in variants:
                return code

        raise ValueError("Code {0} is not detected.".format(language_data))

    @classmethod
    def quote_params(cls, **mapping):
        result = set()
        for key, value in mapping.iteritems():
            if isinstance(value, (list, tuple, set, frozenset)):
                result.update(map(lambda v: cls.quote(key, v), value))
            else:
                result.add(cls.quote(key, value))
        return '&'.join(sorted(result))

    @staticmethod
    def quote(key, value):
        if isinstance(key, unicode):
            key = key.encode("utf_8", "ignore")
        if isinstance(value, unicode):
            value = value.encode("utf_8", "ignore")
        return '='.join(map(urllib2.quote, map(bytes, (key, value))))

    def create_translate_url(self, text, dest, src, **kwargs):
        params = {
            "client": "webapp",
            "sl": src,
            "tl": dest,
            "hl": dest,
            "dt": ("at", "bd", "ex", "ld", "md", "qca", "rw", "rm", "ss", "t"),
            "ie": "UTF-8",
            "oe": "UTF-8",
            "otf": 1,
            "ssel": 0,
            "tsel": 0,
            "tk": self._token_generator.generate_final_token(text),
            "q": text
        }
        params.update(kwargs)
        url = translate_url
        return urllib2.urlparse.ParseResult(
            url.scheme,
            url.netloc,
            url.path,
            url.params,
            self.quote_params(**params),
            url.fragment
        )
