import select
import logging
import socket
import pickle
import sys

import pygame
import random
import math

logging.basicConfig(level=logging.DEBUG)


class server:
    def __init__(self):
        self.game = Game()
        self.SERVER_PORT = 5555
        self.SERVER_IP = '0.0.0.0'
        logging.debug("Setting up server...")
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.SERVER_IP, self.SERVER_PORT))
        self.server_socket.listen()
        logging.info("Listening for clients...")
        self.client_sockets = []
        self.messages_to_send = []
        self.number_of_client = 0
        self.max_clients = 10
        self.players_conection = {}

    def print_client_sockets(self, client_sockets):
        for i in range(len(client_sockets)):
            logging.debug(client_sockets[i])

    def newclient(self, me, current_socket, client_sockets, players):
        connection, client_address = current_socket.accept()
        logging.info("New client joined!")
        client_sockets.append(connection)
        self.print_client_sockets(client_sockets)
        player = Game.Player()
        players.add(player)
        me.players_conection[player] = connection
        me.players_conection[connection] = player

        player.rect.center = self.game.teleport(self.game.all_sprites)
        self.game.leaderboard.change_places(self.game.players)

    def client_mesege(self, current_socket):
        try:
            rsv = current_socket.recv(1024)  # get the client messege, do what ever u want with it--->
            rsv = pickle.loads(rsv)
        except:
            logging.error("problem with resiving a message: " + str(current_socket))
            rsv = "quit"
        return rsv

    def get_from_clients(self, rlist, players):
        players_movement = []
        mov_makers = []
        for current_socket in rlist:
            if current_socket is self.server_socket:  # new client joins
                if self.max_clients - self.number_of_client > 0:
                    self.newclient(self, current_socket, self.client_sockets, players)  # create new client
                    self.number_of_client += 1
                    print("players left to join: " + str(self.max_clients - self.number_of_client))
                else:
                    connection, client_address = current_socket.accept()
                    connection.send("cant connect".encode())
                    self.player_quit(self.client_sockets, current_socket, players)
            else:  # what to do with client
                move = self.client_mesege(current_socket)
                if move == "quit":
                    self.player_quit(self.client_sockets, current_socket, players)
                else:
                    players_movement.append(move)
                    self.players_conection[move] = current_socket
                    mov_makers.append(current_socket)
        return players_movement, mov_makers

    def make_messeges(self, rlist, players, enemies, all_sprites, LeaderBoard):
        for current_socket in rlist:
            bit_mesege = []
            for player in players:
                bit_mesege.append(player.Serialize())
            for bullet in enemies:
                bit_mesege.append(bullet.Serialize())
            for wall in all_sprites:
                bit_mesege.append(wall.Serialize())
            for i in range(len(LeaderBoard.txts)):
                bit_mesege.append(LeaderBoard.Serialize(i))
            self.messages_to_send.append((current_socket, pickle.dumps(bit_mesege)))

    def player_quit(self, client_sockets, current_socket, players):
        print(str(current_socket) + " left")
        players.remove(self.players_conection[current_socket])
        current_socket.shutdown(socket.SHUT_RDWR)
        current_socket.close()
        client_sockets.remove(current_socket)

    def sending(self, mov_makers):
        self.make_messeges(mov_makers, self.game.players, self.game.enemies, self.game.all_sprites,
                           self.game.leaderboard)

        for message in self.messages_to_send:
            current_socket, data = message
            # if current_socket in wlist:
            try:
                current_socket.send(str(len(str(len(data)))).zfill(4).encode() + str(len(data)).encode() + data)
                self.messages_to_send.remove(message)
            except Exception as e:
                logging.error("problem with sending a message: " + str(current_socket))

    def colisions(self, game):
        hit = pygame.sprite.Group()
        for bullet in game.enemies:
            bullet.mov()
            if pygame.sprite.spritecollideany(bullet,
                                              game.all_sprites) or 1000 < bullet.rect.x or bullet.rect.x < 0 or 800 < bullet.rect.y or bullet.rect.y < 0:
                bullet.kill()
            elif pygame.sprite.spritecollideany(bullet, game.players):
                bullet.owner.score += 1
                hit.add(bullet)
                game.leaderboard.change_places(game.players)

        for player in game.players:
            if pygame.sprite.spritecollideany(player, hit):
                player.rect.center = game.teleport(game.all_sprites)

        for bullet in hit:
            bullet.kill()
        del hit

    def gamerun(self):

        running = True

        while running:
            rlist, wlist, xlist = select.select([self.server_socket] + self.client_sockets, [], [])
            player_movement, mov_makers = self.get_from_clients(rlist, self.game.players)

            if self.game.game_time > 0:
                for movement in player_movement:
                    try:
                        current_sucket = self.players_conection.pop(movement)
                        current_player = self.players_conection[current_sucket]
                        look = movement[2]
                        fire = movement[1]
                        move = movement[0]
                        self.game.Player.set_directangleion(current_player, look)
                        val = self.game.Player.mov(current_player, self.game.all_sprites, move, fire)
                        if val != "successful":
                            self.game.enemies.add(val)
                    except Exception as e:
                        print(str(e) + " <---error")

            self.colisions(self.game)

            pygame.time.delay(15)  # 60 frames per second
            self.game.game_time -= 1
            # print(self.game.game_time)

            if self.game.game_time == 0:
                self.game.leaderboard.winner(self.game.players)
                # print("time's over")

            if self.game.game_time == -200:
                running = False

            self.sending(mov_makers)


