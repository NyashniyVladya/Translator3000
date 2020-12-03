# -*- coding: utf-8 -*-
"""
@author: Vladya
"""

import logging
from . import (
    _paths,
    utils
)


class Logger(logging.Logger):

    __author__ = "Vladya"

    root = logging.RootLogger(logging.CRITICAL)
    manager = logging.Manager(root)

    @classmethod
    def getLogger(cls, name):

        cls.manager.setLoggerClass(cls)
        _logger = cls.manager.getLogger(name)

        _formatter = logging.Formatter(
            "%(asctime)s %(levelname)s:%(name)s\n%(message)s\n"
        )

        utils.create_dir_for_file(_paths._logfile)
        _handler = logging.FileHandler(_paths._logfile)
        _handler.setFormatter(_formatter)
        _logger.addHandler(_handler)

        if not utils.renpy:
            _handler = logging.StreamHandler()
            _handler.setFormatter(_formatter)
            _logger.addHandler(_handler)

        return _logger
