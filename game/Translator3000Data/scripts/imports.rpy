
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
    from googleTranslateHandler import (
        LOGGER,
        translator,
        utils
    )

    DEBUG = False
    LOGGER.setLevel((logging.DEBUG if DEBUG else logging.CRITICAL))
