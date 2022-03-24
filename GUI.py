import logging
import pickle
import socket

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
        self.my_socket = socket.socket()
        ip = "127.0.0.1"
        port = 5555
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


class LeaderBoard:
    def __init__(self):
        self.txts = []

        self.font = pygame.font.Font('freesansbold.ttf', 32)
        text = self.font.render('leaderboard', True, (255, 0, 0), (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (300 // 2 + 800, 10)
        self.txts.append((text, textRect))

    def change_places(self, players):
        leader_place = 50
        for player in players:
            text = self.font.render(str(player.name) + "           " + str(player.score), True, (255, 0, 0),
                                    (0, 0, 0))
            textRect = text.get_rect()
            textRect.center = (300 // 2 + 800, leader_place)
            self.txts.append((text, textRect))
            leader_place += 50


class Orientation:
    def __init__(self, x, y, width, height, angle, color, name):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.angle = angle
        self.name = name
        self.color = color


def main():
    logging.basicConfig(level=logging.DEBUG)
    me = ClientSide()
    me.game_run()


if __name__ == "__main__":
    main()
