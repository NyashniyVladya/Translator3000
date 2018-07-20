
init python:

    import json
    from requests import Session
    from shutil import copy as filecopy
    from os import (
        path,
        remove
    )

    class Translator3000(Session):

        __author__ = u"Vladya"
        __version__ = (1, 1, 1)

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
                renpy.config.basedir,
                u"vladya_translator_database.json"
            )
        )

        YANDEX_API_KEY_PLACEHOLDER = (
            u"Write your key here, replacing this text."
        )

        def __init__(self):

            super(self.__class__, self).__init__()

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
                self.__database = {}
                self.backup_database()

            with open(self.SETTING, "rb") as _file:
                self.__setting = json.load(_file)

            with open(self.DATABASE, "rb") as _file:
                self.__database = json.load(_file)

        def __call__(self, text):

            _start_text = text
            text = self.substitute(text).strip()

            langDict = self.__database.setdefault(
                self.__setting[u"gameLanguage"],
                {}
            ).setdefault(
                self.__setting[u"directionOfTranslation"],
                {}
            )

            if text in langDict.iterkeys():
                return langDict[text]

            APIKey = self.__setting.get(u"yandexTranslatorAPIKey", None)
            if (APIKey == self.YANDEX_API_KEY_PLACEHOLDER) or (not APIKey):
                return _start_text

            try:
                req = self.post(
                    self.TRANSLATOR_URL,
                    data={
                        u"key": APIKey,
                        u"text": text,
                        u"lang": self.lang
                    }
                )
                req.raise_for_status()
                data = req.json().get(u"text", [])
                data = u'\n'.join(data).strip()
                data = self.uni(data)
                if not data:
                    return _start_text

                langDict[text] = data
                self.backup_database()
                return data

            except Exception:
                return _start_text

        @property
        def lang(self):
            return u"{gameLanguage}-{directionOfTranslation}".format(
                **self.__setting
            )

        def save_setting(self):
            self._write_json(json_data=self.__setting, filename=self.SETTING)

        def backup_database(self):
            self._write_json(json_data=self.__database, filename=self.DATABASE)

        @staticmethod
        def _write_json(json_data, filename):

            name, _ = path.splitext(filename)
            backup = u"{0}.backup".format(name)
            with open(backup, "wb") as _file:
                json.dump(json_data, _file, indent=4)
            filecopy(backup, filename)
            remove(backup)

        @classmethod
        def substitute(cls, s):
            s = renpy.translation.notags_filter(s)
            s %= renpy.exports.tag_quoting_dict
            s = renpy.substitutions.substitute(s)[0]
            return cls.uni(s)

        @staticmethod
        def uni(s):
            assert isinstance(s, basestring), u"{0!r} is not a text.".format(s)
            if isinstance(s, str):
                s = s.decode("utf-8", "ignore")
            return s

    config.say_menu_text_filter = Translator3000()
