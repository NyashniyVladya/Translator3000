# -*- coding: utf-8 -*-
"""
@author: Vladya
"""

from os import path
from .. import (
    translator_abstract,
    current_session
)
from . import (
    _paths,
    LOGGER
)


try:
    import urllib3
except ImportError:
    from requests.packages import urllib3


class Translator(translator_abstract.TranslatorAbstract):

    __version__ = "1.0.1"

    TRANSLATOR_NAME = "google"

    LOGGER = LOGGER.getChild("Translator")
    DATABASE_FN = path.join(_paths.DATABASE_FOLDER, u"translations.json")
    LOCAL_DATABASE_FN = path.join(
        _paths.LOCAL_DATABASE_FOLDER,
        u"translations.json"
    )

    HOSTNAME = "clients5.google.com"

    SYMB_LIMIT = 5000

    def __init__(self):
        super(Translator, self).__init__()

    def get_base_url(self):
        return urllib3.util.Url(
            scheme='https',
            auth=None,
            host=self.HOSTNAME,
            port=None,
            path="/translate_a/t",
            query=None,
            fragment=None
        )

    def _web_translate(self, text, dest, src):

        dest, src = map(self.get_lang_code, (dest, src))
        params = {
            "client": "dict-chrome-ex",
            "sl": src,
            "tl": dest,
            "q": text
        }

        base_url = self.get_base_url()
        url = urllib3.util.Url(
            scheme=base_url.scheme,
            auth=base_url.auth,
            host=base_url.host,
            port=base_url.port,
            path=base_url.path,
            query=self._urlencode(params),
            fragment=base_url.fragment
        ).url

        if self.FORCE_RPM is not None:
            current_session.FORCE_RPM = self.FORCE_RPM
        request = current_session.get(url)
        self.LOGGER.debug("Answer:\n%s", request.content)
        _json = request.json()
        if isinstance(_json, dict):
            result = u""
            for answer in _json["sentences"]:
                if "trans" in answer:
                    result += answer["trans"]
        else:
            result = u"".join(_json)
        return result
