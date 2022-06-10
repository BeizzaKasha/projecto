import time
import select
import logging
import socket
import pickle
import sys
from Constants import constant
import hashlib
import pygame
import random
import math

logging.basicConfig(level=logging.DEBUG)


class ClientSide:
    def __init__(self, server_port, server_ip, max_clients, database_ip):
        self.my_socket = socket.socket()
        ip = database_ip
        port = 7777
        logging.debug("connected ot " + str(ip) + "," + str(port))
        self.my_socket.connect((ip, port))
        self.send(pickle.dumps((constant.NEW_GAMESERVER, server_port, server_ip.encode(), max_clients)))
        self.read()

    def send(self, data):
        self.my_socket.send(str(len(str(len(data)))).zfill(4).encode() + str(len(data)).encode() + data)

    def read(self):
        try:
            lenoflen = int(self.my_socket.recv(4).decode())
            lenght = int(self.my_socket.recv(lenoflen).decode())
            data = self.my_socket.recv(lenght)
            data = pickle.loads(data)
            return data
        except Exception as e:
            logging.error(e)

    def make_message(self, players, quiters, space):
        stats = [constant.GAMESERVER_UPDATE, space]
        print("sending")
        for player in players:
            stats.append((player.name, player.score))
        for player in quiters:
            stats.append((player.name, player.score))
        return stats

    def run(self, players, quiters, space):
        stats = self.make_message(players, quiters, space)
        self.send(pickle.dumps(stats))
        self.read()

    def close(self, players, quiters, space):
        stats = self.make_message(players, quiters, space)
        self.send(pickle.dumps(stats))
        self.read()
        self.send(pickle.dumps((constant.SERVER_QUIT, constant.QUITING)))


