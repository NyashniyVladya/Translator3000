# -*- coding: utf-8 -*-
"""
@author: Vladya
"""

import urllib2
import threading
import json
from os import path
from requests.packages import urllib3
from . import (
    DATABASE_FOLDER,
    LOGGER,
    _url_getter,
    _url_opener,
    token,
    utils
)


class GoogleTranslator(object):

    __author__ = "Vladya"

    LOGGER = LOGGER.getChild("GoogleTranslator")
    DATABASE_FN = path.join(DATABASE_FOLDER, u"translations.json")

    def __init__(self):

        self.__token_generator = token.TokenGenerator()

        self.__hdd_lock = threading.Lock()
        self.__database_lock = threading.Lock()

        self.__database = {}
        if path.isfile(self.DATABASE_FN):
            with open(self.DATABASE_FN, "rb") as _db_file:
                self.__database = json.load(_db_file)

    def translate(self, text, dest, src, _update_on_hdd=True):

        dest, src = map(utils._get_lang_code, (dest, src))
        text = text.strip()

        if not text:
            return u""

        if not isinstance(text, unicode):
            text = text.decode("utf_8", "ignore")

        _text = (text if (len(text) <= 100) else u"{0}...".format(text[:97]))
        self.LOGGER.debug(
            "Start translating \"%s\" from %s to %s.",
            _text.encode("utf_8", "ignore"),
            utils._get_lang_name(src).lower(),
            utils._get_lang_name(dest).lower()
        )
        with self.__database_lock:

            source_lang_db = self.__database.setdefault(src, {})
            text_db = source_lang_db.setdefault(text, {})

            if dest in text_db:
                self.LOGGER.debug("Translation is available in database.")
                return text_db[dest]

            self.LOGGER.debug("Translation is not available in database.")

            raw_result = self._web_translate(text, dest, src)
            result = u""
            for _raw_data in raw_result[0]:
                translation_chunk = _raw_data[0]
                if isinstance(translation_chunk, basestring):
                    result += translation_chunk

            self.LOGGER.debug("Successfully translated.")

            text_db[dest] = result

        if _update_on_hdd:
            self.backup_database()

        return result

    def _web_translate(self, text, dest, src):

        dest, src = map(utils._get_lang_code, (dest, src))
        text = text.strip()
        if not isinstance(text, unicode):
            text = text.decode("utf_8", "ignore")

        self.LOGGER.debug("Start creating link for request.")
        url = self._create_translate_url(text, dest, src)
        self.LOGGER.debug("Link have been created. Start online translation.")
        result = _url_opener.get(url)
        self.LOGGER.debug("Answer has been received. Data is being processed.")
        return result.json()

    def backup_database(self):

        self.LOGGER.debug("Database backup has been requested.")

        with self.__hdd_lock:

            with self.__database_lock:
                database_dump_bytes = json.dumps(
                    self.__database,
                    ensure_ascii=False
                )

            if isinstance(database_dump_bytes, unicode):
                database_dump_bytes = database_dump_bytes.encode("utf_8")

            utils._save_data_to_file(database_dump_bytes, self.DATABASE_FN)
            self.LOGGER.debug("Backup has been created.")

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

    def _create_translate_url(self, text, dest, src, **kwargs):

        dest, src = map(utils._get_lang_code, (dest, src))
        text = text.strip()
        if not isinstance(text, unicode):
            text = text.decode("utf_8", "ignore")

        params = {
            "client": "webapp",
            "sl": src,
            "tl": dest,
            "hl": dest,
            "dt": (
                "at",
                "bd",
                "ex",
                "ld",
                "md",
                "qca",
                "rw",
                "rm",
                "sos",
                "ss",
                "t"
            ),
            "ie": "UTF-8",
            "oe": "UTF-8",
            "otf": 1,
            "ssel": 0,
            "tsel": 0,
            "tk": self.__token_generator(text),
            "q": text
        }
        params.update(kwargs)

        _translate_url = _url_getter.get_translate_url()
        url_object = urllib3.util.Url(
            scheme=_translate_url.scheme,
            auth=_translate_url.auth,
            host=_translate_url.host,
            port=_translate_url.port,
            path=_translate_url.path,
            query=self.quote_params(**params),
            fragment=_translate_url.fragment
        )
        return url_object.url
