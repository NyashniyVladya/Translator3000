# -*- coding: utf-8 -*-
"""
@author: Vladya
"""

import json
from os import path
from requests.packages import urllib3
from .. import (
    translator_abstract,
    current_session
)
from . import (
    utils,
    _paths,
    LOGGER
)


class Translator(translator_abstract.TranslatorAbstract):

    __version__ = "1.0.1"

    LOGGER = LOGGER.getChild("Translator")
    DATABASE_FN = path.join(_paths.DATABASE_FOLDER, u"translations.json")

    SYMB_LIMIT = 5000

    BASE_URL = urllib3.util.Url(
        scheme="https",
        auth=None,
        host="translate.google.com",
        port=None,
        path='/',
        query=None,
        fragment=None
    )

    GOOGLE_RPCIDS = "MkEWBc"

    def __init__(self):
        super(Translator, self).__init__()

    @property
    def request_url(self):
        return urllib3.util.Url(
            scheme="https",
            auth=None,
            host=self.BASE_URL.hostname,
            port=None,
            path="/_/TranslateWebserverUi/data/batchexecute",
            query=None,
            fragment=None
        ).url

    def get_lang_code(self, data):
        if not isinstance(data, basestring):
            return TypeError("Language id should be a string.")
        return utils._get_lang_code(data)

    def translate(self, text, dest, src, _update_on_hdd=True):

        dest, src = map(utils._get_lang_code, (dest, src))
        text = text.strip()

        if not text:
            return u""

        if not isinstance(text, unicode):
            text = text.decode("utf_8", "ignore")

        parts = tuple(self.get_parts_from_text(text))
        if len(parts) > 1:

            def _translate_child(txt):
                return self.translate(txt, dest, src, _update_on_hdd)

            return self.join_parts_to_text(map(_translate_child, parts))

        elif not parts:
            return u""

        text = parts[0]
        if len(text) >= self.SYMB_LIMIT:
            text = u"{0}...".format(text[:(self.SYMB_LIMIT - 4)].strip())

        _text_for_log = text
        if len(_text_for_log) >= 100:
            _text_for_log = u"{0}...".format(_text_for_log[:96].strip())

        with self._database_lock:

            self.LOGGER.debug(
                "Start translating \"%s\" from %s to %s.",
                _text_for_log.encode("utf_8", "ignore"),
                utils._get_lang_name(src).lower(),
                utils._get_lang_name(dest).lower()
            )

            _lang_db = self._database.setdefault(src, {})
            _text_db = _lang_db.setdefault(text, {})

            if dest in _text_db:
                self.LOGGER.debug("Translation is available in database.")
                return _text_db[dest]

            self.LOGGER.debug("Translation is not available in database.")

            result = self._web_translate(text, dest, src)
            self.LOGGER.debug("Successfully translated.")

            _text_db[dest] = result

        if _update_on_hdd:
            self.backup_database()

        return result

    def _web_translate(self, text, dest, src):

        extra_headers = {"Referer": self.BASE_URL.url}

        request = current_session.post(
            self.request_url,
            data=self._get_request_data(text, dest, src),
            headers=extra_headers
        )

        _json_start = request.content.find('[')
        answer = json.loads(request.content[_json_start:], encoding="utf_8")
        answer = json.loads(answer[0][2])
        answer = answer[1][0][0][5]

        result = u""
        for data in answer:
            add_space = False
            if len(data) >= 3:
                add_space = data[2]
            if add_space:
                result += u' '
            result += data[0]

        return result.strip()

    def _get_request_data(self, text, dest, src):

        """
        Generates the json string containing the query:
            [
                [
                    [
                        "MkEWBc",
                        "[[\"Hello, world!\",\"en\",\"ru\",true],[1]]",
                        null,
                        "generic"
                    ]
                ]
            ]
        Main request:
            [
                [
                    "Hello, world!",
                    "en",
                    "ru",
                    true
                ],
                [
                    1
                ]
            ]
        """

        dest, src = map(utils._get_lang_code, (dest, src))
        if not isinstance(text, unicode):
            text = text.decode("utf_8", "ignore")

        query = [[text, src, dest, True], [1]]
        query_string = json.dumps(query, separators=(',', ':'))
        full_query = [[[self.GOOGLE_RPCIDS, query_string, None, "generic"]]]
        return {"f.req": json.dumps(full_query, separators=(',', ':'))}
