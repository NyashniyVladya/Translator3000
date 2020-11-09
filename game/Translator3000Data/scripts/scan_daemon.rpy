
init -9 python in _translator3000:

    class Preparer(threading.Thread, NoRollback):

        """
        Демон для параллельного перевода всего текста в игре.
        """

        __author__ = "Vladya"

        def __init__(self, translator_object):

            super(Preparer, self).__init__()
            self.daemon = True

            self._translator = translator_object

            self._status = None
            self._completed = False

        def _show_scan_status(self, *screen_args, **screen_kwargs):

            """
            Демонстрация статуса сканирования.
            """

            if (not self._completed) and self._status:
                _done, _scope_of_work = self._status
                ui.text(
                    __("Переведено {0} строк из {1} ({2:.1%}).").format(
                        _done,
                        _scope_of_work,
                        (float(_done) / float(_scope_of_work))
                    ),
                    color="#fff",
                    outlines=[(2, "#000", 0, 0)],
                    anchor=(.0, .0),
                    pos=(.01, .01)
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
                for counter, say_node in enumerate(say_objects):
                    self._status = (counter, text_len)
                    renpy.restart_interaction()  # Для перерисовки статуса.
                    self._translator(say_node.what, _update_on_hdd=False)
            finally:
                self._translator._translator_object.backup_database()
                self._status = None
                self._completed = True
