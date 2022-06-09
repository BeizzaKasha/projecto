import logging
import pickle
import socket
import tkinter as tk
import tkinter.ttk as ttk
import sys
import time
from Constants import constant
import game_server
import multiprocessing
from multiprocessing import freeze_support
import hashlib

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
    def __init__(self, ip, port, name):
        logging.debug("client begin")
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("GUI- " + str(ip) + "," + str(port))
        self.my_socket.connect((ip, port))
        """date = time.localtime()
        print(str(hashlib.md5((str(date[3]).zfill(2) + ":" + str(date[4]).zfill(2)).encode()).digest()))"""
        """date = time.localtime()
        minute_now = hashlib.md5((str(date[3]).zfill(2) + ":" + str(date[4]).zfill(2)).encode()).digest()
        minute_plus_one = hashlib.md5((str(date[3]).zfill(2) + ":" + str(int(date[4] + 1)).zfill(2)).encode()).digest()
        self.my_socket.send(pickle.dumps(hashlib.md5((constant.USER_CONNECTING, minute_now, minute_plus_one))))"""
        logging.info("connect to server at {0} with port {1}".format(ip, port))
        pygame.init()
        self.SCREEN_WIDTH = 1100
        self.SCREEN_HEIGHT = 600
        pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.display_surface = pygame.display.set_mode((1000, 20))
        pygame.display.set_caption('Show Text')
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.game = "no image"
        self.name = name

    class Demo_print(pygame.sprite.Sprite):
        def __init__(self, x, y, width, height, angle, color, name):
            super(ClientSide.Demo_print, self).__init__()
            self.rectangle = pygame.Surface((width, height), pygame.SRCALPHA)
            self.rect = self.rectangle.get_rect()
            self.rect.move_ip(x, y)
            self.color = color
            self.angle = angle
            self.rectangle.fill(pygame.Color(self.color))
            self.rot_image = pygame.transform.rotate(self.rectangle, self.angle)
            self.rot_image_rect = self.rot_image.get_rect(center=self.rect.center)
            self.name = name
            self.font = pygame.font.Font("C:\Windows\Fonts\Arial.ttf", int(self.angle))
            try:
                obj_name = self.name.split(",")
                self.text = self.font.render(obj_name[1], True, self.color, (0, 0, 0))
            except:
                self.text = self.font.render(self.name, True, self.color, (0, 0, 0))
            self.text.set_colorkey((0, 0, 0))

        def change_color(self, color):
            self.color = color
            self.rectangle.fill(pygame.Color(self.color))
            self.rot_image = pygame.transform.rotate(self.rectangle, self.angle)
            self.rot_image_rect = self.rot_image.get_rect(center=self.rect.center)
            try:
                obj_name = self.name.split(",")
                self.text = self.font.render(obj_name[1], True, self.color, (0, 0, 0))
            except:
                self.text = self.font.render(self.name, True, self.color, (0, 0, 0))

    def game_run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.my_socket.send(pickle.dumps("quit"))
                        running = self.close(True)
                elif event.type == QUIT:
                    self.my_socket.send(pickle.dumps("quit"))
                    running = self.close(True)

            movement = self.mov()
            self.send(pickle.dumps((constant.USER_ACTION, self.name, movement)))

            self.screen.fill((0, 0, 0))

            reading = self.getting_message()
            if reading == constant.QUITING:
                running = False

            # try:
            if self.game != "no image":
                self.built_all(self.game)
            # except Exception as e:
            #     logging.error(f"building error: {e}")
            pygame.display.flip()
        pygame.quit()

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
                obj_name = sprit.name.split(",")
                if len(obj_name) == 1:
                    self.screen.blit(sprit.text, sprit.rect)
                else:
                    if str(obj_name[1]) == str(self.name):
                        sprit.change_color('blue')
                    self.screen.blit(sprit.rot_image, sprit.rot_image_rect.topleft)

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

    def getting_message(self):
        try:
            self.read()
        except Exception as e:
            logging.error(f"reading error in client_side in GUI: {e}")
            self.game = "no image"
            try:
                self.read()
                print(self.game)
            except Exception as e:
                print(e)
            # self.close(True)
            # return constant.QUITING

    def read(self):
        lenoflen = int(self.my_socket.recv(4).decode())
        lenght = int(self.my_socket.recv(lenoflen).decode())
        print(str(lenght))
        self.game = self.my_socket.recv(lenght)
        print(f"len of game: {len(self.game)}")
        if lenght != len(self.game):
            self.game = "no image"
            print(self.my_socket.recv(lenght - len(self.game)))
        else:
            self.game = pickle.loads(self.game)
            if self.game == "close":
                print("exit")
                self.close(False)
                return constant.QUITING

    def send(self, data):
        self.my_socket.send(str(len(str(len(data)))).zfill(4).encode() + str(len(data)).encode() + data)

    def close(self, cause):
        if cause:
            logging.debug("client close, client side")
        else:
            logging.debug("client close, server side")
        return False


