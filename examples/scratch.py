import time

import windowlib


def create_new():
    windowlib.Button("Creating new character!")
    time.sleep(3)


def load_old(fn):
    windowlib.Button("Loading from JSON")
    import json
    with open(fn, "r") as d:
        return json.load(d)
    time.sleep(3)



def exit_program():
    windowlib.annihilate()



def demo():
    win = windowlib.DefaultWindow()
    choices = {
        0: create_new,
        1: load_old,
        2: exit_program
    }

    menu = windowlib.Menu()
    menu.register_button("Create New Form", width=40)
    menu.register_button("Load Form", width=40)
    menu.register_button("Quit", width=40)
    import time
    time.sleep(2)
    reply = menu.run_menu("!!")
    action = choices[reply]()


def jsdemo():
    win = windowlib.DefaultWindow()
    jsform = windowlib.FormTemplate("test.json")
    o = jsform.run_form(jsform.questions(), title="JSON Template Form", inputsz=30, labelsz=30)
    import time
    for r in o:
        jsform.master.cprint(r + "\n")
    time.sleep(3)


def tester():
    import time
    win = windowlib.DefaultWindow()
    win.cprint("        " + str(win.window_width) + " : " + str(win.window_width))
    time.sleep(3)
