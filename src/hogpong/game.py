import pygame, sys
from pygame.locals import *
import pickle
import select
import socket
from hogpong.constants import SIDE_ENUMERATION, RIGTH_SIDE, LEFT_SIDE, TOP_SIDE, BOTTOM_SIDE

### General Parameters
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
WIDTH = HEIGHT = 1200
BUFFERSIZE = 2048

# Paddle parameters
PADDLE_WIDTH = HEIGHT / 90
PADDLE_HEIGHT = PADDLE_WIDTH ** 2

p1x = WIDTH / 30
p1y = HEIGHT / 2 - (PADDLE_WIDTH ** 2) / 2

p2x = WIDTH - (WIDTH / 30)
p2y = HEIGHT / 2 - ((PADDLE_WIDTH) ** 2) / 2

INITIAL_PADDLE_POSITIONS = ((p1x, p1y), (p2x, p2y), (p1y, p1x), (p2y, p2x))

# Ball parameters
BALL_WIDTH = WIDTH / 120
INITIAL_BX = HEIGHT/2
INITIAL_BY = HEIGHT/2
bx = INITIAL_BX
by = INITIAL_BY
INITIAL_BXV= HEIGHT/180
INITIAL_BYV = 0
bxv = INITIAL_BXV
byv = INITIAL_BYV


def drawpaddle(screen, x, y, w, h):
    pygame.draw.rect(screen, WHITE, (x, y, w, h))


def drawball(screen, x, y):
    pygame.draw.circle(screen, WHITE, (int(x), int(y)), int(BALL_WIDTH))


def select_paddle_near_the_ball(paddles, side):
    selected = [p for p in paddles if p.side == side]
    if selected:
        return selected[0]



def upblnv(paddles):
    global bx
    global bxv
    global by
    global byv

    left_x_limit = PADDLE_WIDTH + p1x
    righ_x_limit = WIDTH - (p1x if len(paddles) >1 else 0)
    top_y_limit = p1x if len(paddles) > 2 else 0
    bottom_y_limit = HEIGHT - (p1x if len(paddles) > 2 else 0)
    estimated_x = bx + bxv
    estimated_y = by + byv

    if estimated_x > righ_x_limit:
        paddle = select_paddle_near_the_ball(paddles, RIGTH_SIDE)
        bxv = -bxv
        if paddle is None:
            pass
        elif paddle.y < estimated_y < paddle.y + PADDLE_HEIGHT:
            byv = byv = ((paddle.y+(paddle.y+PADDLE_HEIGHT))/2)-by
            byv = -byv/((5*BALL_WIDTH)/7)
        else:
            bxv, bxy, bx, by = INITIAL_BXV, INITIAL_BYV, INITIAL_BX, INITIAL_BY

    if estimated_x < left_x_limit:
        paddle = select_paddle_near_the_ball(paddles, LEFT_SIDE)
        bxv = -bxv
        if paddle is None:
            pass
        elif paddle.y < estimated_y < paddle.y + PADDLE_HEIGHT:
            byv = ((paddle.y + (paddle.y + PADDLE_HEIGHT)) / 2) - by
            byv = -byv / ((5 * BALL_WIDTH) / 7)
        else:
            bxv, bxy, bx, by = INITIAL_BXV, INITIAL_BYV, INITIAL_BX, INITIAL_BY

    if estimated_y > bottom_y_limit:
        paddle = select_paddle_near_the_ball(paddles, BOTTOM_SIDE)
        byv = -byv
        if paddle is None:
            pass
        elif paddle.x < estimated_x < paddle.x + PADDLE_HEIGHT:
            bxv = ((paddle.x + (paddle.x + PADDLE_HEIGHT)) / 2) - bx
            bxv = -bxv / ((5 * BALL_WIDTH) / 7)
        else:
            bxv, bxy, bx, by = INITIAL_BXV, INITIAL_BYV, INITIAL_BX, INITIAL_BY

    if estimated_y < top_y_limit:
        paddle = select_paddle_near_the_ball(paddles, TOP_SIDE)
        byv = -byv
        if paddle is None:
            pass
        elif paddle.x < estimated_x < paddle.x + PADDLE_HEIGHT:
            bxv = ((paddle.x + (paddle.x + PADDLE_HEIGHT)) / 2) - bx
            bxv = -bxv / ((5 * BALL_WIDTH) / 7)
        else:
            bxv, bxy, bx, by = INITIAL_BXV, INITIAL_BYV, INITIAL_BX, INITIAL_BY


    #if (bx+bxv < p1x+paddle_width) and ((p1y < by+byv+bw) and (by+byv-bw < p1y+paddle_height)):
    #    bxv = -bxv
    #    byv = ((p1y+(p1y+paddle_height))/2)-by
    #    byv = -byv/((5*bw)/7)
    #elif bx+bxv < 0:
    #    p2score += 1
    #    bx = W/2
    #    bxv = H/60
    #    by = H/2
    #    byv = 0
    #if (bx+bxv > p2x) and ((p2y < by+byv+bw) and (by+byv-bw < p2y+paddle_height)):
    #    bxv = -bxv
    #    byv = ((p2y+(p2y+paddle_height))/2)-by
    #    byv = -byv/((5*bw)/7)
    #elif bx+bxv > W:
    #    p1score += 1
    #    bx = W/2
    #    bxv = -H/60
    #    by = H/2
    #    byv = 0
    #if by+byv > H or by+byv < 0:
    #    byv = -byv

    bx += bxv
    by += byv


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

    class Paddle:
        def __init__(self, x, y, id, vertical=True, side="right"):
            self.x = x
            self.y = y
            self.vertical = vertical
            self.vx = 0
            self.vy = 0
            self.id = id
            self.side = side

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

    cc = Paddle(0, 0, 0)

    paddles = []
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
                cc.side = SIDE_ENUMERATION[position]
            if gameEvent[0] == "player locations":
                gameEvent.pop(0)
                paddles = []
                for minion in gameEvent:
                    if minion[0] != playerid:
                        paddles.append(
                            Paddle(minion[1], minion[2], minion[0], vertical=minion[3], side=minion[4])
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

        upblnv(paddles + [cc])
        drawball(screen, bx, by)

        cc.update()

        for m in paddles:
            m.render()

        cc.render()

        pygame.display.flip()

        ge = ["position update", playerid, cc.x, cc.y, cc.vertical, cc.side]
        s.send(pickle.dumps(ge))
    s.close()
