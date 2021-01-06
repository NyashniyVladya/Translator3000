
init -98:

    screen translator3000_base_vbox_in_window(*_actions):

        # Предполагается, что объект 'translator3000'
        # имеется в глобальном пространстве.

        tag translator3000_screen
        style_prefix "translator3000"

        $ back_action = (_actions + (translator3000._gui.BackAction(),))

        showif translator3000._gui.show:
            if renpy.context()._menu:
                key "game_menu" action back_action
            window:
                hbox:
                    box_reverse True
                    textbutton "[[<=]":
                        # Закрыть окно.
                        align (1., .0)
                        action back_action
                    viewport:
                        id "translator_base_wp"
                        mousewheel True
                        draggable True
                        vbox:
                            transclude
                    vbar value YScrollValue("translator_base_wp")
                at translator3000_general_window

    screen translator3000_gui:

        # Основной скрин.

        tag translator3000_screen
        style_prefix "translator3000"

        key "alt_K_BACKQUOTE" action ToggleField(translator3000._gui, "show")

        $ _gui =  translator3000._gui
        $ _t = _gui.translate

        if translator3000._translator_switcher:
            $ state = "Приостановить перевод."
        else:
            $ state = "Возобновить перевод."

        use translator3000_base_vbox_in_window:
            label "Translator3000. {0}".format(
                _t("Версия {0}.{1}.{2}.")
            ).format(*_translator3000.VERSION)
            textbutton _t(state):
                action ToggleField(
                    translator3000,
                    "_translator_switcher"
                )
            textbutton _t("Сделать бэкап БД."):
                action Function(translator3000.backup_database)

            textbutton _t("Поменять язык интерфейса."):
                action _gui.ForwardAction("translator3000_gui_language")

            textbutton _t("Настройки переводчика."):
                action _gui.ForwardAction("translator3000_user_preferences")

            null height 10
            use translator3000_github_update
            null height 10
            use translator3000_prescan_status

    screen translator3000_gui_language:

        # Язык интерфейса.

        tag translator3000_screen
        style_prefix "translator3000"

        $ _t = translator3000._gui.translate
        $ quote = translator3000.quote

        use translator3000_base_vbox_in_window:
            label _t("Язык интерфейса (не перевода).")
            for t in sorted(translator3000._gui.available_languages):
                textbutton quote(t).title():
                    action SetField(translator3000._gui, "gui_language", t)

    screen translator3000_set_language(field_name):

        # Язык перевода (или игры).

        tag translator3000_screen
        style_prefix "translator3000"

        $ _t = translator3000._gui.translate
        $ quote = translator3000.quote
        $ py_translator = translator3000._translator_object
        $ service = translator3000._setting["translationService"]

        use translator3000_base_vbox_in_window:
            label _t("Выбор языка.")
            for code in sorted(translator3000.get_all_lang_codes()):
                textbutton quote(
                    py_translator.get_lang_name(service, code)
                ).title():
                    action (
                        SetDict(translator3000._setting, field_name, code),
                        translator3000._gui.ApplySettingAction(True)
                    )

    screen translator3000_sample_text:

        #  Пример текста, с использованием панграм.

        tag translator3000_screen
        style_prefix "say"

        $ _gui = translator3000._gui
        $ _t = _gui.translate
        $ quote = translator3000.quote

        input:
            style "translator3000_input_text"
            align (.5, .5)
            value FieldInputValue(_gui, "_sample_text")

        window:
            yalign 1.
            text translator3000._apply_enabled_text_tags(
                quote(_gui._sample_text)
            ):
                layout "tex"
                align (
                    _translator3000_gui.PHI_CONST2,
                    _translator3000_gui.PHI_CONST
                )

    screen translator3000_set_font(from_game=True):

        # Установка шрифта.

        tag translator3000_screen
        style_prefix "translator3000"

        $ _gui = translator3000._gui
        $ quote = translator3000.quote
        $ _fs_object = _gui._fs_object
        $ _t = _gui.translate
        $ text_setting = translator3000._setting["extraTextOptions"]

        default current_dir = ("" if from_game else _fs_object.desktop)

        use translator3000_sample_text
        use translator3000_base_vbox_in_window:

            label _t("Настройки шрифта.")

            if text_setting["font"] is not None:
                text quote(
                    _fs_object.get_clear_filename(text_setting["font"])
                ):
                    size 30

            if from_game == "from_database":

                for fnt in reversed(
                    tuple(translator3000._multi_persistent.fonts.iterkeys())
                ):
                    textbutton quote(_fs_object.get_clear_filename(fnt)):
                        action Function(
                            _gui._set_font_pref,
                            fnt,
                            from_renpy="from_database"
                        )

            else:

                if current_dir:
                    text current_dir
                    textbutton _t("Перейти в предыдущую директорию."):
                        action SetScreenVariable(
                            "current_dir",
                            _fs_object.dirname(current_dir, from_game)
                        )

                null height 30
                vbox:
                    $ data_in_dir = _fs_object.listdir(current_dir, from_game)
                    for _directory in data_in_dir["dirs"]:
                        $ full_path = _fs_object.join(
                            current_dir,
                            _directory,
                            from_renpy=from_game
                        )
                        textbutton _t("Перейти в \"{0}\".").format(
                            quote(_directory)
                        ):
                            action SetScreenVariable("current_dir", full_path)
                    null height 10
                    for _filename in data_in_dir["files"]:
                        $ full_path = _fs_object.join(
                            current_dir,
                            _filename,
                            from_renpy=from_game
                        )
                        $ ext = _translator3000_gui.path.splitext(full_path)[1]
                        if ext.lower() in _fs_object.available_font_exts:
                            textbutton quote(
                                _fs_object.get_clear_filename(_filename)
                            ):
                                action Function(
                                    _gui._set_font_pref,
                                    full_path,
                                    from_renpy=from_game
                                )

    screen translator3000_extra_text_preferences:

        # Настройки "предпочтений" юзера. size, font etc.

        tag translator3000_screen
        style_prefix "translator3000"

        $ _gui = translator3000._gui
        $ quote = translator3000.quote
        $ _t = _gui.translate
        $ text_setting = translator3000._setting["extraTextOptions"]

        use translator3000_sample_text
        use translator3000_base_vbox_in_window:
            label _t("Настройки отображаемого текста.")
            vbox:
                textbutton _t("Курсивный текст."):
                    action (
                        ToggleDict(text_setting, "italic"),
                        _gui.ApplySettingAction()
                    )
                textbutton _t("Жирный текст."):
                    action (
                        ToggleDict(text_setting, "bold"),
                        _gui.ApplySettingAction()
                    )
            vbox:
                label _t("Размер.")
                if text_setting["size"] is None:
                    text _t("Не установлено.")
                else:
                    text "{size}".format(**text_setting):
                        size 30
                vbox:
                    for _mod in "+-":
                        $ _false = unicode(_gui._text_size_without_mod)
                        $ _true = "{0}{1}".format(_mod, _false)
                        textbutton _mod:
                            text_size 30
                            action (
                                ToggleDict(
                                    text_setting,
                                    "size",
                                    true_value=_true,
                                    false_value=_false
                                ),
                                _gui.ApplySettingAction()
                            )
                bar value FieldValue(
                    _gui,
                    "_text_size_without_mod",
                    range=300,
                    step=1
                )
            vbox:
                label _t("Шрифт.")
                if text_setting["font"] is None:
                    text _t("Не установлено.")
                else:
                    $ _fs_object = _gui._fs_object
                    text quote(
                        _fs_object.get_clear_filename(text_setting["font"])
                    ):
                        size 30
                    textbutton _t("Сбросить."):
                        action (
                            SetDict(text_setting, "font", None),
                            _gui.ApplySettingAction()
                        )
                textbutton _t("Выбрать из файлов игры."):
                    action _gui.ForwardAction(
                        "translator3000_set_font",
                        from_game=True
                    )
                textbutton _t("Выбрать из файлов ПК."):
                    action _gui.ForwardAction(
                        "translator3000_set_font",
                        from_game=False
                    )
                textbutton _t("Выбрать из использовавшихся ранее."):
                    action _gui.ForwardAction(
                        "translator3000_set_font",
                        from_game="from_database"
                    )

    screen translator3000_user_preferences:

        # Графическая настройка параметров перевода.

        tag translator3000_screen
        style_prefix "translator3000"

        $ _t = translator3000._gui.translate
        $ quote = translator3000.quote
        $ py_translator = translator3000._translator_object
        $ _setting = translator3000._setting

        $ _action = translator3000._gui.ApplySettingAction()
        use translator3000_base_vbox_in_window(_action):

            label _t("Настройки переводчика.")

            textbutton _t("Настроить параметры отображаемого текста."):
                action translator3000._gui.ForwardAction(
                    "translator3000_extra_text_preferences"
                )

            for _label, _key in (
                ("Исходный язык игры.", "gameLanguage"),
                ("Направление перевода.", "directionOfTranslation")
            ):
                vbox:
                    label _t(_label)
                    if _setting[_key] is None:
                        text _t("Не установлено.")
                    else:
                        text quote(
                            py_translator.get_lang_name(
                                _setting["translationService"],
                                _setting[_key]
                            )
                        ).title()
                    textbutton _t("Сменить."):
                        action translator3000._gui.ForwardAction(
                            "translator3000_set_language",
                            field_name=_key
                        )

            vbox:
                label _t("Булевые параметры.")
                textbutton _t("Предварительное сканирование при запуске."):
                    action (
                        ToggleDict(_setting, "prescan"),
                        translator3000._gui.ApplySettingAction()
                    )
                textbutton _t("Режим отладки."):
                    action (
                        ToggleDict(_setting, "_debug_mode"),
                        translator3000._gui.ApplySettingAction()
                    )
                textbutton _t("Сохранять оригинал в истории."):
                    action (
                        ToggleDict(_setting, "originalInHistory"),
                        translator3000._gui.ApplySettingAction()
                    )

            vbox:
                label _t("Сервис перевода.")
                $ services = py_translator.get_available_translator_services()
                for srv in services:
                    textbutton quote(srv.title()):
                        action (
                            SetDict(_setting, "translationService", srv),
                            translator3000._gui.ApplySettingAction(True)
                        )

            vbox:
                label _t("Частота запросов.")
                if _setting["requestsFrequency"] is None:
                    text _t("Не установлено.")
                else:
                    text _t("{0:.0f} запросов в минуту.").format(
                        float(_setting["requestsFrequency"])
                    )
                bar value FieldValue(
                    translator3000._gui,
                    "requests_frequency_pref",
                    offset=10.,
                    range=500.,
                    step=.01
                )

    screen translator3000_github_update:

        # Информация об обновлениях на GitHub.

        tag translator3000_screen
        style_prefix "translator3000"

        $ _t = translator3000._gui.translate
        $ git = translator3000._github_checker
        $ process = git._download_process

        if process:

            vbox:

                label _t("Модуль обновления переводчика.")

                if process.is_running():
                    # Процесс запущен.
                    text _t("Загружено {0:.2f}Мб из {1:.2f}.").format(
                        process.current_size,
                        process.total_size
                    )
                    text _t("{0:.2f} Мбит/сек.").format(process.speed)
                    bar value StaticValue(process.status)
                elif process.is_over():
                    # Процесс окончен.
                    if process.is_successful():
                        text _t("Загрузка окончена. Перезапустите игру.")
                    else:
                        text _t("Загрузка неудачна.")
                        textbutton _t("Бросить трейсбек."):
                            action Function(process._raise_from_thread)
                    textbutton _t("Скрыть уведомление."):
                        action Function(git._hide_ui)
                else:
                    # Процесс ещё не начинался.
                    text _t("На GitHub доступно обновление переводчика.")
                    text _t("Версия {0}.{1}.{2}.").format(*git.version)
                    text _t("Размер {0:.2f}Мб.").format(
                        process._b_to_mb(git.size)
                    )
                    textbutton _t("Начать загрузку."):
                        action Function(process.start)

    screen translator3000_prescan_status:

        # Информация о предварительном сканировании.

        tag translator3000_screen
        style_prefix "translator3000"

        $ _t = translator3000._gui.translate
        $ pr = translator3000._translate_preparer

        vbox:

            if (pr._switcher or (not pr.is_completed())):
                label _t("Модуль предварительного сканирования.")

            if not pr.is_completed():
                $ txt = _t(("Приостановить" if pr._switcher else "Запустить"))
                textbutton _t("{0} предварительное сканирование.").format(txt):
                    action ToggleField(pr, "_switcher")

            if pr._switcher:

                if pr.has_exception():
                    text _t("Возникла ошибка в потоке сканирования.")
                    textbutton _t("Бросить трейсбек."):
                        action Function(pr._raise_from_thread)

                if pr.is_completed():
                    text _t("Предварительное сканирование закончено.")
                    textbutton _t("Скрыть уведомление."):
                        action SetField(pr, "_switcher", False)
                else:
                    text _t("Переведено {done} строк из {total}.").format(
                        **pr.get_info()
                    )
                    text "{0:.1%}".format(pr.status)
                    bar value StaticValue(pr.status)
