
init -97 python in _translator3000_gui:

    class FileSystemWrapper(SingleTone):

        __author__ = "Vladya"

        available_font_exts = frozenset((".ttf", ".ttc", ".otf"))

        @property
        def desktop(self):
            user_folder = path.abspath(path.expanduser('~'))
            variant = path.join(user_folder, "Desktop")
            if path.isdir(variant):
                return variant
            return user_folder

        @staticmethod
        def _unicode_path(name):
            if not isinstance(name, basestring):
                raise TypeError(self.translate("Путь должен быть строкой."))
            return renpy.fsdecode(name)

        @classmethod
        def is_same_files(cls, descriptor1, descriptor2):

            hash1 = hashlib.md5()
            hash2 = hashlib.md5()
            for _hash, _descriptor in (
                (hash1, descriptor1),
                (hash2, descriptor2)
            ):
                _descriptor.seek(0)
                while True:
                    chunk = _descriptor.read((2 ** 10))
                    if not chunk:
                        break
                    _hash.update(chunk)

            if hash1.hexdigest() == hash2.hexdigest():
                return True
            return False

        @staticmethod
        def get_windows_mountdrive():
            for mount in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                mount = "{0}:\\".format(mount)
                if path.exists(mount):
                    yield mount

        @classmethod
        def _normpath(cls, filename):
            filename = cls._unicode_path(filename)
            if not filename.strip():
                return ""
            return path.normpath(filename)

        @classmethod
        def dirname(cls, filename, from_renpy=True):
            filename = cls._normpath(cls._unicode_path(filename))
            if (not from_renpy) and renpy.windows and path.ismount(filename):
                return ""
            directory = path.dirname(filename)
            if from_renpy:
                directory = directory.replace("\\", "/")
            return directory

        @classmethod
        def join(cls, *parts, **kwargs):
            from_renpy = kwargs.pop("from_renpy", True)
            result = cls._normpath(path.join(*parts, **kwargs))
            if from_renpy:
                result = result.replace("\\", "/")
            return result

        @classmethod
        def listdir(cls, directory, from_renpy=True):

            directory = cls._normpath(directory)

            result = {"dirs": set(), "files": set()}
            if from_renpy:

                for filename in map(cls._normpath, renpy.list_files()):

                    parent_dir, filename = path.split(filename)
                    if parent_dir == directory:
                        result["files"].add(filename)
                        continue

                    while parent_dir:
                        parent_dir, _directory = path.split(parent_dir)
                        if parent_dir == directory:
                            result["dirs"].add(_directory)
                            break

            elif not directory.strip():
                if renpy.windows:
                    result["dirs"].update(cls.get_windows_mountdrive())

            else:
                try:
                    _lisddir_result = tuple(os.listdir(directory))
                except Exception:
                    pass
                else:
                    for filename in _lisddir_result:
                        if path.isfile(path.join(directory, filename)):
                            result["files"].add(filename)
                        else:
                            result["dirs"].add(filename)

            return dict(
                map(lambda x: (x[0], tuple(sorted(x[1]))), result.iteritems())
            )

        @classmethod
        def get_clear_filename(cls, filename, delete_ext=True):
            """
            Возвращает имя файла без расширения и директорий.
            """
            filename = cls._normpath(filename)
            filename = path.basename(filename)
            if delete_ext:
                filename, _ext = path.splitext(filename)
            return filename

    class GUI(SingleTone):

        __author__ = "Vladya"

        available_languages = frozenset(("russian", "english"))

        def __init__(self, translator):

            if self.initialized:
                return

            self._translator = translator
            self._fs_object = FileSystemWrapper()
            self._current_menu_stack = []

            self._original_sample_text = (
                "Съешь же ещё этих мягких французских булок, да выпей чаю.\n"
                "The quick brown fox jumps over the lazy dog.\n"
                "(1 + 2) - 3 = (45 / 6789) * 0"
            )
            self._sample_text = self.translate(self._original_sample_text)

            self.initialized = True

        def _confirm(self, message, action):
            return self._forward(
                "translator3000_confirm_screen",
                message=message,
                yes_action=action
            )

        def _back(self):

            if not renpy.context()._menu:
                # Игрок вышел из контекста иным образом.
                self._current_menu_stack = []

            if not self._current_menu_stack:
                return setattr(self, "show", False)

            self._current_menu_stack.pop()
            if not self._current_menu_stack:
                return renpy.run(store.Return())

            return renpy.run(store.ShowMenu(self._current_menu_stack[-1]))

        def _forward(self, dest_screen, *screen_args, **screen_kwargs):
            if not renpy.context()._menu:
                self._current_menu_stack = []
            self._current_menu_stack.append(dest_screen)
            return renpy.run(
                store.ShowMenu(dest_screen, *screen_args, **screen_kwargs)
            )

        def ConfirmAction(self, message, action):
            return store.Function(self._confirm, message, action)

        def BackAction(self):
            """
            Для использования в качестве 'action'.
            """
            return store.Function(self._back)

        def ForwardAction(self, dest_screen, *screen_args, **screen_kwargs):
            return store.Function(
                self._forward,
                dest_screen,
                *screen_args,
                **screen_kwargs
            )

        def ApplySettingAction(self, restart_prescan_thread=False):
            translator = self._translator
            funcs = [translator._dump_setting, translator._check_setting]
            if restart_prescan_thread:
                funcs.append(translator._translate_preparer.restart)
            return tuple(map(store.Function, funcs))

        def is_correct_font(self, renpy_path_to_font):
            if renpy.game.context().init_phase:
                raise Exception("This method use render and not work in init.")
            filename = self._fs_object._normpath(
                renpy_path_to_font
            ).replace("\\", '/')
            if not renpy.loadable(filename):
                return False
            try:
                txt = store.Text("Test", font=filename)
                txt.render(
                    renpy.config.screen_width,
                    renpy.config.screen_height,
                    0,
                    0
                )
            except Exception as ex:
                return False
            else:
                return True

        def _set_font_pref(self, font, from_renpy=True):

            """
            Устанавливает шрифт.
            :font:
                Путь к файлу шрифта.
            :from_renpy:
                Если True, путь будет интерпретирован, как ренпаевский.
                Если False, шрифт будет скопирован в папку в директории ренпая
                и установлен.
                Если "from_database" будет установлено значение из базы данных.
            """

            font = self._fs_object._normpath(font)
            if not font.strip():
                raise ValueError(self.translate("Файл шрифта не найден."))

            if from_renpy:
                font = font.replace("\\", '/')
                renpy.loader.loadable_cache.pop(font, None)
                if from_renpy == "from_database":
                    m_pers = self._translator._multi_persistent
                    m_pers.fonts[font] = m_pers.fonts.pop(font)
                    m_pers.save()
                else:
                    if not self.is_correct_font(font):
                        return
                    self._translator.add_font_to_database(font)
                set_dict = self._translator._setting["extraTextOptions"]
                set_dict["font"] = font
                return renpy.run(self.ApplySettingAction())

            font = path.abspath(font)
            if not path.isfile(font):
                raise ValueError(self.translate("Файл шрифта не найден."))

            _counter = 0
            while True:
                filename = path.basename(font)
                if _counter:
                    filename = "{1} ({0}){2}".format(
                        _counter,
                        *path.splitext(filename)
                    )
                out_fn = path.abspath(
                    path.join(
                        renpy.config.gamedir,
                        self._translator._renpy_folder,
                        "pc_fonts",
                        filename
                    )
                )
                if not path.exists(out_fn):
                    break
                if path.isfile(out_fn):
                    # Если файл существует, проверяем тот же ли это файл,
                    # сравнивая хэш.
                    with open(font, "rb") as _f1:
                        with open(out_fn, "rb") as _f2:
                            if self._fs_object.is_same_files(_f1, _f2):
                                break
                _counter += 1

            with open(font, "rb") as _font_file:
                _translator3000.utils.save_data_to_file(_font_file, out_fn)

            renpy_fn = path.relpath(out_fn, renpy.config.gamedir)
            renpy_fn = self._fs_object._normpath(renpy_fn).replace("\\", '/')

            return self._set_font_pref(renpy_fn, from_renpy=True)

        @staticmethod
        def parse_size_format(value):
            """
            Преобразует формат размера текста '+10'/'-5'/'6' в два значения.
            Первое - размер текста (int).
            Второе - модификатор (unicode).
            """
            modifier = ""
            value = unicode(value)
            if value[0] in "+-":
                modifier, value = value[0], value[1:]
            if not value.isdigit():
                _msg = self.translate("Значение '{0}' должно быть числом.")
                raise ValueError(_msg.format(value))
            return (int(value), modifier)

        @property
        def _text_size_pref(self):
            size = self._translator._setting["extraTextOptions"]["size"]
            if size is None:
                size = "+0"
            value, mod = self.parse_size_format(size)
            return "{0}{1}".format(mod, value)

        @_text_size_pref.setter
        def _text_size_pref(self, new_size):
            value, mod = self.parse_size_format(new_size)
            self._translator._setting["extraTextOptions"]["size"] = (
                "{0}{1}".format(mod, value)
            )
            renpy.run(self.ApplySettingAction())

        @property
        def _text_size_without_mod(self):
            return self.parse_size_format(self._text_size_pref)[0]

        @_text_size_without_mod.setter
        def _text_size_without_mod(self, new_size):
            mod = self.parse_size_format(self._text_size_pref)[-1]
            self._text_size_pref = "{0}{1}".format(mod, new_size)

        @property
        def requests_frequency_pref(self):
            frq = self._translator._setting["requestsFrequency"]
            if frq is None:
                frq = _translator3000.current_session.__class__.RPM
            return float(frq)

        @requests_frequency_pref.setter
        def requests_frequency_pref(self, new_freq):
            new_freq = float(new_freq)
            self._translator._setting["requestsFrequency"] = new_freq
            renpy.run(self.ApplySettingAction())

        @property
        def gui_language(self):
            name = self.get_persistent_name("gui_language")
            if getattr(persistent, name) is None:
                setattr(persistent, name, "english")
            return getattr(persistent, name)

        @gui_language.setter
        def gui_language(self, new_language):
            new_language = new_language.strip().lower()
            if new_language not in self.available_languages:
                raise ValueError("Incorrect lang '{0}'.".format(new_language))
            if new_language != self.gui_language:
                name = self.get_persistent_name("gui_language")
                setattr(persistent, name, new_language)
                self._sample_text = self.translate(self._original_sample_text)

        @property
        def show(self):
            """
            Демонстрируется ли сейчас окно.
            """
            name = self.get_persistent_name("show")
            if getattr(persistent, name) is None:
                setattr(persistent, name, True)
            return getattr(persistent, name)

        @show.setter
        def show(self, new_status):
            new_status = bool(new_status)
            if new_status != self.show:
                name = self.get_persistent_name("show")
                setattr(persistent, name, new_status)

        @staticmethod
        def get_persistent_name(name):
            return "translator3000_{0}".format(name)

        def translate(self, text, language=None):
            """
            Небольшая обёртка над 'renpy.translation.translate_string'.
            По сути, аналог ренпаевского '__', но с конкретным указанием языка.
            """
            if not isinstance(text, basestring):
                raise TypeError("'text' should be a string.")
            if not isinstance(text, unicode):
                text = text.decode("utf_8")
            if language is None:
                language = self.gui_language
            if language not in self.available_languages:
                raise ValueError("Incorrect language '{0}'.".format(language))
            return renpy.translation.translate_string(
                text,
                language=language
            )
