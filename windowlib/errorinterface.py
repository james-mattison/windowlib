import logging
import os


class CCTLogger:

    def __init__(self, handler_name, output_filename="window.log"):
        self.fn = output_filename
        if not os.path.exists(output_filename):
            print("Warn: starting new logfile in {}".format(output_filename))
        self.handler_name = handler_name
        self.logger = logging.getLogger(handler_name)
        self.logger.setLevel(logging.DEBUG)
        self.formatting = logging.Formatter("%(asctime)s [%(name)s][%(levelname)s]: %(message)s", "%m-%y-%Y (%H:%M:%S)")
        self.create_file_handler()

    def create_file_handler(self):
        fh = logging.FileHandler(self.fn, "a")
        fh.setLevel(logging.DEBUG)
        fmt = logging.Formatter("%(asctime)s [%(name)s][%(levelname)s]: %(message)s", "%m-%y-%Y (%H:%M:%S)")
        fh.setFormatter(fmt)
        self.logger.addHandler(fh)

    def set_output(self, onoroff):
        self.force_stdout = onoroff

    def log(self, data, level="debug"):
        levels = {"debug": 10, "info": 20, "warning": 30, "error": 40, "critical": 50}
        if level in levels:
            self.logger.log(levels[level], data)

    def fatal(self, obs):
        self.logger.exception(obs, exc_info=True)


class SysLogger(CCTLogger):
    obs = []

    def __init__(self, script_interface_name, logfile="window.log"):
        super().__init__(script_interface_name, logfile)


class _WindowException(BaseException):
    pass


class GeometryError(_WindowException):

    def __init__(self, m, axis=None):
        self.m = "\nWindow Exception: Geometry management failure: \nThis means the screen size is too small," \
                 "or an object greater than the amount of remaining space was drawn without recompiling the window.\n" \
                 "Message: {}    {}".format(m, "Axis: {}".format(axis) if axis else "")

    def __str__(self):
        return self.m
