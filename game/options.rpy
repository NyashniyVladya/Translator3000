
init python:

    build.directory_name = "Translator3000-1.2.0"
    build.executable_name = "Translator3000"

    build.include_update = False

    build.archive(u"translator3000", u"all")
    build.classify('**~', None)
    build.classify('**.bak', None)
    build.classify('**/.**', None)
    build.classify('**/#**', None)
    build.classify('**/thumbs.db', None)
    build.classify(u"game/options.*", None)
    build.classify(u"game/cache/**", None)
    build.classify(u"game/saves/**", None)
    build.classify(u"game/**", u"translator3000")

    build.documentation('*.html')
    build.documentation('*.txt')
