
init python:

    import json
    from threading import Lock
    from requests import Session
    from shutil import copy as filecopy
    from os import (
        path,
        remove
    )

    class _Translator3000(Session, NoRollback):

        __author__ = u"Vladya"
        __version__ = (1, 4, 1)
        __database_version__ = 2

        TRANSLATOR_URL = (
            u"https://translate.yandex.net/api/v1.5/tr.json/translate"
        )

        SETTING = path.abspath(
            path.join(
                renpy.config.basedir,
                u"vladya_translator_setting.json"
            )
        )
        DATABASE = path.abspath(
            path.join(
                path.expanduser(u"~"),
                u"vladya_translator_database.json"
            )
        )

        YANDEX_API_KEY_PLACEHOLDER = (
            u"Write your key here, replacing this text."
        )

        def __init__(self):

            super(self.__class__, self).__init__()

            try:
                self._notags_filter = renpy.translation.notags_filter
            except Exception:
                self._notags_filter = renpy.translation.dialogue.notags_filter

            self.__database_lock = Lock()
            self.__network_lock = Lock()
            self.__file_lock = Lock()

            if path.isfile(self.DATABASE):
                with open(self.DATABASE, "rb") as _file:
                    _db = json.load(_file, encoding="utf-8")
                _file_version = _db.get(u"database_version", 0)
                if self.__database_version__ > _file_version:
                    remove(self.DATABASE)

            if not path.isfile(self.SETTING):
                self.__setting = {
                    u"gameLanguage":
                        u"en",
                    u"directionOfTranslation":
                        u"ru",
                    u"yandexTranslatorAPIKey":
                        self.YANDEX_API_KEY_PLACEHOLDER
                }
                self.save_setting()

            if not path.isfile(self.DATABASE):
                self.__database = {
                    u"database_version": self.__database_version__,
                    u"database": {}
                }
                self.backup_database()

            with open(self.SETTING, "rb") as _file:
                self.__setting = json.load(_file, encoding="utf-8")

            with open(self.DATABASE, "rb") as _file:
                self.__database = json.load(_file, encoding="utf-8")

        def request(self, *args, **kwargs):
            with self.__network_lock:
                resp = super(self.__class__, self).request(*args, **kwargs)
                self.close()
                resp.raise_for_status()
                return resp

        def __call__(self, text):

            _start_text = text
            text = self._format_text(text).strip()

            with self.__database_lock:
                text_translations = self.__database[u"database"].setdefault(
                    self.__setting[u"gameLanguage"],
                    {}
                ).setdefault(text, {})

                needLang = self.__setting[u"directionOfTranslation"]
                if needLang in text_translations.iterkeys():
                    return text_translations[needLang]

                APIKey = self.__setting.get(u"yandexTranslatorAPIKey", None)
                if (APIKey == self.YANDEX_API_KEY_PLACEHOLDER) or (not APIKey):
                    return _start_text
            try:
                resp = self.post(
                    self.TRANSLATOR_URL,
                    data={
                        u"key": APIKey,
                        u"text": text,
                        u"lang": self.lang
                    },
                    timeout=30.
                )
                data = resp.json().get(u"text", [])
                data = u'\n'.join(data).strip()
                data = self.uni(data)
                if not data:
                    return _start_text
            except Exception:
                return _start_text

            with self.__database_lock:
                text_translations[needLang] = data
            self.backup_database()
            return data

        @property
        def lang(self):
            with self.__database_lock:
                return u"{gameLanguage}-{directionOfTranslation}".format(
                    **self.__setting
                )

        def save_setting(self):
            self._write_json(json_data=self.__setting, filename=self.SETTING)

        def backup_database(self):
            self._write_json(json_data=self.__database, filename=self.DATABASE)

        def _write_json(self, json_data, filename):

            with self.__database_lock:
                data = json.dumps(
                    json_data,
                    ensure_ascii=False,
                    encoding="utf-8",
                    indent=4
                )
            data = self.uni(data)

            name, _ = path.splitext(filename)
            backup = u"{0}.backup".format(name)
            with self.__file_lock:
                with open(backup, "wb") as _file:
                    _file.write(data.encode("utf-8"))
                filecopy(backup, filename)
                remove(backup)

        @staticmethod
        def _substitute(s):
            s = renpy.substitutions.substitute(s, force=True, translate=True)
            if isinstance(s, basestring):
                return s
            return s[0]

        def _format_text(self, s):
            s = self._substitute(s)
            s %= renpy.exports.tag_quoting_dict
            s = self._notags_filter(s)
            return self.uni(s)

        @staticmethod
        def uni(s):
            assert isinstance(s, basestring), u"{0!r} is not a text.".format(s)
            if isinstance(s, str):
                s = s.decode("utf-8", "ignore")
            return s

    config.say_menu_text_filter = _Translator3000()
