import atexit
import locale
import os
from typing import List, Tuple

from .colors import *
from .errorinterface import SysLogger

""" If you don't set the encoding, you end up with @@@@ instead of nice border lines."""
locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()

""" Start the syslogger """
logger = SysLogger("window_controller", "window.log")

def log(*args, **kwargs):
    logger.log(*args, **kwargs)

log("\n\n\nInitialized for {}.".format(__name__))

void = None

# If this throws an uncaught error before atexit gets called and the terminal looks funny, use this to reset it
# If you are using this in the python console, you _must_ use this after you first instantiate the window.
#           r = windowlib.__reset
# if running this interactively is a good idea.
__reset = lambda: os.system("reset")
# To reset the TTY back to normal.


def annihilate():
    """ Ensure that the TTY is returned to normal when exiting! """
    import os
    curses.endwin()
    os.system("reset")
    print("Destroyed.")


atexit.register(annihilate)


class _DefaultWindow(object):
    """
    Window base class
    screen: The curses stdscr
    window: curses window object
    window_height, window_width: total size if the window measured outside of its borders.
    xoffset: position, starting from 0 on the x axis, at which the left border is drawn
    yoffset: position, from the top, at which the top border line starts, in characters.
    inner_y_offset, inner_x_offset:
        The position, counting from INSIDE the borders of the window, at which the
        first character is rendered. This is is the starting x,y for all objects in the window
    bordered: Draw a border or not? (Geometry is still handled the same)
    This is the container class, that handles text output (cprint), geometry, and input that is not done with
    ButtonGroups or Forms (getch, getstr).

    """
    screen = None  # type: type or None
    window = None  # type: type or None
    window_height: int = None
    window_width: int = None
    xoffset: int = 0
    yoffset: int = 0
    inner_x_offset: int = 4  # indented 4 from far side; get past the border.
    inner_y_offset: int = 1  # one from the top, inside the border
    window_bordered: bool = True
    colors: dict = None
    booted: bool = False
    buttons = []  # type: List[type]
    inputs = []  # type: List[dict]

    def __new__(cls, **kwargs):
        """ Create as a singleton, register it by its ID so we can track it."""
        if not hasattr(cls, 'instance'):
            cls.instance = object.__new__(cls)
        log("Instantiate Window, ID: {}".format(id(cls.instance)))
        return cls.instance

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if k in self.__dict__.keys():
                setattr(self, k, v)
        if "noboot" in kwargs.keys():
            if kwargs["noboot"] is True:
                pass
        else:
            if not self.booted:
                self.boot()

    @classmethod
    def boot(cls):
        """ Initializer. Starts the standard screen, calculates the size to use when drawing the window,
        turns off the cursor blink, starts the color mappings (used for style=), draws a border, and then
        refreshes the streen. """
        cls.screen = curses.initscr()
        if not cls.window_height:
            cls.window_height = cls.screen.getmaxyx()[0]
        if not cls.window_width:
            cls.window_width = cls.screen.getmaxyx()[1]
        cls.window = curses.newwin(cls.window_height, cls.window_width, cls.yoffset, cls.xoffset)
        log("Starting window: H: {}  W: {} startY: {}  startX: {}".format(cls.window_height, cls.window_width,
                                                                          cls.yoffset, cls.xoffset)
            )

        curses.noecho()
        curses.curs_set(0)
        log("Initializing colors.")
        curses.start_color()
        cls.colors = initialize_color_pallette()
        log("Color started: {} pairs. Flushing buffer.".format(len(cls.colors.keys())))
        cls.screen.refresh()
        cls.window.border(0)
        cls.window.refresh()
        log("--> Initialized.")

    def decompile(self) -> void:
        """ Destroy the window entirely. This, combined with atexit above, ensures that curses is entirely
        deinitialized and no artifacts are left in the users' terminals."""
        self.window.clear()
        curses.endwin()

        print("Exit OK")

    @classmethod
    def recompile_window(cls, **kwargs) -> void:
        """ Erase all objects on the menu, and entirely re-draw it, setting the cursor back at the position
        at which it was when the window was first drawn. Refresh both the screen and the window."""
        if kwargs:
            for option in ["screen", "window", "xoffset", "yoffset", "window_width", "window_height"]:
                if option in kwargs.keys():
                    setattr(cls, option, kwargs[option])
        cls.window.erase()
        cls.window.redrawwin()
        cls.window.addstr(cls.inner_y_offset, cls.inner_x_offset, "")
        cls.screen.refresh()
        cls.window.refresh()

    def reload(self) -> void:
        """ Re-draw the window. Does not delete things that are currently on the window. """
        self.window.border(0)
        self.window.refresh()
        self.window.border(0)

    def find_curs(self) -> Tuple[int, int]:
        """ Retrieve the y, x position of the cursor, as a tuple."""
        h, w = curses.getsyx()
        return h, w

    def get_max_sz(self) -> Tuple[int, int]:
        """ Retrivew the maximum size that the screen is capable of."""
        h, w = self.screen.getmaxyx()
        return h, w

    def set_pos(self, y: int, x: int) -> void:
        """ Set the position at which the next character/item will be drawn. """
        self.window.addstr(y, x, "")
        self.reload()

    def set_cursor_pos(self, y, x) -> void:
        """
        Set the position at which the cursor is rendered. Only use this if attempting to draw, or otherwise
        alter the selectors in the window. To set the actual position for the next output, use set_pos!!
        """
        curses.setsyx(y, x)
        curses.doupdate()


    @classmethod
    def checkyx(cls, h=None, w=None, xmargin=4, ymargin=1) -> bool or void:
        """
        Perform a rudimentary check if we have enough room to draw an object or output a string.
        TODO: Add check for \n, \r, \b
        """
        cury, curx = curses.getsyx()
        if h is not None and w is None:
            if cury + int(h) + int(ymargin) >= int(cls.window_height):
                return False
            else:
                return True
        if w is not None and h is None:
            if curx + int(w) + int(xmargin) >= int(cls.window_width):
                return False
            else:
                return True
        if w is not None and h is not None:
            if (curx + int(w) + int(xmargin) >= int(cls.window_width)) or (
                    int(cury) + int(h) + int(ymargin) >= int(cls.window_height)):
                return False
            else:
                return True
        else:
            return

    def cprint(self,
               data,  # type: str
               end="\n",  # type: str
               offset=None,  # type: int
               style=None,  # type: str
               delim=" ",  # type str
               window=None,  # type: DefaultWindow.window
               ) -> void:
        """
        Emulate an enhanced version of print().
        offset: Number of characters from the current on the x axis to being the string.
        style: colors [from the color pairs in colors.py ]
        delim: String, which, times the offset, forms the indentation character.
        window: Window object to write into, if not DefaultWindow
        """
        if not window:
            window = self.window
        if offset is None:
            offset = self.inner_x_offset
            xo = delim * offset
        elif offset >= 0:
            xo = delim * offset
        elif offset < 0:
            curses.setsyx(self.find_curs()[0], self.find_curs()[1] - offset)
            xo = "\b \b"
        else:
            xo = ""
        if style in self.colors.keys():
            window.addstr(xo + data + end, self.colors[style])
        else:
            window.addstr(xo + data + end)
        window.refresh()
        # window.addstr(end)
        self.reload()

    def getstr(self,
               prompt=None,  # type: str
               ):
        """ Retrieve a full string from the user, until \n """
        if not prompt:
            self.window.addstr(*self.find_curs(), "")
            self.reload()
        else:
            self.window.addstr(*self.find_curs(), prompt)
        ## Wait 0.2 seconds (allow time for the window to redraw, and avoid having the user skip the next
        ## input because of a double tap.

        curses.napms(200)
        return self.window.getstr().decode()

    def getch(self,
              prompt=None,  # type: str
              raw=False  # type: bool
              ) -> str:
        """ Return a single character that is entered by the user.
        In default mode, returns a unicode string
        raw: Return the ASCII chr as an integer (ie, for KEY UP / KEY DOWN)
        """
        if not prompt:
            self.window.addstr("")
        else:
            self.window.addstr(prompt)
        self.reload()

        if raw:
            k = self.window.getch()
        else:
            k = self.window.getkey()
        self.reload()
        return k

    @classmethod
    def _rebuffer_input(cls,
                        masked=False,  # type: bool
                        style=None,  # type: str
                        window=None,  # type: DefaultWindow.window
                        starty=None,  # type: int
                        startx=None,  # type: int
                        ) -> str:
        """
        Emulate input(), but using single-entered characters, except they can have foreground and background
        colors, or stylings.
        masked: output * instead of the character, ie PASSWORD: *******
        window: window object, if not DefaultWindow, to write to.
        starty, startx: pos to at which the first character will be drawn
        """
        if not window:
            window = cls.window
        curses.noecho()
        curses.cbreak()
        if startx is not None and starty is not None:
            window.addstr(startx, starty, "")
        s = ""
        while True:
            k = window.getch()
            s += chr(k)
            if k == 13 or k == 10:
                break
            if k == 8 or k == 127:
                window.addstr("\b \b", cls.colors[style])
                s = s[:-2]
                window.refresh()
                continue
            else:
                window.addstr(chr(k) if not masked else "*", cls.colors[style])
                window.refresh()

        curses.echo()
        curses.nocbreak()
        window.refresh()
        cls.window.refresh()
        cls.screen.refresh()

        return s.strip("\n")


