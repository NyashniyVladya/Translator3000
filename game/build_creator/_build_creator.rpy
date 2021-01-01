
init 10 python in _build_creator:

    import os
    from os import path
    from store import (
        archiver,
        config
    )

    class _gamedir(object):

        """
        Сохранить файл в корневой директории.
        """

    class _samedir(object):

        """
        Сохранить файл в той же директории, что и есть.
        """

    class PackingData(object):

        __author__ = "Vladya"

        def __init__(self, renpy_name, pack_name, _type, exts=None):

            """
            :renpy_name:
                Имя файла/папки в формате Ренпая (относительно папки 'game').
            :pack_name:
                Имя файла/папки в формате Ренпая
                с которым данные будут архивированы.
            :_type:
                Два возможных значения:
                    "folder": Работаем с папкой.
                    "file": Работаем с файлом.
            :exts:
                Только для папки. Для файла игнорируется.
                Расширения файлов, которые архивируем.
                None - архивируем всё.
            """

            self.__type = _type.strip().lower()
            if self.__type not in ("file", "folder"):
                raise ValueError(__("Некорректно указан тип \"файл/папка\"."))

            self.__exts = None
            if (self.__type == "folder") and (exts is not None):
                self.__exts = frozenset(map(lambda x: x.strip().lower(), exts))

            self.__renpy_name = path.normpath(renpy_name).replace('\\', '/')

            if pack_name not in (_gamedir, _samedir):
                pack_name = path.normpath(pack_name).replace('\\', '/')
            self.__pack_name = pack_name

        def get_data_for_pack(self):

            """
            Возвращает генератор формата:
                (a, b)
                Где:
                    'a': Имя файла в формате Ренпая.
                    'b': Абсолютный путь к файлу на ЖД.
            """

            _path_to_data = self._get_abs_path(self.__renpy_name, self.__type)

            if self.__type == "file":

                if self.__pack_name is _samedir:
                    pack_name = self.__renpy_name
                elif self.__pack_name is _gamedir:
                    pack_name = path.basename(self.__renpy_name)
                else:
                    pack_name = self.__pack_name
                yield (pack_name, _path_to_data)

            elif self.__type == "folder":

                for _dir, dirnames, filenames in os.walk(_path_to_data):

                    for filename in filenames:

                        full_fn = path.abspath(path.join(_dir, filename))

                        pack_name = path.relpath(full_fn, _path_to_data)
                        if self.__pack_name is _samedir:
                            pack_name = path.join(self.__renpy_name, pack_name)
                        elif self.__pack_name is _gamedir:
                            pass
                        else:
                            pack_name = path.join(self.__pack_name, pack_name)
                        pack_name = path.normpath(pack_name).replace('\\', '/')

                        ext = path.splitext(full_fn)[-1].strip().lower()
                        if (self.__exts is None) or (ext in self.__exts):
                            yield (pack_name, full_fn)

            else:
                raise RuntimeError(__("Некорректно определён тип данных."))

        @staticmethod
        def _get_abs_path(renpy_path, _type):

            """
            Вычисляет абсолютный путь из относительного имени Ren'Py.
            """

            _type = _type.strip().lower()
            if _type == "folder":
                _check_func = path.isdir
            elif _type == "file":
                _check_func = path.isfile
            else:
                raise ValueError(__("Некорректно указан тип \"файл/папка\"."))

            for searchpath in config.searchpath:
                variant = path.abspath(path.join(searchpath, renpy_path))
                if _check_func(variant):
                    return variant

            raise Exception(__("Путь \"{0}\" не найден.").format(renpy_path))

    class RPACreator(archiver.Archive):

        __author__ = "Vladya"
        __version__ = "2.0.0"

        DATA_FOR_PACKING = (
            PackingData(
                renpy_name="Translator3000Data/my_python_modules",
                pack_name=_gamedir,
                _type="folder",
                exts=(".py",)
            ),
            PackingData(
                renpy_name="Translator3000Data/third_party_python_modules",
                pack_name=_gamedir,
                _type="folder",
                exts=(".pem", ".py")
            ),
            PackingData(
                renpy_name="Translator3000Data/scripts",
                pack_name="Translator3000Scripts",
                _type="folder",
                exts=(".rpyc",)
            ),
            PackingData(
                renpy_name="Translator3000Data/ingame_gui",
                pack_name="Translator3000GUIScripts",
                _type="folder",
                exts=(".rpyc",)
            ),
            PackingData(
                renpy_name="tl/english/000translate_trigger.rpyc",
                pack_name="tl/english/translator3000_gui_tl.rpyc",
                _type="file"
            )
        )

        def __init__(self, name):
            """
            Архив будет размещён в основной директории игры (НЕ в game).
            """
            name = "{0}.rpa".format(*path.splitext(name))
            _rpa_name = path.abspath(path.join(config.basedir, name))
            super(RPACreator, self).__init__(_rpa_name)

        @classmethod
        def create_build(cls, build_name):
            with cls(build_name) as _rpa:
                _rpa._pack()

        def _pack(self):
            """
            Пакует данные, указанные в 'self.DATA_FOR_PACKING'.
            """
            for data_object in self.DATA_FOR_PACKING:
                for renpy_fn, abs_fn in data_object.get_data_for_pack():
                    self.add(renpy_fn, abs_fn)

        def add(self, name, path):
            """
            :name:
                Имя в формате ренпая.
            :path:
                Путь к файлу на ЖД.
            """
            return super(RPACreator, self).add(name, path)

        def __enter__(self):
            return self

        def __exit__(self, ex_type, ex_value, traceback):
            if ex_value:
                self.f.close()
                if path.isfile(self.f.name):
                    os.remove(self.f.name)
                raise ex_type(
                    __("Сборка неудачна.\n{0}").format(ex_value.message)
                )
            self.close()
