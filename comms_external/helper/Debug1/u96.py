import sys
import socket
import threading
import random
import base64
import time
from math import floor
from Crypto.Cipher import AES
from Crypto import Random
from threading import Thread
from queue import Queue
from collections import deque
from features_fpga import get_features
from MLP_predict_fpga import MLP_predict
from MLP_predict_fpga import MLP_start

# imports for SQL
import mysql.connector
import sshtunnel
import pymysql
import paramiko
import pandas as pd
from paramiko import SSHClient
from sshtunnel import SSHTunnelForwarder
from os.path import expanduser

### this runs on the ultra96 and connects to the eval_server

GROUP_ID = 18
SECRET_KEY = "abcdefghijklmnop"
LAPTOP_ULTRA96_SECRET_KEY = "abcdefghijklmnop"

DUMMY_DATA = ['zigzag', 'rocket', 'hair', 'logout']

# create a socket connection to each of the dancer's laptops
LAPTOP_IP = ['192.168.1.73'] 
MAX_LAPTOP_CONNECTIONS = 12; #3
BLUNO_PER_LAPTOP = 1;

PREDICTION_MAP = {
    0 : "hair",
    1 : "rocket",
    2 : "zigzag",
    3 : "No move"
}

PREDICTION_MAP_SQL = {
    0 : "HAIR",
    1 : "ROCKET",
    2 : "ZIGZAG",
    3 : "NO MOVE",
    4 : "WINDOWS",
    5 : "PUSHBACK",
    6 : "ELBOW_LOCK",
    7 : "SCARECROW",
    8 : "SHOULDER_SHRUG"
}
PREDICTION_COUNT = {
    0 : 0,
    1 : 0,
    2 : 0,
    3 : 0
}

PREDICTION_THRESHOLD = 10 # once this many same predictions are made, sent to eval server
'''
Set this to True when attempting to connect to evaluation server
'''
CONNECT_TO_EVAL_SERVER = False

'''
Set this to True if you want to send data to sql database
'''
CONNECT_TO_SQL_DATABASE = False

'''
Connection to SQL Database
'''
sql_hostname = 'localhost'
sql_username = 'capstone'
sql_password = 'CG4002Weiyang1997!'
sql_main_database = 'CG4002'
sql_port = 3306
ssh_host = 'little_peter'

ssh_user = 'little-peter'
ssh_port = 22
sql_ip = 'localhost'
ssh_address = '172.25.107.67'
WEI_YANG_IP = '172.25.100.23'

FILE_WRITE_START_TIME = 0
FILE_WRITE_END_TIME = 0
DATA_COLLECTION_MODE = False


