import json

import select
import logging
import socket
import pickle
import sys

import pygame
import random
import math

SERVER_PORT = 5555
SERVER_IP = '0.0.0.0'

logging.basicConfig(level=logging.DEBUG)


class Game:
    def __init__(self):
        self.game_time = 500
        self.SCREEN_WIDTH = 1100
        self.SCREEN_HEIGHT = 600
        """pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.display_surface = pygame.display.set_mode((1000, 20))
        pygame.display.set_caption('Show Text')"""
        # self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

        self.players = pygame.sprite.Group()
        self.players_list = []

        self.enemies = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()

        for i in range(random.randint(10, 15)):
            wall = Game.Walls()
            self.all_sprites.add(wall)

        self.leaderboard = Game.LeaderBoard()
        self.leaderboard.change_places(self.players)
        bord, line = self.leaderboard.set_place()
        self.all_sprites.add(bord)
        self.all_sprites.add(line)

    class Demo(pygame.sprite.Sprite):
        def __init__(self):
            super(Game.Demo, self).__init__()
            self.rectangle = pygame.Surface((24, 24), pygame.SRCALPHA)
            self.rect = self.rectangle.get_rect()

    class Enemy(pygame.sprite.Sprite):
        def __init__(self, player):
            super(Game.Enemy, self).__init__()
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

            self.orientation = Orientation(self.rect.x, self.rect.y, self.rect.width, self.rect.height, self.angle,
                                           'white')

        def update(self):
            self.rect.move_ip(math.cos(self.angle) * self.bullet_speed, math.sin(self.angle) * -self.bullet_speed)
            self.rot_image_rect = self.rot_image.get_rect(center=self.rect.center)

        def Serialize(self):
            return pickle.dumps(self.orientation)

    def teleport(self, walls):
        demo = Game.Demo()
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
            super(Game.Player, self).__init__()
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
            self.name = str(random.randint(1, 20))
            self.score = 0
            self.orientation = Orientation(self.rect.x, self.rect.y, self.rect.width, self.rect.height, self.angle,
                                           'red')

        def Serialize(self):
            print("red")
            return pickle.dumps(self.orientation)

        def fire(self, game):
            new_enemy = game.Enemy(self)
            return new_enemy

        def set_directangleion(self, look):
            mx, my = look
            dx, dy = mx - self.rect.centerx, my - self.rect.centery
            self.angle = math.degrees(math.atan2(-dy, dx)) - 90

            self.rot_image = pygame.transform.rotate(self.rectangle, self.angle)
            self.rot_image_rect = self.rot_image.get_rect(center=self.rect.center)

        def mov(self, walls, game, player_movement, fire):
            val = "successful"
            if player_movement == 'w' and not self.rect.top - self.rect.height / 3 < 0:
                self.rect.move_ip(0, -self.speed)
                if pygame.sprite.spritecollideany(self, walls):
                    self.rect.move_ip(0, self.speed)
            if player_movement == 's' and not self.rect.bottom + self.rect.height / 3 > game.SCREEN_HEIGHT:
                self.rect.move_ip(0, self.speed)
                if pygame.sprite.spritecollideany(self, walls):
                    self.rect.move_ip(0, -self.speed)
            if player_movement == 'a' and not (self.rect.left - self.rect.width / 3 < 0):
                self.rect.move_ip(-self.speed, 0)
                if pygame.sprite.spritecollideany(self, walls):
                    self.rect.move_ip(self.speed, 0)
            if player_movement == 'd' and not (self.rect.right + self.rect.width / 3 > game.SCREEN_WIDTH):
                self.rect.move_ip(self.speed, 0)
                if pygame.sprite.spritecollideany(self, walls):
                    self.rect.move_ip(-self.speed, 0)
            if fire == 'fire' and self.fire_wait <= 0:
                val = self.fire(game)
                self.fire_wait = 60

            if self.fire_wait > 0:
                self.fire_wait -= self.firing_speed
            return val

    class Walls(pygame.sprite.Sprite):
        def __init__(self):
            super(Game.Walls, self).__init__()
            self.center = (random.randint(1, 801), random.randint(1, 601))
            self.size = (random.randint(50, 201), random.randint(50, 201))
            self.angle = random.randint(0, 4) * 90
            self.rectangle = pygame.Surface(self.size, pygame.SRCALPHA)
            self.rectangle.fill(pygame.Color('dark gray'))
            self.rect = self.rectangle.get_rect()
            self.rect.move_ip(self.center)
            self.rectangle = pygame.transform.rotate(self.rectangle, self.angle)
            self.rect = self.rectangle.get_rect(center=self.rect.center)
            self.orientation = Orientation(self.rect.x, self.rect.y, self.rect.width, self.rect.height, self.angle,
                                           'gray')

        def Serialize(self):
            return pickle.dumps(self.orientation)

    class LeaderBoard:
        def __init__(self):

            self.bord = self.block((800, 0), (200, 600), 'black')
            self.line = self.block((800, 0), (8, 600), 'gray')

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

        def bilt(self, game):
            for text in self.txts:
                game.display_surface.blit(text[0], text[1])

        class block(pygame.sprite.Sprite):
            def __init__(self, size, place, color):
                super(Game.LeaderBoard.block, self).__init__()
                # self.bord = pygame.sprite.Sprite()
                self.rectangle = pygame.Surface(size, pygame.SRCALPHA)
                self.rectangle.fill(pygame.Color(color))
                self.rect = self.rectangle.get_rect()
                self.rect = self.rectangle.get_rect()
                self.rect.move_ip(place)
                self.orientation = Orientation(self.rect.x, self.rect.y, self.rect.width,
                                               self.rect.height, 0, color)

            def Serialize(self):
                return pickle.dumps(self.orientation)

    def winner(self, players):
        winner = players.sprites()[0]
        for player in players:
            if winner.score < player.score:
                winner = player
        font = pygame.font.Font('freesansbold.ttf', 60)
        text = font.render(str(winner.name) + " is the winner!!!", True, (255, 10, 150), (0, 0, 0))
        text.set_colorkey((0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (550, 300)
        self.display_surface.blit(text, textRect)
        print(str(winner.name) + "is the winner!!!")


class Orientation:
    def __init__(self, x, y, width, height, angle, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.angle = angle
        self.color = color


def print_client_sockets(client_sockets):
    for i in range(len(client_sockets)):
        logging.debug(client_sockets[i])


def newclient(current_socket, client_sockets, players, players_list, game):
    connection, client_address = current_socket.accept()
    logging.info("New client joined!")
    client_sockets.append(connection)
    print_client_sockets(client_sockets)
    player = Game.Player()
    # players.add(player)
    # players_list.append((current_socket, player))
    players_conection[player] = connection
    players_conection[connection] = player

    player.rect.center = game.teleport(game.all_sprites)


def client_mesege(current_socket):
    rsv = "null"
    try:
        rsv = current_socket.recv(1024)  # get the client messege, do what ever u want with it--->
        rsv = pickle.loads(rsv)
        # print("rsv: " + str(rsv))
    except:
        print("a problem accrued")
    return rsv


def get_from_clients(rlist, number_of_client, max_clients, players, players_list, game):
    players_movement = []
    for current_socket in rlist:
        # players_movement.append(current_socket)
        if current_socket is server_socket:  # new client joins
            if max_clients - number_of_client > 0:
                newclient(current_socket, client_sockets, players, players_list, game)  # create new client
                number_of_client += 1
                # players_movement.append("new guy")
                print("players left to join: " + str(max_clients - number_of_client))
            else:
                connection, client_address = current_socket.accept()
                connection.send("cant connect".encode())
                connection.shutdown(socket.SHUT_RDWR)
                connection.close()
                # players_movement.append("guy left")
        else:  # what to do with client
            move = client_mesege(current_socket)
            players_movement.append(move)
            players_conection[move] = current_socket
    return players_movement


def make_messeges(rlist, players, enemies, all_sprites):
    for current_socket in rlist:
        bit_mesege = []
        for player in players:
            bit_mesege.append(player.Serialize())
        for bullet in enemies:
            bit_mesege.append(bullet.Serialize())
        for wall in all_sprites:
            bit_mesege.append(wall.Serialize())
        messages_to_send.append((current_socket, pickle.dumps(bit_mesege)))


logging.debug("Setting up server...")
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen()
logging.info("Listening for clients...")
client_sockets = []
messages_to_send = []
number_of_client = 0
max_clients = 2
players_conection = {}


# place for parameters

def main():
    pygame.init()
    game = Game()

    running = True

    while running:
        rlist, wlist, xlist = select.select([server_socket] + client_sockets, client_sockets, [])
        player_movement = get_from_clients(rlist, number_of_client, max_clients, game.players, game.players_list, game)

        if game.game_time > 0:
            # current_mov = ""
            # print("player list: " + str(game.players_list))
            for movement in player_movement:
                # try:
                print(players_conection)
                current_sucket = players_conection.pop(movement)
                current_player = players_conection[current_sucket]
                look = movement[2]
                fire = movement[1]
                move = movement[0]
                print(look, move)
                game.Player.set_directangleion(current_player, look)
                val = game.Player.mov(current_player, game.all_sprites, game, move, fire)
                if val != "successful":
                    game.enemies.add(val)
                """except Exception as e:
                    # i = 1
                    print(str(e) + " <---error")"""

            """ game.enemies.update()

        for entity in game.all_sprites:
            game.screen.blit(entity.rectangle, entity.rect.topleft)
        for player in game.players:
            game.screen.blit(player.rot_image, player.rot_image_rect.topleft)"""

        for bullet in game.enemies:
            # pygame.draw.circle(game.screen, (255, 255, 255), (bullet.rot_image_rect.x, bullet.rot_image_rect.y), 5)
            if pygame.sprite.spritecollideany(bullet, game.all_sprites):
                bullet.kill()
            elif pygame.sprite.spritecollideany(bullet, game.players):
                for player in game.players:
                    if bullet.owner == player:
                        player.score += 1
                        player.rect.center = game.teleport(game.all_sprites)
                bullet.kill()
                game.leaderboard.change_places(game.players)

        # game.leaderboard.bilt(game)

        pygame.time.delay(15)  # 60 frames per second
        """game.game_time -= 1"""
        # print(game.game_time)

        if game.game_time < 0:
            # game.winner(game.players)
            print("time's over")

        if game.game_time == -100:
            running = False
            main()

        # pygame.display.flip()
        make_messeges(rlist, game.players, game.enemies, game.all_sprites)

        for message in messages_to_send:
            current_socket, data = message
            if current_socket in wlist:
                # print(str(len(str(len(data)))).zfill(4) + "    " + str(len(data)))
                current_socket.send(str(len(str(len(data)))).zfill(4).encode() + str(len(data)).encode() + data)
                messages_to_send.remove(message)

    sys.exit()


if __name__ == "__main__":
    main()
