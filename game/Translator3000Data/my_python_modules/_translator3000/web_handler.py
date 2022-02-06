# -*- coding: utf-8 -*-
"""
@author: Vladya
"""

import time
import random
import threading
import requests

try:
    import urllib3
except ImportError:
    from requests.packages import urllib3


class HostInfo(object):

    __author__ = "Vladya"

    def __init__(self, host):

        self._host = host
        self._last_request = None
        self._lock = threading.Lock()


class WebHandler(requests.Session):

    __author__ = "Vladya"

    RPM = 100.  # Requests per minute.
    FORCE_RPM = None
    MAX_ATTEMPTS = 5

    single_instance = None

    def __new__(cls, logger_object):

        if cls.single_instance is None:
            cls.single_instance = super(WebHandler, cls).__new__(cls)

        return cls.single_instance

    def __init__(self, logger_object):

        super(WebHandler, self).__init__()

        _new_headers = {
            "User-Agent": (
                # Pretending a chrome browser.
                "Mozilla/5.0 (Windows NT 6.3; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/86.0.4240.193 "
                "Safari/537.36"
            ),
            "Accept": "*/*",
            "Accept-Language": "en-US,en-GB; q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive"
        }
        self.headers.update(_new_headers)

        self.LOGGER = logger_object.getChild("WebHandler")

        self.__request_lock = threading.Lock()

        self.__create_host_object_lock = threading.Lock()
        self.__hosts = {}

    def _get_host_object(self, url):
        _url = urllib3.util.parse_url(url)
        name = '.'.join(_url.hostname.split('.')[-2:])
        with self.__create_host_object_lock:
            if name not in self.__hosts:
                self.__hosts[name] = HostInfo(name)
            return self.__hosts[name]

    def request(self, method, url, *args, **kwargs):

        _url = urllib3.util.parse_url(url)
        host_object = self._get_host_object(url)

        _counter = 0
        _last_exception = Exception("Undefined error.")
        while True:

            _counter += 1
            if _counter > self.MAX_ATTEMPTS:
                raise _last_exception

            with host_object._lock:

                if host_object._last_request is not None:

                    if self.FORCE_RPM and (self.FORCE_RPM > .0):
                        rpm = self.FORCE_RPM
                    elif self.RPM > .0:
                        rpm = self.RPM
                    else:
                        raise Exception("Incorrect RPM value.")
                    _rpm = rpm * random.uniform(.75, 1.)
                    if _rpm <= .0:
                        # If 'rpm' is equal to a very small value.
                        _rpm = rpm
                    _need_to_wait = 60. / _rpm
                    while True:
                        _waiting_time = time.time() - host_object._last_request
                        if _waiting_time >= _need_to_wait:
                            break
                        time.sleep(.1)

                self.__request_lock.acquire()
                try:
                    self.LOGGER.debug(
                        "Try send '%s' request to '%s'. Attempt %d.",
                        method,
                        _url.hostname,
                        _counter
                    )
                    self.close()
                    result = super(WebHandler, self).request(
                        method,
                        url,
                        *args,
                        **kwargs
                    )
                except Exception as _last_exception:
                    #  Request was not sent. Do not update time.
                    self.LOGGER.error(_last_exception.message)
                    continue
                else:
                    #  Request was sent. Update time and check HTTP errors.
                    host_object._last_request = time.time()
                    try:
                        result.raise_for_status()
                    except Exception as _last_exception:
                        self.LOGGER.error(_last_exception.message)
                        continue
                    else:
                        self.LOGGER.debug(
                            "'%s' request to '%s' was successful. %d.",
                            method,
                            _url.hostname,
                            result.status_code
                        )
                        return result
                finally:
                    self.close()
                    self.__request_lock.release()
