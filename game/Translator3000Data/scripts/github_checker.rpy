
init -9 python in _translator3000:

    class GitChecker(NoRollback):

        __author__ = "Vladya"

        LOGGER = LOGGER.getChild("GitChecker")

        OWNER = "NyashniyVladya"
        REPO = "Translator3000"

        filename = "Translator3000.rpa"

        def __init__(self, translator_object):

            self._translator = translator_object

            self.__json_answer = None
            self.__lock = threading.Lock()
            self.__ui_lock = threading.Lock()

            self.__need_init_process = True
            self._download_process = None

        def init_download_process(self):

            self.__need_init_process = False
            self._download_process = None

            try:
                if self.is_need_update():
                    self._download_process = Downloader(
                        self.download_link,
                        self._get_rpa_path()
                    )
            except Exception as ex:
                # Проблемы с интернетом.
                if DEBUG:
                    raise ex
                self._download_process = None

        def _overlay_callable(self):

            with self.__ui_lock:

                if self.__need_init_process:
                    self.init_download_process()

                if self._download_process:

                    ui.vbox()

                    if self._download_process.is_running():
                        # Процесс запущен.

                        self._translator._ui_text(
                            __("Загружено {0:.2f}Мб из {1:.2f}.").format(
                                self._download_process.current_size,
                                self._download_process.total_size
                            )
                        )
                        self._translator._ui_text(
                            "{0} Mbit/s".format(self._download_process.speed)
                        )
                        ui.bar(1., self._download_process.status, xmaximum=200)

                    elif self._download_process.is_over():
                        # Процесс окончен.

                        if self._download_process.is_successful():
                            self._translator._ui_text(
                                __("Загрузка окончена. Перезапустите игру.")
                            )
                        else:
                            if DEBUG:
                                self._download_process._raise_from_thread()
                            self._translator._ui_text(__("Произошла ошибка."))

                        self._translator._ui_textbutton(
                            __("Закрыть окно."),
                            clicked=Function(self._hide_ui)
                        )

                    else:
                        # Процесс ещё не начинался.
                        _text = __(
                            (
                                "На GitHub доступно обновление переводчика.\n"
                                "Версия {0[0]}.{0[1]}.{0[2]} "
                                "(текущая {1[0]}.{1[1]}.{1[2]}).\n"
                                "Размер {2:.2f}Мб."
                            )
                        ).format(
                            self.version,
                            VERSION,
                            self._download_process._b_to_mb(self.size)
                        )
                        self._translator._ui_text(_text)
                        self._translator._ui_textbutton(
                            __("Начать загрузку."),
                            clicked=Function(self._download_process.start)
                        )

                    ui.close()

        def _hide_ui(self):
            with self.__ui_lock:
                self.__need_init_process = False
                self._download_process = None

        def is_need_update(self):
            return (self.version > VERSION)

        def _get_rpa_path(cls):
            for fn in renpy.list_files():
                fn = path.normpath(fn)
                if path.basename(fn) == cls.filename:
                    for _searchpath in config.searchpath:
                        full_fn = path.abspath(path.join(_searchpath, fn))
                        if path.isfile(full_fn):
                            return full_fn
            return path.abspath(path.join(config.gamedir, cls.filename))

        @property
        def download_link(self):
            return self.rpa["browser_download_url"]

        @property
        def size(self):
            return self.rpa["size"]

        @property
        def version(self):
            return tuple(
                map(int, self.latest_release["tag_name"][1:].split('.'))
            )

        @property
        def latest_release(self):
            with self.__lock:
                if self.__json_answer is None:
                    url = self.get_url("/repos/{owner}/{repo}/releases/latest")
                    _request = requests.get(url)
                    try:
                        self.__json_answer = _request.json()
                    finally:
                        _request.close()
                return self.__json_answer

        @property
        def rpa(self):
            return self.latest_release["assets"][0]

        def get_url(self, _path):
            return urllib3.util.Url(
                scheme="https",
                auth=None,
                host="api.github.com",
                port=None,
                path=_path.format(owner=self.OWNER, repo=self.REPO),
                query=None,
                fragment=None
            ).url

    class Downloader(threading.Thread, NoRollback):

        __author__ = "Vladya"

        LOGGER = LOGGER.getChild("Downloader")

        def __init__(self, url, out_fn):

            super(Downloader, self).__init__()
            self.daemon = True

            if not isinstance(url, urllib3.util.Url):
                url = urllib3.util.parse_url(url)
            self.__url = url

            if not isinstance(out_fn, basestring):
                raise TypeError(__("Путь должен быть строкой."))

            if not isinstance(out_fn, unicode):
                out_fn = out_fn.decode("utf_8")

            self.__out_fn = path.abspath(out_fn)

            self.__current_size = 0
            self.__total_size = None

            self.__is_running = False
            self.__is_over = False
            self.__exception = None

            # Для подсчёта скорости загрузки.
            self.__last_timestamp = None
            # Значение в байтах в секунду.
            self.__speed = None

        @staticmethod
        def _b_to_mb(value):
            return ((float(value) / (2. ** 10.)) / (2. ** 10.))

        @property
        def speed(self):
            """
            Скорость в Мбит/с.
            """
            if self.__speed is None:
                return .0
            return (self._b_to_mb(self.__speed) * 8.)

        @property
        def status(self):
            if not self.__total_size:
                return .0
            current, total = map(
                float,
                (self.__current_size, self.__total_size)
            )
            return (current / total)

        @property
        def current_size(self):
            return self._b_to_mb(self.__current_size)

        @property
        def total_size(self):
            if not self.__total_size:
                return float("+inf")
            return self._b_to_mb(self.__total_size)

        def is_running(self):
            return self.__is_running

        def is_over(self):
            return self.__is_over

        def is_successful(self):
            return (self.is_over() and (not self.has_exception()))

        def has_exception(self):
            if isinstance(self.__exception, Exception):
                return True
            return False

        def _raise_from_thread(self):
            if self.has_exception():
                raise self.__exception

        def run(self):

            try:
                self.__is_running = True
                temp_fn = "{0}.tmp".format(self.__out_fn)
                utils.create_dir_for_file(temp_fn)
                _stream = requests.get(self.__url, stream=True)
                try:
                    self.__total_size = int(_stream.headers["Content-Length"])
                    with open(temp_fn, "wb") as _write_file:
                        self.__last_timestamp = time.time()
                        for chunk in _stream.iter_content((2 ** 10)):
                            chunk_size = len(chunk)
                            _write_file.write(chunk)
                            self.__current_size += chunk_size
                            elapsed = time.time() - self.__last_timestamp
                            if elapsed > .0:
                                self.__speed = chunk_size / elapsed
                            self.__last_timestamp = time.time()
                            renpy.restart_interaction()
                finally:
                    _stream.close()
                if path.isfile(self.__out_fn):
                    os.remove(self.__out_fn)
                utils.create_dir_for_file(self.__out_fn)
                os.rename(temp_fn, self.__out_fn)
            except Exception as ex:
                self.__exception = ex
            finally:
                self.__is_running = False
                self.__is_over = True
                self.__last_timestamp = None
                self.__speed = None
                renpy.restart_interaction()
