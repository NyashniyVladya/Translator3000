
init -10 python in _translator3000:

    # Минимальная поддерживаемая версия Ren'Py - 6.99.12.4.
    # Код пишется с расчётом, что дефолтные строки являются юникодом.

    import __builtin__
    import time
    import types
    import copy
    import os
    import pickle
    import logging
    import requests
    import threading
    import json
    import collections
    import store
    from os import path
    from store import (
        NoRollback,
        Function,
        config,
        _preferences
    )
    from _translator3000 import (
        LOGGER as parent_logger,
        current_session,
        translator,
        utils,
        _paths
    )

    if renpy.version(True) >= (7, 4, 0):
        import urllib3
    else:
        from requests.packages import urllib3

    VERSION = (2, 10, 6)

    DEBUG = False
    parent_logger.setLevel((logging.DEBUG if DEBUG else logging.CRITICAL))
    LOGGER = parent_logger.getChild("Ren'Py")

    _ORIGINAL_SET_TEXT_METHOD = renpy.text.text.Text.set_text
    _ORIGINAL_DEVELOPER_MODE = config.developer

    SingleTone = store.translator3000_preinit.SingleTone

    class _MultiGameData(SingleTone):

        """
        Вообще, по идее, эта логика должна работать через MultiPersistent,
        но в старых версиях ренпая он поломан, так что,
        для совместимости со всеми версиями, делаем рабочий "велосипед".
        """

        __author__ = "Vladya"
        __version__ = "1.0.0"

        lock = threading.RLock()

        filename = path.join(
            _paths.DATABASE_FOLDER,
            "Ren'Py MuitiGame Data.pickle"
        )

        pickle_protocol = 2

        @classmethod
        def get_object(cls):

            with cls.lock:

                if path.isfile(cls.filename):
                    try:
                        with open(cls.filename, "rb") as _file:
                            final_object = pickle.load(_file)
                        major, minor, patch = map(
                            int,
                            final_object._version.split('.')
                        )
                        delattr(final_object, "_version")
                        if major == int(cls.__version__.split('.')[0]):
                            return final_object
                    except Exception as ex:
                        if DEBUG:
                            raise ex

                return cls()

        def __getattr__(self, name):
            if name.startswith("__") and name.endswith("__"):
                raise AttributeError(name)
            return None

        def __getstate__(self):
            with self.lock:
                data = copy.deepcopy(self.__dict__)
            data.pop("initialized", None)
            data["_version"] = self.__version__
            return data

        def __setstate__(self, data):
            with self.lock:
                self.__dict__.update(copy.deepcopy(data))
                self.initialized = True

        def save(self):
            with self.lock:
                savebytes = pickle.dumps(self, self.pickle_protocol)
                utils.save_data_to_file(savebytes, self.filename)