class Orientation:
    def __init__(self, x, y, width, height, angle, color, name):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.angle = angle
        self.name = name
        self.color = color


class IpCatcher:
    def __init__(self, top):
        _bgcolor = '#c1cdcd'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9'  # X11 color: 'gray85'
        _ana1color = '#d9d9d9'  # X11 color: 'gray85'
        _ana2color = '#ececec'  # Closest X11 color: 'gray92'
        self.ip = ""

        self.top = top
        top.geometry("600x450+504+171")
        top.minsize(360, 220)
        top.maxsize(500, 380)
        top.resizable(1, 1)
        top.title("Enter to game")
        top.configure(background=_bgcolor)
        top.configure(highlightbackground="#d9d9d9")
        top.configure(highlightcolor="black")
        self.style = ttk.Style()

        self.Label1 = tk.Label(self.top)
        self.Label1.place(relx=0.05, rely=0.01, height=50, width=280)
        self.Label1.configure(activebackground="#f9f9f9")
        self.Label1.configure(activeforeground="black")
        self.Label1.configure(anchor='w')
        self.Label1.configure(background=_bgcolor)
        self.Label1.configure(compound='center')
        self.Label1.configure(disabledforeground="#a3a3a3")
        self.Label1.configure(foreground="#000000")
        self.Label1.configure(highlightbackground="#d9d9d9")
        self.Label1.configure(highlightcolor="black")
        self.Label1.configure(text="ENTER SERVER IP")
        self.Label1.config(font=('Comic Sans MS', 20))

        self.Entry1 = tk.Entry(self.top)
        self.Entry1.place(relx=0.01, rely=0.3, height=40, relwidth=0.45)
        self.Entry1.configure(background="#e0eeee")
        self.Entry1.configure(disabledforeground="#ff3030")
        self.Entry1.configure(font="TkFixedFont")
        self.Entry1.configure(foreground="#000000")
        self.Entry1.configure(highlightbackground="#d9d9d9")
        self.Entry1.configure(highlightcolor="black")
        self.Entry1.configure(insertbackground="black")
        self.Entry1.configure(selectbackground="blue")
        self.Entry1.configure(selectforeground="white")

        self.Button1 = tk.Button(self.top)
        self.Button1.place(relx=0.1, rely=0.733, height=60, width=115)
        self.Button1.configure(activebackground="#838b8b")
        self.Button1.configure(activeforeground="#000000")
        self.Button1.configure(background="#e0eeee")
        self.Button1.configure(compound='left')
        self.Button1.configure(disabledforeground="#a3a3a3")
        self.Button1.configure(foreground="#000000")
        self.Button1.configure(highlightbackground="#d9d9d9")
        self.Button1.configure(highlightcolor="black")
        self.Button1.configure(pady="0")
        self.Button1.configure(text="ENTER")
        self.Button1.configure(command=self.enter_ip)

        self.style.configure('TSizegrip', background=_bgcolor)
        self.TSizegrip1 = ttk.Sizegrip(self.top)
        self.TSizegrip1.place(anchor='se', relx=1.0, rely=1.0)

    def enter_ip(self):
        self.ip = str(self.Entry1.get())
        self.top.destroy()


