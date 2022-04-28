import logging
import pickle
import socket
import time
import tkinter as tk
import tkinter.ttk as ttk
import sys

import pygame
from pygame.locals import (
    K_w,
    K_s,
    K_a,
    K_d,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)


class ClientSide:
    def __init__(self):
        logging.debug("client begin")
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip = "10.51.101.87"
        port = 55555
        self.my_socket.connect((ip, port))
        logging.info("connect to server at {0} with port {1}".format(ip, port))
        pygame.init()

        self.SCREEN_WIDTH = 1100
        self.SCREEN_HEIGHT = 600
        pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.display_surface = pygame.display.set_mode((1000, 20))
        pygame.display.set_caption('Show Text')
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.game = ""

    def game_run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.my_socket.send(pickle.dumps("quit"))
                        running = False
                        self.close(True)
                elif event.type == QUIT:
                    running = False
                    self.my_socket.send(pickle.dumps("quit"))
                    self.close(True)

            movement = self.mov()
            self.my_socket.send(pickle.dumps(movement))
            self.screen.fill((0, 0, 0))

            try:
                lenoflen = int(self.my_socket.recv(4).decode())
                lenght = int(self.my_socket.recv(lenoflen).decode())
                print(str(lenght))
                self.game = self.my_socket.recv(lenght)
                self.game = pickle.loads(self.game)
                if self.game == "close":
                    print("exit")
                    self.close(False)

            except Exception as e:
                print(str(e) + " <---error")
                self.close(True)

            self.built_all(self.game)
            pygame.display.flip()

    def built_all(self, game_obj):
        objects = []
        for obj in game_obj:
            objects.append(pickle.loads(obj))
        sprits = []
        for obj in objects:
            sprit = self.Demo_print(obj.x, obj.y, obj.width, obj.height, obj.angle, obj.color, obj.name)
            sprits.append(sprit)

        for sprit in sprits:
            if sprit.name == "":
                self.screen.blit(sprit.rot_image, sprit.rot_image_rect.topleft)
            else:
                self.screen.blit(sprit.text, sprit.rect)

    class Demo_print(pygame.sprite.Sprite):
        def __init__(self, x, y, width, height, angle, color, name):
            super(ClientSide.Demo_print, self).__init__()
            self.rectangle = pygame.Surface((width, height), pygame.SRCALPHA)
            self.rect = self.rectangle.get_rect()
            self.rect.move_ip(x, y)
            self.color = color
            self.rectangle.fill(pygame.Color(self.color))
            self.rot_image = pygame.transform.rotate(self.rectangle, angle)
            self.rot_image_rect = self.rot_image.get_rect(center=self.rect.center)
            self.name = name
            self.font = pygame.font.Font('freesansbold.ttf', 32)
            self.text = self.font.render(self.name, True, self.color, (0, 0, 0))

    def mov(self):
        mx, my = pygame.mouse.get_pos()
        mouse = pygame.mouse.get_pressed(3)
        move = "no input"
        val = 'no input'
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_w]:
            move = 'w'
        if pressed_keys[K_s]:
            move = 's'
        if pressed_keys[K_a]:
            move = 'a'
        if pressed_keys[K_d]:
            move = 'd'
        if mouse[0]:
            val = "fire"

        return move, val, (mx, my)

    def close(self, cause):
        if cause:
            logging.debug("client close, client side")
        else:
            logging.debug("client close, server side")
        sys.exit()


class Orientation:
    def __init__(self, x, y, width, height, angle, color, name):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.angle = angle
        self.name = name
        self.color = color


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
        self.correct = False
        self.Label4 = tk.Label(self.top)

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
        self.Button1.configure(command=self.entername)

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
        self.Button2.configure(command=self.quit)

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

    def entername(self):
        print("username = " + str(self.Entry1.get()))
        print("password = " + str(self.Entry2.get()))
        if str(self.Entry1.get()) != "nadav":
            self.print_error()
            self.Entry1.delete(0, 'end')
            self.Entry2.delete(0, 'end')
        else:
            self.delete_error()
            self.top.destroy()
            return


def entering():
    root = tk.Tk()
    root.protocol('WM_DELETE_WINDOW', root.destroy)
    _w1 = Toplevel1(root)
    # root.after(1000, _w1.loop, root)
    root.mainloop()


def main():
    entering()
    logging.basicConfig(level=logging.DEBUG)
    me = ClientSide()
    me.game_run()


if __name__ == "__main__":
    main()
