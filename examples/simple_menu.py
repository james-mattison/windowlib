import windowlib

win = windowlib.DefaultWindow()

choices = [
        "New Game", 
        "Load Game",
        "Options",
        "Exit"
]

menu = windowlib.Menu()

for choice in choices:
    menu.register_button(choice, width=40, style="boldgreen")

menu.run_menu()
