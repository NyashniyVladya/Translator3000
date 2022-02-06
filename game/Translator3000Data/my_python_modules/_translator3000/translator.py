# -*- coding: utf-8 -*-
"""
@author: Vladya
"""

from ._google_gtx import translator as google_gtx_translator
from ._google_client5 import translator as google_client5_translator


class Translator(object):

    CLASSES = {
        "google_gtx": google_gtx_translator.Translator,
        "google_client5": google_client5_translator.Translator,
    }

    alias_mapping = {
        #  For backward compatibility with the settings in the file.
        "google_client5": (
            "google",
        )
    }

    def __init__(self):

        self.__translators = {}
        for translator_name, _Translator in self.CLASSES.iteritems():
            self.__translators[translator_name.lower()] = _Translator()

    def get_available_translator_services(self):
        return tuple(sorted(self.__translators.iterkeys()))

    def _get_translator(self, service):

        _service = service.strip().lower()
        if _service not in self.__translators:
            for new_name, aliases in self.alias_mapping.iteritems():
                if _service in aliases:
                    _service = new_name.strip().lower()
                    break
            if _service not in self.__translators:
                raise ValueError("Translator '{0}' not found".format(service))

        return self.__translators[_service]

    def translate(self, service, text, dest, src, _update_on_hdd=True):
        translator = self._get_translator(service)
        return translator.translate(text, dest, src, _update_on_hdd)

    def get_lang_code(self, service, data):
        translator = self._get_translator(service)
        return translator.get_lang_code(data)

    def get_lang_name(self, service, data):
        translator = self._get_translator(service)
        return translator.get_lang_name(data)

    def get_all_lang_codes(self, service):
        translator = self._get_translator(service)
        return translator.get_all_lang_codes()

    def backup_database(self, service):
        translator = self._get_translator(service)
        return translator.backup_database()

    def clear_cache(self, service, local):
        translator = self._get_translator(service)
        return translator.clear_cache(local)
