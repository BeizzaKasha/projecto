import mysql.connector
import select
import logging
import socket
import pickle
from Constants import constant

logging.basicConfig(level=logging.INFO)


class ServerSide:
    def __init__(self):
        self.SERVER_PORT = 6666
        self.SERVER_IP = str(socket.gethostname())
        logging.info("Setting up server at-> " + self.SERVER_IP)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.SERVER_IP, self.SERVER_PORT))
        self.server_socket.listen()
        logging.info("Listening for clients...")
        self.client_sockets = []
        self.number_of_client = 0
        self.messages_to_send = []
        self.game_servers = {}

        self.db = Database()

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
                    players_movement = self.client_actions(current_socket)
            self.sending(players_movement)

    def client_actions(self, current_socket):
        players_movement = []
        client_mov = self.client_mesege(current_socket)
        if client_mov == constant.QUITING:
            self.client_quit(current_socket)
        elif client_mov[0] == constant.GAMESERVER_UPDATE:  # game_server
            print(client_mov[1])
            self.update_all(client_mov[1])
            players_movement.append((current_socket, "I love..."))
        elif client_mov[0] == constant.USER_CONNECTING:  # user connects
            is_ok = self.check_connection(client_mov[1], client_mov[2], client_mov[3], client_mov[4])
            # print(f"is_ok = {is_ok}")
            players_movement.append((current_socket, is_ok))
        elif client_mov[0] == constant.HOMESCREEN_CONNECTS:  # home screen
            player = self.db.read(client_mov[1].decode())
            position = self.find_position(player)
            players_movement.append((current_socket, (player, position)))
        elif client_mov[0] == constant.HOMESCREEN_QUITING:  # home screen quit
            player = self.db.read(client_mov[1].decode())
            self.db.add(player[0], player[1], player[5], player[2], player[3], player[4], False)
            players_movement.append((current_socket, constant.QUITING))
        return players_movement

    def find_position(self, player):
        all_players = self.db.to_string()
        position = len(all_players)
        for other_player in all_players:
            if player != other_player:
                if player[4] >= other_player[4]:
                    position -= 1
        return position

    def check_connection(self, name, password, date, client_name):
        if date != "" and client_name != "":
            if self.db.is_exist(name):
                return False
            else:
                try:
                    self.db.add(name, password, client_name, date, "", 0, True)
                    return True
                except Exception as e:
                    # print(e)
                    return False
        else:
            if not self.db.is_exist(name):
                return False
            else:
                player = self.db.read(name)
                if password == player[1] and player[6] == 0:
                    self.db.add(player[0], player[1], player[5], player[2], player[3], player[4], True)
                    return True
                else:
                    return False

    def update_all(self, client_mov):
        try:
            for player in client_mov:
                self.update_individual(player)
            return True
        except Exception as e:
            logging.info(f"universal updating error: {e}")
            return False

    def update_individual(self, client_player):
        database_player = self.db.read(client_player[0])
        print(client_player, database_player)
        name = database_player[0]
        password = database_player[1]
        date = database_player[2]
        client_name = database_player[5]
        try:
            history = database_player[3]
            if history == "":
                self.db.add(name, password, client_name, date, client_player[1], client_player[1], True)
            else:
                try:
                    former_points = str(history).split(",")
                    points = 0
                    for former_point in former_points:
                        points += float(former_point)
                except:
                    points = float(history)
                    former_points = [history]
                self.db.add(name, password, client_name, date,
                            str(history) + "," + str(client_player[1]),
                            (client_player[1] + points) / (len(former_points) + 1), True)
        except Exception as e:
            logging.info(f"{name} updating problem: {e}")
            self.db.add(name, password, client_name, date, client_player[1], client_player[1], True)
        finally:
            logging.info("update successful")

    def newclient(self, current_socket):
        connection, client_address = current_socket.accept()
        logging.info("New client joined!")
        self.client_sockets.append(connection)

    def make_messages(self, players_movement):
        for client_data in players_movement:
            self.messages_to_send.append((client_data[0], pickle.dumps(client_data[1])))

    def client_mesege(self, current_socket):
        rsv = ""
        try:
            lenoflen = int(current_socket.recv(4).decode())
            lenght = int(current_socket.recv(lenoflen).decode())
            rsv = current_socket.recv(lenght)
            rsv = pickle.loads(rsv)
        except:
            logging.error("problem with resiving a message: " + str(current_socket))
            rsv = 99
        finally:
            return rsv

    def sending(self, players_movement):
        self.make_messages(players_movement)
        for message in self.messages_to_send:
            current_socket, data = message
            try:
                current_socket.send(str(len(str(len(data)))).zfill(4).encode() + str(len(data)).encode() + data)
                self.messages_to_send.remove(message)
            except Exception as e:
                logging.error("problem with sending a message: " + str(current_socket))
                self.client_quit(current_socket)

    def client_quit(self, current_socket):
        print(str(current_socket) + " left")
        try:
            current_socket.shutdown(socket.SHUT_RDWR)
            current_socket.close()
        finally:
            self.client_sockets.remove(current_socket)
            return


