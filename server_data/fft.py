from tkinter import *
from tkinter import messagebox

window = Tk()
window.title("Login Form")
window.geometry("400x300")

global e1
global e2

Label(window, text = "Username").place(x=10, y=10)
Label(window, text= "Password").place(x=10, y=40)

e1 = Entry(window)
e1.place(x=140, y=10)

e2 = Entry(window)
e2.place(x=140, y=40)
e2.config(show="*")

Button(window, text = "Login", height= 3, width= 13).place(x=130, y=100)

window.mainloop()
