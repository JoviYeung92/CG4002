import sys
import copy
import socket
import random
from pytunneling import TunnelNetwork
from time import sleep
from time import perf_counter
from time import time
from time import time_ns
from math import floor
from threading import Thread
from queue import Queue
import ntplib
from datetime import datetime, timezone
import xlsxwriter
import base64
from Crypto.Cipher import AES
from Crypto import Random
import crc8
from bluepy import btle
from bluepy.btle import BTLEException, Scanner, BTLEDisconnectError
from threading import Lock
import threading
import json

service_uuid = "0000dfb0-0000-1000-8000-00805f9b34fb"
char_uuid = "0000dfb1-0000-1000-8000-00805f9b34fb"

connections = {}
connection_threads = {}
connected_addr=[]
lock=Lock()

main_data={} #strore all info from all thread. bluno_id -> [millis -> data_set]

#listed all bluetooth MAC address.
a = "34:15:13:22:A1:26"
b ="34:15:13:22:A5:72"  #ok ......
c = "2C:AB:33:CC:17:46" 
d = "C8:DF:84:FE:43:70"   #ok
e= "2C:AB:33:CC:68:D4" #ok 
f = "C8:DF:84:FE:52:77" #ok

#define comms bluetooth
glove_bt = d
position_bt = b
#Set up initial state for bluno
bt_addrs = [glove_bt, position_bt]

FIRST_HOP_SSH_ADDRESS = "sunfire.comp.nus.edu.sg"
FIRST_HOP_SSH_USERNAME = "sdsamuel"
FIRST_HOP_SSH_PKEY = "~/.ssh/id_rsa"
FIRST_HOP_SSH_PASSWORD = "iLoveTeam18!"

SECOND_HOP_SSH_ADDRESS = "137.132.86.241"
SECOND_HOP_SSH_USERNAME = "xilinx"
SECOND_HOP_PASSWORD = "xilinx"

TARGET_IP = SECOND_HOP_SSH_ADDRESS
TARGET_PORT = 14899
SECRET_KEY = "abcdefghijklmnop"

tunnel_info = [
    {"ssh_address_or_host": FIRST_HOP_SSH_ADDRESS,
    "ssh_username": FIRST_HOP_SSH_USERNAME,
    "ssh_password": FIRST_HOP_SSH_PASSWORD, # If applicable
    },
    {"ssh_address_or_host": SECOND_HOP_SSH_ADDRESS,
    "ssh_username": SECOND_HOP_SSH_USERNAME,
    "ssh_password": SECOND_HOP_PASSWORD,
    }
]

NTP_SERVER = "uk.pool.ntp.org"
BLUNO_PER_LAPTOP = 2;

LAPTOP_ULTRA96_SECRET_KEY = "abcdefghijklmnop"

HAND_BLUNO_ID = 0
POSITION_BLUNO_ID = 1

'''
          ___
Switch __/ __ for piping data between dummybluno and actual blunos 
Set DATA_SOURCE to True -> data from real Blunos
    DATA_SOURCE to False -> data from DummyBluno2
'''
DATA_SOURCE = False
PRINT_PACKETS = True

BLUNO_TIME_DIFF = 0 # used for synchronizing bluno time to NTP
LAPTOP_TIME_DIFF = 0 # used for synchronizing laptop time to NTP
NTP_TIME_DIFF = 0 # used for synchronizing bluno time to NTP

TUNNEL = 0 # ssh tunnel

