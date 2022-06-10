import select
import logging
import socket
import pickle
from Constants import constant
import hashlib

logging.basicConfig(level=logging.DEBUG)


class ServerSide:
    def __init__(self):
        self.SERVER_PORT = 7777
        self.SERVER_IP = str(socket.gethostname())
        logging.info("Setting up server at-> " + self.SERVER_IP)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.SERVER_IP, self.SERVER_PORT))
        self.server_socket.listen()
        logging.info("Listening for clients...")
        self.client_sockets = []
        self.number_of_client = 0
        self.messages_to_send = []
        self.client_side = ClientSide()
        self.game_servers = {}

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
                    players_movement.append(self.client_requests(current_socket))
            self.sending(players_movement)
            del players_movement

    def client_requests(self, current_socket):
        players_movement = []
        client_mov = self.client_mesege(current_socket)
        if client_mov == constant.QUITING:
            self.client_quit(current_socket)
            return False
        else:
            if client_mov[0] == constant.USER_CONNECTING:  # user connect / new user
                player = self.chek_user_request(client_mov[1], client_mov[2], client_mov[3], client_mov[4])
                if not player:
                    players_movement = (current_socket, False)
                else:
                    self.client_side.send(pickle.dumps(player))
                    is_ok = self.client_side.read()
                    players_movement = (current_socket, is_ok)
            elif client_mov[0] == constant.HOMESCREEN_CONNECTS:  # home screen connects
                self.client_side.send(pickle.dumps(client_mov))
                is_ok = self.client_side.read()
                players_movement = (current_socket, is_ok)
            elif client_mov[0] == constant.HOMESCREEN_QUITING:  # home screen quiting
                self.client_side.send(pickle.dumps(client_mov))
                self.client_side.read()
                self.client_quit(current_socket)
            elif client_mov[0] == constant.NEW_GAMESERVER:  # new game server
                logging.info(client_mov[1:])
                self.game_servers[current_socket] = [client_mov[1], str(client_mov[2])[2:-1], client_mov[3]]
                players_movement = (current_socket, constant.CHECK_LIVE)
            elif client_mov[0] == constant.GAMESERVER_UPDATE:  # game server update
                self.game_servers[current_socket][2] = client_mov[1]
                # print(self.game_servers[current_socket])
                self.client_side.send(pickle.dumps((constant.GAMESERVER_UPDATE, client_mov[2:])))
                is_ok = self.client_side.read()
                players_movement = (current_socket, is_ok)
            elif client_mov[0] == constant.SERVER_QUIT:  # game server quiting
                self.game_servers[current_socket].pop()
                self.client_quit(current_socket)
            elif client_mov[0] == constant.SERVER_REQUEST:  # GUI requesting for server
                server = self.pick_server()
                players_movement = (current_socket, server)
            return players_movement

    def chek_user_request(self, name, password, date, client_name):
        if name != "" and password != "" and len(name) < 10 and client_name != "":
            print(str(hashlib.md5(password.encode())))
            return [constant.USER_CONNECTING, name, str(hashlib.md5(password.encode()).digest()), date, client_name]
        else:
            logging.debug("not sending")
            return False

    def pick_server(self):
        minimum = 10
        selected_server = None
        if not self.game_servers:
            print(f"no selected server")
            return False
        for server in self.game_servers:
            print(self.game_servers[server])
            try:
                if self.game_servers[server][2] < minimum and self.game_servers[server][2] != 0:
                    selected_server = [self.game_servers[server][0], self.game_servers[server][1], server]
                    print(f"selected_server = {selected_server}")
                    minimum = self.game_servers[server][2]
                if selected_server is None:
                    print(f"why did we get here?")
                    return False
                else:
                    try:
                        data = pickle.dumps([constant.CHECK_LIVE, selected_server[:-1]])
                        selected_server[-1].send(str(len(str(len(data)))).zfill(4).encode() + str(len(data)).encode() + data)
                        return selected_server[:-1]
                    except:
                        self.game_servers.pop(selected_server[-1])
                        print("servers: " + str(self.game_servers))
                        self.client_quit(selected_server[-1])
                        selected_server = self.pick_server()
                        if not selected_server:
                            print(f"no selected server x2")
                            return False
                        else:
                            return selected_server[:-1]
            except:
                if selected_server is not None:
                    self.game_servers.pop(selected_server[-1])
                    print("servers: " + str(self.game_servers))
                    self.client_quit(selected_server[-1])
                    selected_server = self.pick_server()
                    if not selected_server:
                        print(f"no selected server x2")
                        return False
                    else:
                        return selected_server[:-1]
                else:
                    return False

    def newclient(self, current_socket):
        connection, client_address = current_socket.accept()
        logging.info(f"New client joined: {client_address}")
        self.client_sockets.append(connection)

    def make_messages(self, players_movement):
        for client_data in players_movement:
            if client_data:
                self.messages_to_send.append((client_data[0], pickle.dumps(client_data[1])))

    def client_mesege(self, current_socket):
        rsv = ""
        try:
            lenoflen = int(current_socket.recv(4).decode())
            lenght = int(current_socket.recv(lenoflen).decode())
            rsv = current_socket.recv(lenght)
            rsv = pickle.loads(rsv)
            # print(rsv)
        except:
            logging.error("problem with resiving a message: " + str(current_socket))
            rsv = constant.QUITING
        finally:
            return rsv

    def sending(self, players_movement):
        self.make_messages(players_movement)
        for message in self.messages_to_send:
            current_socket, data = message
            try:
                current_socket.send(
                    str(len(str(len(data)))).zfill(4).encode() + str(len(data)).encode() + data)
                self.messages_to_send.remove(message)
            except Exception as e:
                logging.error("problem with sending a message: " + str(current_socket))
                self.client_quit(current_socket)

    def client_quit(self, current_socket):
        logging.debug(f"{current_socket} left")
        try:
            current_socket.shutdown(socket.SHUT_RDWR)
            current_socket.close()
            self.client_sockets.remove(current_socket)
        finally:
            return


class ClientSide:
    def __init__(self):
        self.my_socket = socket.socket()
        ip = socket.gethostname()
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


def main():
    ds = ServerSide()
    ds.run()


if __name__ == "__main__":
    main()