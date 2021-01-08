
init -100 python in _translator3000_gui:

    import os
    import hashlib
    import store
    import _translator3000
    from os import path
    from store import (
        persistent
    )

    PHI_CONST = (((5. ** (1. / 2.)) - 1.) / 2.)
    PHI_CONST, PHI_CONST2 = ((1. - PHI_CONST), PHI_CONST)

    window_width, window_height = map(
        lambda x: int((float(x) * PHI_CONST)),
        (store.config.screen_width, store.config.screen_height)
    )

    SingleTone = store.translator3000_preinit.SingleTone
