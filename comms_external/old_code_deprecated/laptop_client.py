import sys
import socket
import threading
import time
import random
import base64
from Crypto.Cipher import AES
from Crypto import Random
from queue import Queue

SECRET_KEY = "abcdefghijklmnop"

class Laptop_client(threading.Thread):
    global isCommunicating
    def __init__(self, ip_addr, port_num):
        super(Laptop_client, self).__init__()

        self.ip_addr = ip_addr
        self.port_num = port_num
        
        # Create a TCP/IP socket and connect to Ultra96
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.setup_connection()
        self.receive_data()

        # Threads and flag for communication
        self.producer_thread = threading.Thread(target=receive_data)
        self.consumer_thread = threading.Thread(target=send_data)
        isCommunicating = False


        # Create FIFO Queue for inter-thread communication
        self.mailbox = Queue(maxsize = 1024) # buffer for queue

        # for testing purposes
        self.counter = 0

        self.start_communication()

    def setup_connection(self):
        ultra96_address = (self.ip_addr, self.port_num)
        print("Socket is starting up on {0}".format(self.port_num))
        self.socket.connect(ultra96_address)
        self.socket.setblocking(True)

    def start_communication(self):
        isCommunicating = True
        self.producer_thread.start()
        self.consumer_thread.start()
    
    def end_communication(self):
        isCommunicating = False
        self.producer_thread.join()
        self.consumer_thread.join()

    def encrypt_data(self, plain_text):
        print("I'm sending this to ultra96: " + plain_text)
        iv = Random.new().read(AES.block_size)
        print(plain_text)
        plain_text = plain_text.rjust(64, " ") # insert left padding
        aes = AES.new(SECRET_KEY, AES.MODE_CBC, iv)
        cipher_text = aes.encrypt(plain_text)
        encoded_message = base64.b64encode(cipher_text)
        return encoded_message

    def receive_data(self):
        while True:
            # for now, this method will produce dummy data
            # eventually, it has to receive data from the bluno beetles
            a_x = round(random.uniform(0, 1), 2)
            a_y = round(random.uniform(0, 1), 2)
            a_z = round(random.uniform(0, 1), 2)
            g_x = round(random.uniform(0, 1), 2)
            g_y = round(random.uniform(0, 1), 2)
            g_z = round(random.uniform(0, 1), 2)

            # pack the data
            msg = '#' + str(a_x) + "|" + str(a_y) + "|" + str(a_z) + "|" + str(g_x) + "|" + str(g_y) + "|" + str(g_z) + "|"
            
            # encrypt the data
            encrypted_msg = self.encrypt_data(msg)

            # put the data in the global FIFO mailbox
            self.mailbox.put(encrypted_msg)

            self.counter += 1
            time.sleep(0.2) # sleep for 200ms

        
    def send_data(self):
        while isCommunicating and not self.mailbox.empty():
            msg = self.mailbox.get()
            self.socket.send(msg)

            # for testing purposes
            if self.counter > 20:
                end_communication()
                self.stop()

    def stop(self):
        # self.end_communication()
        self.socket.close()
        sys.exit()  

def main():
    # requires the ip of the ultra96 client and the port number for socket connection
    if len(sys.argv) != 3:
        print("Invalid number of arguments")
        print("python laptop_client.py [IP address of ultra96 client] [Port]")
        sys.exit()

    ip_addr = sys.argv[1]
    port_num = int(sys.argv[2])

    # connect to the ultra96 client
    laptop_client = Laptop_client(ip_addr, port_num)
    laptop_client.start()

if __name__ == "__main__":
    main()
