
init -10 python in _translator3000:

    # Минимальная поддерживаемая версия Ren'Py - 6.99.12.4.
    # Код пишется с расчётом, что дефолтные строки являются юникодом.

    import __builtin__
    import time
    import copy
    import os
    import logging
    import requests
    import threading
    import json
    import collections
    import store
    from os import path
    from requests.packages import urllib3
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
        utils
    )

    VERSION = (2, 5, 5)

    DEBUG = False
    parent_logger.setLevel((logging.DEBUG if DEBUG else logging.CRITICAL))
    LOGGER = parent_logger.getChild("Ren'Py")

    class SingleTone(NoRollback):

        initialized = False
        single_instance = None

        def __new__(cls, *args, **kwargs):
            if cls.single_instance is None:
                cls.single_instance = super(SingleTone, cls).__new__(cls)
            return cls.single_instance

        def __init__(self):
            self.initialized = True

        def __getstate__(self):
            return None

        def __setstate__(self, data):
            self.__init__()
