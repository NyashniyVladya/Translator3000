
init 1 python:

    build.executable_name = u"Translator3000"
    build.directory_name = u"{0}-ver.{1}.{2}.{3}".format(
        build.executable_name,
        *_Translator3000.__version__
    )

    build.include_update = False

    _archive_name = build.executable_name.lower()
    build.archive(_archive_name, u"all")
    build.classify(u"**~", None)
    build.classify(u"**.bak", None)
    build.classify(u"**/.**", None)
    build.classify(u"**/#**", None)
    build.classify(u"**/thumbs.db", None)
    build.classify(u"**.rpy", None)
    build.classify(u"game/options.*", None)
    build.classify(u"game/cache/**", None)
    build.classify(u"game/saves/**", None)
    build.classify(u"game/**", _archive_name)

    build.documentation(u"*.html")
    build.documentation(u"*.txt")
