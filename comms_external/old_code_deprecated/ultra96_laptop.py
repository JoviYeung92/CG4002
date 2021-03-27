import sys
import socket
import threading
import random
import base64
import time
import select
from Crypto.Cipher import AES
from Crypto import Random


### this is a test module

class ultra96_laptop(threading.Thread):
    def __init__(self, ip_addr, port_num):
        super(ultra96_laptop, self).__init__()

        self.ip_addr = ip_addr
        self.port_num = port_num

        # Create a TCP/IP socket and connect to Clients
        self.setup_connection()

    
    def setup_connection(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.ip_addr, self.port_num))
        self.server_socket.listen()

        self.clientsocket, self.address = self.server_socket.accept()
        print(f"Client at {self.address} has connected")

        # self.socket_list = [self.server_socket]
        # self.client_dict = {}
        # self.num_connected_clients = 0
    
    def receive_message(self):
        while True:
            msg = self.client_socket.recv(1024)
            print("Received: "+msg)

    # def receive_message(self, client_socket):
    #     try:
    #         msg = client_socket.recv(1024)

    #     except:
    #         print("Something went wrong when receiving message")
    #         return False

    # def consume(self):
    #     read_sockets, _, exception_sockets = select.select(self.socket_list, [], self.socket_list)
        
    #     for notified_socket in read_sockets:
    #         if notified_socket == self.server_socket:
    #             client_socket, client_address = server_socket.accept()
                
    #             if self.receive_message(client_socket) is False:
    #                 continue

    #             socket_list.append(client_socket)
    #             clients[client_socket] = self.num_connected_clients
    #             print(f"New connection from user client with id: {self.num_connected_clients}")
    #             self.num_connected_clients += 1
    #         else:
    #             message = receive_message(notified_socket)

    #             if message is False:
    #                 print(f"Closed a connection")
    #                 self.socket_list.remove(notified_socket)
    #                 del self.client_dict[notified_socket]
    #                 continue
                
    #             user_id = clients[notified_socket]
    #             print(f"Received a message from {user_id}")

    #             # send the information to the AI for prediction

        


            
            


        

        

def main():
    # requires the ip of the ultra96 client and the port number for socket connection
    if len(sys.argv) != 3:
        print("Invalid number of arguments")
        print("python laptop_client.py [IP address of ultra96 client] [Port]")
        sys.exit()

    ip_addr = sys.argv[1]
    port_num = int(sys.argv[2])

    # connect to the ultra96 client
    ultra96_laptop1 = ultra96_laptop(ip_addr, port_num)
    ultra96_laptop1.start()

if __name__ == "__main__":
    main()
