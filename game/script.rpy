
label start:

    while True:
        menu:
            "Собрать билду":
                if _translator3000.DEBUG:
                    "Внимание! Билда собирается с включённым режимом дебага."
                $ _translator3000build._RPA.create_build(build.name)
                "Собрано."
    return
