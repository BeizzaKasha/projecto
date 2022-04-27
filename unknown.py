import sys
import tkinter as tk
import tkinter.ttk as ttk


class Toplevel1:

    def __init__(self, top):
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9'  # X11 color: 'gray85'
        _ana1color = '#d9d9d9'  # X11 color: 'gray85'
        _ana2color = '#ececec'  # Closest X11 color: 'gray92'

        self.top = top
        top.geometry("600x450+504+171")
        top.minsize(120, 1)
        top.maxsize(1604, 881)
        top.resizable(1, 1)
        top.title("Enter to game")
        top.configure(background="#d9d9d9")
        top.configure(highlightbackground="#d9d9d9")
        top.configure(highlightcolor="black")
        self.style = ttk.Style()

        self.Label1 = tk.Label(self.top)
        self.Label1.place(relx=0.05, rely=0.01, height=20, width=600)
        self.Label1.configure(activebackground="#f9f9f9")
        self.Label1.configure(activeforeground="black")
        self.Label1.configure(anchor='w')
        self.Label1.configure(background="#d9d9d9")
        self.Label1.configure(compound='center')
        self.Label1.configure(disabledforeground="#a3a3a3")
        self.Label1.configure(foreground="#000000")
        self.Label1.configure(highlightbackground="#d9d9d9")
        self.Label1.configure(highlightcolor="black")
        self.Label1.configure(text='''WELCOME TO SHOOTY SHOOTY GAME''')
        self.Label1.config(font=('Helvatical bold', 20))

        self.Entry1 = tk.Entry(self.top)
        self.Entry1.place(relx=0.01, rely=0.25, height=40, relwidth=0.307)
        self.Entry1.configure(background="white")
        self.Entry1.configure(disabledforeground="#a3a3a3")
        self.Entry1.configure(font="TkFixedFont")
        self.Entry1.configure(foreground="#000000")
        self.Entry1.configure(highlightbackground="#d9d9d9")
        self.Entry1.configure(highlightcolor="black")
        self.Entry1.configure(insertbackground="black")
        self.Entry1.configure(selectbackground="blue")
        self.Entry1.configure(selectforeground="white")

        self.Label2 = tk.Label(self.top)
        self.Label2.place(relx=0, rely=0.15, height=20, width=114)
        self.Label2.configure(activebackground="#f9f9f9")
        self.Label2.configure(activeforeground="black")
        self.Label2.configure(anchor='w')
        self.Label2.configure(background="#d9d9d9")
        self.Label2.configure(compound='left')
        self.Label2.configure(disabledforeground="#a3a3a3")
        self.Label2.configure(foreground="#000000")
        self.Label2.configure(highlightbackground="#d9d9d9")
        self.Label2.configure(highlightcolor="black")
        self.Label2.configure(text='''ENTER NAME''')
        self.Label2.config(font=('Helvatical bold', 10))

        self.Entry2 = tk.Entry(self.top)
        self.Entry2.place(relx=0.01, rely=0.5, height=40, relwidth=0.307)
        self.Entry2.configure(background="white")
        self.Entry2.configure(disabledforeground="#a3a3a3")
        self.Entry2.configure(font="TkFixedFont")
        self.Entry2.configure(foreground="#000000")
        self.Entry2.configure(highlightbackground="#d9d9d9")
        self.Entry2.configure(highlightcolor="black")
        self.Entry2.configure(insertbackground="black")
        self.Entry2.configure(selectbackground="blue")
        self.Entry2.configure(selectforeground="white")

        self.Label3 = tk.Label(self.top)
        self.Label3.place(relx=0, rely=0.4, height=20, width=130)
        self.Label3.configure(activebackground="#f9f9f9")
        self.Label3.configure(activeforeground="black")
        self.Label3.configure(anchor='w')
        self.Label3.configure(background="#d9d9d9")
        self.Label3.configure(compound='left')
        self.Label3.configure(disabledforeground="#a3a3a3")
        self.Label3.configure(foreground="#000000")
        self.Label3.configure(highlightbackground="#d9d9d9")
        self.Label3.configure(highlightcolor="black")
        self.Label3.configure(text='''ENTER PASSWORD''')
        self.Label3.config(font=('Helvatical bold', 10))

        self.Button1 = tk.Button(self.top)
        self.Button1.place(relx=0.1, rely=0.733, height=54, width=107)
        self.Button1.configure(activebackground="#ececec")
        self.Button1.configure(activeforeground="#000000")
        self.Button1.configure(background="#d9d9d9")
        self.Button1.configure(compound='left')
        self.Button1.configure(disabledforeground="#a3a3a3")
        self.Button1.configure(foreground="#000000")
        self.Button1.configure(highlightbackground="#d9d9d9")
        self.Button1.configure(highlightcolor="black")
        self.Button1.configure(pady="0")
        self.Button1.configure(text='''ENTER''')
        self.Button1.configure(command=entername)

        self.Button2 = tk.Button(self.top)
        self.Button2.place(relx=0.6, rely=0.778, height=44, width=87)
        self.Button2.configure(activebackground="#ececec")
        self.Button2.configure(activeforeground="#000000")
        self.Button2.configure(background="#d9d9d9")
        self.Button2.configure(compound='left')
        self.Button2.configure(disabledforeground="#a3a3a3")
        self.Button2.configure(foreground="#000000")
        self.Button2.configure(highlightbackground="#d9d9d9")
        self.Button2.configure(highlightcolor="black")
        self.Button2.configure(pady="0")
        self.Button2.configure(text='''quit''')
        self.Button2.configure(command=quit)

        self.style.configure('TSizegrip', background=_bgcolor)
        self.TSizegrip1 = ttk.Sizegrip(self.top)
        self.TSizegrip1.place(anchor='se', relx=1.0, rely=1.0)

    def print_error(self):
        self.Label4 = tk.Label(self.top)
        self.Label4.place(relx=0, rely=0.6, height=20, width=120)
        self.Label4.configure(activebackground="#f9f9f9")
        self.Label4.configure(activeforeground="black")
        self.Label4.configure(anchor='w')
        self.Label4.configure(background="#d9d9d9")
        self.Label4.configure(compound='left')
        self.Label4.configure(disabledforeground="#a3a3a3")
        self.Label4.configure(foreground="red")
        self.Label4.configure(highlightbackground="#d9d9d9")
        self.Label4.configure(highlightcolor="black")
        self.Label4.configure(text='''INCORRECT NAME''')
        self.Label4.config(font=('Helvatical bold', 10))

    def delete_error(self):
        self.Label4.destroy()


def quit(*args):
    print('---------------quit----------------')
    for arg in args:
        print('another arg:', arg)
    sys.stdout.flush()
    sys.exit()


def entername():
    print("username = " + str(_w1.Entry1.get()))
    print("password = " + str(_w1.Entry2.get()))
    if str(_w1.Entry1.get()) != "nadav":
        _w1.print_error()
    else:
        _w1.delete_error()
    _w1.Entry1.delete(0, 'end')
    _w1.Entry2.delete(0, 'end')


def main(*args):
    global root
    root = tk.Tk()
    root.protocol('WM_DELETE_WINDOW', root.destroy)
    # Creates a toplevel widget.
    global _w1
    _w1 = Toplevel1(root)
    root.mainloop()


if __name__ == '__main__':
    main()
