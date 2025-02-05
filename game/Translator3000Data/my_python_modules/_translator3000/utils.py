# -*- coding: utf-8 -*-
"""
@author: Vladya
"""

import io
import os
import sys
import shutil
from os import path

try:
    from renpy import defaultstore as store
    from renpy import exports as renpy
except ImportError:
    renpy = store = None


class _DataSaver(object):

    __author__ = "Vladya"
    __version__ = "1.0.0"

    def __init__(self, data, out_fn):

        if isinstance(data, (bytes, str)):
            self.__bytedata = data
        elif (hasattr(data, "read") and hasattr(data, "seek")):
            #  file-like object
            data.seek(0)
            self.__bytedata = b""
            while True:
                _chunk = data.read((2 ** 20))
                if not _chunk:
                    break
                self.__bytedata += _chunk
        else:
            raise ValueError("'data' should be file-like object or string.")

        if not isinstance(self.__bytedata, bytes):
            self.__bytedata = self.__bytedata.encode("utf_8")

        if not isinstance(out_fn, (bytes, str)):
            raise TypeError("'out_fn' should be a string.")

        if not isinstance(out_fn, str):
            out_fn = out_fn.decode(self._get_filesystemencoding())
        self.__filename = path.abspath(out_fn)

    @classmethod
    def save(cls, data, out_fn):
        saver_object = cls(data, out_fn)
        return saver_object._save()

    @staticmethod
    def _get_filesystemencoding():
        return (sys.getfilesystemencoding() or "utf_8")

    @classmethod
    def _create_dir_for_file(cls, filename):
        if not isinstance(filename, str):
            filename = filename.decode(cls._get_filesystemencoding())
        filename = path.abspath(filename)
        directory = path.dirname(filename)
        if not path.isdir(directory):
            os.makedirs(directory)

    def _save(self):
        temp_fn = u"{0}.tmp".format(self.__filename)
        self._create_dir_for_file(temp_fn)
        with io.BytesIO(self.__bytedata) as _read_file:
            with open(temp_fn, "wb") as _write_file:
                while True:
                    _chunk = _read_file.read((2 ** 20))
                    if not _chunk:
                        break
                    _write_file.write(_chunk)
        if path.isfile(self.__filename):
            os.remove(self.__filename)
        self._create_dir_for_file(self.__filename)
        os.rename(temp_fn, self.__filename)


def remove_dir(dirname):

    if not isinstance(dirname, str):
        dirname = dirname.decode(_DataSaver._get_filesystemencoding())
    dirname = path.abspath(dirname)

    if path.isdir(dirname):
        shutil.rmtree(dirname)


save_data_to_file = _DataSaver.save
create_dir_for_file = _DataSaver._create_dir_for_file
