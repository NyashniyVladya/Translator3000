# -*- coding: utf-8 -*-
"""
@author: Vladya
"""

import io
import os
from os import path
from requests.packages import urllib3
from . import consts


class UrlGetter(object):

    __author__ = "Vladya"

    DEFAULT_TRANSLATE_HOST = "translate.google.com"

    def __init__(self, logger=None):

        self.LOGGER = None
        if logger:
            self.LOGGER = logger.getChild("UrlGetter")

    @property
    def base(self):
        url_object = self.get_base_url()
        return url_object.url

    @property
    def translate(self):
        url_object = self.get_translate_url()
        return url_object.url

    def get_base_url(self):
        return urllib3.util.Url(
            scheme="https",
            auth=None,
            host=self.DEFAULT_TRANSLATE_HOST,
            port=None,
            path=None,
            query=None,
            fragment=None
        )

    def get_translate_url(self):
        return urllib3.util.Url(
            scheme="https",
            auth=None,
            host=self.DEFAULT_TRANSLATE_HOST,
            port=None,
            path="/translate_a/single",
            query=None,
            fragment=None
        )


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


def _save_data_to_file(bytedata, out_fn):

    if not isinstance(bytedata, basestring):
        raise TypeError("'bytedata' should be a string.")

    if isinstance(bytedata, unicode):
        bytedata = bytedata.encode("utf_8")

    out_fn = path.abspath(out_fn)
    directory = path.dirname(out_fn)
    if not path.isdir(directory):
        os.makedirs(directory)

    _temp_fn = u"{0}.tmp".format(out_fn)

    with io.BytesIO(bytedata) as _read_file:
        with open(_temp_fn, "wb") as _write_file:
            while True:
                chunk = _read_file.read((2 ** 20))
                if not chunk:
                    break
                _write_file.write(chunk)

    if path.isfile(out_fn):
        os.remove(out_fn)
    os.rename(_temp_fn, out_fn)
