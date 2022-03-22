import logging
import pickle
import socket

import math
import sys

import pygame
import random
from pygame.locals import (
    K_w,
    K_s,
    K_a,
    K_d,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

logging.basicConfig(level=logging.DEBUG)

logging.debug("client begin")
my_socket = socket.socket()
ip = "127.0.0.1"
port = 5555
my_socket.connect((ip, port))
logging.info("connect to server at {0} with port {1}".format(ip, port))


def close():
    logging.error("client close")
    sys.exit()


def built_all(game_obj):
    # print(str(game_obj) + " <--do here built for what need how it is on server")
    objects = []
    # print(game_obj[-1])
    for obj in game_obj:
        objects.append(pickle.loads(obj))
    sprits = []
    for obj in objects:
        sprit = Demo_print(obj.x, obj.y, obj.width, obj.height, obj.angle, obj.color, obj.name)
        # print(obj.x, obj.y, obj.width, obj.height, obj.angle, obj.color)
        sprits.append(sprit)
    # print("///////////////////////////////////////////////////")

    for sprit in sprits:
        if sprit.name == "":
            screen.blit(sprit.rot_image, sprit.rot_image_rect.topleft)
        else:
            screen.blit(sprit.text, sprit.rect)


class Orientation:
    def __init__(self, x, y, width, height, angle, color, name):  # put name and do it print txt if needed!!!!
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.angle = angle
        self.name = name
        self.color = color


class Demo_print(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, angle, color, name):
        super(Demo_print, self).__init__()
        self.rectangle = pygame.Surface((width, height), pygame.SRCALPHA)
        self.rect = self.rectangle.get_rect()
        self.rect.move_ip(x, y)
        self.rectangle.fill(pygame.Color(color))
        self.rot_image = pygame.transform.rotate(self.rectangle, angle)
        self.rot_image_rect = self.rot_image.get_rect(center=self.rect.center)
        self.name = name
        self.font = pygame.font.Font('freesansbold.ttf', 32)
        self.text = self.font.render(self.name, True, color, (0, 0, 0))


def mov():
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


class LeaderBoard:
    def __init__(self):

        # self.bord = self.block((800, 0), (200, 600), 'black')
        # self.line = self.block((800, 0), (8, 600), 'gray')

        self.txts = []

        self.font = pygame.font.Font('freesansbold.ttf', 32)
        text = self.font.render('leaderboard', True, (255, 0, 0), (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (300 // 2 + 800, 10)
        self.txts.append((text, textRect))

    """def set_place(self):
        place = [self.bord, self.line]
        return place"""

    def change_places(self, players):
        leader_place = 50
        for player in players:
            text = self.font.render(str(player.name) + "           " + str(player.score), True, (255, 0, 0),
                                    (0, 0, 0))
            textRect = text.get_rect()
            textRect.center = (300 // 2 + 800, leader_place)
            self.txts.append((text, textRect))
            leader_place += 50

    def bilt(self, game):
        for text in self.txts:
            game.display_surface.blit(text[0], text[1])


pygame.init()

SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 600
pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
display_surface = pygame.display.set_mode((1000, 20))
pygame.display.set_caption('Show Text')
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
game = ""


def main():
    global game

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    my_socket.send(pickle.dumps("quit"))
                    running = False
                    continue
            elif event.type == QUIT:
                running = False
                my_socket.send(pickle.dumps("quit"))
                continue

        movement = mov()
        my_socket.send(pickle.dumps(movement))
        screen.fill((0, 0, 0))

        try:
            lenoflen = int(my_socket.recv(4).decode())
            lenght = int(my_socket.recv(lenoflen).decode())
            print(str(lenght))
            game = my_socket.recv(lenght)
            game = pickle.loads(game)
            # print(game)
            if game == "close":
                print("exit")

        except Exception as e:
            print(str(e) + " <---error")
            close()

        built_all(game)
        pygame.display.flip()


if __name__ == "__main__":
    main()
