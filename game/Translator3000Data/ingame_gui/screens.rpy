
init -38:

    screen translator3000_base_vbox_in_window(*_actions):

        # Предполагается, что объект 'translator3000'
        # имеется в глобальном пространстве.

        tag translator3000_screen
        style_prefix "translator3000"

        showif translator3000._gui.show:
            if renpy.context()._menu:
                key "game_menu" action (
                    (_actions + (translator3000._gui.BackAction(),))
                )
            window:
                hbox:
                    box_reverse True
                    textbutton "{{#notTranslate}}{0}".format("[[<=]"):
                        # Закрыть окно.
                        align (1., .0)
                        action (_actions + (translator3000._gui.BackAction(),))
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

        if translator3000._translator_switcher:
            $ state = "Приостановить перевод."
        else:
            $ state = "Возобновить перевод."

        $ patreon_pic_zoom = .05
        $ boosty_pic_zoom = ((1080. / 788.) * patreon_pic_zoom)
        $ discord_pic_zoom = (((1080. - (71. * 2.)) / 470.) * patreon_pic_zoom)

        use translator3000_base_vbox_in_window:
            textbutton "Translator3000. {0}\n{1}".format(
                translator3000._gui.translate("Версия {0}.{1}.{2}."),
                translator3000._gui.translate("Ознакомительная версия."),
            ).format(*_translator3000.VERSION):
                text_style "translator3000_label_text"
                text_hover_color "#888"
                text_selected_outlines [(2, "#000", 0, 0), (1, "#050", 0, 0)]
                action OpenURL("https://www.patreon.com/NyashniyVladya")
            hbox:
                xanchor .0
                xpos .006
                xfill False
                spacing 10

                imagebutton:
                    yalign .5
                    idle Transform("Translator3000OtherFiles/BoostyColor.png", zoom=boosty_pic_zoom)
                    hover Transform("Translator3000OtherFiles/BoostyDark.png", zoom=boosty_pic_zoom)
                    action OpenURL("https://boosty.to/nyashniyvladya")

                imagebutton:
                    yalign .5
                    idle Transform("Translator3000OtherFiles/Digital-Patreon-Logo_FieryCoral.png", zoom=patreon_pic_zoom)
                    hover Transform("Translator3000OtherFiles/Digital-Patreon-Logo_Black.png", zoom=patreon_pic_zoom)
                    action OpenURL("https://www.patreon.com/bePatron?u=62209932")

                imagebutton:
                    yalign .5
                    idle Transform("Translator3000OtherFiles/icon_clyde_blurple_RGB.png", zoom=discord_pic_zoom)
                    hover Transform("Translator3000OtherFiles/icon_clyde_black_RGB.png", zoom=discord_pic_zoom)
                    action OpenURL("https://discord.gg/FqsQXNH6Fg")

            null height 10
            textbutton translator3000._gui.translate("На Patreon и Boosty уже доступна новая версия переводчика."):
                action OpenURL("https://boosty.to/nyashniyvladya")
            null height 10

            textbutton translator3000._gui.translate(state):
                action ToggleField(
                    translator3000,
                    "_translator_switcher"
                )
            textbutton translator3000._gui.translate("Сделать бэкап БД."):
                action Function(translator3000.backup_database)

            textbutton translator3000._gui.translate("Очистить кэш переводов игры."):
                action translator3000._gui.ConfirmAction("Кэш переводов для игры будет очищен.", Function(translator3000.clear_local_cache))

            textbutton translator3000._gui.translate("Очистить весь кэш переводов."):
                action translator3000._gui.ConfirmAction("Кэш переводов будет очищен.", Function(translator3000.clear_cache))

            textbutton translator3000._gui.translate("Поменять язык интерфейса."):
                action translator3000._gui.ForwardAction("translator3000_gui_language")

            textbutton translator3000._gui.translate("Настройки переводчика."):
                action translator3000._gui.ForwardAction("translator3000_user_preferences")

            null height 10
            textbutton translator3000._gui.translate("Поддержать разработчика через Boosty."):
                action OpenURL("https://boosty.to/nyashniyvladya")
            textbutton translator3000._gui.translate("Поддержать разработчика через Patreon."):
                action OpenURL("https://www.patreon.com/bePatron?u=62209932")
            textbutton translator3000._gui.translate("Присоединиться к Discord сообществу."):
                action OpenURL("https://discord.gg/FqsQXNH6Fg")
            null height 10

            use translator3000_github_update
            null height 10
            use translator3000_prescan_status

    screen translator3000_confirm_screen(message, yes_action):

        tag translator3000_screen
        style_prefix "translator3000"

        use translator3000_base_vbox_in_window:
            label translator3000._gui.translate(message)
            textbutton translator3000._gui.translate("Да."):
                action (yes_action, translator3000._gui.BackAction())
            textbutton translator3000._gui.translate("Нет."):
                action translator3000._gui.BackAction()

    screen translator3000_gui_language:

        # Язык интерфейса.

        tag translator3000_screen
        style_prefix "translator3000"

        use translator3000_base_vbox_in_window:
            label translator3000._gui.translate("Язык интерфейса (не перевода).")
            for t in sorted(translator3000._gui.available_languages):
                textbutton "{{#notTranslate}}{0}".format(translator3000.quote(t).title()):
                    action SetField(translator3000._gui, "gui_language", t)

    screen translator3000_set_language(field_name):

        # Язык перевода (или игры).

        tag translator3000_screen
        style_prefix "translator3000"

        use translator3000_base_vbox_in_window:
            label translator3000._gui.translate("Выбор языка.")
            for code in sorted(
                translator3000.get_all_lang_codes(),
                key=lambda _c: translator3000._translator_object.get_lang_name(translator3000._setting["translationService"], _c)
            ):
                textbutton "{{#notTranslate}}{0}".format(
                    translator3000.quote(
                        translator3000._translator_object.get_lang_name(translator3000._setting["translationService"], code)
                    ).title()
                ):
                    action (
                        SetDict(translator3000._setting, field_name, code),
                        translator3000._gui.ApplySettingAction(True)
                    )

    screen translator3000_sample_text:

        #  Пример текста, с использованием панграм.

        tag translator3000_screen
        style_prefix "say"

        input:
            style "translator3000_input_text"
            align (.5, .5)
            value FieldInputValue(translator3000._gui, "_sample_text")

        window:
            yalign 1.
            text "{{#notTranslate}}{0}".format(
                translator3000._apply_enabled_text_tags(
                    translator3000.quote(translator3000._gui._sample_text)
                )
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

        default current_dir = ("" if from_game else translator3000._gui._fs_object.desktop)

        use translator3000_sample_text
        use translator3000_base_vbox_in_window:

            label translator3000._gui.translate("Настройки шрифта.")

            if translator3000._setting["extraTextOptions"]["font"] is not None:
                text "{{#notTranslate}}{0}".format(
                    translator3000.quote(translator3000._gui._fs_object.get_clear_filename(translator3000._setting["extraTextOptions"]["font"]))
                ):
                    size 30

            if from_game == "from_database":

                for fnt in reversed(
                    tuple(translator3000._multi_persistent.fonts.iterkeys())
                ):
                    textbutton "{{#notTranslate}}{0}".format(translator3000.quote(translator3000._gui._fs_object.get_clear_filename(fnt))):
                        action Function(
                            translator3000._gui._set_font_pref,
                            fnt,
                            from_renpy="from_database"
                        )

            else:

                if current_dir:
                    text "{{#notTranslate}}{0}".format(current_dir)
                    textbutton translator3000._gui.translate("Перейти в предыдущую директорию."):
                        action SetScreenVariable(
                            "current_dir",
                            translator3000._gui._fs_object.dirname(current_dir, from_game)
                        )

                null height 30
                vbox:
                    $ data_in_dir = translator3000._gui._fs_object.listdir(current_dir, from_game)
                    for _directory in data_in_dir["dirs"]:
                        $ full_path = translator3000._gui._fs_object.join(
                            current_dir,
                            _directory,
                            from_renpy=from_game
                        )
                        textbutton translator3000._gui.translate("Перейти в \"{0}\".").format(
                            translator3000.quote(_directory)
                        ):
                            action SetScreenVariable("current_dir", full_path)
                    null height 10
                    for _filename in data_in_dir["files"]:
                        $ full_path = translator3000._gui._fs_object.join(
                            current_dir,
                            _filename,
                            from_renpy=from_game
                        )
                        $ ext = _translator3000_gui.path.splitext(full_path)[1]
                        if ext.lower() in translator3000._gui._fs_object.available_font_exts:
                            textbutton "{{#notTranslate}}{0}".format(
                                translator3000.quote(
                                    translator3000._gui._fs_object.get_clear_filename(_filename)
                                )
                            ):
                                action Function(
                                    translator3000._gui._set_font_pref,
                                    full_path,
                                    from_renpy=from_game
                                )

    screen translator3000_extra_text_preferences:

        # Настройки "предпочтений" юзера. size, font etc.

        tag translator3000_screen
        style_prefix "translator3000"

        use translator3000_sample_text
        use translator3000_base_vbox_in_window:
            label translator3000._gui.translate("Настройки отображаемого текста.")
            vbox:
                textbutton translator3000._gui.translate("Курсивный текст."):
                    action (
                        ToggleDict(translator3000._setting["extraTextOptions"], "italic"),
                        translator3000._gui.ApplySettingAction()
                    )
                textbutton translator3000._gui.translate("Жирный текст."):
                    action (
                        ToggleDict(translator3000._setting["extraTextOptions"], "bold"),
                        translator3000._gui.ApplySettingAction()
                    )
            vbox:
                label translator3000._gui.translate("Размер.")
                if translator3000._setting["extraTextOptions"]["size"] is None:
                    text translator3000._gui.translate("Не установлено.")
                else:
                    text "{{#notTranslate}}{size}".format(**translator3000._setting["extraTextOptions"]):
                        size 30
                vbox:
                    for _mod in "+-":
                        $ _false = unicode(translator3000._gui._text_size_without_mod)
                        $ _true = "{0}{1}".format(_mod, _false)
                        textbutton "{{#notTranslate}}{0}".format(_mod):
                            text_size 30
                            action (
                                ToggleDict(
                                    translator3000._setting["extraTextOptions"],
                                    "size",
                                    true_value=_true,
                                    false_value=_false
                                ),
                                translator3000._gui.ApplySettingAction()
                            )
                bar value FieldValue(
                    translator3000._gui,
                    "_text_size_without_mod",
                    range=300,
                    step=1
                )
            vbox:
                label translator3000._gui.translate("Шрифт.")
                if translator3000._setting["extraTextOptions"]["font"] is None:
                    text translator3000._gui.translate("Не установлено.")
                else:
                    text "{{#notTranslate}}{0}".format(
                        translator3000.quote(translator3000._gui._fs_object.get_clear_filename(translator3000._setting["extraTextOptions"]["font"]))
                    ):
                        size 30
                    textbutton translator3000._gui.translate("Сбросить."):
                        action (
                            SetDict(translator3000._setting["extraTextOptions"], "font", None),
                            translator3000._gui.ApplySettingAction()
                        )
                textbutton translator3000._gui.translate("Выбрать из файлов игры."):
                    action translator3000._gui.ForwardAction(
                        "translator3000_set_font",
                        from_game=True
                    )
                textbutton translator3000._gui.translate("Выбрать из файлов ПК."):
                    action translator3000._gui.ForwardAction(
                        "translator3000_set_font",
                        from_game=False
                    )
                textbutton translator3000._gui.translate("Выбрать из использовавшихся ранее."):
                    action translator3000._gui.ForwardAction(
                        "translator3000_set_font",
                        from_game="from_database"
                    )

    screen translator3000_user_preferences:

        # Графическая настройка параметров перевода.

        tag translator3000_screen
        style_prefix "translator3000"

        use translator3000_base_vbox_in_window(translator3000._gui.ApplySettingAction()):

            label translator3000._gui.translate("Настройки переводчика.")

            textbutton translator3000._gui.translate("Настроить параметры отображаемого текста."):
                action translator3000._gui.ForwardAction(
                    "translator3000_extra_text_preferences"
                )

            for _label, _key in (
                ("Исходный язык игры.", "gameLanguage"),
                ("Направление перевода.", "directionOfTranslation")
            ):
                vbox:
                    label translator3000._gui.translate(_label)
                    if translator3000._setting[_key] is None:
                        text translator3000._gui.translate("Не установлено.")
                    else:
                        text "{{#notTranslate}}{0}".format(
                            translator3000.quote(
                                translator3000._translator_object.get_lang_name(
                                    translator3000._setting["translationService"],
                                    translator3000._setting[_key]
                                )
                            ).title()
                        )
                    textbutton translator3000._gui.translate("Сменить."):
                        action translator3000._gui.ForwardAction(
                            "translator3000_set_language",
                            field_name=_key
                        )

            vbox:
                label translator3000._gui.translate("Булевые параметры.")
                textbutton translator3000._gui.translate("Предварительное сканирование при запуске."):
                    action (
                        ToggleDict(translator3000._setting, "prescan"),
                        translator3000._gui.ApplySettingAction()
                    )
                textbutton translator3000._gui.translate("Режим отладки."):
                    action (
                        ToggleDict(translator3000._setting, "_debug_mode"),
                        translator3000._gui.ApplySettingAction()
                    )
                textbutton translator3000._gui.translate("Сохранять оригинал в истории."):
                    action (
                        ToggleDict(translator3000._setting, "originalInHistory"),
                        translator3000._gui.ApplySettingAction()
                    )

            vbox:
                label translator3000._gui.translate("Сервис перевода.")
                $ services = translator3000._translator_object.get_available_translator_services()
                for srv in services:
                    textbutton "{{#notTranslate}}{0}".format(translator3000.quote(srv.title())):
                        action (
                            SetDict(translator3000._setting, "translationService", srv),
                            translator3000._gui.ApplySettingAction(True)
                        )

            vbox:
                label translator3000._gui.translate("Способ работы переводчика.")

                textbutton translator3000._gui.translate("Перевод диалогов и меню."):
                    action (
                        SetDict(translator3000._setting, "workMethod", "dialogueOnly"),
                        translator3000._gui.ApplySettingAction(update_work_method=True)
                    )

                textbutton translator3000._gui.translate("Перевод всего текста в игре (Бета)."):
                    action (
                        SelectedIf((translator3000._setting["workMethod"] == "allText")),
                        translator3000._gui.ConfirmAction(
                            "При первом включении этого режима игра может \"зависнуть\" на продолжительное время, т.к. необходимо перевести все элементы окружения. Продолжить?",
                            (
                                SetDict(translator3000._setting, "workMethod", "allText"),
                                translator3000._gui.ApplySettingAction(update_work_method=True)
                            )
                        )
                    )
            vbox:
                label translator3000._gui.translate("Частота запросов.")
                if translator3000._translator_object._get_translator(translator3000._setting["translationService"]).FORCE_RPM is not None:
                    text translator3000._gui.translate("Для этого сервиса перевода частота фиксированная.")
                else:
                    if translator3000._setting["requestsFrequency"] is None:
                        text translator3000._gui.translate("Не установлено.")
                    else:
                        text translator3000._gui.translate("{0:.0f} запросов в минуту.").format(
                            float(translator3000._setting["requestsFrequency"])
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

        if translator3000._github_checker._download_process:

            vbox:

                label translator3000._gui.translate("Модуль обновления переводчика.")

                if translator3000._github_checker._download_process.is_running():
                    # Процесс запущен.
                    text translator3000._gui.translate("Загружено {0:.2f}Мб из {1:.2f}.").format(
                        translator3000._github_checker._download_process.current_size,
                        translator3000._github_checker._download_process.total_size
                    )
                    text translator3000._gui.translate("{0:.2f} Мбит/сек.").format(translator3000._github_checker._download_process.speed)
                    bar value StaticValue(translator3000._github_checker._download_process.status)
                elif translator3000._github_checker._download_process.is_over():
                    # Процесс окончен.
                    if translator3000._github_checker._download_process.is_successful():
                        text translator3000._gui.translate("Загрузка окончена. Файл сохранён рядом с папкой \"game\". Переместите его в папку \"game\", заменив старый.")
                    else:
                        text translator3000._gui.translate("Загрузка неудачна.")
                        textbutton translator3000._gui.translate("Бросить трейсбек."):
                            action Function(translator3000._github_checker._download_process._raise_from_thread)
                    textbutton translator3000._gui.translate("Скрыть уведомление."):
                        action Function(translator3000._github_checker._hide_ui)
                else:
                    # Процесс ещё не начинался.
                    text translator3000._gui.translate("На GitHub доступно обновление переводчика.")
                    text translator3000._gui.translate("Версия {0}.{1}.{2}.").format(*translator3000._github_checker.version)
                    text translator3000._gui.translate("Размер {0:.2f}Мб.").format(
                        translator3000._github_checker._download_process._b_to_mb(translator3000._github_checker.size)
                    )
                    textbutton translator3000._gui.translate("Начать загрузку."):
                        action Function(translator3000._github_checker._download_process.start)

    screen translator3000_prescan_status:

        # Информация о предварительном сканировании.

        tag translator3000_screen
        style_prefix "translator3000"

        vbox:

            if (translator3000._translate_preparer._switcher or (not translator3000._translate_preparer.is_completed())):
                label translator3000._gui.translate("Модуль предварительного сканирования.")

            if not translator3000._translate_preparer.is_completed():
                $ txt = translator3000._gui.translate(("Приостановить" if translator3000._translate_preparer._switcher else "Запустить"))
                textbutton translator3000._gui.translate("{0} предварительное сканирование.").format(txt):
                    action ToggleField(translator3000._translate_preparer, "_switcher")

            if translator3000._translate_preparer._switcher:

                if translator3000._translate_preparer.has_exception():
                    text translator3000._gui.translate("Возникла ошибка в потоке сканирования.")
                    textbutton translator3000._gui.translate("Бросить трейсбек."):
                        action Function(translator3000._translate_preparer._raise_from_thread)

                if translator3000._translate_preparer.is_completed():
                    text translator3000._gui.translate("Предварительное сканирование закончено.")
                    textbutton translator3000._gui.translate("Скрыть уведомление."):
                        action SetField(translator3000._translate_preparer, "_switcher", False)
                else:
                    text translator3000._gui.translate("Переведено {done} строк из {total}.").format(
                        **translator3000._translate_preparer.get_info()
                    )
                    text "{{#notTranslate}}{0}".format("{0:.1%}".format(translator3000._translate_preparer.status))
                    bar value StaticValue(translator3000._translate_preparer.status)
