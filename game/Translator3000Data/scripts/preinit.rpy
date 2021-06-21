
init -50 python in translator3000_preinit:

    import store

    class SingleTone(store.NoRollback):

        initialized = False
        single_instance = None

        def __new__(cls, *args, **kwargs):
            if cls.single_instance is None:
                cls.single_instance = super(SingleTone, cls).__new__(cls)
            return cls.single_instance

        def __init__(self, *args, **kwargs):
            self.initialized = True

        def __getstate__(self):
            return None

        def __setstate__(self, data):
            self.__init__()


    if renpy.version(True) < (7, 4, 0):
        renpy.config.search_prefixes.append("old_requests_module/")
