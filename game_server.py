import select
import logging
import socket
import pickle

SERVER_PORT = 5555
SERVER_IP = '0.0.0.0'

logging.basicConfig(level=logging.DEBUG)


def print_client_sockets(client_sockets):
    for i in range(len(client_sockets)):
        logging.debug(client_sockets[i])


def newclient(current_socket, client_sockets):
    connection, client_address = current_socket.accept()
    logging.info("New client joined!")
    client_sockets.append(connection)
    print_client_sockets(client_sockets)


def client_mesege(current_socket):
    rsv = current_socket.recv(1024).decode()  # get the client messege, do what ever u want with it--->
    print(rsv)
    mesege = pickle.dumps(str(rsv) + ", hello there")
    messages_to_send.append((current_socket, mesege))


logging.debug("Setting up server...")
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen()
logging.info("Listening for clients...")
client_sockets = []
messages_to_send = []
number_of_client = 0
# place for parameters


while True:
    rlist, wlist, xlist = select.select([server_socket] + client_sockets, client_sockets, [])
    for current_socket in rlist:
        if current_socket is server_socket:  # new client joins
            newclient(current_socket, client_sockets)  # create new client
        else:  # what to do with new client
            number_of_client += 1
            print(number_of_client)
            client_mesege(current_socket)

    for message in messages_to_send:
        current_socket, data = message
        if current_socket in wlist:
            current_socket.send(data)
            messages_to_send.remove(message)