class Button:
    """
    Create a button, the base non-stdout widget that this module uses.
    Normally, produces a simple rectangular button, then goes to the next line, as in the Menu classes below.
    as_input: draw the button, and recieve input, like an HTML input box - used for the Form classes below
    reset_xpos: MUST be specified if you do not want to scroll the output down past the button.

    Default:                        reset_xpos (width as_input called in the second button)

    +--------------+          +--------------+           +--------------+
    | Howdy!       |          | Username:    |           |              |
    +--------------+          +--------------+           +--------------+
    +--------------+
    | Bye now!     |
    +--------------+


    """

    member = None  # type: dict or None
    button = None  # type: type or None
    buffer: list = []

    def __init__(self,
                 text,  # type: str
                 xpos=None,  # type: int
                 ypos=None,  # type: int
                 style=None,  # type: str
                 indent=1,  # type: int
                 height=3,  # type: int
                 width=20,  # type: int
                 centered=False,  # type: bool,
                 draw_immediately=True,  # type: bool
                 window=None,  # type: DefaultWindow
                 reset_xpos=True,  # type: bool
                 as_input=False  # type: bool
                 ):

        """
        Window:
            xpos, ypos: position on window to start drawing the box
        Subwindow (inside button):
            Style can either be any of the color pairs in colors or 'ok', 'good', 'fail', etc
            indent = number of spaces of padding inside the box before the beginning of the string, as int
            height: height of a button. Minimum is 3 (border,text,border)
            width: width of button
            centered: center text inside button?
            window: if not playing the button in the main window, then where
            draw_immediately: flush buffer?
        """

        window_ob = DefaultWindow
        # if we dont get window as arg, and DefaultWindow has not been fully initialized, then initialize
        # the window or we have no way to interact with the screen, producing a silent fail.
        if not window:
            if window_ob.window is None:
                window_ob = DefaultWindow().boot()
                window = window_ob.window
            else:
                window = DefaultWindow.window

        if xpos is None: xpos = curses.getsyx()[1] + DefaultWindow.inner_x_offset
        if ypos is None: ypos = curses.getsyx()[0] + DefaultWindow.inner_y_offset
        if DefaultWindow.checkyx(height, width) is False:
            window.addstr("Next page --> ")
            window.getch()
            window.erase()
            ypos = DefaultWindow.inner_y_offset
            xpos = DefaultWindow.inner_x_offset
            window.refresh()

        if style is None: style = "white"
        button = window.subwin(height, width, ypos, xpos)
        button.box()
        button.immedok(True)
        if centered:
            indent = ((width) - len(text)) / 2
        s = " " * int(indent)
        if as_input is False:
            button.addstr(1, 1, "{}{}".format(s, text), DefaultWindow.colors[style])
        else:
            button.addstr(1, 1, s)

            resp = window_ob._rebuffer_input(False, style, button, )
            self.pulse(resp)

        button.box()
        if reset_xpos:
            window.addstr(ypos + height - 1, DefaultWindow.xoffset, "")
        else:
            window.addstr(ypos - 1, xpos + width + 2, "")
        if draw_immediately:
            button.refresh()
        window.refresh()
        self.member = {
            "memid": id(self.button),
            "button": button,
            "xpos": xpos,
            "ypos": ypos,
            "style": style,
            "indent": indent,
            "height": height,
            "width": width,
            "centered": centered,
            "window": window
        }
        self.button = self.member["button"]

    def pulse(self, data=None):
        if data is not None:
            if len(self.buffer) == 0:
                self.buffer.append(data)
        else:
            return self.buffer

    def __getitem__(self, item):
        """ Return a property. """
        if item in self.member.keys():
            return self.member[item]


