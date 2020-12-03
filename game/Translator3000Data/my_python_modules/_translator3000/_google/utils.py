# -*- coding: utf-8 -*-
"""
@author: Vladya
"""

from . import consts


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

    raise ValueError("Code \"{0}\" is not detected.".format(language_data))


def _get_lang_name(language_data):
    lang_code = _get_lang_code(language_data)
    return consts.LANG_CODES[lang_code][0]
