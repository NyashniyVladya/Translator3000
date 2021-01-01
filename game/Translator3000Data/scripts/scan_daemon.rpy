
init -8 python in _translator3000:

    class Preparer(threading.Thread, NoRollback):

        """
        Демон для параллельного перевода всего текста в игре.
        """

        __author__ = "Vladya"

        LOGGER = LOGGER.getChild("Preparer")

        def __init__(self, translator_object):

            super(Preparer, self).__init__()
            self.daemon = True

            self._translator = translator_object

            self.__status = None
            self.__completed = False
            self.__last_exception = None

            self._switcher = False
            self.__need_restart = True

        def restart(self):
            """
            Перезапуск скана.
            Например, если были сменены направления перевода.
            """
            self.LOGGER.debug(b"Restart of prescan thread has been requested.")
            self.__need_restart = True

        def get_info(self):
            done = total = 0
            status = .0
            if self.__status:
                done, total = self.__status
                if total > 0:
                    status = float(done) / float(total)
            return {"done": done, "total": total, "status": status}

        @property
        def status(self):
            info = self.get_info()
            return info["status"]

        def is_completed(self):
            return self.__completed

        def has_exception(self):
            if isinstance(self.__last_exception, Exception):
                return True
            return False

        def _raise_from_thread(self):
            if self.has_exception():
                raise self.__last_exception

        def run(self):

            _renpy_translator = renpy.game.script.translator

            while True:

                if not self.__need_restart:
                    time.sleep(1.)
                    continue

                self.__need_restart = False

                self.__status = None
                self.__completed = False
                self.__last_exception = None

                say_objects = tuple(
                    sorted(
                        map(
                            lambda tl: tl.predict()[0],
                            _renpy_translator.default_translates.itervalues()
                        ),
                        key=lambda _node: (_node.filename, _node.linenumber)
                    )
                )
                text_len = len(say_objects)

                try:
                    self.LOGGER.debug(b"Prescan thread is started.")
                    for counter, say_node in enumerate(say_objects):

                        while True:
                            if self._switcher:
                                break
                            time.sleep(1.)

                        if self.__need_restart:
                            break

                        self.__status = (counter, text_len)
                        renpy.restart_interaction()  # Для перерисовки статуса.
                        if ((counter % 100) == 0):
                            # Сохраняем бэкап на ЖД каждые 100 запросов.
                            self._translator.backup_database()
                        if not hasattr(say_node, "what"):
                            continue
                        if not isinstance(say_node.what, basestring):
                            continue
                        try:
                            self._translator(
                                say_node.what,
                                _update_on_hdd=False,
                                _force=True
                            )
                        except Exception as ex:
                            self.LOGGER.exception(ex.message)
                            self.__last_exception = ex
                            continue
                finally:
                    self._translator.backup_database()
                    self.__status = None
                    self.__completed = True
                    renpy.restart_interaction()
                    self.LOGGER.debug(b"Pre-scan is complete.")