class _ButtonGroup:
    """
    Create a menu, using buttons stacked on top of each other

    Quit Program?
    +-------+
    |  YES  |
    +-------+

    +-------+
    >  NO   |
    +-------+



    """
    colors = None
    window = None
    screen = None
    buttons = []
    members = []

    def __init__(self):
        self.master = DefaultWindow()
        self.colors = DefaultWindow.colors
        self.screen = DefaultWindow.screen
        self.window = DefaultWindow.window

    def run_menu(self,
                 pt=">"  # type: str
                 ) -> int:
        """
        Run a menu, using the buttons registered to the class with register_button below.
        Returns an integer representing the index for the buttons in the menu; eg, if
        Yes is selected above, return 0, if No, return 1
        pointer: the character(s) to be drawn as the indication that we are "hovering" over the button the user wants.
        """
        # index, ie, from top of menu, where are we.
        index = 0
        curses.cbreak()
        curses.noecho()
        DefaultWindow.screen.keypad(True)
        for button in self.buttons:
            button.box()
            button.refresh()
        log("entering menuloop")
        while True:
            # get the raw key, in a numerical ascii value
            keypress = self.window.getch()
            if keypress == 65:
                ## 65: UP ARROW: go up the menu, decreasing the index
                self.buttons[index].addstr(1, 0, " ")
                self.buttons[index].box()
                if index >= 1:
                    index -= 1
                self.buttons[index].addstr(1, 0, str(pt), self.colors["blue"])
            elif keypress == 66:
                ## 66: DOWN_ARROW: go down the menu, increasing the index
                self.buttons[index].addstr(1, 0, " ")
                self.buttons[index].box()
                if index <= len(self.buttons) - 2:
                    index += 1
                self.buttons[index].addstr(1, 0, str(pt), self.colors["blue"])

            elif keypress == 13 or keypress == 10:
                ## 13/10: \r\n and \n, ie KEY_ENTER
                log("got KEYENTER, with index {}".format(index))
                self.window.refresh()
                self.screen.keypad(False)
                break
            # Refresh after each iteration
            self.window.refresh()
            self.screen.refresh()
        # Restore echo
        curses.echo()

        # Turn off cbreak mode: return to normal bufferedmode.
        curses.nocbreak()

        self.window.addstr("Got {}".format(index))
        self.window.refresh()
        return index

    @classmethod
    def register_button(cls, *args, **kwargs) -> void:
        # Register a button object, to be used as an option in the menu.
        btn = Button(*args, **kwargs)
        cls.buttons.append(btn.button)
        cls.members.append(btn.member)

    @classmethod
    def clear(cls) -> void:
        """ By default, if you run two menus one after the other, you will get MENU1; MENU1+MENU2 - the registry of
        Button objects is not cleared automatically after the menu is run.
        """
        cls.buttons = []

    def pop(self, index) -> Button:
        """ Pop a button from buttons[] """
        return self.buttons[index]

    def prune(self, index) -> void:
        _ = self.buttons.pop(index)

    def select(self, index) -> Button:
        # retrieve a button
        return self.buttons[index]

    def get_member(self,
                   index_or_name  # type: str or int
                   ) -> Button:
        """
        Rather than getting the button object, get the metadata with which the button was instantiated
        as a dict of the object.

        Useful for logging, or to serialize the object with JSON, etc, for templating use.
        Does not pop.
        """

    @classmethod
    def clear_members(cls) -> void:
        """ Wipe out the array of members, ie the button metadata info """
        cls.members = []

