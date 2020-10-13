
init -10 python in _translator3000:

    import os
    import io
    import json
    import types
    import logging
    import threading
    from os import path
    from googleTranslateHandler import (
        LOGGER,
        translator,
        consts
    )
    from store import (
        NoRollback,
        config,
        _preferences
    )

    DEBUG = False

    LOGGER.setLevel((logging.DEBUG if DEBUG else logging.CRITICAL))