class Dancer_Client(Thread):
    def __init__(self):
        super(Dancer_Client, self).__init__()

        """
        Unique identifier for each dancer client
        """
        self.DANCER_CLIENT_ID = self.get_unique_dancer_client_id()

        """
        global data structures for intercommunication between threads
        """
        self.bluno_data_queue = Queue()
        self.processed_data_queue = Queue()
        self.bluno_done = 0
        self.accuracy_data = []
        self.main_data={}
        self.main_data[0]=Queue()
        self.main_data[1]=Queue()

        # self.initialize_ssh_tunneling()
        self.blunos_started = False

        self.socket_exception = False
        with TunnelNetwork(tunnel_info=copy.deepcopy(tunnel_info), target_ip=TARGET_IP, target_port=TARGET_PORT) as self.tn:
            self.LOCAL_PORT = self.tn.local_bind_port
            print(f"Tunnel available at localhost:{self.LOCAL_PORT}")
            sleep(2)

            self.connect_to_ultra96()

            if not self.blunos_started:
                """
                Start running the dummy bluno
                """ 
                self.producer_thread_1 = Thread(target=self.start_dummy_bluno_2, args=(HAND_BLUNO_ID, self.main_data[0]))
                self.producer_thread_1.daemon = True
                self.producer_thread_1.start()

                self.producer_thread_2 = Thread(target=self.start_dummy_bluno3, args=(POSITION_BLUNO_ID, self.main_data[1]))
                self.producer_thread_2.daemon = True
                self.producer_thread_2.start()

                self.blunos_started = True

            """
            Start consuming the data and sending it to Ultra96
            """
            self.consumer_thread_1 = Thread(target=self.consume_data_test, args=(0,))
            self.consumer_thread_1.daemon = True
            self.consumer_thread_1.start()    

            while not self.socket_exception:
                sleep(5)
        print("SOCKET EXCEPTION has occured and trying to establish reconnection")
        self.socket_ultra96.close()

    def initialize_ssh_tunneling(self):
        self.tn = TunnelNetwork(tunnel_info=tunnel_info, target_ip=TARGET_IP, target_port=TARGET_PORT).__enter__()
        self.LOCAL_PORT = self.tn.local_bind_port
        print(f"Tunnel available at localhost:{self.LOCAL_PORT}")
        print("Tunnel info:")
        print(f"{self.tn}")
        sleep(2)

    # def generate_more_dummy_data(self):
    #     while True:
    #         string_to_send = "i don't why the pipe breaks halp"
    #         self.socket_ultra96_2.send(string_to_send.encode("utf-8"))
    #         print(f"sending {string_to_send}")
    #         sleep(1)

    '''
    Need to edit this method to consume data from the 2 queues for the 2 blunos
    can implement flow control here as well
    '''
    def consume_data_test(self, id):
        while True:
            if not self.main_data[id].empty():
                # print(f"data: {self.main_data[0].get()}")
                mData = self.main_data[id].get()
                try:
                    # convert this into a packet
                    curr_roll = mData["roll"]
                    curr_pitch = mData["pitch"]
                    curr_yaw = mData["yaw"]
                    curr_AccX = mData["AccX"]
                    curr_AccY = mData["AccY"]
                    curr_AccZ = mData["AccZ"]
                    curr_time = mData["millis"]

                    # Hmmmm perhaps u can make an assumption tat when ((AccX >= 1.2 || AccX <= -0.03) && (AccY >= 0.13 || AccY<= -0.25)), dance move has started. I'm not sure if change in position will affect these values tho
                    
                    if ((float(curr_AccX) >= 1.2 or float(curr_AccX) <= -0.03) and (float(curr_AccY) >= 0.13 or float(curr_AccY) <= -0.25)):
                        packet_marker = "a" # start marker
                        print(f"===== this is a start packet =======")
                    else:
                        packet_marker = "b"
                    
                    # correct the time data over here
                    curr_time = int(curr_time)

                    #package all the data into a separate packet    
                    curr_packet = "#" + str(self.DANCER_CLIENT_ID) + "|" +str(id) + "|" + str(curr_time) + "|" + str(curr_roll) + "|" + str(curr_pitch) + "|" + str(curr_yaw) + "|" + str(curr_AccX) + "|" + str(curr_AccY) + "|" + str(curr_AccZ) + "|" + packet_marker + "|"
                    encrypted_packet = self.encrypt_message_to_ultra96(curr_packet)
                    newPadLength = 512 - len(encrypted_packet)
                    for i in range(newPadLength):
                        encrypted_packet = " ".encode("utf-8") + encrypted_packet
                    if PRINT_PACKETS:
                        print(f"sending this packet: {curr_packet}")
                    msg_sent = False
                    while not msg_sent:
                        try:
                            self.socket_ultra96.send(encrypted_packet)
                            msg_sent = True
                        except Exception as e:
                            print("exception in sending the message")
                            print(e)
                            # print("trying to create a new socket to re-establish a connection")
                            # self.initialize_ssh_tunneling()
                            # self.connect_to_ultra96()
                            self.socket_exception = True
                            #self.socket_ultra96.close()
                            #self.connect_to_ultra96()
                            break
                            # msg_sent = True
                except Exception as e:
                    print("======")
                    print("Error in eccrypitng the packet from bluno 1 dance")
                    print(e)
                    self.socket_exception = True
                    #self.socket_ultra96.close()
                    #self.connect_to_ultra96()
                    print("======")

            if self.socket_exception:
                break

            if not self.main_data[1].empty():
                try:
                    mData = self.main_data[1].get()
                    # convert this into a packet
                    curr_AccZ = mData["AccZ"]
                    #package this data into a separate packet
                    curr_packet = "#" + str(self.DANCER_CLIENT_ID) + "|" + str(1) + "|" + str(curr_AccZ) + "|"
                    encrypted_packet = self.encrypt_message_to_ultra96(curr_packet)
                    newPadLength = 512 - len(encrypted_packet)
                    for i in range(newPadLength):
                        encrypted_packet = " ".encode("utf-8") + encrypted_packet
                    if PRINT_PACKETS:
                        print(f"sending this packet: {curr_packet}")
                    msg_sent = False
                    while not msg_sent:
                        try:
                            self.socket_ultra96.send(encrypted_packet)
                            msg_sent = True
                        except Exception as e:
                            print("exception caused by data from bluno 2 - position xx")
                            print("trying to create a new socket to re-establish a connection")
                            print(e)
                            self.socket_exception = True
                            #self.socket_ultra96.close()
                            #self.connect_to_ultra96()
                            msg_sent = True
                except Exception as e:
                    print("exception in exncrypting data from bluno 2 - position")
                    self.socket_exception = True
                    #self.socket_ultra96.close()
                    #self.connect_to_ultra96()
                    print(e)

            if self.socket_exception:
                break
            sleep(0.1)

    def encrypt_message_to_ultra96(self, plain_text):
        iv = Random.new().read(AES.block_size)
        plain_text = plain_text.rjust(128, " ") # insert left padding
        aes = AES.new(LAPTOP_ULTRA96_SECRET_KEY.encode("utf-8"), AES.MODE_CBC, iv)
        cipher_text = aes.encrypt(plain_text.encode("utf-8"))
        encoded_message = base64.b64encode(cipher_text)
        return encoded_message

    """
    Dummy Bluno data generation
    """
    def start_dummy_bluno_2(self, id, laptop_queue):
        mDummyBluno = DummyBluno2(id)
        NTP_Client = ntplib.NTPClient()
        t1 = floor(time_ns() / 1000000)
        bluno_queue, t2 = mDummyBluno.handshake(laptop_queue)
        t3 = floor(time_ns()/ 1000000)
        RTT_BY_TWO = (t3 - t1) / 2
        BLUNO_TIME_DIFF = floor((t3 - RTT_BY_TWO) - t2)
        NTP_TIME_DIFF = BLUNO_TIME_DIFF - LAPTOP_TIME_DIFF
        mDummyBluno.generate_data()

    def start_dummy_bluno3(self, id, laptop_queue):
        mDummyBluno =  DummyBluno3(id)
        bluno_queue = mDummyBluno.handshake(laptop_queue)
        mDummyBluno.generate_data()

    """
    Creates a Python Socket and binds the laptop's local address and local port
    used to create the tunnel to the Ultra96. Informs dancer once connection is
    successfully established
    """
    def connect_to_ultra96(self):
        self.socket_ultra96 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        addr = (socket.gethostbyname(socket.gethostname()), self.LOCAL_PORT)
        self.socket_ultra96.connect(addr)
        print("connected to xilinx")
        print("Socket 1 created")
        sleep(5)
        
    '''
    Returns a random number below 1000 which can be used as unique id
    '''
    def get_unique_dancer_client_id(self):
        random.seed(floor(time()))
        u_id = floor(random.random() * 1000)
        return 555
        return u_id
        


