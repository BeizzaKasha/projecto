import sys
import logging
import pickle
import socket
import pygame

logging.basicConfig(level=logging.DEBUG)

logging.debug("client begin")
my_socket = socket.socket()
ip = "127.0.0.1"
port = 5555
my_socket.connect((ip, port))
logging.info("connect to server at {0} with port {1}".format(ip, port))


def close():
    logging.error("client close")
    sys.exit()


def built_all(game):
    print(str(game) + "do here built for what need how it is on server")


def main():
    game = ""
    while True:
        send = "hello"
        my_socket.send(send.encode())

        try:
            data = my_socket.recv(1024)
            data = pickle.loads(data)
            print(data)
            if data != "close":
                game = pickle.loads(data)

        except Exception as e:
            print(str(e))
            close()

        built_all(game)


if __name__ == "__main__":
    main()