class HomeScreen:
    def __init__(self, top, connectir_ip, connectir_port, name):
        _bgcolor = '#ffe4e1'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9'  # X11 color: 'gray85'
        _ana1color = '#d9d9d9'  # X11 color: 'gray85'
        _ana2color = '#ececec'  # Closest X11 color: 'gray92'

        logging.debug("connection begin")
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.connect((connectir_ip, connectir_port))
        self.name = name
        self.gui_run = True

        self.send(pickle.dumps([constant.HOMESCREEN_CONNECTS, self.name.encode()]))
        data = self.read()
        self.player = data[0]
        self.position = data[1]
        self.send(pickle.dumps([constant.SERVER_REQUEST, self.name.encode()]))
        data = self.read()
        logging.debug(f"server to connect: {data}")
        if not data:
            self.open_server((connectir_ip, "helo"))
            self.send(pickle.dumps([constant.SERVER_REQUEST, self.name.encode()]))
            data = self.read()
            logging.debug(f"server to connect: {data}")
        ip, port = data
        self.ip = ip
        self.port = port

        self.top = top
        top.geometry("600x450+504+171")
        top.minsize(120, 1)
        top.maxsize(1604, 881)
        top.resizable(1, 1)
        top.title("Enter to game")
        top.configure(background=_bgcolor)
        top.configure(highlightbackground="#d9d9d9")
        top.configure(highlightcolor="black")
        self.style = ttk.Style()
        self.Label4 = tk.Label(self.top)

        self.Label1 = tk.Label(self.top)
        self.Label1.place(relx=0.05, rely=0.01, height=60, width=600)
        self.Label1.configure(activebackground="#f9f9f9")
        self.Label1.configure(activeforeground="black")
        self.Label1.configure(anchor='w')
        self.Label1.configure(background=_bgcolor)
        self.Label1.configure(compound='center')
        self.Label1.configure(disabledforeground="#a3a3a3")
        self.Label1.configure(foreground="#000000")
        self.Label1.configure(highlightbackground="#d9d9d9")
        self.Label1.configure(highlightcolor="black")
        self.Label1.configure(text='''welcome to GENERCUBE\n      HOME SCREEN ''' + str(self.player[5]))
        self.Label1.config(font=('Comic Sans MS', 20))

        self.Label2 = tk.Label(self.top)
        self.Label2.place(relx=0, rely=0.2, height=30, width=200)
        self.Label2.configure(activebackground="#f9f9f9")
        self.Label2.configure(activeforeground="black")
        self.Label2.configure(anchor='w')
        self.Label2.configure(background=_bgcolor)
        self.Label2.configure(compound='left')
        self.Label2.configure(disabledforeground="#a3a3a3")
        self.Label2.configure(foreground="#000000")
        self.Label2.configure(highlightbackground="#d9d9d9")
        self.Label2.configure(highlightcolor="black")
        self.Label2.configure(text='''Your personal record: ''' + str(self.player[4]))
        self.Label2.config(font=('Comic Sans MS', 10))

        self.Label3 = tk.Label(self.top)
        self.Label3.place(relx=0, rely=0.4, height=30, width=360)
        self.Label3.configure(activebackground="#f9f9f9")
        self.Label3.configure(activeforeground="black")
        self.Label3.configure(anchor='w')
        self.Label3.configure(background=_bgcolor)
        self.Label3.configure(compound='left')
        self.Label3.configure(disabledforeground="#a3a3a3")
        self.Label3.configure(foreground="#000000")
        self.Label3.configure(highlightbackground="#d9d9d9")
        self.Label3.configure(highlightcolor="black")
        self.Label3.configure(text='''You are playing this game since ''' + self.player[2])
        self.Label3.config(font=('Comic Sans MS', 10))

        self.Label4 = tk.Label(self.top)
        self.Label4.place(relx=0, rely=0.6, height=30, width=250)
        self.Label4.configure(activebackground="#f9f9f9")
        self.Label4.configure(activeforeground="black")
        self.Label4.configure(anchor='w')
        self.Label4.configure(background=_bgcolor)
        self.Label4.configure(compound='left')
        self.Label4.configure(disabledforeground="#a3a3a3")
        self.Label4.configure(foreground="#000000")
        self.Label4.configure(highlightbackground="#d9d9d9")
        self.Label4.configure(highlightcolor="black")
        self.Label4.configure(text=self.position_placer(self.position))
        self.Label4.config(font=('Comic Sans MS', 10))

        self.Button1 = tk.Button(self.top)
        self.Button1.place(relx=0.1, rely=0.733, height=60, width=115)
        self.Button1.configure(activebackground="#eecbad")
        self.Button1.configure(activeforeground="#000000")
        self.Button1.configure(background="#ffefd5")
        self.Button1.configure(compound='left')
        self.Button1.configure(disabledforeground="#a3a3a3")
        self.Button1.configure(foreground="#000000")
        self.Button1.configure(highlightbackground="#d9d9d9")
        self.Button1.configure(highlightcolor="black")
        self.Button1.configure(pady="0")
        self.Button1.configure(text='''ENTER GAME''')
        self.Button1.configure(command=self.Enter_game)

        self.Button2 = tk.Button(self.top)
        self.Button2.place(relx=0.7, rely=0.733, height=60, width=115)
        self.Button2.configure(activebackground="#eecbad")
        self.Button2.configure(activeforeground="#000000")
        self.Button2.configure(background="#ffefd5")
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

    def open_server(self, database_ip):
        server = multiprocessing.Process(target=game_server.starting, args=database_ip)
        server.start()
        time.sleep(2)

    def quit(self):
        self.send(pickle.dumps([constant.HOMESCREEN_QUITING, self.name.encode()]))
        print('---------------quit----------------')
        sys.stdout.flush()
        self.my_socket.close()
        self.top.destroy()
        self.gui_run = False
        # sys.exit()

    def read(self):
        lenoflen = int(self.my_socket.recv(4).decode())
        lenght = int(self.my_socket.recv(lenoflen).decode())
        data = self.my_socket.recv(lenght)
        data = pickle.loads(data)
        return data

    def send(self, data):
        self.my_socket.send(str(len(str(len(data)))).zfill(4).encode() + str(len(data)).encode() + data)

    def position_placer(self, position):
        if position == 1:
            return "You are the best in the game!"
        else:
            return "Your position the player ranking is " + str(position) + "!"

    def Enter_game(self):
        self.my_socket.close()
        self.top.destroy()