class DummyBluno2:
    def __init__(self, bluno_id, offset = 0):
        self.offset = offset
        self.bluno_id = bluno_id
        self.bluno_queue = Queue()

    def handshake(self, laptop_queue):
        self.laptop_queue = laptop_queue
        t2 = self.get_time_millis()
        return self.bluno_queue, t2

    def generate_data(self):
        # print("Initial waiting for 60s for NONE")
        # sleep(60)
        # print("Going to start")
        num_dance_moves = 100
        num_data_per_move = 100
        for i in range(num_dance_moves):
            for j in range(num_data_per_move):
                current_data = {}
                current_data["roll"] = round(random.uniform(0, 1), 2)
                current_data["pitch"] = round(random.uniform(0, 1), 2)
                current_data["yaw"] = round(random.uniform(0, 1), 2)
                current_data["AccX"] = round(random.uniform(0, 1), 2)
                current_data["AccY"] = round(random.uniform(0, 1), 2)
                current_data["AccZ"] = round(random.uniform(0, 1), 2)
                current_data["millis"] = self.get_time_millis()
                self.laptop_queue.put(current_data)
                sleep(0.1)
            print("Sent one dance move worth of data over")
            sleep(3)
    
    def get_time_millis(self):
        return floor((time() * 1000) % 10000000)
        
class DummyBluno3:
    def __init__(self, bluno_id, offset = 0):
        self.offset = offset
        self.bluno_id = bluno_id
        self.bluno_queue = Queue()

    def handshake(self, laptop_queue):
        self.laptop_queue = laptop_queue
        return self.bluno_queue

    def generate_data(self):
        num_dance_moves = 100
        num_data_per_move = 100
        for i in range(num_dance_moves):
            for j in range(num_data_per_move):
                current_data = {}
                current_data["AccZ"] = round(random.uniform(0,1), 2)
                self.laptop_queue.put(current_data)
                sleep(0.1)
            print("Sent one dance move worth of dummy positional data over")
        sleep(3)

    def get_time_millis(self):
        return floor((time() * 1000) % 10000000)
def main():
    # re-establish connection if connection drops
    while True:
        dancer_client = Dancer_Client()
        dancer_client.start()
        print("EXCEPTION HAS OCCURRED!!!!!! RUNNING THE PROGRAM AGAIN")

if __name__ == "__main__":
    main()