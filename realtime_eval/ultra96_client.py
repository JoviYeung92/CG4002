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
from MLP_predict_fpga import ETC_predict, ETC_start, getPosWeights, position_predict
import datetime
# imports for SQL
import mysql.connector
import sshtunnel
import pymysql
import paramiko
import pandas as pd
from paramiko import SSHClient
from sshtunnel import SSHTunnelForwarder
from os.path import expanduser
import pytz
import copy
import pickle
# from sklearn.ensemble import ExtraTreesClassifier
#import sklearn

"""
We will be using python sockets and send data to the local database
"""

### this runs on the ultra96 and connects to the eval_server

GROUP_ID = 18
SECRET_KEY = "abcdefghijklmnop"
SQL_SECRET_KEY = "abcdefghijklmnop"
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
    3 : "windowwipe",
    4 : "pushback",
    5 : "elbowlock",
    6 : "scarecrow",
    7 : "shouldershrug",
    8 : "logout",
    9 : "left",
    10 : "right",
    11 : "nomove"
}

PREDICTION_MAP_SQL = {
    0 : "HAIR",
    1 : "ROCKET",
    2 : "ZIGZAG",
    3 : "WINDOWS",
    4 : "PUSHBACK",
    5 : "ELBOW_LOCK",
    6 : "SCARECROW",
    7 : "SHOULDER_SHRUG",
    8 : "LOGOUT",
    9 : "LEFT",
    10 : "RIGHT",
    11 : "NOMOVE"
}


PREDICTION_COUNT = {
    0 : 0,
    1 : 0,
    2 : 0,
    3 : 0,
    4 : 0,
    5 : 0,
    6 : 0,
    7 : 0,
    8 : 0,
    9 : 0,
    10 : 0,
    11 : 0,
    "none" : 0,
    "left" : 0,
    "right" : 0
}

PREDICTION_THRESHOLD_MAP = {
    1 : 3,
    2 : 4,
    3 : 5
}

ENABLE_START_MARKER = False
'''
Set this to True when attempting to connect to evaluation server
'''
CONNECT_TO_EVAL_SERVER = True

'''
Set this to True if you want to send data to sql database
'''
CONNECT_TO_SQL_DATABASE = True

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

DATABASE_AMAZON_HOST = "ec2-34-239-124-200.compute-1.amazonaws.com"

CONNECTION_PORT = 15005
SQL_TARGET_PORT = 5678

PRINT_LOW_PRIORITY_STATEMENTS = True

NUM_OF_DANCERS = 3 # adjust this everytime to detect start of dance move
PREDICTION_THRESHOLD = PREDICTION_THRESHOLD_MAP[NUM_OF_DANCERS] # once this many same predictions are made, sent to eval server

