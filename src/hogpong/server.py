import socket
import asyncore
import random
import pickle
from hogpong.constants import SIDE_ENUMERATION, RIGTH_SIDE, LEFT_SIDE

BUFFERSIZE = 512

outgoing = []


class Paddle:
    def __init__(self, ownerid):
        self.x = 50
        self.y = 50
        self.ball_x = 0
        self.ball_y = 0
        self.vertical = True
        self.ownerid = ownerid
        self.side = SIDE_ENUMERATION[0]

class Ball:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0


paddle_map = {}
ball = Ball()


def updateWorld(message):
    arr = pickle.loads(message)
    # print(str(arr))
    playerid = arr[1]
    x = arr[2]
    y = arr[3]
    vertical = arr[4]
    side = arr[5]
    ball_x = arr[6]
    ball_y = arr[7]
    ball_xv = arr[8]
    ball_yv = arr[9]

    if playerid == 0:
        return

    paddle_map[playerid].x = x
    paddle_map[playerid].y = y
    paddle_map[playerid].vertical = vertical
    paddle_map[playerid].side = side

    remove = []

    for i in outgoing:
        update = ["player locations"]

        for key, value in paddle_map.items():
            update.append([value.ownerid, value.x, value.y, value.vertical, value.side, ball_x, ball_y, ball_xv, ball_yv])

        try:
            i.send(pickle.dumps(update))
        except Exception:
            remove.append(i)
            continue


        for r in remove:
            outgoing.remove(r)


class MainServer(asyncore.dispatcher):
    def __init__(self, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(("", port))
        self.listen(10)

    def handle_accept(self):
        conn, addr = self.accept()
        outgoing.append(conn)
        playerid = random.randint(1000, 1000000)
        position = len(paddle_map)
        player_paddle = Paddle(playerid)
        paddle_map[playerid] = player_paddle
        conn.send(pickle.dumps(["id update", playerid, position]))
        SecondaryServer(conn)


class SecondaryServer(asyncore.dispatcher_with_send):
    def handle_read(self):
        recievedData = self.recv(BUFFERSIZE)
        if recievedData:
            updateWorld(recievedData)
        else:
            self.close()


def run_server():
    MainServer(4321)
    asyncore.loop()
