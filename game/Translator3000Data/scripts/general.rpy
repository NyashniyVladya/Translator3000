
init -8 python in _translator3000:

    class Translator3000(NoRollback):

        __author__ = "Vladya"
        _user_setting_file = path.abspath(
            path.join(config.basedir, "_translator3000_setting.json")
        )

        DEFAULT_SETTING = {
            "gameLanguage": None,
            "directionOfTranslation": None,
            "prescan": False,
            "_debug_mode": False
        }

        def __init__(self):

            self._setting = {}
            if path.isfile(self._user_setting_file):
                with open(self._user_setting_file, "rb") as _file:
                    self._setting = json.load(_file)

            _need_dump = False
            for k, v in self.DEFAULT_SETTING.iteritems():
                if k not in self._setting:
                    self._setting[k] = v
                    _need_dump = True

            if _need_dump:
                self._dump_setting()

            self._translator_object = translator.GoogleTranslator()
            self._translate_preparer = Preparer(translator_object=self)

        @classmethod
        def turn_on(cls):

            _tr_object = cls()

            config.say_menu_text_filter = _tr_object

            if _tr_object._setting["_debug_mode"]:
                store._translator3000.DEBUG = True
                LOGGER.setLevel(logging.DEBUG)

            if _tr_object._setting["prescan"]:

                if renpy.game.context().init_phase:
                    renpy.game.post_init.append(
                        _tr_object._translate_preparer.start
                    )
                else:
                    _tr_object._translate_preparer.start()

                config.overlay_functions.append(
                    _tr_object._translate_preparer._show_scan_status
                )

        def __call__(self, text, _update_on_hdd=True):
            """
            Непосредственно - метод перевода.
            """
            try:
                result = self._translator_object.translate(
                    text=self.unquote(text),
                    dest=self.direction_of_translation_code,
                    src=self.game_language_code,
                    _update_on_hdd=_update_on_hdd
                )
            except Exception as ex:
                if DEBUG:
                    raise ex
                return text
            return self.quote(result)

        def _dump_setting(self):
            _backup = json.dumps(self._setting, ensure_ascii=False, indent=4)
            if isinstance(_backup, unicode):
                _backup = _backup.encode("utf_8")
            utils._save_data_to_file(_backup, self._user_setting_file)

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
        def game_language_code(self):

            """
            Язык игры с которого будет переводиться текст.

            Сначала проверяем настройки юзера;
            если их нет - пытаемся определить язык игры;
            если и это не удалось - ставим английский,
            как самый популярный язык новелл.
            """

            if self._setting["gameLanguage"]:
                try:
                    code = utils._get_lang_code(self._setting["gameLanguage"])
                except ValueError:
                    pass
                else:
                    return code

            code = self.detect_game_language_code()
            if code:
                return code

            return utils._get_lang_code("English")

        @property
        def direction_of_translation_code(self):

            """
            Язык направления перевода, на который будет переводиться текст.

            Сначала проверяем настройки юзера;
            если их нет - пытаемся определить язык операционной системы;
            если и это не удалось - ставим русский,
            потому что... Потому что - почему бы и нет.
            """

            if self._setting["directionOfTranslation"]:
                try:
                    code = utils._get_lang_code(
                        self._setting["directionOfTranslation"]
                    )
                except ValueError:
                    pass
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

            return utils._get_lang_code("Russian")

        def detect_game_language_code(self):

            """
            Пытаемся получить код языка игры.
            """

            if not _preferences.language:
                return None

            try:
                code = utils._get_lang_code(_preferences.language)
            except ValueError:
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
                    code = utils._get_lang_code(variant)
                except ValueError:
                    continue
                else:
                    return code
            return None

    Translator3000.turn_on()
