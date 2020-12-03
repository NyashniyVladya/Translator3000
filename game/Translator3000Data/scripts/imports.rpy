
init -10 python in _translator3000:

    # Минимальная поддерживаемая версия Ren'Py - 6.99.12.4.
    # Код пишется с расчётом, что дефолтные строки являются юникодом.

    import logging
    import threading
    import json
    import store
    from os import path
    from store import (
        NoRollback,
        config,
        _preferences
    )
    from _translator3000 import (
        LOGGER as parent_logger,
        translator,
        utils
    )

    DEBUG = False
    parent_logger.setLevel((logging.DEBUG if DEBUG else logging.CRITICAL))
    LOGGER = parent_logger.getChild("Ren'Py")
