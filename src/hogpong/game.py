import pygame, sys
from pygame.locals import *
import pickle
import select
import socket
from hogpong.parser import parse_args

### Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
WIDTH = HEIGHT = 1200
BUFFERSIZE = 2048
ball_x = HEIGHT / 2
ball_y = HEIGHT / 2
BALL_WIDTH = WIDTH / 120
PADDLE_WIDTH = HEIGHT / 90
PADDLE_HEIGHT = PADDLE_WIDTH ** 2

p1x = WIDTH / 30
p1y = HEIGHT / 2 - (PADDLE_WIDTH ** 2) / 2

p2x = WIDTH - (WIDTH / 30)
p2y = HEIGHT / 2 - ((PADDLE_WIDTH) ** 2) / 2

INITIAL_PADDLE_POSITIONS = ((p1x, p1y), (p2x, p2y), (p1y, p1x), (p2y, p2x))


def drawpaddle(screen, x, y, w, h):
    pygame.draw.rect(screen, WHITE, (x, y, w, h))


def drawball(screen, x, y):
    pygame.draw.circle(screen, WHITE, (int(x), int(y)), int(BALL_WIDTH))


def run_game(host="127.0.0.1"):

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("HogPong")
    screen.fill(BLACK)
    pygame.display.flip()

    clock = pygame.time.Clock()

    serverAddr = host

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((serverAddr, 4321))

    playerid = 0

    class Minion:
        def __init__(self, x, y, id, vertical=True):
            self.x = x
            self.y = y
            self.vertical = vertical
            self.vx = 0
            self.vy = 0
            self.id = id

        def update(self):
            if self.vertical:
                self.y += self.vy if self.vertical else 0
                if self.y > HEIGHT - PADDLE_HEIGHT:
                    self.y = HEIGHT - PADDLE_HEIGHT
                if self.y < 0:
                    self.y = 0
            else:
                self.x += self.vx if not self.vertical else 0
                if self.x > WIDTH - PADDLE_HEIGHT:
                    self.x = WIDTH - PADDLE_HEIGHT
                if self.x < 0:
                    self.x = 0

            if self.id == 0:
                self.id = playerid

        def render(self):
            width, height = (
                (PADDLE_WIDTH, PADDLE_HEIGHT)
                if self.vertical
                else (PADDLE_HEIGHT, PADDLE_WIDTH)
            )
            drawpaddle(screen, self.x, self.y, width, height)

    # game events
    # ['event type', param1, param2]
    #
    # event types:
    # id update
    # ['id update', id]
    #
    # player locations
    # ['player locations', [id, x, y], [id, x, y] ...]

    # user commands
    # position update
    # ['position update', id, x, y]

    class GameEvent:
        def __init__(self, vx, vy):
            self.vx = vx
            self.vy = vy

    cc = Minion(0, 0, 0)

    minions = []
    position = 0

    while True:
        ins, outs, ex = select.select([s], [], [], 0)
        for inm in ins:
            gameEvent = pickle.loads(inm.recv(BUFFERSIZE))
            if gameEvent[0] == "id update":
                playerid = gameEvent[1]
                position = gameEvent[2]
                cc.x, cc.y = INITIAL_PADDLE_POSITIONS[position]
                cc.vertical = position <= 1
            if gameEvent[0] == "player locations":
                gameEvent.pop(0)
                minions = []
                for minion in gameEvent:
                    if minion[0] != playerid:
                        minions.append(
                            Minion(minion[1], minion[2], minion[0], vertical=minion[3])
                        )

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_LEFT:
                    cc.vx = -10
                if event.key == K_RIGHT:
                    cc.vx = 10
                if event.key == K_UP:
                    cc.vy = -10
                if event.key == K_DOWN:
                    cc.vy = 10
            if event.type == KEYUP:
                if event.key == K_LEFT and cc.vx == -10:
                    cc.vx = 0
                if event.key == K_RIGHT and cc.vx == 10:
                    cc.vx = 0
                if event.key == K_UP and cc.vy == -10:
                    cc.vy = 0
                if event.key == K_DOWN and cc.vy == 10:
                    cc.vy = 0

        clock.tick(60)
        screen.fill(BLACK)
        drawball(screen, ball_x, ball_y)

        cc.update()

        for m in minions:
            m.render()

        cc.render()

        pygame.display.flip()

        ge = ["position update", playerid, cc.x, cc.y, cc.vertical]
        s.send(pickle.dumps(ge))
    s.close()
