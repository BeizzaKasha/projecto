import mysql.connector
import select
import logging
import socket

logging.basicConfig(level=logging.DEBUG)


class ServerSide:
    def __init__(self):
        self.SERVER_PORT = 6666
        self.SERVER_IP = '0.0.0.0'
        logging.debug("Setting up server...")
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.SERVER_IP, self.SERVER_PORT))
        self.server_socket.listen()
        logging.info("Listening for clients...")
        self.client_sockets = []
        self.number_of_client = 0

    def run(self):
        while True:
            rlist, wlist, xlist = select.select([self.server_socket] + self.client_sockets, [], [])
            for current_socket in rlist:
                if current_socket is self.server_socket:  # new client joins
                    try:
                        self.newclient(current_socket, self.client_sockets)  # create new client
                        self.number_of_client += 1
                    except Exception as e:
                        connection, client_address = current_socket.accept()
                        connection.send("cant connect".encode())
                        self.client_quit(self.client_sockets, current_socket)
                else:  # what to do with client
                    print("help")

    def newclient(self, current_socket, client_sockets):
        connection, client_address = current_socket.accept()
        logging.info("New client joined!")
        client_sockets.append(connection)

    def client_quit(self, client_sockets, current_socket):
        print(str(current_socket) + " left")
        current_socket.shutdown(socket.SHUT_RDWR)
        current_socket.close()
        client_sockets.remove(current_socket)


class Database:
    def __init__(self):
        self.mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root"
        )

        self.mycursor = self.mydb.cursor()

    def is_exist(self, name):
        sql = "SELECT * FROM mytry.help WHERE name = '" + name + "'"
        self.mycursor.execute(sql)
        place = self.mycursor.fetchall()
        if len(place) == 0:
            return False
        else:
            return True

    def add(self, name, password, point):  # add a value new, if already exist change old one to match the new input
        try:
            if self.is_exist(name):
                self.delete(name)
            sql = "INSERT INTO mytry.help (name, password, point) VALUES (%s, %s, %s)"
            val = (name, password, point)
            self.mycursor.execute(sql, val)
            self.mydb.commit()

            return True  # if add successful return True
        except Exception as e:
            # print(e)
            return False  # if doesn't work return False

    def delete(self, name):
        try:
            sql = "DELETE FROM mytry.help WHERE name = '" + name + "'"
            self.mycursor.execute(sql)
            myresult = self.mycursor.fetchall()
            return myresult  # if delete successfully return what was deleted
        except Exception as e:
            # print(e)
            return False  # if doesn't work return False

    def read(self, name):
        self.mycursor.execute("SELECT * FROM mytry.help where name = '" + name + "'")
        myresult = self.mycursor.fetchall()
        return myresult

    def to_string(self):
        to_string = ""
        self.mycursor.execute("SELECT * FROM mytry.help")
        myresult = self.mycursor.fetchall()
        for x in myresult:
            to_string += str(x) + """
"""
        return to_string

    def update_all(self, what, update):
        sql = "UPDATE help SET " + what + " = '" + update + "'"
        self.mycursor.execute(sql)
        self.mydb.commit()

    def get_names(self):
        names = []
        self.mycursor.execute("SELECT * FROM mytry.help")
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
    db = Database()

    db.add('yuval', 'boiiiii', 90)

    print(db.to_string())
    print(db.get_winner()[0::2])


if __name__ == "__main__":
    main()
