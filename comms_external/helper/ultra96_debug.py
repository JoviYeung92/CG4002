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

        self.previous_actual_positions = 0

        self.data_collection_list = []

        # deques data for sql database
        self.sql_data_queue = deque()
        self.sql_data_prediction_queue = deque()

        # dummy variable for the purpose of testing to stimulate log out
        self.num_moves_predicted = 0

        # dictionary to store the start timings
        self.start_time_map_dancers = {}

        # run lucas start code
        self.overlay, self.dma = MLP_start()

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

        # call shreyas method using a thread
        self.prediction_thread = Thread(target=self.generate_predictions)
        self.prediction_thread.daemon = True
        self.prediction_thread.start()

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

    """
    Parses the data to be sent to evaluation server
    Encyrpts the data
    Sends the data to the evaluation server by socket
    """
    def send_message_to_eval_server(self, positions, action, sync_delay):
        msg = "#" + positions + "|" + action + "|" + sync_delay + "|"
        self.eval_server_socket.send(self.encrypt_message(msg))
        # reset the time map
        for key in self.start_time_map_dancers:
            self.start_time_map_dancers[key] = -1
        while True:
            data_packet = self.eval_server_socket.recv(1024)
            if not len(data_packet):
                print("Data packet is empty")
                self.eval_server_socket.close()
            else:
                self.previous_actual_positions = data_packet.decode("utf-8")
                print(f"Previous positions from eval_server: {self.previous_actual_positions}")
                break

    """
    Creates server socket on Ultra96 to listen for connections from laptops
    Spawns a thread to receive data from laptop for each laptop (up to 3 laptops)
    Puts the data received from the laptops into a single global data queue
    """
    def init_connections_to_laptops(self):
        print("Ultra96 server is starting up to receive connections from 3 dancer laptops")
        self.xilinx_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.xilinx_ip_addr = "137.132.86.241"
        self.xilinx_socket.bind((self.xilinx_ip_addr, 8081))
        self.xilinx_socket.listen(12)

        # I'm accepting connections from 3 laptops only
        laptop_connection_counter = 0;
        while True:
            laptop_socket, laptop_address = self.xilinx_socket.accept()
            # laptop_socket.settimeout(300)
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
            try:
                msg = laptop_socket.recv(512)
                laptop_socket
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
        
        # self.id = 0 # dummy data code
        # self.eval_server_thread = Thread(target=self.receive_message_from_eval_server)
        # self.eval_server_thread.daemon = True
        # self.eval_server_thread.start()

        #self.receive_message()

    # """
    # Sends the predicted data to the evaluation server and retrieves the correct
    # previous dance positions from the evaluation server for recallibration
    # """
    # ## can consider changing name as communicate with eval_server
    # def receive_message_from_eval_server(self):
    #     # need to find an indication to say that connection has been established
    #     print("waiting for 10 seconds")
    #     time.sleep(10)
    #     #try to send something first
    #     action_to_send = "zigzag"
    #     self.send_message_to_eval_server("1 2 3", action_to_send, "1.87")
    #     while True:
    #         data_packet = self.eval_server_socket.recv(1024)
    #         if not len(data_packet):
    #             print("Data packet is empty")
    #             self.eval_server_socket.close()
    #         else:
    #             self.id += 1
    #             positions_from_server = data_packet.decode("utf-8") # append this into global prediction queue
    #             print(f"Positions returned from server: {positions_from_server}")
    #             action_to_send = random.choice(DUMMY_DATA)
    #             while action_to_send == "logout" and self.id < 5:
    #                 action_to_send = random.choice(DUMMY_DATA)
    #             time.sleep(5)
    #             self.send_message_to_eval_server(positions_from_server, action_to_send, "1.87")
    #             if action_to_send == "logout":
    #                 self.stop()    
    #                 self.end = True
    #                 break
    
    def feature_extraction(self, in_data):
        features = get_features(in_data)
        
        output = MLP_predict(features, self.overlay, self.dma)
        return output  


    def generate_predictions(self):
        print("Running prediction")
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
            if len(data_list_0) > 0:
                result0 = self.feature_extraction(data_list_0)
                print(f"Predicted result for dancer 1: {PREDICTION_MAP[result0]}")
                self.sql_data_prediction_queue.append([PREDICTION_MAP_SQL[result0], 1 + floor(random.random() * 10) % 3, 1, "2008-11-11", "2008-11-11"])
                PREDICTION_COUNT[result0] += 1
            if len(data_list_1) > 0:
                result1 = self.feature_extraction(data_list_1)
                print(f"Predicted result for dancer 2: {PREDICTION_MAP[result1]}")
                self.sql_data_prediction_queue.append([PREDICTION_MAP_SQL[result0], 1 + floor(random.random() * 10) % 3, 2, "2008-11-11", "2008-11-11"])
                PREDICTION_COUNT[result1] += 1
            if len(data_list_2) > 0:
                result2 = self.feature_extraction(data_deque2)
                print(f"Predicted result for dancer 3: {PREDICTION_MAP[result2]}")
                self.sql_data_prediction_queue.append([PREDICTION_MAP_SQL[result0], 1 + floor(random.random() * 10) % 3, 3, "2008-11-11", "2008-11-11"])
                PREDICTION_COUNT[result2] += 1
            max_record = max(PREDICTION_COUNT[result0], PREDICTION_COUNT[result1], PREDICTION_COUNT[result2])
            if max_record >= PREDICTION_THRESHOLD:
                # send the prediction to eval server
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
                print(f"final prediction for this dance move: {dance_prediction}")
                self.num_moves_predicted += 1
                if CONNECT_TO_EVAL_SERVER:
                    if self.num_moves_predicted == 13:
                        self.send_message_to_eval_server("1 2 3", "logout", "0.0")
                    else:
                        self.send_message_to_eval_server("1 2 3", dance_prediction, "0.0")
            end = time.time()
            print(f"Time taken: {end - start}")
            # sleep for 2.56 seconds
            rest_time = 2.56 - (end - start)
            if rest_time > 0:
                time.sleep(rest_time)

    '''
    Resets the global prediction counts of all dance moves to 0
    Called after a final prediction has been made for a dance move
    '''
    def reset_prediction_count(self):
        for i in range(len(PREDICTION_MAP)):
            PREDICTION_COUNT[i] = 0

    def sql_task(self):
        print("Establishing connection with SQL database")
        # self.init_connection_to_laptop_sql_connector()
        self.sql_data_piping_thread = Thread(target=self.connect_to_laptop_sql_connector)
        self.sql_data_piping_thread.daemon = True
        self.sql_data_piping_thread.start()

    # establish connection with the sql 
    def init_connection_to_laptop_sql_connector(self):
        self.xilinx_sql_connector_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.xilinx_ip_addr = "137.132.86.241"
        self.xilinx_sql_connector_socket.bind((self.xilinx_ip_addr, 5678))
        self.xilinx_sql_connector_socket.listen(1)
        


    def connect_to_laptop_sql_connector(self):
        connection = mysql.connector.connect(host='ec2-52-91-189-192.compute-1.amazonaws.com', user=sql_username,
            passwd=sql_password, db=sql_main_database,
            port=5001)  
        print("Connected to the sql database")
        query = '''SELECT VERSION();'''
        data = pd.read_sql_query(query, connection)
        print(data)
        rt_counter = 1
        p_counter = 1
        while True:
            if self.sql_data_prediction_queue:
                data = self.sql_data_prediction_queue.popleft()
                print(f"Trying to insert this prediction into sql: {data}")
                try:
                    mySql_insert_query4 = """INSERT INTO predictions
                                            VALUES 
                                            (%s, %s, %s, %s, %s, %s)"""
                    tuple1 = (p_counter, data[0], data[1], 1, data[3], data[4])
                    cursor = connection.cursor()
                    cursor = connection.cursor()
                    cursor.execute(mySql_insert_query4, tuple1)
                    connection.commit()
                    print(cursor.rowcount, "record inserted [prediction]")
                    cursor.close()
                    p_counter += 1
                except mysql.connector.Error as error:
                    print("Failed to insert record {}".format(error))
                    print(f"Printed data: {data}")

            if self.sql_data_queue:
                data = self.sql_data_queue.popleft()
                print(f"Trying to insert this into sql: {data}")
                try:
                    mySql_insert_query1 = """INSERT INTO rawSensorData
                                            VALUES 
                                            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                    cursor = connection.cursor()
                    tuple1 = (rt_counter, data[0], data[1], data[2], data[3], data[4], data[5], data[6], "2008-11-11", "2008-11-11")
                    cursor.execute(mySql_insert_query1, tuple1)
                    connection.commit()
                    print(cursor.rowcount, "record inserted")
                    rt_counter += 1
                    cursor.close()
                except mysql.connector.Error as error:
                    print("Failed to insert record {}".format(error))
                    print(f"Printed data: {data}")
        connection.close()

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