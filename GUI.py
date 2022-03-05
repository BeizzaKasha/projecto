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

class Orientation:
    def __init__(self, x, y, width, height, angle):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.angle = angle


def close():
    logging.error("client close")
    sys.exit()


def built_all(game_obj):
    # image = pygame.image.fromstring(game_obj, (1100, 600), "RGB")  # convert received image from string
    # print(str(game_obj) + " <--do here built for what need how it is on server")
    objects = []
    for obj in game_obj:
        objects.append(pickle.loads(obj))
    sprits = []
    for obj in objects:
        sprit = Demo_print(obj.x, obj.y, obj.width, obj.height, obj.angle, obj.color)
        print(obj.x, obj.y, obj.width, obj.height, obj.angle, obj.color)
        sprits.append(sprit)
    print("///////////////////////////////////////////////////")

    for sprit in sprits:
        screen.blit(sprit.rot_image, sprit.rot_image_rect.topleft)

    """screen.blit(image, (0, 0))  # "show image" on the screen
    pygame.display.update()
    enemies.update()

    for entity in all_sprites:
        screen.blit(entity.rectangle, entity.rect.topleft)

    for player in players:
        screen.blit(player.rot_image, player.rot_image_rect.topleft)

    leaderboard.bilt(game)"""

class Demo_print(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, angle, color):
        super(Demo_print, self).__init__()
        self.rectangle = pygame.Surface((width, height), pygame.SRCALPHA)
        self.rect = self.rectangle.get_rect()
        self.rect.move_ip(x, y)
        self.rectangle.fill(pygame.Color(color))
        self.rot_image = pygame.transform.rotate(self.rectangle, angle)
        self.rot_image_rect = self.rot_image.get_rect(center=self.rect.center)


class Demo(pygame.sprite.Sprite):
    def __init__(self):
        super(Demo, self).__init__()
        self.rectangle = pygame.Surface((24, 24), pygame.SRCALPHA)
        self.rect = self.rectangle.get_rect()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, player):
        super(Enemy, self).__init__()
        self.rectangle = pygame.Surface((10, 10), pygame.SRCALPHA)
        self.rectangle.fill(pygame.Color('white'))
        self.rect = self.rectangle.get_rect()

        self.angle = (player.angle + 90) * math.pi / 180
        self.rect.move_ip(int(player.rect.centerx + 28 * math.cos(self.angle)),
                          int(player.rect.centery - 28 * math.sin(self.angle)))
        self.rot_image = self.rectangle
        self.rot_image_rect = self.rot_image.get_rect(center=self.rect.center)

        self.owner = player
        self.bullet_speed = 10

    def update(self):
        self.rect.move_ip(math.cos(self.angle) * self.bullet_speed, math.sin(self.angle) * -self.bullet_speed)
        self.rot_image_rect = self.rot_image.get_rect(center=self.rect.center)


def teleport(walls):
    demo = Demo()
    t = False
    while not t:
        demo.rect.center = (random.randint(1, 801), random.randint(1, 601))
        if not pygame.sprite.spritecollideany(demo, walls):
            t = True
    new_center = demo.rect.center
    demo.kill()
    return new_center


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.mouse = pygame.mouse
        self.rectangle = pygame.Surface((24, 24), pygame.SRCALPHA)
        self.rectangle.fill(pygame.Color('red'))
        self.rectangle.fill(pygame.Color('white'), (5, 6, 14, 5))
        self.rect = self.rectangle.get_rect()
        self.rot_image = self.rectangle
        self.rot_image_rect = self.rot_image.get_rect(center=self.rect.center)
        self.angle = 0
        self.speed = 8
        self.firing_speed = 15
        self.fire_wait = 120
        self.t_wait = 120
        self.name = "Nadav"
        self.score = 0

    def fire(self):
        new_enemy = Enemy(self)
        return new_enemy

    def set_directangleion(self):
        mx, my = pygame.mouse.get_pos()
        dx, dy = mx - self.rect.centerx, my - self.rect.centery
        self.angle = math.degrees(math.atan2(-dy, dx)) - 90

        self.rot_image = pygame.transform.rotate(self.rectangle, self.angle)
        self.rot_image_rect = self.rot_image.get_rect(center=self.rect.center)


