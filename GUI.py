import logging
import pickle
import socket
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

import GUI


class ClientSide:
    def __init__(self, ip, port, name):
        logging.debug("client begin")
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
        self.name = name

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
            self.font = pygame.font.Font('freesansbold.ttf', int(angle))
            self.text = self.font.render(self.name, True, self.color, (0, 0, 0))
            # self.text.set_alpha(200)
            self.text.set_colorkey((0, 0, 0))

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
            self.my_socket.send(pickle.dumps((self.name, movement)))
            self.screen.fill((0, 0, 0))

            self.read()

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

    def read(self):
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


class HomeScreen:
    def __init__(self, top, connectir_ip, connectir_port, name):
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9'  # X11 color: 'gray85'
        _ana1color = '#d9d9d9'  # X11 color: 'gray85'
        _ana2color = '#ececec'  # Closest X11 color: 'gray92'

        logging.debug("connection begin")
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.connect((connectir_ip, connectir_port))

        self.send(pickle.dumps([2, name.decode()]))
        lenoflen = int(self.my_socket.recv(4).decode())
        lenght = int(self.my_socket.recv(lenoflen).decode())
        data = self.my_socket.recv(lenght)
        data = pickle.loads(data)
        self.player = data

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
        self.Label4 = tk.Label(self.top)
        self.ip = "127.0.0.1"
        self.port = 5555
        self.name = "none"

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
        self.Label1.configure(text='''WELCOME TO HOME SCREEN!''')
        self.Label1.config(font=('Helvatical bold', 20))

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
        self.Button1.place(relx=0.1, rely=0.733, height=60, width=115)
        self.Button1.configure(activebackground="#ececec")
        self.Button1.configure(activeforeground="#000000")
        self.Button1.configure(background="#d9d9d9")
        self.Button1.configure(compound='left')
        self.Button1.configure(disabledforeground="#a3a3a3")
        self.Button1.configure(foreground="#000000")
        self.Button1.configure(highlightbackground="#d9d9d9")
        self.Button1.configure(highlightcolor="black")
        self.Button1.configure(pady="0")
        self.Button1.configure(text='''botton1''')
        self.Button1.configure(command=self.quit())

        self.Button2 = tk.Button(self.top)
        self.Button2.place(relx=0.8, rely=0.778, height=54, width=107)
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

    def quit(self, *args):
        try:
            self.send(pickle.dumps(99))
        finally:
            print('---------------quit----------------')
            for arg in args:
                print('another arg:', arg)
            sys.stdout.flush()
            sys.exit()

    def send(self, data):
        self.my_socket.send(str(len(str(len(data)))).zfill(4).encode() + str(len(data)).encode() + data)


class Toplevel_mother:
    def __init__(self, top, headline, botton1, error_msg):
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9'  # X11 color: 'gray85'
        _ana1color = '#d9d9d9'  # X11 color: 'gray85'
        _ana2color = '#ececec'  # Closest X11 color: 'gray92'

        logging.debug("connection begin")
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connector_ip = "127.0.0.1"
        self.connector_port = 7777
        self.my_socket.connect((self.connector_ip, self.connector_port))
        logging.info("connect to server at {0} with port {1}".format(self.connector_ip, self.connector_port))

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
        self.Label4 = tk.Label(self.top)
        self.error_msg = error_msg
        self.name = ""

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
        self.Label1.configure(text=headline)
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
        self.Button1.place(relx=0.1, rely=0.733, height=60, width=115)
        self.Button1.configure(activebackground="#ececec")
        self.Button1.configure(activeforeground="#000000")
        self.Button1.configure(background="#d9d9d9")
        self.Button1.configure(compound='left')
        self.Button1.configure(disabledforeground="#a3a3a3")
        self.Button1.configure(foreground="#000000")
        self.Button1.configure(highlightbackground="#d9d9d9")
        self.Button1.configure(highlightcolor="black")
        self.Button1.configure(pady="0")
        self.Button1.configure(text=botton1)
        self.Button1.configure(command=self.entername)

        self.Button2 = tk.Button(self.top)
        self.Button2.place(relx=0.8, rely=0.778, height=54, width=107)
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
        self.Label4.configure(text=self.error_msg)
        self.Label4.config(font=('Helvatical bold', 10))

    def delete_error(self):
        self.Label4.destroy()

    def quit(self, *args):
        try:
            self.send(pickle.dumps(99))
        finally:
            print('---------------quit----------------')
            for arg in args:
                print('another arg:', arg)
            sys.stdout.flush()
            sys.exit()

    def send(self, data):
        self.my_socket.send(str(len(str(len(data)))).zfill(4).encode() + str(len(data)).encode() + data)

    def entername(self):
        print("username = " + str(self.Entry1.get()))
        print("password = " + str(self.Entry2.get()))
        self.send(pickle.dumps((0, self.Entry1.get(), self.Entry2.get())))

        try:
            lenoflen = int(self.my_socket.recv(4).decode())
            lenght = int(self.my_socket.recv(lenoflen).decode())
            data = self.my_socket.recv(lenght)
            data = pickle.loads(data)
            # print(data)
            if not data:
                self.print_error()
                self.Entry1.delete(0, 'end')
                self.Entry2.delete(0, 'end')
            else:
                self.name = str(self.Entry1.get())
                self.my_socket.close()
                self.delete_error()
                self.top.destroy()
        except Exception as e:
            print(str(e) + " <---error")
            sys.exit()