class _InputGroup(_ButtonGroup):
    """
    Use for creation of a form, or a username and password box - etc

    +----------------+   +----------------------------+
    | <QUESTION>     |   | <ANSWER>                   |
    +--------------- +   +----------------------------+

    Can be combined with a Menu, to create an input, then a response selected with the keyboard.

    The whole menu is run out of run_menu because I am lazy.
    args: the labels used as the left-hand side ("questions")
    title: produce a title box
    labelsz: Manually set the left-hand size. Default 20 chars
    inputsz: Manually set the right hand input box size: Default 40 chars

    """
    input_group = []
    responses = []
    buttons = []
    _questions = []

    def run_form(self, *questions, title=None, labelsz=None, inputsz=None):
        if not labelsz:
            labelsz = 20
        if not inputsz:
            inputsz = 40
        cmp = labelsz + inputsz + 6
        if title is not None:
            title = Button(str(title), width=cmp, centered=True, style="yellow")
        for i, question in enumerate(questions):
            self._questions.append(question)
            left = self.register_button(str(question), reset_xpos=False, width=labelsz, style="boldblue")
            right = Button("", as_input=True, width=inputsz, style="green")
            self.responses.append(right.pulse().pop())
        return self.responses

    def answers(self):
        return [ans for ans in self.responses]

    def questions(self):
        return self.questions

    @classmethod
    def clear(cls):
        cls._questions = []
        cls.responses = []


class _JSONTemplatedForm(_InputGroup):
    """
     Create a form from a JSON file template, ie { 'questions': [ 'What is your name'], 'answers': [],
     and optionally re-write the responses back to the same or another JSON file.
    """

    def __init__(self,
                 filename  # type: str
                 ):
        super().__init__()
        self._questions = self._check(filename)
        self._title = None

    def _check(self, filename):
        import json
        with open(filename, "r") as tf_fb:
            pre_temp = json.load(tf_fb)
        if "questions" in pre_temp.keys():
            src = pre_temp["questions"]
        elif "labels" in pre_temp.keys():
            src = pre_temp["labels"]
        else:
            raise Exception("\nTemplate error: need either questions or labels as in global keys.")
        if "title" in pre_temp.keys():
            self._title = src["title"]
        return src

    def run_form(self, *args, **kwargs):
        seq = [x for x in self._questions]
        return super().run_form(*seq, **kwargs)


class DefaultWindow(_DefaultWindow):
    pass


class Menu(_ButtonGroup):
    pass


class Form(_InputGroup):
    pass


class FormTemplate(_JSONTemplatedForm):
    pass

