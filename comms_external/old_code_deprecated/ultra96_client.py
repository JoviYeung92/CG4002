import sys
import socket
import threading
import random
import base64
import time
from Crypto.Cipher import AES
from Crypto import Random

### this runs on the ultra96 and connects to the eval_server

GROUP_ID = 18;
SECRET_KEY = "abcdefghijklmnop"

DUMMY_DATA = ['zigzag', 'rocket', 'hair', 'logout']

# create a socket connection to each of the dancer's laptops
LAPTOP_IP = ['192.168.1.73'] 

class Ultra96_client(threading.Thread):
    def __init__(self, ip_addr, port_num):
        super(Ultra96_client, self).__init__()
        
        self.ip_addr = ip_addr
        self.port_num = port_num
        self.id = 0

        # Create a TCP/IP socket and connect to server
        self.shutdown = threading.Event()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.setup_connection()
        self.receive_message()

    def encrypt_message(self, plain_text):
        print("ID Number: " + str(self.id))
        print("I'm sending this to server: " + plain_text)
        iv = Random.new().read(AES.block_size)
        print(plain_text)
        plain_text = plain_text.rjust(48, " ") # insert left padding
        aes = AES.new(SECRET_KEY, AES.MODE_CBC, iv)
        cipher_text = aes.encrypt(plain_text)
        encoded_message = base64.b64encode(cipher_text)
        return encoded_message

    def setup_connection(self):
        client_address = (self.ip_addr, self.port_num)
        print("ultra96 client starting up on {0}".format(self.port_num))
        self.socket.connect(client_address)
        self.socket.setblocking(True)

    def send_message(self, positions, action, sync_delay):
        msg = "#" + positions + "|" + action + "|" + sync_delay + "|"
        self.socket.send(self.encrypt_message(msg))

    def receive_message(self):
        # print("waiting for 10 seconds")
        # time.sleep(10)
        # try to send something first
        action_to_send = "zigzag"
        self.send_message("1 2 3", action_to_send, "1.87")
        while True:
            data_packet = self.socket.recv(1024)
            if not len(data_packet):
                print("Data packet is empty")
                self.socket.close()
            else:
                self.id += 1
                positions_from_server = data_packet.decode("utf-8")
                print(positions_from_server)
                action_to_send = random.choice(DUMMY_DATA)
                while action_to_send == "logout" and self.id < 5:
                    action_to_send = random.choice(DUMMY_DATA)
                self.send_message(positions_from_server, action_to_send, "1.87")
                if action_to_send == "logout":
                    self.stop()
    
    def stop(self):
        self.socket.close()
        sys.exit()

def main():
    if len(sys.argv) != 3:
        print("Invalid number of arguments")
        print('python ultra96_client.py [IP address] [Port]')
        sys.exit()
    
    ip_addr = sys.argv[1]
    port_num = int(sys.argv[2])

    ## connect to the evaluation server 
    my_client = Ultra96_client(ip_addr, port_num)
    my_client.start()

        # pass it the key for decryption
        # print out what it says
        # communicate with the eval_server -> give it whatever info it needs (the predictions)


if __name__ == "__main__":
    main()