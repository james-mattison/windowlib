import curses


class ColorRegistry:
    registry = None

    def __init__(self, o):
        if self.registry is not None:
            self.registry = o
        else:
            pass

    def allcolors(self):
        for color in self.registry:
            for k, v in color:
                if k == "id":
                    yield curses.color_pair(v)


def initialize_color_pallette():
    curses.start_color()
    colors = [
        {
            "tag": "red",
            "foreground": curses.COLOR_RED,
            "background": curses.COLOR_BLACK,
            "id": 1
        },
        {"tag": "green",
         "foreground": curses.COLOR_GREEN,
         "background": curses.COLOR_BLACK,
         "id": 2
         },
        {
            "tag": "yellow",
            "foreground": curses.COLOR_YELLOW,
            "background": curses.COLOR_BLACK,
            "id": 3
        },
        {
            "tag": "blue",
            "foreground": curses.COLOR_BLUE,
            "background": curses.COLOR_BLACK,
            "id": 4
        },
        {
            "tag": "magenta",
            "foreground": curses.COLOR_MAGENTA,
            "background": curses.COLOR_BLACK,
            "id": 5
        },
        {
            "tag": "cyan",
            "foreground": curses.COLOR_CYAN,
            "background": curses.COLOR_BLACK,
            "id": 6
        },
        {
            "tag": "white",
            "foreground": curses.COLOR_WHITE,
            "background": curses.COLOR_BLACK,
            "id": 7
        },
        {
            "tag": "blackblack",
            "foreground": curses.COLOR_BLACK,
            "background": curses.COLOR_BLACK,
            "id": 8
        },
        {
            "tag": "whitewhite",
            "foreground": curses.COLOR_WHITE,
            "background": curses.COLOR_WHITE,
            "id": 10
        },
        {
            "tag": "bluewhite",
            "foreground": curses.COLOR_BLUE,
            "background": curses.COLOR_WHITE,
            "id": 11
        },
        {
            "tag": "blackwhite",
            "foreground": curses.COLOR_BLACK,
            "background": curses.COLOR_WHITE,
            "id": 12
        },
        {
            "tag": "boldblue",
            "foreground": curses.COLOR_BLUE,
            "background": curses.COLOR_BLACK,
            "id": 20
        },
        {
            "tag": "boldgreen",
            "foreground": curses.COLOR_GREEN,
            "background": curses.COLOR_BLACK,
            "id": 21
        }
    ]
    r = {}
    for color in colors:

        curses.init_pair(int(color["id"]), color["foreground"], color["background"])
        if "bold" in color["tag"]:
            r[color["tag"]] = curses.A_BOLD | curses.color_pair(int(color["id"]))
        else:
            r[color["tag"]] = curses.color_pair(int(color["id"]))
    ColorRegistry(r)
    return r
