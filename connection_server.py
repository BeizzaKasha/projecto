import select
import logging
import socket
import pickle

logging.basicConfig(level=logging.DEBUG)


class ServerSide:
    def __init__(self):
        self.SERVER_PORT = 7777
        self.SERVER_IP = '0.0.0.0'
        logging.debug("Setting up server...")
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.SERVER_IP, self.SERVER_PORT))
        self.server_socket.listen()
        logging.info("Listening for clients...")
        self.client_sockets = []
        self.number_of_client = 0
        self.messages_to_send = []
        self.client_side = ClientSide()

    def run(self):
        while True:
            rlist, wlist, xlist = select.select([self.server_socket] + self.client_sockets, [], [])
            players_movement = []
            for current_socket in rlist:
                if current_socket is self.server_socket:  # new client joins
                    try:
                        self.newclient(current_socket)  # create new client
                        self.number_of_client += 1
                    except Exception as e:
                        connection, client_address = current_socket.accept()
                        connection.send("cant connect".encode())
                        self.client_quit(current_socket)
                else:  # what to do with client
                    client_mov = self.client_mesege(current_socket)
                    if client_mov == 99:
                        self.client_quit(current_socket)
                    elif client_mov[0] == 0:
                        is_ok = self.client_side.comunicate(client_mov)
                        if is_ok[1] == 1:
                            is_ok = [False]
                        players_movement.append((current_socket, is_ok))
                    elif client_mov[0] == 1:
                        is_ok = self.client_side.comunicate(client_mov)
                        if is_ok[1] == 0:
                            is_ok = [True]
                        if is_ok:
                            is_ok = [False]
                        players_movement.append((current_socket, is_ok))
                    elif client_mov[0] == 2:
                        self.client_side.send([3, client_mov[1]])
                        is_ok = self.client_side.read()
                        players_movement.append((current_socket, is_ok))
            self.sending(players_movement)
            del players_movement

    def newclient(self, current_socket):
        connection, client_address = current_socket.accept()
        logging.info("New client joined!")
        self.client_sockets.append(connection)

    def make_messages(self, players_movement):
        for client_data in players_movement:
            print(client_data)
            if not client_data[1][0]:
                self.messages_to_send.append((client_data[0], pickle.dumps(False)))
            else:
                print(client_data)
                self.messages_to_send.append((client_data[0], pickle.dumps((client_data[1][1][0], client_data[1][1][1]))))

    def client_mesege(self, current_socket):
        rsv = ""
        try:
            lenoflen = int(current_socket.recv(4).decode())
            lenght = int(current_socket.recv(lenoflen).decode())
            rsv = current_socket.recv(lenght)
            rsv = pickle.loads(rsv)
            print(rsv)
        except:
            logging.error("problem with resiving a message: " + str(current_socket))
            rsv = 99
        finally:
            return rsv

    def sending(self, players_movement):
        self.make_messages(players_movement)
        for message in self.messages_to_send:
            current_socket, data = message
            # try:
            current_socket.send(
                str(len(str(len(data)))).zfill(4).encode() + str(len(data)).encode() + data)
            self.messages_to_send.remove(message)
            """except Exception as e:
                logging.error("problem with sending a message: " + str(current_socket))
                self.client_quit(current_socket)"""

    def client_quit(self, current_socket):
        print(str(current_socket) + " left")
        current_socket.shutdown(socket.SHUT_RDWR)
        current_socket.close()
        self.client_sockets.remove(current_socket)


class ClientSide:
    def __init__(self):
        self.my_socket = socket.socket()
        ip = "127.0.0.1"
        port = 6666
        self.my_socket.connect((ip, port))
        logging.debug("client side connected...")

    def send(self, data):
        self.my_socket.send(str(len(str(len(data)))).zfill(4).encode() + str(len(data)).encode() + data)

    def read(self):
        try:
            lenoflen = int(self.my_socket.recv(4).decode())
            lenght = int(self.my_socket.recv(lenoflen).decode())
            # print(str(lenght))
            data = self.my_socket.recv(lenght)
            data = pickle.loads(data)
            return data
        except Exception as e:
            logging.error(e)

    def make_message(self, name, password):
        if name != "" and password != "":
            return [1, name, password]
        else:
            print("not sending")
            return 0

    def comunicate(self, client_mov):
        message = self.make_message(client_mov[0], client_mov[1])
        if message[0] == 1:
            self.send(pickle.dumps(message))
            rtr = self.read()
            return rtr
        return False


def main():
    ds = ServerSide()
    ds.run()


if __name__ == "__main__":
    main()
