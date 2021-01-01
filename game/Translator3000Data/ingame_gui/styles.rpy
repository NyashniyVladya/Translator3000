
init -99:

    style translator3000_viewport is default:
        xmaximum _translator3000_gui.window_width
        ymaximum _translator3000_gui.window_height

    style translator3000_window is default:
        xmaximum _translator3000_gui.window_width
        ymaximum _translator3000_gui.window_height
        xpadding 5
        ypadding 5

    style translator3000_bar is bar:
        xmaximum _translator3000_gui.window_width

    style translator3000_vbar is vbar:
        ymaximum _translator3000_gui.window_height

    style translator3000_vbox is default:
        xfill True
        box_layout "vertical"
        first_spacing 15
        spacing 5

    style translator3000_hbox is translator3000_vbox:
        box_layout "horizontal"
        first_spacing None

    style translator3000_text is default:
        size 25
        color "#eee"
        outlines [(2, "#000", 0, 0)]

    style translator3000_input_text is translator3000_text

    style translator3000_label_text is translator3000_text:
        color "#fff"
        size 30

    style translator3000_button_text is translator3000_text:
        color "#ddd"
        hover_color "#888"

    transform translator3000_general_window:
        on appear:
            anchor (.0, .0)
            pos (.01, .01)
        on show:
            linear .1 anchor (.0, .0) pos (.01, .01)
        on hide:
            linear .1 anchor (1., .0) pos ((-.01), .01)