class TopLevelMother:
    def __init__(self, top, headline, botton1, error_msg, ip, is_connect):
        _bgcolor = '#ffe4e1'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9'  # X11 color: 'gray85'
        _ana1color = '#d9d9d9'  # X11 color: 'gray85'
        _ana2color = '#ececec'  # Closest X11 color: 'gray92'

        logging.debug("connection begin")
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if is_connect != 0:
            self.database_ip = ip
            self.connector_ip = ip
            self.connector_port = 7777
            try:
                self.my_socket.connect((self.connector_ip, self.connector_port))
            except Exception as e:
                print(e)
                sys.exit()
            logging.info("connect to server at {0} with port {1}".format(self.connector_ip, self.connector_port))
        else:
            self.my_socket = ip
            self.database_ip = self.my_socket.getsockname()

        self.top = top
        top.geometry("600x450+504+171")
        top.minsize(120, 1)
        top.maxsize(1604, 881)
        top.resizable(1, 1)
        top.title("Enter to game")
        top.configure(background=_bgcolor)
        top.configure(highlightbackground="#d9d9d9")
        top.configure(highlightcolor="black")
        self.style = ttk.Style()
        self.Label4 = tk.Label(self.top)
        self.error_msg = error_msg
        self.name = ""

        headline = headline.split(",")
        self.Label1 = tk.Label(self.top)
        self.Label1.place(relx=headline[1], rely=headline[2], height=headline[3], width=600)
        self.Label1.configure(activebackground=_bgcolor)
        self.Label1.configure(activeforeground="black")
        self.Label1.configure(anchor='w')
        self.Label1.configure(background=_bgcolor)
        self.Label1.configure(compound='center')
        self.Label1.configure(disabledforeground="#a3a3a3")
        self.Label1.configure(foreground="#000000")
        self.Label1.configure(highlightbackground="#d9d9d9")
        self.Label1.configure(highlightcolor="black")
        self.Label1.configure(text=headline[0])
        self.Label1.config(font=('Comic Sans MS', 25))

        self.Entry1 = tk.Entry(self.top)
        self.Entry1.place(relx=0.01, rely=0.25, height=40, relwidth=0.307)
        self.Entry1.configure(background="#fdf5e6")
        self.Entry1.configure(disabledforeground="#eee0e5")
        self.Entry1.configure(font="TkFixedFont")
        self.Entry1.configure(foreground="#000000")
        self.Entry1.configure(highlightbackground="#d9d9d9")
        self.Entry1.configure(highlightcolor="black")
        self.Entry1.configure(insertbackground="black")
        self.Entry1.configure(selectbackground="blue")
        self.Entry1.configure(selectforeground="white")

        self.Label2 = tk.Label(self.top)
        self.Label2.place(relx=0, rely=0.15, height=20, width=114)
        self.Label2.configure(activebackground=_bgcolor)
        self.Label2.configure(activeforeground="black")
        self.Label2.configure(anchor='w')
        self.Label2.configure(background=_bgcolor)
        self.Label2.configure(compound='left')
        self.Label2.configure(disabledforeground="#a3a3a3")
        self.Label2.configure(foreground="#000000")
        self.Label2.configure(highlightbackground="#d9d9d9")
        self.Label2.configure(highlightcolor="black")
        self.Label2.configure(text='''ENTER NAME''')
        self.Label2.config(font=('Comic Sans MS', 10))

        self.Entry2 = tk.Entry(self.top)
        self.Entry2.place(relx=0.01, rely=0.5, height=40, relwidth=0.307)
        self.Entry2.configure(background="#fdf5e6")
        self.Entry2.configure(disabledforeground="#eee0e5")
        self.Entry2.configure(font="TkFixedFont")
        self.Entry2.configure(foreground="#000000")
        self.Entry2.configure(highlightbackground="#d9d9d9")
        self.Entry2.configure(highlightcolor="black")
        self.Entry2.configure(insertbackground="black")
        self.Entry2.configure(selectbackground="blue")
        self.Entry2.configure(show="*")
        self.Entry2.configure(selectforeground="white")

        self.Label3 = tk.Label(self.top)
        self.Label3.place(relx=0, rely=0.4, height=20, width=130)
        self.Label3.configure(activebackground=_bgcolor)
        self.Label3.configure(activeforeground="black")
        self.Label3.configure(anchor='w')
        self.Label3.configure(background=_bgcolor)
        self.Label3.configure(compound='left')
        self.Label3.configure(disabledforeground="#a3a3a3")
        self.Label3.configure(foreground="#000000")
        self.Label3.configure(highlightbackground="#d9d9d9")
        self.Label3.configure(highlightcolor="black")
        self.Label3.configure(text='''ENTER PASSWORD''')
        self.Label3.config(font=('Comic Sans MS', 10))

        self.Button1 = tk.Button(self.top)
        self.Button1.place(relx=0.1, rely=0.733, height=80, width=130)
        self.Button1.configure(activebackground="#eecbad")
        self.Button1.configure(activeforeground="#000000")
        self.Button1.configure(background="#ffefd5")
        self.Button1.configure(compound='left')
        self.Button1.configure(disabledforeground="#a3a3a3")
        self.Button1.configure(foreground="#000000")
        self.Button1.configure(highlightbackground="#d9d9d9")
        self.Button1.configure(highlightcolor="black")
        self.Button1.configure(pady="0")
        self.Button1.configure(text=botton1)
        self.Button1.configure(command=self.entername)
        self.Button1.config(font=('Comic Sans MS', 10))

        self.Button2 = tk.Button(self.top)
        self.Button2.place(relx=0.7, rely=0.733, height=80, width=130)
        self.Button2.configure(activebackground="#eecbad")
        self.Button2.configure(activeforeground="#000000")
        self.Button2.configure(background="#ffefd5")
        self.Button2.configure(compound='left')
        self.Button2.configure(disabledforeground="#a3a3a3")
        self.Button2.configure(foreground="#000000")
        self.Button2.configure(highlightbackground="#d9d9d9")
        self.Button2.configure(highlightcolor="black")
        self.Button2.configure(pady="0")
        self.Button2.configure(text='''quit''')
        self.Button2.configure(command=self.quit)
        self.Button2.config(font=('Comic Sans MS', 10))

        self.style.configure('TSizegrip', background=_bgcolor)
        self.TSizegrip1 = ttk.Sizegrip(self.top)
        self.TSizegrip1.place(anchor='se', relx=1.0, rely=1.0)

    def print_error(self):
        self.Label4 = tk.Label(self.top)
        self.Label4.place(relx=0, rely=0.6, height=20, width=120)
        self.Label4.configure(activebackground='#ffe4e1')
        self.Label4.configure(activeforeground="black")
        self.Label4.configure(anchor='w')
        self.Label4.configure(background='#ffe4e1')
        self.Label4.configure(compound='left')
        self.Label4.configure(disabledforeground="#a3a3a3")
        self.Label4.configure(foreground="red")
        self.Label4.configure(highlightbackground="#d9d9d9")
        self.Label4.configure(highlightcolor="black")
        self.Label4.configure(text=self.error_msg)
        self.Label4.config(font=('Comic Sans MS', 10))

    def delete_error(self):
        self.Label4.destroy()

    def quit(self, *args):
        try:
            self.send(pickle.dumps(constant.QUITING))
        finally:
            print('---------------quit----------------')
            for arg in args:
                print('another arg:', arg)
            sys.stdout.flush()
            sys.exit()

    def send(self, data):
        self.my_socket.send(str(len(str(len(data)))).zfill(4).encode() + str(len(data)).encode() + data)

    def entername(self):
        logging.debug(f"username = {self.Entry1.get()}")
        logging.debug(f"password = {self.Entry2.get()}")
        self.send(pickle.dumps((constant.USER_CONNECTING, self.Entry1.get(), self.Entry2.get(), "", "player")))
        try:
            lenoflen = int(self.my_socket.recv(4).decode())
            lenght = int(self.my_socket.recv(lenoflen).decode())
            data = self.my_socket.recv(lenght)
            data = pickle.loads(data)
            if not data:
                self.print_error()
                self.Entry1.delete(0, 'end')
                self.Entry2.delete(0, 'end')
            else:
                self.name = str(self.Entry1.get())
                self.my_socket.send(pickle.dumps(constant.QUITING))
                self.my_socket.close()
                self.delete_error()
                self.top.destroy()
        except Exception as e:
            logging.error(f"TopLevelMother error occurred: {e}")
            sys.exit()


