import pickle
import pygame

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Line:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2


class ClosedPolyline:
    def __init__(self, lines):
        self.lines = lines


def main():
    """p1 = Point(2, 3)
    p2 = Point(3, 5)
    p3 = Point(0, 0)
    line1 = Line(p1, p2)
    line2 = Line(p1, p3)
    line3 = Line(p2, p3)
    closed_polyline = ClosedPolyline([line1, line2, line3])

    print(closed_polyline)
    bin_data = pickle.dumps(closed_polyline)
    print(bin_data)
    new_obj = pickle.loads(bin_data)
    print(new_obj)"""
    pygame.init()
    screen = pygame.display.set_mode((1100, 600))
    font = pygame.font.Font('freesansbold.ttf', 60)
    text = font.render("meeeeeee" + " is the winner!!!", True, (255, 0, 10), (0, 0, 0))
    # text.set_alpha(200)
    # text.set_colorkey((0, 0, 0))
    textRect = text.get_rect()
    textRect.center = (500, 300)
    while True:
        screen.blit(text, textRect)
        pygame.display.flip()

    """pygame.init()
    screen = pygame.display.set_mode((1100, 600))
    font = pygame.font.Font('freesansbold.ttf', 100)
    textsurface = font.render('Test', True, (0, 0, 0))
    surface = pygame.Surface((100, 30))
    surface.fill((255, 255, 255))
    surface.blit(textsurface, pygame.Rect(0, 0, 10, 10))
    surface.set_alpha(50)
    while True:
        screen.blit(surface, pygame.Rect(0, 30, 10, 10))"""


if __name__ == "__main__":
    main()