class Toplevel1(GUI.Toplevel_mother):
    def __init__(self, top):
        super().__init__(top, '''WELCOME TO SHOOTY SHOOTY GAME''', '''ENTER GAME!''',
                         '''INCORRECT NAME OR PASSWORD''')
        # self.root = top

        self.Button3 = tk.Button(self.top)
        self.Button3.place(relx=0.8, rely=0.478, height=54, width=110)
        self.Button3.configure(activebackground="#ececec")
        self.Button3.configure(activeforeground="#000000")
        self.Button3.configure(background="#d9d9d9")
        self.Button3.configure(compound='left')
        self.Button3.configure(disabledforeground="#a3a3a3")
        self.Button3.configure(foreground="#000000")
        self.Button3.configure(highlightbackground="#d9d9d9")
        self.Button3.configure(highlightcolor="black")
        self.Button3.configure(pady="0")
        self.Button3.configure(text='''create new user''')
        self.Button3.configure(command=self.move_level2)

    def move_level2(self):
        self.top.withdraw()
        root = tk.Tk()
        root.protocol('WM_DELETE_WINDOW', root.destroy)
        _w2 = Toplevel2(root, self.top)
        self.name = _w2.name


class Toplevel2(GUI.Toplevel_mother):
    def __init__(self, top, level1):
        super().__init__(top, '''A NEW USER APPEAR!''', '''CREATE NEW USER!''',
                         '''not possible''')
        self.level1 = level1

        self.Button3 = tk.Button(self.top)
        self.Button3.place(relx=0.8, rely=0.478, height=54, width=110)
        self.Button3.configure(activebackground="#ececec")
        self.Button3.configure(activeforeground="#000000")
        self.Button3.configure(background="#d9d9d9")
        self.Button3.configure(compound='left')
        self.Button3.configure(disabledforeground="#a3a3a3")
        self.Button3.configure(foreground="#000000")
        self.Button3.configure(highlightbackground="#d9d9d9")
        self.Button3.configure(highlightcolor="black")
        self.Button3.configure(pady="0")
        self.Button3.configure(text='''I have a user already''')
        self.Button3.configure(command=self.back_to_level1)

        self.Entry3 = tk.Entry(self.top)
        self.Entry3.place(relx=0.51, rely=0.25, height=40, relwidth=0.307)
        self.Entry3.configure(background="white")
        self.Entry3.configure(disabledforeground="#a3a3a3")
        self.Entry3.configure(font="TkFixedFont")
        self.Entry3.configure(foreground="#000000")
        self.Entry3.configure(highlightbackground="#d9d9d9")
        self.Entry3.configure(highlightcolor="black")
        self.Entry3.configure(insertbackground="black")
        self.Entry3.configure(selectbackground="blue")
        self.Entry3.configure(selectforeground="white")

        self.Label5 = tk.Label(self.top)
        self.Label5.place(relx=0.5, rely=0.15, height=20, width=114)
        self.Label5.configure(activebackground="#f9f9f9")
        self.Label5.configure(activeforeground="black")
        self.Label5.configure(anchor='w')
        self.Label5.configure(background="#d9d9d9")
        self.Label5.configure(compound='left')
        self.Label5.configure(disabledforeground="#a3a3a3")
        self.Label5.configure(foreground="#000000")
        self.Label5.configure(highlightbackground="#d9d9d9")
        self.Label5.configure(highlightcolor="black")
        self.Label5.configure(text='''ENTER NAME''')
        self.Label5.config(font=('Helvatical bold', 10))

    def back_to_level1(self):
        self.level1.deiconify()
        self.top.destroy()

    def entername(self):
        print("username = " + str(self.Entry1.get()))
        print("password = " + str(self.Entry2.get()))
        self.send(pickle.dumps((1, self.Entry1.get(), self.Entry2.get())))

        try:
            lenoflen = int(self.my_socket.recv(4).decode())
            lenght = int(self.my_socket.recv(lenoflen).decode())
            data = self.my_socket.recv(lenght)
            data = pickle.loads(data)
            # print(data)
            if not data:
                self.print_error()
                self.Entry1.delete(0, 'end')
                self.Entry2.delete(0, 'end')
                self.Entry3.delete(0, 'end')
            else:
                self.name = str(self.Entry1.get())
                self.ip = data[0].decode()
                self.port = data[1]
                self.my_socket.close()
                self.delete_error()
                self.back_to_level1()
        except Exception as e:
            print(str(e) + " <---error")
            self.back_to_level1()


def entering():
    root = tk.Tk()
    root.protocol('WM_DELETE_WINDOW', root.destroy)
    _w1 = Toplevel1(root)
    # root.after(1000, _w1.loop, root)
    root.mainloop()
    return _w1.connector_ip, _w1.connector_port, _w1.name


def stay_screen(ip, port, name):
    root = tk.Tk()
    root.protocol('WM_DELETE_WINDOW', root.destroy)
    home_screen = HomeScreen(root, ip, port, name)
    root.mainloop()
    return home_screen.ip, home_screen.port


def main():
    connector_ip, connector_port, name = entering()
    ip, port = stay_screen(connector_ip, connector_port, name)
    logging.basicConfig(level=logging.DEBUG)
    me = ClientSide(ip, port, name)
    me.game_run()


if __name__ == "__main__":
    main()
