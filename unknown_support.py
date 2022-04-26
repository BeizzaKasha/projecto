import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.constants import *
import unknown


def main(*args):
    global root
    root = tk.Tk()
    root.protocol('WM_DELETE_WINDOW', root.destroy)
    # Creates a toplevel widget.
    global _top1, _w1
    _top1 = root
    _w1 = unknown.Toplevel1(_top1)
    root.mainloop()


def quit(*args):
    print('---------------quit----------------')
    for arg in args:
        print('another arg:', arg)
    sys.stdout.flush()
    sys.exit()


def entername():
    print(_w1.Entry1.get())


if __name__ == '__main__':
    unknown.start_up()
