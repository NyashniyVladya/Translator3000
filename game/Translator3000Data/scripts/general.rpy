
init -8 python in _translator3000:

    class Translator3000(NoRollback):

        __author__ = "Vladya"

        LOGGER = LOGGER.getChild("Translator3000")
        _user_setting_file = path.abspath(
            path.join(config.basedir, "_translator3000_setting.json")
        )

        DEFAULT_SETTING = {
            "gameLanguage": None,
            "directionOfTranslation": None,
            "prescan": False,
            "_debug_mode": False,
            "translationService": "google",
            "originalInHistory": False
        }

        def __init__(self):

            self._setting = {}
            if path.isfile(self._user_setting_file):
                with open(self._user_setting_file, "rb") as _file:
                    try:
                        _setting = json.load(_file)
                    except ValueError:
                        raise Exception(__("Ошибка при чтении настроек."))
                    else:
                        self._setting = _setting.copy()

            _need_dump = False
            for k, v in self.DEFAULT_SETTING.iteritems():
                if k not in self._setting:
                    self._setting[k] = v
                    _need_dump = True

            if _need_dump:
                self._dump_setting()

            self._original_mapping = {}

            self._translator_object = translator.Translator()
            self._translate_preparer = Preparer(translator_object=self)

        @classmethod
        def turn_on(cls):

            _tr_object = cls()

            if _tr_object._setting["_debug_mode"]:
                store._translator3000.DEBUG = True
                parent_logger.setLevel(logging.DEBUG)

            if _tr_object._setting["prescan"]:

                if renpy.game.context().init_phase:
                    renpy.game.post_init.append(
                        _tr_object._translate_preparer.start
                    )
                else:
                    _tr_object._translate_preparer.start()

                config.overlay_functions.append(
                    _tr_object._translate_preparer._overlay_callable
                )

            config.say_menu_text_filter = _tr_object
            config.history_callbacks.append(_tr_object._history_callback)

        def __call__(self, text, _update_on_hdd=True):
            """
            Непосредственно - метод перевода.
            """
            try:
                result = self._translator_object.translate(
                    service=self._setting["translationService"],
                    text=self.unquote(text),
                    dest=self.direction_of_translation,
                    src=self.game_language,
                    _update_on_hdd=_update_on_hdd
                )
            except Exception as ex:
                if DEBUG:
                    raise ex
                return text
            result = self.quote(result)
            self._original_mapping[result] = text
            return result

        def _get_original(self, translated_text):
            if translated_text in self._original_mapping:
                return self._original_mapping[translated_text]
            return translated_text

        def _history_callback(self, entry_object):
            if not hasattr(entry_object, "translator3000_original_what"):
                entry_object.translator3000_original_what = self._get_original(
                    entry_object.what
                )
            if self._setting["originalInHistory"]:
                entry_object.what = entry_object.translator3000_original_what

        def _dump_setting(self):
            _backup = json.dumps(self._setting, ensure_ascii=False, indent=4)
            if isinstance(_backup, unicode):
                _backup = _backup.encode("utf_8")
            utils.save_data_to_file(_backup, self._user_setting_file)

        @staticmethod
        def _substitute(s):
            """
            Заменяем переменные в тексте на конкретные значения.
            """
            s = renpy.substitutions.substitute(s, force=True, translate=False)
            if isinstance(s, basestring):
                return s
            return s[0]

        def unquote(self, s):
            """
            Преобразуется форматированный текст в "чистый",
            без тегов, переменных и т.п.
            """
            # Подстановка значений вида "[variable]".
            s = self._substitute(s)
            # То же, но для "%(variable)s".
            s %= renpy.tag_quoting_dict
            # Удаление тегов из текста вида "{b}{i}Some text.{/i}{/b}".
            s = renpy.translation.dialogue.notags_filter(s)
            return s

        @staticmethod
        def quote(s):
            """
            Экранирует спецсимволы ренпая, такие как '{', '[', '%'.
            """
            for old, new in {'{': "{{", '[': "[[", '%': "%%"}.iteritems():
                s = s.replace(old, new)
            return s

        @property
        def game_language(self):

            """
            Язык игры с которого будет переводиться текст.

            Сначала проверяем настройки юзера;
            если их нет - пытаемся определить язык игры;
            если и это не удалось - ставим английский,
            как самый популярный язык новелл.
            """

            if self._setting["gameLanguage"] is not None:
                try:
                    code = self._translator_object.get_lang_code(
                        service=self._setting["translationService"],
                        data=self._setting["gameLanguage"]
                    )
                except Exception as ex:
                    if DEBUG:
                        raise ex
                else:
                    return code

            code = self.detect_game_language_code()
            if code:
                return code

            return self._translator_object.get_lang_code(
                service=self._setting["translationService"],
                data="English"
            )

        @property
        def direction_of_translation(self):

            """
            Язык направления перевода, на который будет переводиться текст.

            Сначала проверяем настройки юзера;
            если их нет - пытаемся определить язык операционной системы;
            если и это не удалось - ставим русский, потому что...
            Потому что - почему бы и нет.
            """

            if self._setting["directionOfTranslation"] is not None:
                try:
                    code = self._translator_object.get_lang_code(
                        service=self._setting["translationService"],
                        data=self._setting["directionOfTranslation"]
                    )
                except Exception as ex:
                    if DEBUG:
                        raise ex
                else:
                    return code

            try:
                code = self.detect_os_language_code()
            except Exception as ex:
                if DEBUG:
                    raise ex
            else:
                if code:
                    return code

            return self._translator_object.get_lang_code(
                service=self._setting["translationService"],
                data="Russian"
            )

        def detect_game_language_code(self):

            """
            Пытаемся получить код языка игры.
            """

            if not _preferences.language:
                return None

            try:
                code = self._translator_object.get_lang_code(
                    service=self._setting["translationService"],
                    data=_preferences.language
                )
            except Exception:
                return None
            else:
                return code

        def detect_os_language_code(self):

            """
            Пытаемся получить код языка операционной системы.
            """

            if renpy.version(tuple=True) < (7, 1, 2):
                return None

            locale, region = renpy.translation.detect_user_locale()
            lang_name = None
            if locale is not None:
                lang_name = config.locale_to_language_function(locale, region)
            for variant in (locale, region, lang_name):
                if not variant:
                    continue
                try:
                    code = self._translator_object.get_lang_code(
                        service=self._setting["translationService"],
                        data=variant
                    )
                except Exception:
                    continue
                else:
                    return code
            return None

    Translator3000.turn_on()
