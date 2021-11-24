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
    def __init__(self, width, height):
        super(Player, self).__init__()
        self.mouse = pygame
        self.rectangle = pygame.Surface((24, 24), pygame.SRCALPHA)
        self.rectangle.fill(pygame.Color('red'))
        self.rectangle.fill(pygame.Color('white'), (5, 6, 14, 5))
        self.speed = 10
        self.surface = pygame.display.set_mode((width, height))
        self.center = pygame.Vector2(self.sprite.rect.center)

    def mov(self):
        mouse_pos = pygame.mouse.get_pos()
        # print(mouse_pos)
        self.set_directangleion()

        val = "successful"
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_w]:
            self.rectangle.move_ip(0, -self.speed)
        if pressed_keys[K_s]:
            self.rectangle.move_ip(0, self.speed)
        if pressed_keys[K_a]:
            self.rectangle.move_ip(-self.speed, 0)
        if pressed_keys[K_d]:
            self.rectangle.move_ip(self.speed, 0)
        if pressed_keys[K_SPACE]:
            val = self.fire()

        if self.rectangle.left < 0:
            self.rectangle.left = 0
        if self.rectangle.right > SCREEN_WIDTH:
            self.rectangle.right = SCREEN_WIDTH
        if self.rectangle.top <= 0:
            self.rectangle.top = 0
        if self.rectangle.bottom >= SCREEN_HEIGHT:
            self.rectangle.bottom = SCREEN_HEIGHT

        return val

    def fire(self):
        new_enemy = Enemy(self)
        return new_enemy

    def set_directangleion(self):
        mouse_pos = pygame.mouse.get_pos()
        """print(self.center)
        print("mouse: " + str(mouse_pos))"""
        if mouse_pos[0] == self.center[0] and mouse_pos[1] == self.center[1]:
            angle = 0
        else:
            top = abs(self.center[0] - mouse_pos[0])
            bottom = int(math.sqrt((self.center[0] - mouse_pos[0]) ** 2 + (self.center[1] - mouse_pos[1]) ** 2))
            if top / bottom < -1 or top / bottom > 1:
                angle = "error -->" + str(top / bottom) + ",  " + str(self.center[0]) + "," + str(mouse_pos[0]) + ",  " + str(self.center[1]) + "," + str(mouse_pos[1])
            else:
                angle = math.acos(top / bottom) * 180 / math.pi
                if self.center[1] - mouse_pos[1] > 0 and mouse_pos[0] - self.center[0] < 0:
                    angle = 180 - angle
                elif self.center[1] - mouse_pos[1] < 0 and mouse_pos[0] - self.center[0] < 0:
                    angle += 180
                if self.center[1] - mouse_pos[1] < 0 and mouse_pos[0] - self.center[0] > 0:
                    angle = 360 - angle
            # print(str(top) + ", " + str(bottom))
        print(angle)
        pygame.transform.rotate(self.surface, angle)
        # self.directangleion = pygame.Vector2(sin(rad), cos(rad))


pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

clock = pygame.time.Clock()


def main():
    player = Player(SCREEN_WIDTH, SCREEN_HEIGHT)
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

        val = player.mov()
        if val != "successful":
            enemies.add(val)
            all_sprites.add(val)
        enemies.update()

        for entity in all_sprites:
            screen.blit(entity.surf, entity.rectangle)

        if pygame.sprite.spritecollideany(player, enemies):
            player.kill()
            running = False

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
