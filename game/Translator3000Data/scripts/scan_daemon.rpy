
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

            self._status = None
            self._completed = False
            self._last_exception = None

        def _overlay_callable(self, *screen_args, **screen_kwargs):

            """
            Демонстрация статуса сканирования.
            """

            if DEBUG and self._last_exception:
                raise self._last_exception

            if (not self._completed) and self._status:
                _done, _scope_of_work = self._status
                self._translator._ui_text(
                    __("Переведено {0} строк из {1} ({2:.1%}).").format(
                        _done,
                        _scope_of_work,
                        (float(_done) / float(_scope_of_work))
                    )
                )

        def run(self):

            _renpy_translator = renpy.game.script.translator

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
                self.LOGGER.debug(b"Pre-scanning process is started.")
                for counter, say_node in enumerate(say_objects):
                    self._status = (counter, text_len)
                    renpy.restart_interaction()  # Для перерисовки статуса.
                    if ((counter % 100) == 0):
                        # Сохраняем бэкап на ЖД каждые 100 запросов.
                        self._translator.backup_database()
                    if not hasattr(say_node, "what"):
                        continue
                    if not isinstance(say_node.what, basestring):
                        continue
                    try:
                        self._translator(say_node.what, _update_on_hdd=False)
                    except Exception as ex:
                        self.LOGGER.exception(ex.message)
                        self._last_exception = ex
                        continue
            finally:
                self._translator.backup_database()
                self._status = None
                self._completed = True
                renpy.restart_interaction()
                self.LOGGER.debug(b"Pre-scan is complete.")
