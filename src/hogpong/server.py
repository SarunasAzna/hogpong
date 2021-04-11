import socket
import asyncore
import random
import pickle
import time

BUFFERSIZE = 512

outgoing = []


class Paddle:
    def __init__(self, ownerid):
        self.x = 50
        self.y = 50
        self.vertical = True
        self.ownerid = ownerid


paddle_map = {}


def updateWorld(message):
    arr = pickle.loads(message)
    # print(str(arr))
    playerid = arr[1]
    x = arr[2]
    y = arr[3]
    vertical = arr[4]

    if playerid == 0:
        return

    paddle_map[playerid].x = x
    paddle_map[playerid].y = y
    paddle_map[playerid].vertical = vertical

    remove = []

    for i in outgoing:
        update = ["player locations"]

        for key, value in paddle_map.items():
            update.append([value.ownerid, value.x, value.y, value.vertical])

        try:
            i.send(pickle.dumps(update))
        except Exception:
            remove.append(i)
            continue

        # print('sent update data')

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
        # print('Connection address:' + addr[0] + " " + str(addr[1]))
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
