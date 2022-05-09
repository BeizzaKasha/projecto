import select
import logging
import socket
import pickle
import sys
import time

import pygame
import random
import math

logging.basicConfig(level=logging.DEBUG)


class ClientSide:
    def __init__(self, server_port, server_ip,  max_clients):
        self.my_socket = socket.socket()
        ip = "127.0.0.1"
        port = 6666
        self.my_socket.connect((ip, port))
        self.send(pickle.dumps([2, server_port, server_ip.encode(),  max_clients]))
        logging.debug("client side connected...")

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

    def make_message(self, game, space):
        stats = [0, space]
        print("sending")
        date = time.localtime()[0:-4]
        update_date = str(date[0]) + "/" + str(date[1]) + "/" + str(date[2]) + " " + str(date[3]) + ":" + str(date[4])
        for player in game.players:
            stats.append((player.name, player.password, "Nadav", update_date,
                          player.score / ((game.round_time * (10 / 1000)) / 60), True))
        for player in game.quiters:
            stats.append((player.name, player.password, "Nadav", update_date,
                          player.score / ((game.round_time * (10 / 1000)) / 60), False))
            # ((game.game_time * (10 / 1000)) / 60) = time of round in minutes
        return stats

    def run(self, game, space):
        stats = self.make_message(game, space)
        self.send(pickle.dumps(stats))
        self.read()

    def close(self, game, space):
        stats = self.make_message(game, space)
        self.send(pickle.dumps(stats))
        self.read()
        self.send(pickle.dumps(99))


class server:
    def __init__(self):
        self.game = Game()
        self.SERVER_PORT = 5555
        self.SERVER_IP = '0.0.0.0'
        logging.debug("Setting up server...")
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.SERVER_IP, self.SERVER_PORT))
        self.server_socket.listen()
        self.max_clients = 10
        self.client_side = ClientSide(self.SERVER_PORT, self.SERVER_IP, self.max_clients)
        self.client_sockets = []
        self.messages_to_send = []
        self.number_of_client = 0
        self.players_conection = {}
        self.active = False # subprocess.popen

    def game_maker(self):
        while True:
            self.gamerun()
            self.game.restart()

    def close_server(self):
        self.client_side.close(self.game, self.max_clients - self.number_of_client)
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
        # print(name, player.name)
        player.name = name

    def client_mesege(self, current_socket):
        try:
            rsv = current_socket.recv(1024)  # get the client messege, do what ever u want with it--->
            rsv = pickle.loads(rsv)
        except:
            logging.error("problem with resiving a message: " + str(current_socket))
            rsv = "quit"
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
                if move == "quit":
                    self.player_quit(current_socket)
                else:
                    self.change_client_name(current_socket, move[0])
                    players_movement.append((move[1], current_socket))
                    self.players_conection[move[1]] = current_socket
                    # mov_makers.append(current_socket)
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
        left = self.players_conection[current_socket]
        self.game.quiters.add(left)
        self.game.players.remove(left)
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

            if self.game.game_time <= 0:
                self.game.leaderboard.winner(self.game.players)

            if self.game.game_time == -300:
                self.client_side.run(self.game, self.max_clients - self.number_of_client)
                running = False

            self.sending(player_movement)


class Game:
    def __init__(self):
        self.game_time = 2000
        self.round_time = self.game_time
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
        self.game_time = 500
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
            self.bullet_speed = 14

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
            self.password = "none"
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

            self.font = pygame.font.Font('freesansbold.ttf', 32)

        def set_place(self):
            place = [self.bord, self.line]
            return place

        def change_places(self, players):
            self.txts.clear()

            text = self.font.render('leaderboard', True, (255, 0, 0), (0, 0, 0))
            text_name = "leaderboard"
            textRect = text.get_rect()
            textRect.center = (920, 10)
            self.txts.append((text_name, textRect, 40, 'white'))

            leader_place = 70
            for player in players:
                text = self.font.render(str(player.name) + "           " + str(player.score), True, (255, 0, 0),
                                        (0, 0, 0))
                text_name = str(player.name) + "           " + str(player.score)
                textRect = text.get_rect()
                textRect.center = (300 // 2 + 800, leader_place)
                self.txts.append((text_name, textRect, 32, 'white'))
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
            winner = players.sprites()[0]
            for player in players:
                if winner.score < player.score:
                    winner = player
            color = (255, 215, 0)
            size = 60
            font = pygame.font.Font('freesansbold.ttf', size)
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


def main():
    pygame.init()
    me = server()
    me.game_maker()


if __name__ == "__main__":
    main()