class Walls(pygame.sprite.Sprite):
    def __init__(self):
        super(Walls, self).__init__()
        self.center = (random.randint(1, 801), random.randint(1, 601))
        self.size = (random.randint(50, 201), random.randint(50, 201))
        self.angle = random.randint(0, 4) * 90
        self.rectangle = pygame.Surface(self.size, pygame.SRCALPHA)
        self.rectangle.fill(pygame.Color('dark gray'))
        self.rect = self.rectangle.get_rect()
        self.rect.move_ip(self.center)
        self.rectangle = pygame.transform.rotate(self.rectangle, self.angle)
        self.rect = self.rectangle.get_rect(center=self.rect.center)


class LeaderBoard:
    def __init__(self):
        self.bord = pygame.sprite.Sprite()
        self.bord.rectangle = pygame.Surface((200, 600), pygame.SRCALPHA)
        self.bord.rectangle.fill(pygame.Color('black'))
        self.bord.rect = self.bord.rectangle.get_rect()
        self.bord.rect.move_ip((800, 0))

        self.line = pygame.sprite.Sprite()
        self.line.rectangle = pygame.Surface((8, 600), pygame.SRCALPHA)
        self.line.rectangle.fill(pygame.Color('white'))
        self.line.rect = self.line.rectangle.get_rect()
        self.line.rect.move_ip((800, 0))

        self.txts = []

        self.font = pygame.font.Font('freesansbold.ttf', 32)
        text = self.font.render('leaderboard', True, (255, 0, 0), (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (300 // 2 + 800, 10)
        self.txts.append((text, textRect))

    def set_place(self):
        place = [self.bord, self.line]
        return place

    def change_places(self, players):
        leader_place = 50
        for player in players:
            text = self.font.render(str(player.name) + "           " + str(player.score), True, (255, 0, 0),
                                    (0, 0, 0))
            textRect = text.get_rect()
            textRect.center = (300 // 2 + 800, leader_place)
            self.txts.append((text, textRect))
            leader_place += 50

    def bilt(self):
        for text in self.txts:
            display_surface.blit(text[0], text[1])


def winner(players):
    winner = players.sprites()[0]
    for player in players:
        if winner.score < player.score:
            winner = player
    font = pygame.font.Font('freesansbold.ttf', 60)
    text = font.render(str(winner.name) + " is the winner!!!", True, (255, 10, 150), (0, 0, 0))
    text.set_colorkey((0, 0, 0))
    textRect = text.get_rect()
    textRect.center = (550, 300)
    display_surface.blit(text, textRect)
    print(str(winner.name) + "is the winner!!!")


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
    """game_time = 500"""

    player = Player()
    players = pygame.sprite.Group()
    players.add(player)

    enemies = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()

    for i in range(random.randint(10, 15)):
        wall = Walls()
        all_sprites.add(wall)

    leaderboard = LeaderBoard()
    leaderboard.change_places(players)
    bord, line = leaderboard.set_place()
    all_sprites.add(bord)
    all_sprites.add(line)

    player.rect.center = teleport(all_sprites)

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                """if event.key == pygame.locals.K_q:  # cheat move
                    running = False
                    main()"""
            elif event.type == QUIT:
                running = False

        movement = mov()
        my_socket.send(pickle.dumps(movement))
        # screen.fill((0, 0, 0))

        try:
            lenoflen = int(my_socket.recv(4).decode())
            lenght = int(my_socket.recv(lenoflen).decode())
            print(str(lenght))
            game = my_socket.recv(lenght)
            game = pickle.loads(game)
            # print(game)
            if game == "close":
                print("exit")
                # game = pickle.loads(data)
                # game = data.decode()

        except Exception as e:
            print(str(e) + " <---error")
            close()

        built_all(game)
        pygame.display.flip()

        """pygame.time.delay(15)  # 60 frames per second
        game_time -= 1
        print(game_time)

        if game_time < 0:
            winner(players)

        if game_time == -100:
            running = False
            main()"""

        pygame.display.flip()


if __name__ == "__main__":
    main()
