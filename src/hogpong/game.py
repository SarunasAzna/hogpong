import pygame, sys
from pygame.locals import *
import pickle
import select
import socket
from hogpong.parser import parse_args

### Colors
WHITE = (255, 255, 255)
BLACK = (0,0,0)
WIDTH = HEIGHT = 1200
BUFFERSIZE = 2048
ball_x = HEIGHT/2
ball_y = HEIGHT/2
BALL_WIDTH = WIDTH/120
PADDLE_WIDTH = HEIGHT/90
PADDLE_HEIGHT = PADDLE_WIDTH**2
p1x = WIDTH/30
p1y = HEIGHT/2 - (PADDLE_WIDTH**2)/2

p2x = WIDTH-(WIDTH/30)
p2y = HEIGHT/2 - ((WIDTH/60)**2)/2

INITIAL_PADDLE_POSITIONS = ((p1x, p1y), (p2x, p2y))


def drawpaddle(screen, x, y, w, h):
    pygame.draw.rect(screen, WHITE, (x, y, w, h))

def drawball(screen, x, y):
    pygame.draw.circle(screen, WHITE, (int(x), int(y)), int(BALL_WIDTH))

def run_game(host="127.0.0.1"):

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('HogPong')
    screen.fill(BLACK)
    pygame.display.flip()

    clock = pygame.time.Clock()

    serverAddr = host

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((serverAddr, 4321))

    playerid = 0



    class Minion:
        def __init__(self, x, y, id):
            self.x = x
            self.y = y
            self.vx = 0
            self.vy = 0
            self.id = id

        def update(self):
            self.x += self.vx
            self.y += self.vy

            if self.x > WIDTH - 50:
                self.x = WIDTH - 50
            if self.x < 0:
                self.x = 0
            if self.y > HEIGHT - 50:
                self.y = HEIGHT - 50
            if self.y < 0:
                self.y = 0

            if self.id == 0:
                self.id = playerid

        def render(self):
            x, y = INITIAL_PADDLE_POSITIONS[self.id % 4] if self.x is None else (self.x, self.y)
            drawpaddle(screen, self.x, self.y, PADDLE_WIDTH, PADDLE_HEIGHT)
            #screen.blit(sprites[self.id % 4], (self.x, self.y))


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

    minion_created = False

    cc = Minion(50, 50, 0)

    minions = []

    while True:
        ins, outs, ex = select.select([s], [], [], 0)
        for inm in ins:
            gameEvent = pickle.loads(inm.recv(BUFFERSIZE))
            if gameEvent[0] == 'id update':
                playerid = gameEvent[1]
                cc.x, cc.y = INITIAL_PADDLE_POSITIONS[gameEvent[2] - 1]
            if gameEvent[0] == 'player locations':
                gameEvent.pop(0)
                minions = []
                for minion in gameEvent:
                    if minion[0] != playerid:
                        minions.append(Minion(minion[1], minion[2], minion[0]))

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_LEFT: cc.vx = -10
                if event.key == K_RIGHT: cc.vx = 10
                if event.key == K_UP: cc.vy = -10
                if event.key == K_DOWN: cc.vy = 10
            if event.type == KEYUP:
                if event.key == K_LEFT and cc.vx == -10: cc.vx = 0
                if event.key == K_RIGHT and cc.vx == 10: cc.vx = 0
                if event.key == K_UP and cc.vy == -10: cc.vy = 0
                if event.key == K_DOWN and cc.vy == 10: cc.vy = 0

        clock.tick(60)
        screen.fill(BLACK)
        drawball(screen, ball_x, ball_y)

        cc.update()

        for m in minions:
            m.render()

        cc.render()

        pygame.display.flip()

        ge = ['position update', playerid, cc.x, cc.y]
        s.send(pickle.dumps(ge))
    s.close()