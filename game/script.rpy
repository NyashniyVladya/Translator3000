
init -100 python in _compile_build_init:

    from store import config

    for _path in (
        "Translator3000Data/third_party_python_modules/",
        "Translator3000Data/my_python_modules/"
    ):
        renpy.add_python_directory(_path)
        config.search_prefixes.append(_path)

label start:
    
    while True:
        menu:
            "Собрать билду.":
                if _translator3000.DEBUG:
                    "Внимание! Билда собирается с включённым режимом дебага."
                $ _build_creator.RPACreator.create_build(build.name)
                "Собрано!"
    return