class ServerSide:
    def __init__(self, database_ip):
        self.game = Game()
        self.SERVER_PORT = 55555
        self.SERVER_IP = str(socket.gethostname())
        logging.debug("Setting up server...")
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.SERVER_IP, self.SERVER_PORT))
        self.server_socket.listen()
        self.max_clients = 5
        self.client_side = ClientSide(self.SERVER_PORT, self.SERVER_IP, self.max_clients, database_ip)
        self.client_sockets = []
        self.messages_to_send = []
        self.number_of_client = 0
        self.players_conection = {}
        self.active = False

    def game_maker(self):
        while True:
            logging.info("new game start")
            self.gamerun()
            self.game.restart()

    def close_server(self):
        self.client_side.close(self.game.players, self.game.quiters, self.max_clients - self.number_of_client)
        sys.exit()

    def print_client_sockets(self, client_sockets):
        for i in range(len(client_sockets)):
            logging.debug("""   """ + str(client_sockets[i]))

    def newclient(self, current_socket, client_sockets):
        connection, client_address = current_socket.accept()
        logging.info("New client joined:")
        client_sockets.append(connection)
        self.print_client_sockets(client_sockets)
        player = Game.Player()
        self.game.players.add(player)
        self.players_conection[player] = connection
        self.players_conection[connection] = player
        self.number_of_client += 1
        self.active = True

        player.rect.center = self.game.teleport(self.game.all_sprites)
        self.game.leaderboard.change_places(self.game.players)

    def change_client_name(self, current_socket, name):
        player = self.players_conection[current_socket]
        player.change_name(name)

    def client_mesege(self, current_socket):
        rsv = ""
        try:
            lenoflen = int(current_socket.recv(4).decode())
            lenght = int(current_socket.recv(lenoflen).decode())
            rsv = current_socket.recv(lenght)
            rsv = pickle.loads(rsv)
            # print(rsv)
        except:
            logging.error("problem with resiving a message: " + str(current_socket))
            rsv = constant.QUITING
        finally:
            return rsv

    def get_from_clients(self, rlist):
        players_movement = []
        for current_socket in rlist:
            if current_socket is self.server_socket:  # new client joins
                if self.max_clients - self.number_of_client > 0:
                    self.newclient(current_socket, self.client_sockets)  # create new client
                    logging.info("    players left to join: " + str(self.max_clients - self.number_of_client))
                else:
                    connection, client_address = current_socket.accept()
                    connection.send("cant connect".encode())
                    self.player_quit(current_socket)
            else:  # what to do with client
                move = self.client_mesege(current_socket)
                if move == constant.QUITING:
                    self.player_quit(current_socket)
                elif move[0] == constant.USER_CONNECTING:  # user just connected
                    date = time.localtime()
                    minute_now = str(
                        hashlib.md5((str(date[3]).zfill(2) + ":" + str(date[4]).zfill(2)).encode()).digest())
                    minute_plus_one = str(
                        hashlib.md5((str(date[3]).zfill(2) + ":" + str(int(date[4] + 1)).zfill(2)).encode()).digest())
                    print(move[1].decode(), minute_now)
                    print(move[2].decode(), minute_plus_one)
                    if move[1] != minute_now.decode() and move[2] != minute_plus_one.decode():
                        logging.debug("wrong client")
                        self.player_quit(current_socket)
                elif move[0] == constant.USER_ACTION:  # user input
                    self.change_client_name(current_socket, move[1])
                    players_movement.append((move[2], current_socket))
                    self.players_conection[move[2]] = current_socket
        return players_movement

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
            self.messages_to_send.append((current_socket[1], pickle.dumps(bit_mesege)))

    def player_quit(self, current_socket):
        logging.info(str(current_socket) + " left")
        player = self.players_conection[current_socket]
        self.game.quiters.add(player)
        self.game.players.remove(player)
        self.players_conection.pop(current_socket)
        current_socket.shutdown(socket.SHUT_RDWR)
        current_socket.close()
        self.client_sockets.remove(current_socket)
        self.number_of_client -= 1
        if self.active and self.number_of_client == 0:
            self.close_server()

    def sending(self, mov_makers):
        self.make_messeges(mov_makers, self.game.players, self.game.enemies, self.game.all_sprites,
                           self.game.leaderboard)

        for message in self.messages_to_send:
            current_socket, data = message
            try:
                current_socket.send(str(len(str(len(data)))).zfill(4).encode() + str(len(data)).encode() + data)
                self.messages_to_send.remove(message)
            except Exception as e:
                logging.error("problem with sending a message: " + str(current_socket))

    def gamerun(self):
        running = True

        while running:
            rlist, wlist, xlist = select.select([self.server_socket] + self.client_sockets, [], [])
            player_movement = self.get_from_clients(rlist)

            if self.game.game_time > 0:
                for movement in player_movement:
                    try:
                        current_sucket = movement[1]
                        the_move = movement[0]
                        current_player = self.players_conection[current_sucket]
                        look = the_move[2]
                        fire = the_move[1]
                        move = the_move[0]
                        self.game.Player.set_directangleion(current_player, look)
                        val = self.game.Player.mov(current_player, self.game.all_sprites, move, fire)
                        if val != "successful":
                            self.game.enemies.add(val)
                    except Exception as e:
                        print(str(e) + " <---error")

            self.game.colisions()

            pygame.time.delay(10)
            self.game.game_time -= 1

            if self.game.game_time == 0:
                self.client_side.run(self.game.players, self.game.quiters, self.max_clients - self.number_of_client)

            if self.game.game_time <= 0:
                self.game.leaderboard.winner(self.game.players)

            if self.game.game_time == -300:
                running = False

            self.sending(player_movement)


