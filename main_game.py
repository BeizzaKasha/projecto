import math

import pygame
from pygame.locals import (
    K_w,
    K_s,
    K_a,
    K_d,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
    K_SPACE
)
import random


class Enemy(pygame.sprite.Sprite):
    def __init__(self, player):
        super(Enemy, self).__init__()
        self.angle = (player.angle + 90) * math.pi/180
        self.rectangle = pygame.Surface((10, 10), pygame.SRCALPHA) # (player.rect.centerx + 100*math.cos(self.angle), player.rect.centery - 100*math.sin(self.angle))
        self.rectangle.fill(pygame.Color('white'))
        # self.rectangle = pygame.Surface((player.rect.top, player.rect.top))
        self.rect = self.rectangle.get_rect()
        self.rect.move_ip(int(player.rect.centerx + 16*math.cos(self.angle) - 3), int(player.rect.centery - 16*math.sin(self.angle)) - 3)
        self.rot_image = self.rectangle
        self.rot_image_rect = self.rot_image.get_rect(center=self.rect.center)
        self.speed = 12

        # print("angle:" + str(self.angle))
        # print(math.cos(self.angle))
        # print(-math.sin(self.angle))

    def update(self):
        self.rect.move_ip(math.cos(self.angle) * self.speed, math.sin(self.angle) * -self.speed)
        # self.rot_image = pygame.transform.rotate(self.rectangle, self.angle * 180/math.pi)
        self.rot_image_rect = self.rot_image.get_rect(center=self.rect.center)



class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.mouse = pygame
        self.rectangle = pygame.Surface((24, 24), pygame.SRCALPHA)
        self.rectangle.fill(pygame.Color('red'))
        self.rectangle.fill(pygame.Color('white'), (5, 6, 14, 5))
        self.rect = self.rectangle.get_rect()
        self.rot_image = self.rectangle
        self.rot_image_rect = self.rot_image.get_rect(center=self.rect.center)
        self.angle = 0
        self.speed = 8
        self.firing_speed = 2
        self.fire_wait = 80

    def mov(self):

        val = "successful"
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_w]:
            self.rect.move_ip(0, -self.speed)
        if pressed_keys[K_s]:
            self.rect.move_ip(0, self.speed)
        if pressed_keys[K_a]:
            self.rect.move_ip(-self.speed, 0)
        if pressed_keys[K_d]:
            self.rect.move_ip(self.speed, 0)
        if pressed_keys[K_SPACE] and self.fire_wait == 0:
            val = self.fire()
            self.fire_wait = 100

        if self.rect.left < 0:
            self.rect.center = (self.rect.width / 2, self.rect.y + self.rect.height / 2)
        if self.rect.right > SCREEN_WIDTH - self.rect.width / 2:
            self.rect.center = (SCREEN_WIDTH - self.rect.width - 1, self.rect.y + self.rect.height / 2)
        if self.rect.top < 0:
            self.rect.center = (self.rect.x + self.rect.width / 2, self.rect.height / 2)
        if self.rect.bottom > SCREEN_HEIGHT - self.rect.height / 2:
            self.rect.center = (self.rect.x + self.rect.width / 2, SCREEN_HEIGHT - self.rect.height + 1)

        if self.fire_wait > 0:
            self.fire_wait -= self.firing_speed

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

        """print(str(pygame.transform.rotate(self.rectangle, self.angle)))
        print(int(self.angle))"""


pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

clock = pygame.time.Clock()


def main():
    player = Player()
    enemies = pygame.sprite.Group()
    all_sprites = [player]

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
            elif event.type == QUIT:
                running = False

        screen.fill((0, 0, 0))

        player.set_directangleion()
        val = player.mov()
        if val != "successful":
            enemies.add(val)
            all_sprites.append(val)
        enemies.update()

        for entity in all_sprites:
            screen.blit(entity.rot_image, entity.rot_image_rect.topleft)

        if pygame.sprite.spritecollideany(player, enemies):
            player.kill()
            running = False

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()