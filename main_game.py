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
        self.surf = pygame.Surface((10, 5))
        self.surf.fill((255, 255, 255))
        self.rectangle = self.surf.get_rectangle(
            center=(
                # random.randint(player.rectangle[0], player.rectangle[0] + 50),
                player.rectangle[0] - 5,
                random.randint(player.rectangle[1], player.rectangle[1] + 25),
            )
        )
        self.speed = 15

    def update(self):
        self.rectangle.move_ip(-self.speed, 0)
        if self.rectangle.right < 0:
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.mouse = pygame
        self.rectangle = pygame.Surface((24, 24), pygame.SRCALPHA)
        self.rectangle.fill(pygame.Color('red'))
        self.rectangle.fill(pygame.Color('white'), (5, 6, 14, 5))
        self.rot_image = self.rectangle
        self.rect = self.rectangle.get_rect()
        self.speed = 10

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
        if pressed_keys[K_SPACE]:
            val = self.fire()

        if self.rect.left < 0:
            self.rect.center = (self.rect.width/2, self.rect.y + self.rect.height/2)
        if self.rect.right > SCREEN_WIDTH - self.rect.width/2:
            self.rect.center = (SCREEN_WIDTH - self.rect.width - 1, self.rect.y + self.rect.height/2)
        if self.rect.top < 0:
            self.rect.center = (self.rect.x + self.rect.width/2, self.rect.height/2)
        if self.rect.bottom > SCREEN_HEIGHT - self.rect.height/2:
            self.rect.center = (self.rect.x + self.rect.width/2, SCREEN_HEIGHT - self.rect.height + 1)

        return val

    def fire(self):
        new_enemy = Enemy(self)
        return new_enemy

    def set_directangleion(self):
        mx, my = pygame.mouse.get_pos()
        """print("player: " + str(self.rect.center))
        print("muse: " + str(mx) + ", " + str(my))"""
        dx, dy = mx - self.rect.centerx, my - self.rect.centery
        if dx == 0:
            angle = 0
        else:
            angle = math.degrees(math.atan(-dy / dx))

        self.rot_image = pygame.transform.rotate(self.rectangle, angle)
        print(int(angle))
        # self.rect = self.rot_image.get_rect(center=self.rot_image.get_rect().center) # (self.rectangle.get_rect().x + self.rect.x, self.rectangle.get_rect().y + self.rect.y)


pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

clock = pygame.time.Clock()


def main():
    player = Player()
    enemies = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

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
            all_sprites.add(val)
        enemies.update()

        for entity in all_sprites:
            screen.blit(entity.rot_image, entity.rect)

        if pygame.sprite.spritecollideany(player, enemies):
            player.kill()
            running = False

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
