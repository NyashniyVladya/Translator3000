
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

    if renpy.version(True) >= (7, 4, 0):
        import urllib3
    else:
        from requests.packages import urllib3

    VERSION = (2, 6, 0)

    DEBUG = False
    parent_logger.setLevel((logging.DEBUG if DEBUG else logging.CRITICAL))
    LOGGER = parent_logger.getChild("Ren'Py")

    SingleTone = store.translator3000_preinit.SingleTone
