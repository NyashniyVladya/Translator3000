# -*- coding: utf-8 -*-
"""
Handling requests to the network.

@author: Vladya
"""

import time
import urllib2
from threading import Lock


class WebError(Exception):
    pass


class HostInfo(object):

    __author__ = "Vladya"

    def __init__(self, host):

        self._host = host
        self._last_request = None
        self._lock = Lock()


class WebHandler(object):

    __author__ = "Vladya"

    RPM = 100.  # Requests per minute.
    headers = {
        "User-Agent": (  # Pretending a browser.
            "Mozilla/5.0 (Windows NT 6.3; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/84.0.4147.105 "
            "Safari/537.36 "
            "OPR/70.0.3728.119"
        )
    }

    def __init__(self, logger=None):

        self.logger = None
        if logger:
            self.logger = logger.getChild("WebHandler")

        self.opener = urllib2.build_opener()

        _headers = dict(self.opener.addheaders)
        _headers.update(self.headers)

        self.opener.addheaders = list(_headers.iteritems())

        self._create_host_object_lock = Lock()
        self._hosts = {}

    def open(self, url, data=None):

        if not isinstance(url, urllib2.urlparse.ParseResult):
            url = urllib2.urlparse.urlparse(url)

        if not url.scheme:
            url = urllib2.urlparse.ParseResult(
                "https",
                url.netloc,
                url.path,
                url.params,
                url.query,
                url.fragment
            )

        with self._create_host_object_lock:  # Parallelization.

            if url.hostname not in self._hosts:
                self._hosts[url.hostname] = HostInfo(url.hostname)

            host_info = self._hosts[url.hostname]

        with host_info._lock:

            if host_info._last_request is not None:
                while True:
                    time_after_request = time.time() - host_info._last_request
                    if time_after_request >= (60. / self.RPM):
                        break
                    time.sleep(.01)
            try:
                if self.logger:
                    self.logger.debug("Try to open \"%s\".", url.geturl())
                result = self.opener.open(url.geturl(), data)
            except Exception as ex:
                if isinstance(ex, urllib2.HTTPError):
                    # Server handle the request. Update time.
                    host_info._last_request = time.time()
                message = getattr(ex, "reason", ex.message)
                raise WebError(message)
            else:
                host_info._last_request = time.time()
                return result
