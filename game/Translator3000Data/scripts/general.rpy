
init -7 python in _translator3000:

    class Translator3000(SingleTone):

        __author__ = "Vladya"

        LOGGER = LOGGER.getChild("Translator3000")
        _user_setting_file = path.abspath(
            path.join(config.basedir, "_translator3000_setting.json")
        )
        _renpy_folder = "translator3000_ingame_files"
        multigame_fonts_folder = path.abspath(
            path.join(config.gamedir, _renpy_folder, "multigame_fonts")
        )

        _multi_persistent = _MultiGameData.get_object()

        MULTIGAME_KEYS = (
            # Настройки, сохраняющиеся в системе и включающиеся по умолчанию
            # в других играх.
            "gameLanguage",
            "directionOfTranslation",
            "translationService",
            "workMethod",
            "originalInHistory",
            "extraTextOptions"
        )
        DEFAULT_SETTING = {
            "gameLanguage": None,
            "directionOfTranslation": None,
            "prescan": False,
            "_debug_mode": False,
            "translationService": "google",
            "workMethod": "dialogueOnly",
            "originalInHistory": False,
            "requestsFrequency": None,
            "extraTextOptions": {
                "font": None,
                "size": None,
                "italic": False,
                "bold": False
            }
        }


        def __init__(self):

            if self.initialized:
                return

            self._gui = store._translator3000_gui.GUI(translator=self)
            self._translator_switcher = True

            if self._multi_persistent.setting is None:
                self._multi_persistent.setting = {}
            if self._multi_persistent.fonts is None:
                self._multi_persistent.fonts = collections.OrderedDict()
            self._multi_persistent.save()

            self._setting = {}
            if path.isfile(self._user_setting_file):
                with open(self._user_setting_file, "rb") as _file:
                    try:
                        _setting = json.load(_file)
                    except ValueError:
                        error_message = (
                            "Возникла ошибка при попытке чтения настроек. "
                            "Перепроверьте введённые данные "
                            "(запятые, кавычки у текстовых значений, "
                            "отстутствие закрывающих токенов - '}', ']' и т.д."
                        )
                        raise Exception(self._gui.translate(error_message))
                    else:
                        self._setting = copy.deepcopy(_setting)

            # Сначала проверяем настройки пользователя для конкретной игры,
            # потом сохранённые настройки для всех игр,
            # потом ставим дефолтные.
            for d in (self._multi_persistent.setting, self.DEFAULT_SETTING):
                self._dict_multisetdefault(self._setting, d)
            utils.remove_dir(self.multigame_fonts_folder)
            if self._setting["extraTextOptions"]["font"] is not None:
                _fnt = self._setting["extraTextOptions"]["font"]
                if renpy.loadable(_fnt):
                    self.add_font_to_database(_fnt)
            self._dump_setting()

            self._original_mapping = {}

            self._all_text_in_game = set()

            self._translator_object = translator.Translator()
            self._translate_preparer = Preparer(translator_object=self)
            self._github_checker = GitChecker(translator_object=self)

            self.initialized = True

        @classmethod
        def turn_on(cls):

            _tr_object = cls()

            _tr_object._check_setting()

            if renpy.game.context().init_phase:
                renpy.game.post_init.append(
                    _tr_object._translate_preparer.start
                )
            else:
                _tr_object._translate_preparer.start()

            if _tr_object._setting["prescan"]:
                _tr_object._translate_preparer._switcher = True
                _tr_object._gui.show = True

            renpy.text.text.Text.set_text = _tr_object._get_text_method()
            _tr_object.update_work_method()

            config.history_callbacks.append(_tr_object._history_callback)

            setattr(store, "translator3000", _tr_object)
            config.overlay_screens.append("translator3000_gui")

            _tr_object._github_checker.init_download_process()
            if _tr_object._github_checker._download_process:
                _tr_object._gui.show = True

        def _get_text_method(self):

            def set_text(text_self, text, *args, **kwargs):

                self._all_text_in_game.add(text_self)
                _translate = (self._setting["workMethod"] == "allText")

                if not isinstance(text, __builtin__.list):
                    text = [text]

                new_text = []
                for t in text:

                    if not isinstance(t, basestring):
                        new_text.append(t)
                        continue

                    if not isinstance(t, unicode):
                        t = t.decode("utf_8", "replace")

                    _first_mark = "###notTranslate###"
                    _second_mark = "{#notTranslate}"
                    if t.startswith(_second_mark) or (_first_mark in t):
                        # Метка "не переводить".
                        t = t.replace(_first_mark, "")
                        if not t.startswith(_second_mark):
                            t = "{0}{1}".format(_second_mark, t)
                        new_text.append(t)
                        continue

                    if _translate:
                        t = self.__call__(
                            renpy.translation.translate_string(t),
                            _check_double_call=True
                        )

                    new_text.append(t)

                text = new_text

                return _ORIGINAL_SET_TEXT_METHOD(
                    text_self,
                    text,
                    *args,
                    **kwargs
                )

            return types.MethodType(set_text, None, renpy.text.text.Text)

        def update_work_method(self):

            method = self._setting["workMethod"]
            _allow_methods = ("dialogueOnly", "allText")
            if method not in _allow_methods:
                if DEBUG:
                    error_message = (
                        "Способ работы переводчика \"{0}\" неизвестен."
                    )
                    raise Exception(
                        self._gui.translate(error_message).format(method)
                    )
                method = "dialogueOnly"

            if method == "dialogueOnly":

                config.say_menu_text_filter = self
                config.developer = _ORIGINAL_DEVELOPER_MODE

            elif method == "allText":

                config.say_menu_text_filter = None

                # Иначе проверка будет говорить,
                # что текст на экране не соответствует тому, что в скрипте.
                # Но... Нам ведь это и нужно.
                config.developer = False

                for text_object in frozenset(self._all_text_in_game):
                    if not hasattr(text_object, "text_parameter"):
                        continue
                    if not hasattr(text_object, "substitute"):
                        continue
                    try:
                        text_object.set_text(
                            text_object.text_parameter,
                            substitute=text_object.substitute,
                            update=True
                        )
                    except Exception as ex:
                        if DEBUG:
                            raise Exception((text_object.text_parameter, ex))

        def add_font_to_database(self, font):

            font = self._gui._fs_object._normpath(font)
            if not font.strip():
                raise ValueError(self._gui.translate("Файл шрифта не найден."))

            font = font.replace("\\", '/')

            result = b""
            with renpy.file(font) as _font_file:
                while True:
                    chunk = _font_file.read((2 ** 10))
                    if not chunk:
                        break
                    result += chunk

            # Для смещения в очереди.
            self._multi_persistent.fonts.pop(font, None)
            self._multi_persistent.fonts[font] = result
            self._multi_persistent.save()

        def get_font(self, font):

            """
            Последовательно ищет шрифт в следующем порядке:
                Сначала проверяется конкретный переданный путь,
                если нет - проверяется наличие в базе данных.
                Если и тут неудача - бросается исключение.
            """

            font = self._gui._fs_object._normpath(font)
            if not font.strip():
                raise ValueError(self._gui.translate("Файл шрифта не найден."))

            font = font_name = font.replace("\\", '/')

            if renpy.loadable(font):
                return font

            out_fn = path.abspath(path.join(self.multigame_fonts_folder, font))
            font = self._gui._fs_object._normpath(
                path.relpath(out_fn, config.gamedir)
            ).replace("\\", '/')

            if renpy.loadable(font):
                return font

            if font_name in self._multi_persistent.fonts:
                renpy.loader.loadable_cache.pop(font, None)
                font_bytes = self._multi_persistent.fonts[font_name]
                utils.save_data_to_file(font_bytes, out_fn)
                return font

            raise ValueError(self._gui.translate("Файл шрифта не найден."))

        def _check_setting(self):

            """
            Проверяет настройки, оказывающие влияние
            на значения из внешней области
            и применяет изменения в необходимых местах.
            """

            # _debug_mode
            store._translator3000.DEBUG = self._setting["_debug_mode"]
            parent_logger.setLevel(
                (logging.DEBUG if DEBUG else logging.CRITICAL)
            )

            # requestsFrequency
            if self._setting["requestsFrequency"] is None:
                _frq = current_session.__class__.RPM
            else:
                _frq = self._setting["requestsFrequency"]
            current_session.RPM = float(_frq)

        @classmethod
        def _dict_multisetdefault(cls, dct, default):

            """
            Устанавливает для 'dct' ключи из 'default', если их там нет.
            Возвращает булевое значение - был ли обновлён словарь.
            """

            _dict = __builtin__.dict

            updated = False
            for k, v in default.iteritems():

                if k not in dct:
                    dct[k] = copy.deepcopy(v)
                    updated = True

                if (isinstance(dct[k], _dict) and isinstance(v, _dict)):
                    _updated = cls._dict_multisetdefault(dct[k], v)
                    if _updated:
                        updated = True

            return updated

        def __call__(self, text, _update_on_hdd=True, **extra_kwargs):

            """
            Основной метод перевода.
            """

            _force = extra_kwargs.pop("_force", False)
            _check_double_call = extra_kwargs.pop("_check_double_call", False)

            if _check_double_call and (text in self._original_mapping):
                # Проверяем повторные вызовы
                # (если метод вызван с собственными результатами).
                return text

            if not (_force or self._translator_switcher):
                return self._apply_enabled_text_tags(text)

            try:

                _params = {
                    "service": self._setting["translationService"],
                    "text": self.unquote(text),
                    "dest": self.direction_of_translation,
                    "src": self.game_language,
                    "_update_on_hdd": _update_on_hdd
                }
                _params.update(extra_kwargs)
                result = self._translator_object.translate(**_params)

            except Exception as ex:
                if DEBUG:
                    raise ex
                return self._apply_enabled_text_tags(text)

            result = self.quote(result)
            result = self._apply_enabled_text_tags(result)

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
                entry_object.what = "{{#notTranslate}}{0}".format(
                    entry_object.translator3000_original_what
                )

        def _dump_setting(self):

            _backup = json.dumps(self._setting, ensure_ascii=False, indent=4)
            if isinstance(_backup, unicode):
                _backup = _backup.encode("utf_8")
            utils.save_data_to_file(_backup, self._user_setting_file)

            self._multi_persistent.setting.clear()
            for k in self.MULTIGAME_KEYS:
                v = self._setting[k]
                if v != self.DEFAULT_SETTING[k]:
                    self._multi_persistent.setting[k] = copy.deepcopy(v)
            self._multi_persistent.save()

        def backup_database(self):
            _service = self._setting["translationService"]
            return self._translator_object.backup_database(_service)

        def clear_cache(self):
            _service = self._setting["translationService"]
            return self._translator_object.clear_cache(_service, False)

        def clear_local_cache(self):
            _service = self._setting["translationService"]
            return self._translator_object.clear_cache(_service, True)

        def get_all_lang_codes(self):
            """
            Возвращает генератор доступных направлений,
            для текущего сервиса перевода.
            """
            _service = self._setting["translationService"]
            return self._translator_object.get_all_lang_codes(_service)

        def _apply_enabled_text_tags(self, text):

            if self._setting["extraTextOptions"]["font"] is not None:
                font = self.get_font(self._setting["extraTextOptions"]["font"])
                text = self._add_text_tag(text, "font", font)

            if self._setting["extraTextOptions"]["size"] is not None:
                size = self._setting["extraTextOptions"]["size"]
                text = self._add_text_tag(text, "size", size)

            if self._setting["extraTextOptions"]["bold"]:
                text = self._add_text_tag(text, 'b')

            if self._setting["extraTextOptions"]["italic"]:
                text = self._add_text_tag(text, 'i')

            return text

        @staticmethod
        def _add_text_tag(text, tag, value=None):
            if value is not None:
                _format_string = "{{{1}={2}}}{0}{{/{1}}}"
            else:
                _format_string = "{{{1}}}{0}{{/{1}}}"
            return _format_string.format(text, tag, value)

        @staticmethod
        def _substitute(s):
            """
            Заменяем переменные в тексте на конкретные значения.
            """
            s = renpy.substitutions.substitute(s, force=True, translate=False)
            if isinstance(s, basestring):
                return s
            return s[0]

        @classmethod
        def unquote(cls, s):
            """
            Преобразуется форматированный текст в "чистый",
            без тегов, переменных и т.п.
            """
            try:
                # Подстановка значений вида "[variable]".
                s = cls._substitute(s)
            except (KeyError, ValueError):
                pass
            try:
                # То же, но для "%(variable)s".
                s %= renpy.tag_quoting_dict
            except (KeyError, ValueError):
                pass
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
