
init -100 python:
    renpy.add_python_directory("Translator3000Data/third_party_python_modules")
    renpy.add_python_directory("Translator3000Data/my_python_modules")

label start:
    
    while True:
        menu:
            "Собрать билду.":
                if _translator3000.DEBUG:
                    "Внимание! Билда собирается с включённым режимом дебага."
                $ _build_creator.RPACreator.create_build(build.name)
                "Собрано!"
    return
