
import windowlib

window = windowlib.DefaultWindow()

form = windowlib.Form()

answers = form.run_form(
    "First Name",
    "Last Name", 
    "Street Address",
    "City",
    "ZIP",
    title="Registration Form"
    )

with open("answers.txt", "w") as formout:
    for reply in answers:
            formout.write(reply + "\n")
            
            
