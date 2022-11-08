import curses


class GeometryManager:
    ylimit = None
    xlimit = None
    inner_x = None
    inner_y = None

    def __init__(self, window_obj, **kwargs):
        self.s = curses.initscr()
        self.window_obj = window_obj
        for k, v in kwargs.items():
            if "ylimit" in kwargs.keys():
                self.ylimit = kwargs["ylimit"]
            if "xlimit" in kwargs.keys():
                self.xlimit = kwargs["xlimit"]
            if "inner_x" in kwargs.keys():
                self.inner_x = kwargs["inner_x"]
            if "inner_y" in kwargs.keys():
                self.inner_x = kwargs["inner_y"]

    def register_bounds(self, **kwargs):
        for item in ["ylimit", "xlimit", "inner_x", "inner_y"]:
            if item in kwargs.keys():
                self.__dict__[item] = kwargs[item]

    def check_x(self, *data):
        o = ""
        for d in data:
            o += str(d)
        y, x = curses.getsyx()
        if len(o) > self.xlimit - x:
            return False
        else:
            return True

    def get_next_y(self, *data):
        s = " ".join([str(d) for d in data])
        baselen = s.count("\n") + 1
        y = curses.getsyx()[0]
        for d in data:
            if len(d) > self.xlimit + self.inner_x:
                for i in range(0, len(d)):
                    if i % self.xlimit - 4 == 0:
                        y += 1
        curses.setsyx(y, self.inner_x)
        curses.doupdate()
        newy = curses.getsyx()[0]
        print("New Y POS: {}".format(newy))
        return newy