class TopLevel1(TopLevelMother):
    def __init__(self, top, ip):
        super(TopLevel1, self).__init__(top, '''welcome to\nGENERCUBE,0.5,0.1, 160''', '''CONNECT TO USER''',
                                        '''INCORRECT NAME OR PASSWORD''', ip, 1)
        self.ip = ip

        self.Button3 = tk.Button(self.top)
        self.Button3.place(relx=0.8, rely=0.478, height=54, width=110)
        self.Button3.configure(activebackground="#eecbad")
        self.Button3.configure(activeforeground="#000000")
        self.Button3.configure(background="#ffefd5")
        self.Button3.configure(compound='left')
        self.Button3.configure(disabledforeground="#a3a3a3")
        self.Button3.configure(foreground="#000000")
        self.Button3.configure(highlightbackground="#d9d9d9")
        self.Button3.configure(highlightcolor="black")
        self.Button3.configure(pady="0")
        self.Button3.configure(text='''create new user''')
        self.Button3.configure(command=self.move_level2)
        self.Button3.config(font=('Comic Sans MS', 10))

    def move_level2(self):
        self.top.withdraw()
        root = tk.Tk()
        root.protocol('WM_DELETE_WINDOW', root.destroy)
        _w2 = TopLevel2(root, self, self.my_socket)
        self.name = _w2.name

    def level2_got_in(self, name):
        self.top.deiconify()
        self.name = name
        if name != "":
            self.my_socket.close()
            self.top.destroy()


