
init 10 python in _translator3000build:

    import os
    from os import path
    from store import (
        archiver,
        config
    )

    class _RPA(archiver.Archive):

        DATA_FOR_PACKING = (
            ("googleTranslateHandler", (".py",)),
            ("Translator3000Scripts", (".rpyc",))
        )

        def __init__(self, name):
            """
            Архив будет размещён в основной директории игры (НЕ в game).
            """
            name = "{0}.rpa".format(*path.splitext(name))
            _rpa_name = path.abspath(path.join(config.basedir, name))
            super(_RPA, self).__init__(_rpa_name)

        @classmethod
        def create_build(cls, build_name):
            with cls(build_name) as _rpa:
                _rpa._pack()

        @staticmethod
        def _get_renpy_fn(filename, gamedir=None):
            """
            Переводит имя файла в формате файловой системы в относительное имя
            RenPy.
            :gamedir:
                Директория папки game.
                Как правило, 'config.gamedir', но могут быть иные значения
                из 'config.searchpath'.
            """
            if not gamedir:
                gamedir = config.gamedir
            filename, gamedir = map(path.abspath, (filename, gamedir))
            filename = path.relpath(filename, gamedir)
            return filename.replace('\\', '/')

        def _pack(self):
            """
            Пакует данные, указанные в 'self.DATA_FOR_PACKING'.
            """
            for searchpath in config.searchpath:
                for data in self.DATA_FOR_PACKING:
                    if isinstance(data, basestring):
                        # Пакуем файл.
                        full_fn = path.abspath(path.join(searchpath, data))
                        renpy_fn = self._get_renpy_fn(full_fn, searchpath)
                        if path.isfile(full_fn):
                            self.add(renpy_fn, full_fn)
                    elif isinstance(data, tuple):
                        # Папку.
                        folder, exts = data
                        folder = path.abspath(path.join(searchpath, folder))
                        if path.isdir(folder):
                            for _path, _f, files in os.walk(folder):
                                for _file in files:
                                    full_fn = path.join(_path, _file)
                                    ext = path.splitext(full_fn)[-1]
                                    if (exts == '*') or (ext in exts):
                                        renpy_fn = self._get_renpy_fn(
                                            full_fn,
                                            searchpath
                                        )
                                        self.add(renpy_fn, full_fn)

        def add(self, name, path):
            """
            :name:
                Имя в формате ренпая.
            :path:
                Путь к файлу на ЖД.
            """
            return super(_RPA, self).add(name, path)

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
