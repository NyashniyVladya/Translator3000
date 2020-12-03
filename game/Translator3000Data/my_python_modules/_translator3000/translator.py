# -*- coding: utf-8 -*-
"""
@author: Vladya
"""

from ._google import translator as google_translator


class Translator(object):

    CLASSES = {
        "google": google_translator.Translator
    }

    def __init__(self):

        self.__translators = {}
        for translator_name, _Translator in self.CLASSES.iteritems():
            self.__translators[translator_name.lower()] = _Translator()

    def _get_translator(self, service):

        _service = service.strip().lower()
        if _service not in self.__translators:
            raise ValueError("Translator \"{0}\" not found".format(service))

        return self.__translators[_service]

    def translate(self, service, text, dest, src, _update_on_hdd=True):
        translator = self._get_translator(service)
        return translator.translate(text, dest, src, _update_on_hdd)

    def get_lang_code(self, service, data):
        translator = self._get_translator(service)
        return translator.get_lang_code(data)

    def backup_database(self, service):
        translator = self._get_translator(service)
        return translator.backup_database()