class Database:
    def __init__(self):
        self.mydb = ""
        self.mycursor = ""
        self.open_sequence()

    def open_sequence(self):
        try:
            self.mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root",
                database="shootydb"
            )
            self.mycursor = self.mydb.cursor()

            is_exist = False
            self.mycursor.execute("SHOW TABLES")

            for x in self.mycursor:
                # print(str(x)[2:-3])
                if str(x)[2:-3] == "players":
                    is_exist = True
            if not is_exist:
                self.create_db()
                return

        except:
            if self.mydb == "":
                self.mydb = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="root"
                )
            if self.mycursor == "":
                self.mycursor = self.mydb.cursor()
            self.create_db()
            return

    def create_db(self):
        self.mycursor.execute("CREATE DATABASE shootydb")
        self.mycursor.execute("CREATE TABLE shootydb.players (PlayerName VARCHAR(255) primary key not null,"
                              " PlayerPassword VARCHAR(255) not null, CreationTime VARCHAR(255) not null,"
                              " GameHistory VARCHAR(255) not null, PersonalRecord double not null,"
                              " ClientName VARCHAR(255) not null, IsConnect boolean not null)")

    def is_exist(self, name):
        sql = "SELECT * FROM shootydb.players WHERE PlayerName = '" + name + "'"
        self.mycursor.execute(sql)
        place = self.mycursor.fetchall()
        if len(place) == 0:
            return False
        else:
            return True

    def add(self, PlayerName, PlayerPassword, ClientName, CreationTime, GameHistory, PersonalRecord,
            is_connect):  # add a value new, if already exist change old one to match the new input
        try:
            if self.is_exist(PlayerName):
                self.delete(PlayerName)
            sql = "INSERT INTO shootydb.players " \
                  "(PlayerName, PlayerPassword, ClientName, CreationTime, GameHistory, PersonalRecord, IsConnect)" \
                  " VALUES (%s, %s, %s, %s, %s, %s, %s)"
            val = (PlayerName, PlayerPassword, ClientName, CreationTime, GameHistory, PersonalRecord, is_connect)
            # print(val)
            self.mycursor.execute(sql, val)
            self.mydb.commit()

            return True  # if add successful return True
        except Exception as e:
            logging.error(e)
            return False  # if doesn't work return False

    def delete(self, name):
        try:
            myresult = self.read(name)
            sql = "DELETE FROM shootydb.players WHERE PlayerName = '" + name + "'"
            self.mycursor.execute(sql)
            self.mydb.commit()
            return myresult  # if delete successfully return what was deleted
        except Exception as e:
            logging.info(f"deleting error: {e}")
            return False  # if doesn't work return False

    def read(self, name):
        self.mycursor.execute("SELECT * FROM shootydb.players where PlayerName = '" + name + "'")
        myresult = self.mycursor.fetchall()
        return myresult[0]

    def to_string(self):
        self.mycursor.execute("SELECT * FROM shootydb.players")
        myresult = self.mycursor.fetchall()
        return myresult

    def update_all(self, what, update):
        sql = "UPDATE help SET " + what + " = '" + update + "'"
        self.mycursor.execute(sql)
        self.mydb.commit()

    def get_names(self):
        names = []
        self.mycursor.execute("SELECT * FROM shootydb.players")
        myresult = self.mycursor.fetchall()
        for x in myresult:
            names.append(x)
        return myresult

    def get_winner(self):
        top = ["", "", -1]
        for player in self.get_names():
            if player[2] > top[2]:
                top = player
        return top


def main():
    ds = ServerSide()
    ds.run()


if __name__ == "__main__":
    main()