class Ultra96_client(Thread):
    def __init__(self, ip_addr, port_num):
        super(Ultra96_client, self).__init__()
        self.shutdown = threading.Event()

        # synchronization data structures for laptop <=> ultra96

        self.laptop_data_map = {}
        self.laptop_data_map[0] = deque()
        self.laptop_data_map[1] = deque()
        self.laptop_data_map[2] = deque()

        self.laptop_positional_data_map = {}
        self.laptop_positional_data_map[0] = deque()
        self.laptop_positional_data_map[1] = deque()
        self.laptop_positional_data_map[2] = deque()

        # some prediction essentials
        self.current_sync_delay = 0
        self.current_positions = "1 2 3"
        self.previous_actual_positions = "1 2 3" # dancers will start off like this

        self.has_predicted_position_dancer_1 = False
        self.has_predicted_position_dancer_2 = False
        self.has_predicted_position_dancer_3 = False
        self.dancer_1_status = "none"
        self.dancer_2_status = "none"
        self.dancer_3_status = "none"
        self.dancer1_pos = 1
        self.dancer2_pos = 2
        self.dancer3_pos = 3

        self.dancing_has_started = False #False

        self.DANCER_ID_MAP = {}

        self.data_collection_list = []

        # deques data for sql database
        self.sql_data_queue = deque()
        self.sql_data_prediction_queue = deque()
        self.sql_data_final_prediction_queue = deque()

        # dummy variable for the purpose of testing to stimulate log out
        self.num_moves_predicted = 0

        # dictionary to store the start timings
        self.start_time_map_dancers = {}
        self.first_dance_timing = time.time()

        # run lucas start code
        self.overlay, self.dma = ETC_start()
        self.layer_0_position,  self.layer_1_position, self.layer_2_position, self.layer_0_bias_pos, self.layer_1_bias_pos, self.layer_2_bias_pos = getPosWeights()
        self.load_pickle_file()
        
        x = input("Press enter to establish all the connections")

        if CONNECT_TO_EVAL_SERVER:
            """
            Connects to the evaluation server on public ip
            Sends predicted data to the evaluation server
            Receives previous correct dancer's positions
            """
            self.init_eval_server_connection(ip_addr, port_num, 0)

        if CONNECT_TO_SQL_DATABASE:
            '''
            Spawns the connection to SQL database on a separate thread
            '''
            self.sql_task()
            print("SQL server on Ultra96 started. You may run the sql client on laptop")

        # call shreyas method using a thread
        self.prediction_thread = Thread(target=self.generate_predictions)
        self.prediction_thread.daemon = True
        self.prediction_thread.start()

        # connect to the laptops
        self.init_connections_to_laptops()

        # just block. Find some condition for this such as after sending the logout action
        while True:
            time.sleep(1000)

        """
        Terminates the programme after necessary communications with
        Ultra96 have been done
        """
        self.stop()

    """
    Encrypts the data message that is to be sent to evaluation server
    with AES encryption library and returns the encrypted message
    """
    def encrypt_message(self, plain_text):
        # print("ID Number: " + str(self.id))
        print("I'm sending this to server: " + plain_text)
        iv = Random.new().read(AES.block_size)
        print(plain_text)
        plain_text = plain_text.rjust(48, " ") # insert left padding
        aes = AES.new(SECRET_KEY.encode("utf-8"), AES.MODE_CBC, iv)
        cipher_text = aes.encrypt(plain_text.encode("utf-8"))
        encoded_message = base64.b64encode(cipher_text)
        return encoded_message

    def encrypt_message_for_sql(self, plain_text):
        iv = Random.new().read(AES.block_size)
        plain_text = plain_text.rjust(128, " ") # insert left padding
        aes = AES.new(SQL_SECRET_KEY.encode("utf-8"), AES.MODE_CBC, iv)
        cipher_text = aes.encrypt(plain_text.encode("utf-8"))
        encoded_message = base64.b64encode(cipher_text)
        return encoded_message

    """
    Parses the data to be sent to evaluation server
    Encyrpts the data
    Sends the data to the evaluation server by socket
    """
    def send_message_to_eval_server(self, action):
        # calculate the sync delay here
        timings = []
        timings_index = 0
        for key in self.start_time_map_dancers:
            timings.append(float(self.start_time_map_dancers[key]))
            if timings[timings_index] == -1:
                print(f"the start timing of laptop {key} is -1")
            timings_index += 1
        # self.current_positions = self.get_final_position(self.previous_actual_positions, self.dancer_1_status, self.dancer_2_status, self.dancer_3_status)
        print(f"THE FINAL POSITION PREDICTION FOR THIS IS: {self.current_positions}")
        self.current_sync_delay = (max(timings) - min(timings)) / 1000
        self.current_sync_delay = str(self.current_sync_delay)
        msg = "#" + self.current_positions + "|" + action + "|" + self.current_sync_delay + "|"
        print(f"Sending this to the eval server: {msg}")
        self.sql_data_final_prediction_queue.append(self.pack_final_prediction_for_sql([self.current_sync_delay, self.current_positions, action]))
        self.eval_server_socket.send(self.encrypt_message(msg))
        # reset the time map
        for key in self.start_time_map_dancers:
            self.start_time_map_dancers[key] = -1
        # reset anything u want here
        self.dancer_1_status = "none"
        self.dancer_2_status = "none"
        self.dancer_3_status = "none"
        self.first_dance_timing = time.time()
        while True:
            data_packet = self.eval_server_socket.recv(1024)
            if not len(data_packet):
                print("Data packet is empty")
                self.eval_server_socket.close()
            else:
                self.previous_actual_positions = data_packet.decode("utf-8")
                print(f"Previous positions from eval_server: {self.previous_actual_positions}")
                
                # sending the eval server log out:
                # if self.num_moves_predicted >= 12:
                #     self.send_message_to_eval_server("logout")
                break

    def print_current_sync_delay(self):
        timings = []
        for key in self.start_time_map_dancers:
            start_time = self.start_time_map_dancers[key]
            if start_time != -1:
                timings.append(float(start_time))
        if len(timings) == 0:
            print("no timings inside the timings list")
        else:
            # print(f"THE CURRENT SYNC DELAY: {(max(timings) - min(timings)) / 1000}")
            pass
    """
    Creates server socket on Ultra96 to listen for connections from laptops
    Spawns a thread to receive data from laptop for each laptop (up to 3 laptops)
    Puts the data received from the laptops into a single global data queue
    """
    def init_connections_to_laptops(self):
        print("Ultra96 server is starting up to receive connections from 3 dancer laptops")
        self.xilinx_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.xilinx_ip_addr = "137.132.86.241"
        self.xilinx_socket.bind((self.xilinx_ip_addr, CONNECTION_PORT))
        self.xilinx_socket.listen(20)

        laptop_connection_counter = 0;
        while True:
            laptop_socket, laptop_address = self.xilinx_socket.accept()
            laptop_socket.settimeout(30)
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

    def load_pickle_file(self):
        self.clf_frequency_ensemble = pickle.load(open('clf_ensemble_Shre_v2.pkl', 'rb'))
        self.clf_frequency_ensemble.n_jobs = 1
        print("Loaded pickle file")
        # return clf_frequency_ensemble

    def write_to_file(self, move_name):
        hasWrittenToFile = False
        while not hasWrittenToFile:
            if time.time() > FILE_WRITE_END_TIME:
                print("starting to write the data to the file")
                file_name = move_name + ".txt"
                f = open(file_name, 'a')
                for i in self.data_collection_list:
                    dataRow = {}
                    dataRow["roll"] = i[0]
                    dataRow["pitch"] = i[1]
                    dataRow["yaw"] = i[2]
                    dataRow["AccX"] = i[3]
                    dataRow["AccY"] = i[4]
                    dataRow["AccZ"] = i[5]
                    dataRow["millis"] = 0
                    f.write(str(dataRow))
                f.close()
                print("finished writing the data to the file")
                hasWrittenToFile = True
            time.sleep(5)

    """
    One thread will be spawned with this method for each laptop connection.
    It will receive the data from the laptop and put it into a 
    global queue shared by all such threads to house all data from laptops
    """
    def receive_data_from_laptop(self, id, laptop_socket, laptop_addr):
        print(f"thread {id} has started")
        sql_data_dropper = 0
        while True:
            # try:
            msg = laptop_socket.recv(256)
            curr_time = time.time()
            if (curr_time - 0 >= self.laptop1_connected_timing) and msg:
                full_msg = self.decrypt_message_from_laptop(msg)
                temp_datas = full_msg.split("|")
                data_type = int(temp_datas[1])
                # dancer_laptop_id = int(temp_datas[0][1:])
                dancer_num = int(temp_datas[0][1:])
                # print(f"THE DANCER NUMBER FOR THIS DANCER IS: {dancer_num}")
                if data_type == 0:
                    #if DATA_COLLECTION_MODE:
                        # self.data_collection_list.append(packed_data)
                    packed_data = self.extract_and_pack_data_from_laptop(full_msg)
                    if self.dancing_has_started and packed_data != 0:
                        self.laptop_data_map[dancer_num - 1].append(packed_data)
                        if sql_data_dropper % 4 == 0:
                            packed_for_sql_data = self.pack_real_time_data_for_sql(packed_data, dancer_num)
                            self.sql_data_queue.append(packed_for_sql_data)
                        sql_data_dropper += 1
                        if not CONNECT_TO_EVAL_SERVER:
                            if PRINT_LOW_PRIORITY_STATEMENTS:
                                print(f"data received {dancer_num}: {packed_data}")
                    else:
                        print("DANCING HAS NOT STARTED YET")
                elif data_type == 1:
                    positional_data = [float(full_msg.split("|")[2])]
                    self.laptop_positional_data_map[dancer_num - 1].append(positional_data)
                else:
                    print(f"Data type should never enter this state: {data_type}")
            elif msg:
                print("dropped packet")
            time.sleep(0.2)
    
    def get_dancer_num_from_laptop_id(self, dancer_laptop_id):
        dancer_num = -1
        if dancer_laptop_id in self.DANCER_ID_MAP:
            dancer_num = self.DANCER_ID_MAP[dancer_laptop_id]
        else:
            dancer_num = 1
            for key in self.DANCER_ID_MAP:
                dancer_num += 1
            self.DANCER_ID_MAP[dancer_laptop_id] = dancer_num
        if dancer_num == -1:
            print("ERROR IN DANCER NUMBER!!!!")
        return dancer_num

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
        
        if not self.dancing_has_started:
            count = 0
            for key in self.start_time_map_dancers:
                count += 1
            print(f"Number of current dancers: {count}")
            if count >= (NUM_OF_DANCERS):
                self.dancing_has_started = True
                self.first_dance_timing = time.time()
                print(f"First dance timing has been set")
            return 0
        else:
            # if not self.dancing_has_started:
            # self.print_current_sync_delay()
            laptop_id = int(laptop_id)
            self.laptop_positional_data_map[laptop_id - 1].append(data[10])
            return [g_x, g_y, g_z, a_x, a_y, a_z]

    def pack_real_time_data_for_sql(self, data, dancer_num):
        # the first 1 indicates that this is for real_time_data table
        return str((1, data[0], data[1], data[2], data[3], data[4], data[5], dancer_num, datetime.datetime.now(pytz.timezone('Asia/Singapore')).strftime('%Y-%m-%d %H:%M:%S'), datetime.datetime.now(pytz.timezone('Asia/Singapore')).strftime('%Y-%m-%d %H:%M:%S')))

    def pack_prediction_data_for_sql(self, data):
        return str((2, data[0], data[1], data[2], data[3], data[4]))

    # TODO update the latency
    def pack_final_prediction_for_sql(self, data):
        dancer_positions = data[1].split(" ")
        dancer1_pos = dancer_positions[0]
        dancer2_pos = dancer_positions[1]
        dancer3_pos = dancer_positions[2]
        final_pos_string = dancer1_pos + "-" + dancer2_pos + "-" + dancer3_pos
        return str((3, data[0], final_pos_string, data[2], 17.05))

    def decrypt_message_from_laptop(self, message):
        message = message.decode("utf-8").strip()
        decoded_message = base64.b64decode(message)
        iv = decoded_message[:16]
        secret_key = bytes(LAPTOP_ULTRA96_SECRET_KEY, encoding="utf-8")
        cipher = AES.new(secret_key, AES.MODE_CBC, iv)
        decrypted_message = cipher.decrypt(decoded_message[16:]).strip()
        decrypted_message = decrypted_message.decode("utf8")
        return decrypted_message

    """
    Creates a python socket and establishes connection to the evaluation server
    Spawns a thread to communicate between Ultra96 and evaluation server
    """
    def init_eval_server_connection(self, ip_addr, port_num, id):
        print("ultra96 client starting up on {0}".format(port_num))
        self.eval_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        eval_server_address = (ip_addr, port_num)
        self.eval_server_socket.connect(eval_server_address)
        #self.eval_server_socket.setblocking(True)
        print("client socket on ultra96 has connected to evaluation server")
    
    def feature_extraction(self, in_data):
        print("entered inside feature extraction")
        features = get_features(in_data)
        print("get_features completed")
        # clf_frequency_ensemble = pickle.load(open('clf_ensemble_Shre_v2.pkl', 'rb'))
        # print("Pickle load works")
        # clf_frequency_ensemble.n_jobs = 1
        # p = clf_frequency_ensemble.predict(X_test)
        # p = self.clf_frequency_ensemble.predict([features])
        # print(f"output of feature extraction: {p}")
        # return p[0]
        output = ETC_predict(features, self.overlay, self.dma)
        return output  

    def feature_extraction_position(self, in_data):
        features = get_features(in_data)
        output = position_predict(features, self.layer_0_position,  self.layer_1_position, self.layer_2_position, self.layer_0_bias_pos, self.layer_1_bias_pos, self.layer_2_bias_pos)
        return (output + 9)

    def get_final_position(self, in_position='1 2 3', dancer1move='none', dancer2move='none', dancer3move='none'):
        print(f"Previous Moves: {in_position} First move: {dancer1move}, Second Move: {dancer2move}, Third Move: {dancer3move}")
        in_pos = in_position.split()
        in_pos = [int(i) for i in in_pos]
        if len(in_pos) != 3:
            print('-----------------------------')
            print('Should never enter this state')
            print('-----------------------------')
            in_pos = [1, 2, 3]
        d1, d2, d3 = in_pos
        """
        Map d1, d2, d3 into the right variables dancer1_move, dancer2_move and dancer3_move
        For ex if d1, d2, d3 = 2, 3, 1 and initial dancer1_move = 'left', dancer2_move = 'right' and dancer3_move = 'none'
        map left, right, none to 2, 3, 1 that is right, none, left
        """
        if d1 == 1:
            dancer1_move = dancer1move
        elif d1 == 2:
            dancer1_move = dancer2move
        else:
            dancer1_move = dancer3move
        if d2 == 1:
            dancer2_move = dancer1move
        elif d2 == 2:
            dancer2_move = dancer2move
        else:
            dancer2_move = dancer3move
        if d3 == 1:
            dancer3_move = dancer1move
        elif d3 == 2:
            dancer3_move = dancer2move
        else:
            dancer3_move = dancer3move

        out_pos = in_pos
        if dancer1_move == 'right' and dancer2_move == 'right' and dancer3_move == 'left':
            out_pos = [d3, d1, d2]
        elif dancer1_move == 'right' and dancer2_move == 'none' and dancer3_move == 'left':
            out_pos = [d3, d2, d1]
        elif dancer1_move == 'right' and dancer2_move == 'left' and dancer3_move == 'none':
            out_pos = [d2, d1, d3]
        elif dancer1_move == 'right' and dancer2_move == 'left' and dancer3_move == 'left':
            out_pos = [d2, d3, d1]
        elif dancer1_move == 'none' and dancer2_move == 'right' and dancer3_move == 'left':
            out_pos = [d1, d3, d2]
        else:
            out_pos = [d1, d2, d3]
        # if dancer1_move == 'right':
        #     if dancer2_move == 'right' and dancer3_move == 'left':
        #         out_pos = [d3, d1, d2]
        #     if dancer2_move == 'none' and dancer3_move == 'left':
        #         out_pos = [d3, d2, d1]
        #     if dancer2_move == 'left' and dancer3_move == 'none':
        #         out_pos = [d2, d1, d3]
        #     if dancer2_move == 'left' and dancer3_move == 'left':
        #         out_pos = [d2, d3, d1]
        #     else:
        #         val = random.random()
        #         if val < 0.25:
        #             out_pos = [d3, d1, d2]
        #         elif val < 0.5:
        #             out_pos = [d3, d2, d1]
        #         elif val < 0.75:
        #             out_pos = [d2, d1, d3]
        #         else:
        #             out_pos = [d2, d3, d1]
        # elif 
        # elif dancer1_move == 'right' and dancer2_move == 'none' and dancer3_move == 'left':
        #     out_pos = [d3, d2, d1]
        # elif dancer1_move == 'right' and dancer2_move == 'left' and dancer3_move == 'none':
        #     out_pos = [d2, d1, d3]
        # elif dancer1_move == 'right' and dancer2_move == 'left' and dancer3_move == 'left':
        #     out_pos = [d2, d3, d1]
        # elif dancer1_move == 'none' and dancer2_move == 'right' and dancer3_move == 'left':
        #     out_pos = [d1, d3, d2]
        # else:
        #     out_pos = [d1, d2, d3]
        string_to_return = ' '.join([str(i) for i in out_pos])
        print(f"THE POSITION RETURNED BY SHREYAS FUNCTION: {string_to_return}")
        return string_to_return


    def position_extraction(self, in_data):
        posDict = {
            'S' : 0,
            'L' : 0,
            'R' : 0,
            '?' : 0
        }
        print(f"Positional data: {in_data}")
        for data in in_data:
            posDict[data] += 1
        total_num = posDict['S'] + posDict['L'] + posDict['R']
        if total_num == 0:
            return "none"
        percentage_left = (posDict['L'] / total_num)
        percentage_right = (posDict['R'] / total_num)
        percentage_still = (posDict['S'] / total_num)
        if percentage_left >= 0.3 and percentage_right >= 0.3:
            if percentage_left > percentage_right:
                return "left"
            else:
                return "right"
        elif percentage_left >= 0.3:
            return "left"
        elif percentage_right >= 0.3:
            return "right"
        else:
            return "none"

    def generate_predictions(self):
        print("=====================Running prediction==================")
        sql_pred1_counter = 0
        sql_pred2_counter = 0
        sql_pred3_counter = 0
        sql_data_rate = 1 # per person
        time_for_position_change = 6 # 2.5 #2
        time_for_position_change_end = 8.56 # 5 # 4.56
        while True:
            start = time.time()
            data_deque0 = deque()
            data_deque1 = deque()
            data_deque2 = deque()
            if self.laptop_data_map[0]:
                data_deque0 = self.laptop_data_map[0].copy()
                self.laptop_data_map[0] = deque()
            if self.laptop_data_map[1]:
                data_deque1 = self.laptop_data_map[1].copy()
                self.laptop_data_map[1] = deque()
            if self.laptop_data_map[2]:
                data_deque2 = self.laptop_data_map[2].copy()
                self.laptop_data_map[2] = deque()
            data_list_0 = []
            data_list_1 = []
            data_list_2 = []
            while data_deque0:
                data_list_0.append(data_deque0.popleft())
            while data_deque1:
                data_list_1.append(data_deque1.popleft())
            while data_deque2:
                data_list_2.append(data_deque2.popleft())
            result0 = 0
            result1 = 1
            result2 = 2
            time_diff = time.time() - self.first_dance_timing
            check_pos = (time_diff > time_for_position_change and time_diff < time_for_position_change_end ) # boolean
            print(f"Value of check_pos is {check_pos}")
            if len(data_list_0) > 0:
                try:
                    if check_pos and not self.has_predicted_position_dancer_1:
                        result0 = self.position_extraction(copy.deepcopy(self.laptop_positional_data_map[0]))
                        self.laptop_positional_data_map[0] = deque()
                        print(f"A POSITION PREDICTION HAS BEEN MADE for dancer 1 ==========>: {result0}")
                        self.dancer_1_status = result0
                        print(f"A POSITION HAS BEEN Updated for dancer 1===========>: {result0}")
                        self.has_predicted_position_dancer_1 = True
                    else:
                        result0 = self.feature_extraction(data_list_0)
                        print(f"result0 is {result0}")
                        # if PRINT_LOW_PRIORITY_STATEMENTS:
                        print(f"PREDICTED RESULT FOR DANCER 1: {PREDICTION_MAP[result0]}")
                        sql_pred1_counter += 1
                        if sql_pred1_counter % sql_data_rate == 0:
                            self.sql_data_prediction_queue.append(self.pack_prediction_data_for_sql([PREDICTION_MAP_SQL[result0], self.dancer1_pos, 1, datetime.datetime.now(pytz.timezone('Asia/Singapore')).strftime('%Y-%m-%d %H:%M:%S'), datetime.datetime.now(pytz.timezone('Asia/Singapore')).strftime('%Y-%m-%d %H:%M:%S')]))
                        PREDICTION_COUNT[result0] += 1
                except Exception as e:
                    print(e)
            if len(data_list_1) > 0:
                try:
                    if check_pos and not self.has_predicted_position_dancer_2:
                        result1 = self.position_extraction(copy.deepcopy(self.laptop_positional_data_map[1]))
                        self.laptop_positional_data_map[1] = deque()
                        print(f"A POSITION PREDICTION HAS BEEN MADE for dancer 2 ==========>: {result1}")
                        self.dancer_2_status = result1
                        print(f"A POSITION HAS BEEN Updated for dancer 2 ===========>: {result1}")
                        self.has_predicted_position_dancer_2 = True
                    else:
                        result1 = self.feature_extraction(data_list_1)
                        print(f"result0 is {result1}")
                        # if PRINT_LOW_PRIORITY_STATEMENTS:
                        print(f"PREDICTED RESULT FOR DANCER 2: {PREDICTION_MAP[result1]}")
                        sql_pred1_counter += 1
                        if sql_pred1_counter % sql_data_rate == 0:
                            self.sql_data_prediction_queue.append(self.pack_prediction_data_for_sql([PREDICTION_MAP_SQL[result1], self.dancer2_pos, 2, datetime.datetime.now(pytz.timezone('Asia/Singapore')).strftime('%Y-%m-%d %H:%M:%S'), datetime.datetime.now(pytz.timezone('Asia/Singapore')).strftime('%Y-%m-%d %H:%M:%S')]))
                        PREDICTION_COUNT[result1] += 1
                except Exception as e:
                    print(e)
            if len(data_list_2) > 0:
                try:
                    if check_pos:
                        result2 = self.position_extraction(copy.deepcopy(self.laptop_positional_data_map[2]))
                        self.laptop_positional_data_map[2] = deque()
                        print(f"A POSITION PREDICTION HAS BEEN MADE for dancer 3==========>: {result2}")
                        self.dancer_3_status = result2
                        print(f"A POSITION HAS BEEN Updated for dancer 3===========>: {result2}")
                        self.has_predicted_position_dancer_3 = True
                    else:
                        result2 = self.feature_extraction(data_list_2)
                        print(f"result0 is {result2}")
                        # if PRINT_LOW_PRIORITY_STATEMENTS:
                        print(f"PREDICTED RESULT FOR DANCER 3: {PREDICTION_MAP[result2]}")
                        sql_pred1_counter += 1
                        if sql_pred1_counter % sql_data_rate == 0:
                            self.sql_data_prediction_queue.append(self.pack_prediction_data_for_sql([PREDICTION_MAP_SQL[result2], self.dancer3_pos, 3, datetime.datetime.now(pytz.timezone('Asia/Singapore')).strftime('%Y-%m-%d %H:%M:%S'), datetime.datetime.now(pytz.timezone('Asia/Singapore')).strftime('%Y-%m-%d %H:%M:%S')]))
                        PREDICTION_COUNT[result2] += 1
                except Exception as e:
                    print(e)
            print(f"++++ CURRENT PREDICTION COUNTS: {PREDICTION_COUNT}")
            max_record = max(PREDICTION_COUNT[result0], PREDICTION_COUNT[result1], PREDICTION_COUNT[result2])
            print(f"the current maximum record {max_record}")
            if self.has_predicted_position_dancer_1 and self.has_predicted_position_dancer_2 and self.has_predicted_position_dancer_3:
                self.current_positions = self.get_final_position(self.previous_actual_positions, self.dancer_1_status, self.dancer_2_status, self.dancer_3_status)
                data = self.current_positions.split(" ")
                self.dancer1_pos = data[0]
                self.dancer2_pos = data[1]
                self.dancer3_pos = data[2]

            if max_record >= PREDICTION_THRESHOLD:
                # send the prediction to eval server
                print("Inside max_record >= prediction_threshold")
                dance_prediction = ""
                if PREDICTION_COUNT[result0] ==  max_record:
                    dance_prediction = PREDICTION_MAP[result0]
                elif PREDICTION_COUNT[result1] == max_record:
                    dance_prediction = PREDICTION_MAP[result1]
                elif PREDICTION_COUNT[result2] == max_record:
                    dance_prediction = PREDICTION_MAP[result2]
                else:
                    print("Code should not have entered this state")
                    dance_prediction = PREDICTION_MAP[result0] # dummy record
                # if time_diff > 40 and dance_prediction == "logout":
                #     dance_prediction = "zigzag"
                print(f"final prediction for this dance move: {dance_prediction}")
                self.num_moves_predicted += 1
                # reset the prediction counts to 0
                self.reset_prediction_count()

                # reset the positional prediction map to 0 and the positional data to 0
                self.reset_position_prediction_data()

                if CONNECT_TO_EVAL_SERVER:
                    if self.num_moves_predicted >= 32:
                        self.send_message_to_eval_server("logout")
                    else:
                        self.send_message_to_eval_server(dance_prediction)

            end = time.time()
            print(f"Time taken: {end - start}")
            # sleep for 2.56 seconds
            rest_time = 2.56 - (end - start)
            if rest_time > 0:
                time.sleep(rest_time)

    def reset_position_prediction_data(self):
        self.dancer_1_status = "none"
        self.dancer_2_status = "none"
        self.dancer_3_status = "none"
        self.laptop_positional_data_map[0] = deque()
        self.laptop_positional_data_map[1] = deque()
        self.laptop_positional_data_map[2] = deque()
        self.has_predicted_position_dancer_1 = False
        self.has_predicted_position_dancer_2 = False
        self.has_predicted_position_dancer_3 = False

    '''
    Resets the global prediction counts of all dance moves to 0
    Called after a final prediction has been made for a dance move
    '''
    def reset_prediction_count(self):
        for i in range(len(PREDICTION_MAP)):
            PREDICTION_COUNT[i] = 0

    def sql_task(self):
        print("Establishing connection with SQL database")
        self.init_connection_to_laptop_sql_connector()
        self.sql_data_piping_thread = Thread(target=self.connect_to_laptop_sql_connector)
        self.sql_data_piping_thread.daemon = True
        self.sql_data_piping_thread.start()

    # establish connection with the sql 
    def init_connection_to_laptop_sql_connector(self):
        self.xilinx_sql_connector_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.xilinx_ip_addr = "137.132.86.241"
        self.xilinx_sql_connector_socket.bind((self.xilinx_ip_addr, SQL_TARGET_PORT))
        self.xilinx_sql_connector_socket.listen(1)
        
    def connect_to_laptop_sql_connector(self):
        while True:
            self.sql_socket, self.sql_laptop_address = self.xilinx_sql_connector_socket.accept()
            print("CONNECTION RECEIVED FROM THE SQL SERVER")
            while True:
                if self.sql_data_queue:
                    data = self.sql_data_queue.popleft()
                    print(f"sending this data {data}")
                    encrypted_data = self.encrypt_message_for_sql(data)
                    newPadLength = 512 - len(encrypted_data)
                    for i in range(newPadLength):
                        encrypted_data = " ".encode("utf-8") + encrypted_data
                    try:
                        self.sql_socket.send(encrypted_data)
                    except Exception as e:
                        print("Error occurred while sending real time data to sql socket")
                        print(e)

                if self.sql_data_prediction_queue:
                    data = self.sql_data_prediction_queue.popleft()
                    print(f"sending this data {data}")
                    encrypted_data = self.encrypt_message_for_sql(data)
                    newPadLength = 512 - len(encrypted_data)
                    for i in range(newPadLength):
                        encrypted_data = " ".encode("utf-8") + encrypted_data
                    try:
                        self.sql_socket.send(encrypted_data)
                    except Exception as e:
                        print("Error occurred while sending real time data to sql socket")
                        print(e) 

                if self.sql_data_final_prediction_queue:
                    data = self.sql_data_final_prediction_queue.popleft()
                    print(f"sending this data for final prediction: {data}")
                    encrypted_data = self.encrypt_message_for_sql(data)
                    newPadLength = 512 - len(encrypted_data)
                    for i in range(newPadLength):
                        encrypted_data = " ".encode("utf-8") + encrypted_data
                    try:
                        self.sql_socket.send(encrypted_data)
                    except Exception as e:
                        print("Error occurred while sending real time data to sql socket")
                        print(e)

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

    global CONNECT_TO_SQL_DATABASE
    
    if CONNECT_TO_SQL_DATABASE:
        global SQL_TARGET_PORT
        SQL_TARGET_PORT = int(input("Please enter the target port for SQL <--> Ultra96 socket connection (default is 5678): \n"))
    
    global CONNECTION_PORT
    CONNECTION_PORT = int(input("Please enter the target port for Laptop <--> Ultra96 socket connection (default is 15005): \n"))

    global NUM_OF_DANCERS
    NUM_OF_DANCERS = int(input("How many dancers will be dancing? \n"))

    global PREDICTION_THRESHOLD
    global PREDICTION_THRESHOLD_MAP
    PREDICTION_THRESHOLD = PREDICTION_THRESHOLD_MAP[NUM_OF_DANCERS]
    
    ## connect to the evaluation server 
    my_client = Ultra96_client(ip_addr, port_num)
    my_client.start()


if __name__ == "__main__":
    main()