class Game:
    def __init__(self):
        self.game_time = 2000
        self.SCREEN_WIDTH = 1100
        self.SCREEN_HEIGHT = 600

        self.players = pygame.sprite.Group()
        self.quiters = pygame.sprite.Group()

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

    def restart(self):
        self.game_time = 2000
        self.all_sprites.empty()
        self.enemies.empty()
        for i in range(random.randint(10, 15)):
            wall = Game.Walls()
            self.all_sprites.add(wall)

        for player in self.players:
            player.score = 0
            player.rect.center = self.teleport(self.all_sprites)

        self.leaderboard = Game.LeaderBoard()
        self.leaderboard.change_places(self.players)
        bord, line = self.leaderboard.set_place()
        self.all_sprites.add(bord)
        self.all_sprites.add(line)

    class Enemy(pygame.sprite.Sprite):
        def __init__(self, player):
            super(Game.Enemy, self).__init__()
            self.rectangle = pygame.Surface((10, 10), pygame.SRCALPHA)
            self.rectangle.fill(pygame.Color('white'))
            self.rect = self.rectangle.get_rect()

            self.angle = math.radians(player.angle - 90)
            self.rect.center = (int(player.rect.centerx + 10 * math.cos(self.angle)),
                                int(player.rect.centery - 10 * math.sin(self.angle)))
            # ^^^in case I make bullet not move:
            # bullet will hit the shooter, because I usually move the bullet before checking for coalition!
            self.rot_image = self.rectangle
            self.rot_image_rect = self.rot_image.get_rect(center=self.rect.center)

            self.owner = player
            self.bullet_speed = 15

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
            self.firing_speed = 6
            self.fire_wait = 120
            self.t_wait = 120
            self.name = "none"
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
            self.angle = math.degrees(math.atan2(-dy, dx)) + 90

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

        def change_name(self, name):
            self.name = name
            self.orientation.name = "0," + str(name)

    def colisions(self):
        self.leaderboard.change_places(self.players)
        hit = pygame.sprite.Group()
        for bullet in self.enemies:
            bullet.mov()
            if pygame.sprite.spritecollideany(bullet,
                                              self.all_sprites) or 1000 < bullet.rect.x or bullet.rect.x < 0 or 800 < bullet.rect.y or bullet.rect.y < 0:
                bullet.kill()
            elif pygame.sprite.spritecollideany(bullet, self.players):
                bullet.owner.score += 1
                hit.add(bullet)

        for player in self.players:
            if pygame.sprite.spritecollideany(player, hit):
                player.rect.center = self.teleport(self.all_sprites)

        for bullet in hit:
            bullet.kill()
        del hit

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

            self.font = pygame.font.Font("C:\Windows\Fonts\Arial.ttf", 32)

        def set_place(self):
            place = [self.bord, self.line]
            return place

        def change_places(self, players):
            self.txts.clear()

            text = self.font.render('leaderboard', True, (255, 0, 0), (0, 0, 0))
            text_name = "leaderboard"
            textRect = text.get_rect()
            textRect.center = (920, 15)
            self.txts.append((text_name, textRect, 40, 'white'))

            leader_place = 75
            for player in players:
                space = " "
                for i in range(16 - len(str(player.name)) - len(str(player.score))):
                    space += " "
                text_name = str(player.name) + space + str(player.score)
                text = self.font.render(text_name, True, (255, 0, 0),
                                        (0, 0, 0))
                textRect = text.get_rect()
                textRect.center = (300 // 2 + 800, leader_place)
                self.txts.append((text_name, textRect, 30, 'white'))
                leader_place += 50

        def Serialize(self, num):
            orientation = Orientation(self.txts[num][1].x, self.txts[num][1].y, self.txts[num][1].width,
                                      self.txts[num][1].height, self.txts[num][2], self.txts[num][3], self.txts[num][0])
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
            if len(players) != 0:
                winner = players.sprites()[0]
                for player in players:
                    if winner.score < player.score:
                        winner = player
                color = (255, 215, 0)
                size = 60
                font = pygame.font.Font("C:\Windows\Fonts\Arial.ttf", size)
                text = font.render(str(winner.name) + " is the winner!!!", True, color)
                text_name = str(winner.name) + " is the winner!!!"
                textRect = text.get_rect()
                textRect.center = (450, 300)
                self.txts.append((text_name, textRect, size, color))


class Orientation:
    def __init__(self, x, y, width, height, angle, color, name):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.angle = angle
        self.color = color
        self.name = name


def starting(database_ip, *args):
    print("extras=> ")
    for arg in args:
        print(arg)
    pygame.init()
    try:
        me = ServerSide(database_ip)
        me.game_maker()
    except Exception as e:
        logging.error(f" game server running problem: {e.with_traceback()}")
        pygame.quit()


def main():
    starting(str(socket.gethostname()))


if __name__ == "__main__":
    main()