class Ultra96_client(Thread):
    def __init__(self, ip_addr, port_num):
        super(Ultra96_client, self).__init__()
        self.shutdown = threading.Event()

        # synchronization data structures for laptop <=> ultra96
        self.laptop_data_queue = deque()
        self.laptop_data_map = {}
        self.laptop_data_map[0] = deque()
        self.laptop_data_map[1] = deque()
        self.laptop_data_map[2] = deque()

        self.laptop_positional_data_map = {}
        self.laptop_positional_data_map[0] = deque()
        self.laptop_positional_data_map[1] = deque()
        self.laptop_positional_data_map[2] = deque()

        # connect to the laptops
        self.init_connections_to_laptops()

        # just block. Find some condition for this such as after sending the logout action
        while True:
            time.sleep(5)

        """
        Terminates the programme after necessary communications with
        Ultra96 have been done
        """
        self.stop() 

    def init_connections_to_laptops(self):
        print("Ultra96 server is starting up to receive connections from 3 dancer laptops")
        self.xilinx_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.xilinx_ip_addr = "137.132.86.241"
        self.xilinx_socket.bind((self.xilinx_ip_addr, 14899))
        self.xilinx_socket.listen(12)

        # I'm accepting connections from 3 laptops only
        laptop_connection_counter = 0;
        while True:
            laptop_socket, laptop_address = self.xilinx_socket.accept()
            laptop_socket.settimeout(20)
            print(f"Connection from {laptop_address} has been established");
            if DATA_COLLECTION_MODE:
                print("Data collection is starting now")
                FILE_WRITE_START_TIME = time.time()
                FILE_WRITE_END_TIME = time.time() + 60 * 3
                # spawn a file writer thread
            laptop_connection_counter += 1
            self.laptop1_connected_timing = time.time()
            if laptop_connection_counter <= MAX_LAPTOP_CONNECTIONS:
                # spawn 1 thread for the each connection
                thread = Thread(target=self.receive_data_from_laptop, args=(laptop_connection_counter, laptop_socket, laptop_address))
                thread.daemon=True
                thread.start()
                if laptop_connection_counter == MAX_LAPTOP_CONNECTIONS:
                    print(f"==== {MAX_LAPTOP_CONNECTIONS} Laptops have been connected with the Ultra96 ====")
                    break;
            else:
                print(f"Warning: more than {MAX_LAPTOP_CONNECTIONS} connections are established")
                break;
        print("end of init connections from laptop")
        while True:
            time.sleep(10)

    """
    One thread will be spawned with this method for each laptop connection.
    It will receive the data from the laptop and put it into a 
    global queue shared by all such threads to house all data from laptops
    """
    def receive_data_from_laptop(self, id, laptop_socket, laptop_addr):
        print(f"thread {id} has started")
        sql_data_dropper = 0
        while True:
            try:
                msg = laptop_socket.recv(512)
                curr_time = time.time()
                if (curr_time - 0 >= self.laptop1_connected_timing) and msg:
                        full_msg = self.decrypt_message_from_laptop(msg)
                        print(full_msg)
                        # extract the data out here
                        data_type = int(full_msg.split("|")[1])
                        if data_type == 0:
                            packed_data = self.extract_and_pack_data_from_laptop(full_msg)
                            self.laptop_data_queue.append(packed_data)
                            self.data_collection_list.append(packed_data)
                            self.laptop_data_map[id - 1].append(packed_data)
                            #pack_for_sql_data = self.pack_data_for_sql(packed_data)
                            if sql_data_dropper % 5 == 0:
                                self.sql_data_queue.append(packed_data)
                                # print("pushed data into sql queue")
                            # else:
                                # print("----Data dropped for sql---")
                            sql_data_dropper += 1
                            if not CONNECT_TO_EVAL_SERVER:
                                print(f"data received {id}: {packed_data}")
                            if msg.decode("utf-8") == "bluno_over":
                                print(f"Closing the socket connection to {laptop_addr}")
                                break
                        elif data_type == 1:
                            positional_data = float(full_msg.split("|")[2])
                            self.laptop_positional_data_map[id - 1].append(positional_data)
                        else:
                            print(f"Data type should never enter this state: {data_type}")
                elif msg:
                    print("dropped packet")
            except Exception as e:
                print("=========")
                print(f"Exception has occurred in receiver thread {id}")
                print(e)
                print("=========")
    # direct data that are dance packets to this metho
    
    """
    This function extracts the dance sensor values and packs it for shreyas AI
    Also, it updates the start timing in the dancer's time map
    """
    def extract_and_pack_data_from_laptop(self, full_msg):
        data = full_msg.split("|")
        laptop_id = data[0][1:]
        a_x = float(data[6])
        a_y = float(data[7])
        a_z = float(data[8])
        g_x = float(data[3])
        g_y = float(data[4])
        g_z = float(data[5])
        packet_marker = data[9]
        curr_time = data[2]
        if packet_marker == "a":
            if laptop_id in self.start_time_map_dancers:
                if self.start_time_map_dancers[laptop_id] == -1:
                    self.start_time_map_dancers[laptop_id] = curr_time
            else:
                self.start_time_map_dancers[laptop_id] = curr_time
        return [g_x, g_y, g_z, a_x, a_y, a_z]

    def pack_data_for_sql(self, data):
        return (data[0], data[1], data[2], data[3], data[4], data[5], "2008-11-11", "2008-11-11")

    def decrypt_message_from_laptop(self, message):
        message = message.decode("utf-8").strip()
        #message = message.strip()
        decoded_message = base64.b64decode(message)
        iv = decoded_message[:16]
        secret_key = bytes(LAPTOP_ULTRA96_SECRET_KEY, encoding="utf-8")
        cipher = AES.new(secret_key, AES.MODE_CBC, iv)
        decrypted_message = cipher.decrypt(decoded_message[16:]).strip()
        decrypted_message = decrypted_message.decode("utf8")
        return decrypted_message
        
    """
    Cleans up resources
    Terminates the programme
    """
                          
    def stop(self):
        self.end = False;
        while True:
            if not self.end:
                time.sleep(3)
            else:
                break
        self.xilinx_socket.close();
        print("socket closed");
        #self.socket.close()
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


if __name__ == "__main__":
    main()