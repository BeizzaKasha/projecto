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

    def mov(self, walls):
        mouse = pygame.mouse.get_pressed(3)
        val = "successful"
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_w] and not self.rect.top - self.rect.height / 3 < 0:
            self.rect.move_ip(0, -self.speed)
            if pygame.sprite.spritecollideany(self, walls):
                self.rect.move_ip(0, self.speed)
        if pressed_keys[K_s] and not self.rect.bottom + self.rect.height / 3 > SCREEN_HEIGHT:
            self.rect.move_ip(0, self.speed)
            if pygame.sprite.spritecollideany(self, walls):
                self.rect.move_ip(0, -self.speed)
        if pressed_keys[K_a] and not (self.rect.left - self.rect.width / 3 < 0):
            self.rect.move_ip(-self.speed, 0)
            if pygame.sprite.spritecollideany(self, walls):
                self.rect.move_ip(self.speed, 0)
        if pressed_keys[K_d] and not (self.rect.right + self.rect.width / 3 > SCREEN_WIDTH):
            self.rect.move_ip(self.speed, 0)
            if pygame.sprite.spritecollideany(self, walls):
                self.rect.move_ip(-self.speed, 0)
        if mouse[0] and self.fire_wait <= 0:
            val = self.fire()
            self.fire_wait = 60
        if pressed_keys[pygame.K_t] and self.t_wait <= 0:  # cheat move
            self.rect.center = teleport(walls)
            self.t_wait = 150
        if pressed_keys[pygame.K_p] and self.fire_wait <= 0:
            val = self.fire()
            val.rect.center = self.rect.center
            self.fire_wait = 60

        if self.fire_wait > 0:
            self.fire_wait -= self.firing_speed

        if self.t_wait > 0:  # cheat move
            self.t_wait -= self.firing_speed

        return val

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
            text = self.font.render(str(player.name) + "           " + str(player.score), True, (255, 0, 0), (0, 0, 0))
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


pygame.init()

SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 600
pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
display_surface = pygame.display.set_mode((1000, 20))
pygame.display.set_caption('Show Text')
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


def main():
    game_time = 500

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
                if event.key == pygame.locals.K_q:  # cheat move
                    running = False
                    main()
            elif event.type == QUIT:
                running = False

        screen.fill((0, 0, 0))

        if game_time > 0:
            player.set_directangleion()
            val = player.mov(all_sprites)
            if val != "successful":
                enemies.add(val)
            enemies.update()

        for entity in all_sprites:
            screen.blit(entity.rectangle, entity.rect.topleft)

        screen.blit(player.rot_image, player.rot_image_rect.topleft)

        for bullet in enemies:
            pygame.draw.circle(screen, (255, 255, 255), (bullet.rot_image_rect.x, bullet.rot_image_rect.y), 5)
            if pygame.sprite.spritecollideany(bullet, all_sprites):
                bullet.kill()
            elif pygame.sprite.spritecollideany(bullet, players):
                for player in players:
                    if bullet.owner == player:
                        player.score += 1
                        player.rect.center = teleport(all_sprites)
                bullet.kill()
                leaderboard.change_places(players)

        leaderboard.bilt()

        pygame.time.delay(15)  # 60 frames per second
        game_time -= 1
        print(game_time)

        if game_time < 0:
            winner(players)

        if game_time == -100:
            running = False
            main()

        pygame.display.flip()

    sys.exit()


if __name__ == "__main__":
    main()