class Game:
    def __init__(self):
        self.game_time = 500
        self.SCREEN_WIDTH = 1100
        self.SCREEN_HEIGHT = 600

        self.players = pygame.sprite.Group()

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
            self.bullet_speed = 12

            self.orientation = Orientation(self.rect.x, self.rect.y, self.rect.width, self.rect.height, self.angle,
                                           'white', "")

        def mov(self):
            self.rect.move_ip(math.cos(self.angle) * self.bullet_speed, math.sin(self.angle) * -self.bullet_speed)
            self.rot_image_rect = self.rot_image.get_rect(center=self.rect.center)
            self.orientation.x = self.rect.x
            self.orientation.y = self.rect.y

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

    def restart(self):
        self.game_time = 500
        self.all_sprites.empty()
        self.enemies.empty()
        for i in range(random.randint(10, 15)):
            wall = Game.Walls()
            self.all_sprites.add(wall)

        self.leaderboard = Game.LeaderBoard()
        self.leaderboard.change_places(self.players)
        bord, line = self.leaderboard.set_place()
        self.all_sprites.add(bord)
        self.all_sprites.add(line)

        for player in self.players:
            player.rect.center = self.teleport(self.all_sprites)

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
                                           'red', "")

        def Serialize(self):
            return pickle.dumps(self.orientation)

        def fire(self):
            new_enemy = Game.Enemy(self)
            return new_enemy

        def set_directangleion(self, look):
            mx, my = look
            dx, dy = mx - self.rect.centerx, my - self.rect.centery
            self.angle = math.degrees(math.atan2(-dy, dx)) - 90

            self.rot_image = pygame.transform.rotate(self.rectangle, self.angle)
            self.rot_image_rect = self.rot_image.get_rect(center=self.rect.center)

        def mov(self, walls, player_movement, fire):
            val = "successful"
            if player_movement == 'w' and not self.rect.top - self.rect.height / 3 < 0:
                self.rect.move_ip(0, -self.speed)
                if pygame.sprite.spritecollideany(self, walls):
                    self.rect.move_ip(0, self.speed)
            if player_movement == 's' and not self.rect.bottom + self.rect.height / 3 > 600:
                self.rect.move_ip(0, self.speed)
                if pygame.sprite.spritecollideany(self, walls):
                    self.rect.move_ip(0, -self.speed)
            if player_movement == 'a' and not (self.rect.left - self.rect.width / 3 < 0):
                self.rect.move_ip(-self.speed, 0)
                if pygame.sprite.spritecollideany(self, walls):
                    self.rect.move_ip(self.speed, 0)
            if player_movement == 'd' and not (self.rect.right + self.rect.width / 3 > 800):
                self.rect.move_ip(self.speed, 0)
                if pygame.sprite.spritecollideany(self, walls):
                    self.rect.move_ip(-self.speed, 0)
            if fire == 'fire' and self.fire_wait <= 0:
                val = self.fire()
                self.fire_wait = 60

            if self.fire_wait > 0:
                self.fire_wait -= self.firing_speed

            self.orientation.x = self.rect.x
            self.orientation.y = self.rect.y
            self.orientation.angle = self.angle
            return val

    class Walls(pygame.sprite.Sprite):
        def __init__(self):
            super(Game.Walls, self).__init__()
            self.center = (random.randint(1, 801), random.randint(1, 601))
            self.size = (random.randint(50, 201), random.randint(50, 201))
            self.rectangle = pygame.Surface(self.size, pygame.SRCALPHA)
            self.rectangle.fill(pygame.Color('dark gray'))
            self.rect = self.rectangle.get_rect()
            self.rect.move_ip(self.center)
            self.rect = self.rectangle.get_rect(center=self.rect.center)
            self.orientation = Orientation(self.rect.x, self.rect.y, self.rect.width, self.rect.height, 0,
                                           'gray', "")

        def Serialize(self):
            return pickle.dumps(self.orientation)

    class LeaderBoard:
        def __init__(self):
            self.bord = self.Block((800, 0), (200, 600), 'black')
            self.line = self.Block((800, 0), (8, 600), 'white')

            self.txts = []

            self.font = pygame.font.Font('freesansbold.ttf', 32)

        def set_place(self):
            place = [self.bord, self.line]
            return place

        def change_places(self, players):
            self.txts.clear()

            text = self.font.render('leaderboard', True, (255, 0, 0), (0, 0, 0))
            text_name = "leaderboard"
            textRect = text.get_rect()
            textRect.center = (300 // 2 + 800, 10)
            self.txts.append((text_name, textRect))

            leader_place = 50
            for player in players:
                text = self.font.render(str(player.name) + "           " + str(player.score), True, (255, 0, 0),
                                        (0, 0, 0))
                text_name = str(player.name) + "           " + str(player.score)
                textRect = text.get_rect()
                textRect.center = (300 // 2 + 800, leader_place)
                self.txts.append((text_name, textRect))
                leader_place += 50

        """def bilt(self, game):
            for text in self.txts:
                game.display_surface.blit(text[0], text[1])"""

        def Serialize(self, num):
            orientation = Orientation(self.txts[num][1].x, self.txts[num][1].y, self.txts[num][1].width,
                                      self.txts[num][1].height, 0, 'white', self.txts[num][0])
            return pickle.dumps(orientation)

        class Block(pygame.sprite.Sprite):
            def __init__(self, place, size, color):
                super(Game.LeaderBoard.Block, self).__init__()
                self.rectangle = pygame.Surface(size, pygame.SRCALPHA)
                self.rectangle.fill(pygame.Color(color))
                self.rect = self.rectangle.get_rect()
                self.rect.move_ip(place)
                self.orientation = Orientation(self.rect.x, self.rect.y, self.rect.width,
                                               self.rect.height, 0, color, "")

            def Serialize(self):
                return pickle.dumps(self.orientation)

        def winner(self, players):
            winner = players.sprites()[0]
            for player in players:
                if winner.score < player.score:
                    winner = player
            font = pygame.font.Font('freesansbold.ttf', 100)
            text = font.render(str(winner.name) + " is the winner!!!", True, (255, 10, 150), (0, 0, 0))
            text_name = str(winner.name) + " is the winner!!!"
            text.set_colorkey((0, 0, 0))
            textRect = text.get_rect()
            textRect.center = (550, 300)
            self.txts.append((text_name, textRect))


class Orientation:
    def __init__(self, x, y, width, height, angle, color, name):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.angle = angle
        self.color = color
        self.name = name


def game_maker(me):
    me.gamerun()

    me.game.restart()


def main():
    pygame.init()
    me = server()

    while True:
        game_maker(me)


if __name__ == "__main__":
    main()