class TopLevel2(TopLevelMother):
    def __init__(self, top, level1, ip):
        super(TopLevel2, self).__init__(top, '''A NEW USER APPEAR!,0.05,0.01, 60''', '''CREATE NEW USER''',
                                        '''not possible''', ip, 0)
        self.level1 = level1

        self.Button3 = tk.Button(self.top)
        self.Button3.place(relx=0.8, rely=0.478, height=54, width=110)
        self.Button3.configure(activebackground="#ececec")
        self.Button3.configure(activeforeground="#000000")
        self.Button3.configure(background="#ffefd5")
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
        self.Entry3.configure(background="#fdf5e6")
        self.Entry3.configure(disabledforeground="#a3a3a3")
        self.Entry3.configure(font="TkFixedFont")
        self.Entry3.configure(foreground="#000000")
        self.Entry3.configure(highlightbackground="#d9d9d9")
        self.Entry3.configure(highlightcolor="black")
        self.Entry3.configure(insertbackground="black")
        self.Entry3.configure(selectbackground="blue")
        self.Entry3.configure(selectforeground="white")

        self.Label5 = tk.Label(self.top)
        self.Label5.place(relx=0.5, rely=0.15, height=20, width=144)
        self.Label5.configure(activebackground="#f9f9f9")
        self.Label5.configure(activeforeground="black")
        self.Label5.configure(anchor='w')
        self.Label5.configure(background="#ffe4e1")
        self.Label5.configure(compound='left')
        self.Label5.configure(disabledforeground="#a3a3a3")
        self.Label5.configure(foreground="#000000")
        self.Label5.configure(highlightbackground="#d9d9d9")
        self.Label5.configure(highlightcolor="black")
        self.Label5.configure(text='''ENTER CLIENT NAME''')
        self.Label5.config(font=('Comic Sans MS', 10))

    def back_to_level1(self):
        self.top.destroy()
        self.level1.level2_got_in(self.name)

    def entername(self):
        logging.debug(f"username = {self.Entry1.get()}")
        logging.debug(f"password = {self.Entry2.get()}")
        date = time.localtime()[0:-4]
        update_date = str(date[0]) + "/" + str(date[1]) + "/" + str(date[2]) + " " + str(date[3]) + ":" + str(
            date[4]).zfill(2)
        self.send(pickle.dumps(
            (constant.USER_CONNECTING, self.Entry1.get(), self.Entry2.get(), update_date, self.Entry3.get())))
        try:
            lenoflen = int(self.my_socket.recv(4).decode())
            lenght = int(self.my_socket.recv(lenoflen).decode())
            data = self.my_socket.recv(lenght)
            data = pickle.loads(data)
            if not data:
                self.print_error()
                self.Entry1.delete(0, 'end')
                self.Entry2.delete(0, 'end')
                self.Entry3.delete(0, 'end')
            else:
                self.name = str(self.Entry1.get())
                self.my_socket.send(pickle.dumps(constant.QUITING))
                self.my_socket.close()
                self.delete_error()
                self.back_to_level1()
        except Exception as e:
            logging.error(f"TopLevel2 error occurred: {e}")
            self.back_to_level1()


