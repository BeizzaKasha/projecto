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
        self.angle = (player.angle + 90) * math.pi / 180
        self.rectangle = pygame.Surface((10, 10), pygame.SRCALPHA)
        self.rectangle.fill(pygame.Color('white'))
        self.rect = self.rectangle.get_rect()
        self.rect.move_ip(int(player.rect.centerx + 20 * math.cos(self.angle)),
                          int(player.rect.centery - 20 * math.sin(self.angle)))
        self.rot_image = self.rectangle
        self.rot_image_rect = self.rot_image.get_rect(center=self.rect.center)
        self.bullet_speed = 12

    def update(self):
        self.rect.move_ip(math.cos(self.angle) * self.bullet_speed, math.sin(self.angle) * -self.bullet_speed)
        self.rot_image_rect = self.rot_image.get_rect(center=self.rect.center)


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
        if pressed_keys[pygame.K_p] and self.t_wait <= 0:
            self.rect.center = self.teleport(walls)
            self.t_wait = 150

        """if self.rect.left < 0 or pygame.sprite.spritecollideany(self, walls):
            self.rect.center = (self.rect.width / 2, self.rect.y + self.rect.height / 2)
        if self.rect.right > SCREEN_WIDTH - self.rect.width / 2 or pygame.sprite.spritecollideany(self, walls):
            self.rect.center = (SCREEN_WIDTH - self.rect.width - 1, self.rect.y + self.rect.height / 2)
        if self.rect.top < 0 or pygame.sprite.spritecollideany(self, walls):
            self.rect.center = (self.rect.x + self.rect.width / 2, self.rect.height / 2)
        if self.rect.bottom > SCREEN_HEIGHT - self.rect.height / 2 or pygame.sprite.spritecollideany(self, walls):
            self.rect.center = (self.rect.x + self.rect.width / 2, SCREEN_HEIGHT - self.rect.height + 1)"""

        if self.fire_wait > 0:
            self.fire_wait -= self.firing_speed

        if self.t_wait > 0:
            self.t_wait -= self.firing_speed

        return val

    def teleport(self, walls):
        demo = Demo()
        t = False
        while not t:
            demo.rect.center = (random.randint(1, 801), random.randint(1, 601))
            if not pygame.sprite.spritecollideany(demo, walls):
                # print(self.rect.center)
                t = True
        new_center = demo.rect.center
        demo.kill()
        return new_center

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


class LeaderBoard(pygame.sprite.Sprite):
    def __init__(self):
        super(LeaderBoard, self).__init__()
        self.center = (900, 300)
        self.size = (100, 300)
        self.rectangle = pygame.Surface(self.size, pygame.SRCALPHA)
        self.rectangle.fill(pygame.Color('red'))


pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
display_surface = pygame.display.set_mode((1000, 20))
pygame.display.set_caption('Show Text')
font = pygame.font.Font('freesansbold.ttf', 32)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


def main():
    game_time = 500

    player = Player()
    enemies = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    for i in range(random.randint(10, 15)):
        wall = Walls()
        all_sprites.add(wall)

    bord = pygame.sprite.Sprite()
    bord.rectangle = pygame.Surface((200, 600), pygame.SRCALPHA)
    bord.rectangle.fill(pygame.Color('black'))
    bord.rect = bord.rectangle.get_rect()
    bord.rect.move_ip((800, 0))
    all_sprites.add(bord)

    line = pygame.sprite.Sprite()
    line.rectangle = pygame.Surface((8, 600), pygame.SRCALPHA)
    line.rectangle.fill(pygame.Color('white'))
    line.rect = line.rectangle.get_rect()
    line.rect.move_ip((800, 0))
    all_sprites.add(line)

    running = True
    player.rect.center = player.teleport(all_sprites)

    while running:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                if event.key == pygame.locals.K_q:
                    running = False
                    main()
            elif event.type == QUIT:
                running = False

        screen.fill((0, 0, 0))

        player.set_directangleion()
        val = player.mov(all_sprites)
        if val != "successful":
            enemies.add(val)
            # all_sprites.append(val)
        enemies.update()

        for entity in all_sprites:
            screen.blit(entity.rectangle, entity.rect.topleft)

        screen.blit(player.rot_image, player.rot_image_rect.topleft)

        for bullet in enemies:
            pygame.draw.circle(screen, (255, 255, 255), (bullet.rot_image_rect.x, bullet.rot_image_rect.y), 5)
            if pygame.sprite.spritecollideany(bullet, all_sprites):
                bullet.kill()

        text = font.render('leader bord', True, (255, 0, 0), (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (200 // 2 + 800, 20 // 2)
        display_surface.blit(text, textRect)

        if pygame.sprite.spritecollideany(player, enemies):
            player.kill()
            running = False

        pygame.display.flip()
        pygame.time.delay(15)  # 60 frames per second
        game_time -= 1
        print(game_time)
        if game_time == 0:
            pygame.time.wait(800)
            main()

    sys.exit()

if __name__ == "__main__":
    main()
