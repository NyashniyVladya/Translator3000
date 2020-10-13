
init -8 python in _translator3000:

    class Translator3000(NoRollback):

        __author__ = "Vladya"
        _user_setting_file = path.abspath(
            path.join(config.basedir, "_translator3000_setting.json")
        )

        def __init__(self):

            self._translator_object = translator.Translator()

            try:
                # Для старых версий ренпая.
                self._notags_filter = renpy.translation.notags_filter
            except Exception:
                # Для новых.
                self._notags_filter = renpy.translation.dialogue.notags_filter

            if path.isfile(self._user_setting_file):
                with open(self._user_setting_file, "rb") as _file:
                    self._setting = json.load(_file)
                if "prescan" not in self._setting:
                    # Файл был создан до введения предварительного скана.
                    self._setting["prescan"] = False
                    self._dump_setting()
            else:
                self._setting = {
                    "gameLanguage": None,
                    "directionOfTranslation": None,
                    "prescan": False
                }
                self._dump_setting()

            self._translate_preparer = Preparer(translator_object=self)

        @classmethod
        def turn_on(cls):

            _tr_object = cls()

            config.say_menu_text_filter = _tr_object

            if _tr_object._setting["prescan"]:

                renpy.game.post_init.append(
                    _tr_object._translate_preparer.start
                )
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

        @staticmethod
        def _substitute(s):
            """
            Заменяем переменные в тексте на конкретные значения.
            """
            s = renpy.substitutions.substitute(s, force=True, translate=True)
            if isinstance(s, basestring):
                return s
            return s[0]

        def unquote(self, s):
            """
            Преобразуется форматированный текст в "чистый",
            без тегов, переменных и т.п.
            """
            s = self._substitute(s)
            s %= renpy.exports.tag_quoting_dict
            s = self._notags_filter(s)
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
                    code = self._translator_object._get_lang_code(
                        self._setting["gameLanguage"]
                    )
                except ValueError:
                    pass
                else:
                    return code

            code = self.detect_game_language_code()
            if code:
                return code

            return self._translator_object._get_lang_code("English")

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
                    code = self._translator_object._get_lang_code(
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

            return self._translator_object._get_lang_code("Russian")

        def _dump_setting(self):

            temp_fn = "{}.temp".format(self._user_setting_file)
            _string_setting_backup = json.dumps(
                self._setting,
                ensure_ascii=False,
                indent=4
            )
            if isinstance(_string_setting_backup, unicode):
                _string_setting_backup = _string_setting_backup.encode("utf_8")
            _setting_backup = io.BytesIO(_string_setting_backup)
            with open(temp_fn, "wb") as _file:
                while True:
                    chunk = _setting_backup.read((2 ** 20))
                    if not chunk:
                        break
                    _file.write(chunk)
            if path.isfile(self._user_setting_file):
                os.remove(self._user_setting_file)
            os.rename(temp_fn, self._user_setting_file)

        def detect_game_language_code(self):

            """
            Пытаемся получить код языка игры.
            """

            if not _preferences.language:
                return None

            try:
                code = self._translator_object._get_lang_code(
                    _preferences.language
                )
            except ValueError:
                return None
            else:
                return code

        def detect_os_language_code(self):

            """
            Пытаемся получить код языка операционной системы.
            """

            locale, region = renpy.translation.detect_user_locale()
            lang_name = None
            if locale is not None:
                lang_name = config.locale_to_language_function(locale, region)
            for variant in (locale, region, lang_name):
                if not variant:
                    continue
                try:
                    code = self._translator_object._get_lang_code(variant)
                except ValueError:
                    continue
                else:
                    return code
            return None

    Translator3000.turn_on()