class screen_manager:
    def get_ip(self):
        root = tk.Tk()
        root.protocol('WM_DELETE_WINDOW', root.destroy)
        start_tk = IpCatcher(root)
        root.mainloop()
        return start_tk.ip

    def entering(self):
        ip = self.get_ip()
        root = tk.Tk()
        root.protocol('WM_DELETE_WINDOW', root.destroy)
        _w1 = TopLevel1(root, ip)
        # root.after(1000, _w1.loop, root)
        root.mainloop()
        return _w1.connector_ip, _w1.connector_port, _w1.name

    def stay_screen(self, ip, port, name):
        root = tk.Tk()
        root.protocol('WM_DELETE_WINDOW', root.destroy)
        home_screen = HomeScreen(root, ip, port, name)
        root.mainloop()
        return home_screen.ip, home_screen.port, home_screen.gui_run

    def screen_control_loop(self):
        logging.basicConfig(level=logging.DEBUG)
        connector_ip, connector_port, name = self.entering()
        gui_run = True
        while gui_run:
            port, ip, gui_run = self.stay_screen(connector_ip, connector_port, name)
            if not gui_run:
                break
            try:
                me = ClientSide(ip, port, name)
                me.game_run()
            except Exception as e:
                logging.error(f"universal error: {e}")
                continue


def main():
    SM = screen_manager()
    SM.screen_control_loop()


if __name__ == "__main__":
    freeze_support()
    multiprocessing.set_start_method('spawn')
    try:
        main()
    except Exception as e:
        print(f"error occurred-> {e.with_traceback(sys.exc_info()[2])}")
        input("wut?")
