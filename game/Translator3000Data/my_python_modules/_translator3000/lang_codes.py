# -*- coding: utf-8 -*-
"""
@author: Vladya
"""


from . import consts


def _format(t):
    return t.lower().strip().replace('-', '_')


def _get_available_translators():
    variants = set()
    for translators_dict in consts.LANG_CODES.values():
        variants.update(translators_dict.keys())
    return frozenset(variants)


_names_format_mappiing = dict(
    map(lambda x: (_format(x), x), consts.LANG_CODES.keys())
)
_available_translators = _get_available_translators()


def get_languages_for_translator(translator_name):

    if translator_name not in _available_translators:
        raise ValueError(
            "Translator '{0}' is not found.".format(translator_name)
        )
    for lang_name, translators_variants in consts.LANG_CODES.items():
        if translator_name in translators_variants:
            yield lang_name


def get_lang_codes_for_translator(translator_name):

    if translator_name not in _available_translators:
        raise ValueError(
            "Translator '{0}' is not found.".format(translator_name)
        )
    for translators_variants in consts.LANG_CODES.values():
        if translator_name in translators_variants:
            yield translators_variants[translator_name][0]


def get_lang_name(language_data):

    if not isinstance(language_data, (bytes, str)):
        raise TypeError("Language id should be a string.")

    _language_data = _format(language_data)
    for lang_name, translators_variants in consts.LANG_CODES.items():
        variants = set()
        variants.add(_format(lang_name))
        for _variants in translators_variants.values():
            variants.update(map(_format, _variants))
        if _language_data in variants:
            return lang_name

    raise ValueError("Code \"{0}\" is not detected.".format(language_data))


def get_lang_code(language_data, translator_name):

    if translator_name not in _available_translators:
        raise ValueError(
            "Translator '{0}' is not found.".format(translator_name)
        )

    lang_name = get_lang_name(language_data)

    if translator_name not in consts.LANG_CODES[lang_name]:
        raise ValueError(
            "'{0}' translator does not support the {1} language.".format(
                translator_name,
                lang_name
            )
        )

    return consts.LANG_CODES[lang_name][translator_name][0]
