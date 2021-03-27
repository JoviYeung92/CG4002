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
import math
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
import pytz
# imports for SQL
import mysql.connector
import sshtunnel
import pymysql
import paramiko
import pandas as pd
from paramiko import SSHClient
from sshtunnel import SSHTunnelForwarder
from collections import deque

DATABASE_AMAZON_HOST = "ec2-34-239-124-200.compute-1.amazonaws.com"

service_uuid = "0000dfb0-0000-1000-8000-00805f9b34fb"
char_uuid = "0000dfb1-0000-1000-8000-00805f9b34fb"

connections = {}
connection_threads = {}
connected_addr=[]
lock=Lock()

main_data={} #strore all info from all thread. bluno_id -> [millis -> data_set]

#(a,b)(c,d)(e,f) <glove,position>
#listed all bluetooth MAC address.
a = "C8:DF:84:FE:43:70" #ok 
b = "34:15:13:22:A1:26" #ok
c = "34:15:13:22:A5:72"  #ok
d = "2C:AB:33:CC:17:46" #ok
e = "2C:AB:33:CC:68:D4" #ok 
f = "C8:DF:84:FE:52:77" #ok

mac_map = {
"a" : "C8:DF:84:FE:43:70", #ok 
"b" : "34:15:13:22:A1:26", #ok
"c" : "34:15:13:22:A5:72",  #ok
"d" : "2C:AB:33:CC:17:46", #ok
"e" : "2C:AB:33:CC:68:D4", #ok 
"f" : "C8:DF:84:FE:52:77", #ok
}
#define comms bluetooth
glove_bt = c
position_bt = d
#Set up initial state for bluno
bt_addrs = [glove_bt]

FIRST_HOP_SSH_ADDRESS = "sunfire.comp.nus.edu.sg"
FIRST_HOP_SSH_USERNAME = "sdsamuel"
FIRST_HOP_SSH_PKEY = "~/.ssh/id_rsa"
FIRST_HOP_SSH_PASSWORD = "iLoveTeam18!"

SECOND_HOP_SSH_ADDRESS = "137.132.86.241"
SECOND_HOP_SSH_USERNAME = "xilinx"
SECOND_HOP_PASSWORD = "xilinx"

TARGET_IP = SECOND_HOP_SSH_ADDRESS
TARGET_PORT = 15006
SECRET_KEY = "abcdefghijklmnop"

tunnel_info = [
    {"ssh_address_or_host": FIRST_HOP_SSH_ADDRESS,
    "ssh_username": FIRST_HOP_SSH_USERNAME,
    "ssh_password": FIRST_HOP_SSH_PASSWORD,
    },
    {"ssh_address_or_host": SECOND_HOP_SSH_ADDRESS,
    "ssh_username": SECOND_HOP_SSH_USERNAME,
    "ssh_password": SECOND_HOP_PASSWORD,
    }
]

sql_username = 'capstone'
sql_password = 'CG4002Weiyang1997!'
sql_main_database = 'CG4002'

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
DATA_SOURCE = True
PRINT_PACKETS = True

"""       **************************************
There will be two versions of dancer_client_test:
1. Send raw data to AWS database from this file. 
   This will be compatible with ultra96_client_w113_2.py
   which sends only predictions to AWS database
   [to use this version, set the CONNECT_TO_DATABASE to True]

2. Ultra96 takes care of sending the real sensor data and prediction
   data to a LOCAL database for dashboard through python sockets.
   This will be compatible with ultra96_client_w113_1.py
   [to use this version, set the CONNECT_TO_DATABASE to False]

You may also set the CONNECT_TO_DATABASE to False simply if
you don't want to pipe data to AWS database system 
           **********************************
"""       
CONNECT_TO_DATABASE = False 

# for time synchronization
BLUNO_TIME_DIFF = 0 # used for synchronizing bluno time to NTP
LAPTOP_TIME_DIFF = 0 # used for synchronizing laptop time to NTP
NTP_TIME_DIFF = 0 # used for synchronizing bluno time to NTP
RTT_BY_2 = 0
T1 = 0
T2 = 0
T3 = 0

TUNNEL = 0 # ssh tunnel

#data processing for incoming packets
def clean_data(info):
    return(info[2:-1])
#data processing for incoming packets
def rm_symbol(data):
    while True:
        if (data[0] == '#'):
            data = data[1:]
        else:
            return data

#Fucntion to check CRC match data receive
def crc_check(data_string):
    hash = crc8.crc8()
    crc = data_string[-2:]
    data_string = data_string[2:-2]
    hash.update(bytes(data_string, "utf-8"))
    if (hash.hexdigest() == crc):
        return True
    else:
        return False

#able to reconnect, but serials comms have junk inside
def reconnection(main_data, addr,index):
        print("reconnecting bluno")
        while True:
            try:
                p = btle.Peripheral(addr)
                connections[index]=p
                t = ConnectionHandlerThread(index, addr,main_data,True)
                #start thread
                t.start()
                connection_threads[index]=t
                break
            except Exception:
                sleep(1)

class Dancer_Client(Thread):
    def __init__(self, unique_laptop_id, glove_bt, position_bt):
        super(Dancer_Client, self).__init__()

        """
        Unique identifier for each dancer client
        """
        self.DANCER_CLIENT_ID = unique_laptop_id

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
        self.sql_raw_data_queue = deque()
        self.global_data_counter = 0
        self.previous_millis = -math.inf
        self.hasSyncedBluno = False

        self.socket_exception = False
        # self.initialize_ssh_tunneling()

        with TunnelNetwork(tunnel_info=copy.deepcopy(tunnel_info), target_ip=TARGET_IP, target_port=TARGET_PORT) as self.tn:
            self.LOCAL_PORT = self.tn.local_bind_port
            print(f"Tunnel available at localhost:{self.LOCAL_PORT}")
            sleep(2)

            '''
            Sync laptop timing with ntp
            #TODO convert this into a thread that syncs every 1 minute
            '''
            hasSynced = False
            while not hasSynced:
                print("attempting to do time sync")
                hasSynced = self.time_sync_laptop_with_ntp()
            print("Initial laptop time sync completed.")
            
            '''
            Establish socket connection with Ultra96 through the tunnel
            '''
            self.connect_to_ultra96()
            
            if CONNECT_TO_DATABASE:
                """
                Establish connection with database
                """
                self.init_connection_to_dashboard()

            if DATA_SOURCE:
                '''
                Establish connection to bluno
                #TODO Need to do handshake and initial time sync
                '''
                self.connectToBluno()
            else:
                """
                Start running the dummy bluno
                """ 
                self.producer_thread_1 = Thread(target=self.start_dummy_bluno_2, args=(HAND_BLUNO_ID, self.main_data[0]))
                self.producer_thread_1.daemon = True
                self.producer_thread_1.start()

                self.producer_thread_2 = Thread(target=self.start_dummy_bluno3, args=(POSITION_BLUNO_ID, self.main_data[1]))
                self.producer_thread_2.daemon = True
                self.producer_thread_2.start()

            if CONNECT_TO_DATABASE:
                print("Starting the thread that sends data to database")
                """
                Start sending data to dashboard
                """
                self.dashboard_thread = Thread(target=self.push_data_to_dashboard_method)
                self.dashboard_thread.daemon = True
                self.dashboard_thread.start()

            """
            Start consuming the data and sending it to Ultra96
            """
            self.consumer_thread_1 = Thread(target=self.consume_data_test, args=(0,))
            self.consumer_thread_1.daemon = True
            self.consumer_thread_1.start()

            '''
            Keeping the main thread alive
            # TODO find a better way to terminate this program
            '''
            while not self.socket_exception:
                sleep(3)

    def initialize_ssh_tunneling(self):
        self.tn = TunnelNetwork(tunnel_info=tunnel_info, target_ip=TARGET_IP, target_port=TARGET_PORT).__enter__()
        self.LOCAL_PORT = self.tn.local_bind_port
        print(f"Tunnel available at localhost:{self.LOCAL_PORT}")
        print("Tunnel info:")
        print(f"{self.tn}")
        sleep(2)


    def init_connection_to_dashboard(self):
        self.connection = mysql.connector.connect(host=DATABASE_AMAZON_HOST, user=sql_username,
            passwd=sql_password, db=sql_main_database,
            port=5001)  
        self.cursor = self.connection.cursor()
        print("Connected to the sql database")
        query = '''SELECT VERSION();'''
        data = pd.read_sql_query(query, self.connection)
        print(data)
        if self.DANCER_CLIENT_ID == 1:
            self.rt_counter = 1
        elif self.DANCER_CLIENT_ID == 2:
            self.rt_counter = 20000
        else:
            self.rt_counter = 40000

    def push_data_to_dashboard_method(self):
        while True:
            if self.sql_raw_data_queue:
                data = self.sql_raw_data_queue.popleft()
                print(f"There is data in the deque: {data}")
                try:
                    mySql_insert_query1 = """INSERT INTO rawSensorData
                        VALUES 
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                    tuple1 = (self.rt_counter, data[0], data[1], data[2], data[3], data[4], data[5], self.DANCER_CLIENT_ID, datetime.now(pytz.timezone('Asia/Singapore')).strftime('%Y-%m-%d %H:%M:%S'), datetime.now(pytz.timezone('Asia/Singapore')).strftime('%Y-%m-%d %H:%M:%S'))
                    print(f"There is data in the deque: {tuple1}")
                    self.rt_counter += 1
                    self.cursor.execute(mySql_insert_query1, tuple1)
                    
                    self.connection.commit()
                    print(self.cursor.rowcount, "record inserted")
                except mysql.connector.Error as error:
                    print("Failed to insert record {}".format(error))
                    print(f"Printed data: {data}")
            sleep(0.4)

    '''
    Need to edit this method to consume data from the 2 queues for the 2 blunos
    can implement flow control here as well
    '''
    def consume_data_test(self, id):
        global NTP_TIME_DIFF
        dashboard_rate = 7
        while True:
            if not self.main_data[id].empty():
                
                mData = self.main_data[id].get()
                
                curr_roll = mData["roll"]
                curr_pitch = mData["pitch"]
                curr_yaw = mData["yaw"]
                curr_AccX = mData["AccX"]
                curr_AccY = mData["AccY"]
                curr_AccZ = mData["AccZ"]
                curr_time = mData["millis"]
                curr_position = mData['position']

                self.global_data_counter += 1

                if self.global_data_counter % 3 == 0:
                    self.sql_raw_data_queue.append([curr_roll, curr_pitch, curr_yaw, curr_AccX, curr_AccY, curr_AccZ])

                if not self.hasSyncedBluno:
                    self.perform_time_sync()

                if ((float(curr_AccX) >= 1.2 or float(curr_AccX) <= -0.03) 
                    and (float(curr_AccY) >= 0.13 or float(curr_AccY) <= -0.25)
                    and float(curr_time) > float(self.previous_millis)):
                    packet_marker = "a" # start marker
                    print(f"===== this is a start packet =======")
                else:
                    packet_marker = "b"
                self.previous_millis = curr_time
                # correct the time data over here

                curr_time = int(curr_time) + NTP_TIME_DIFF

                #package all the data into a separate packet    
                curr_packet = "#" + str(self.DANCER_CLIENT_ID) + "|" +str(id) + "|" + str(curr_time) + "|" + str(curr_roll) + "|" + str(curr_pitch) + "|" + str(curr_yaw) + "|" + str(curr_AccX) + "|" + str(curr_AccY) + "|" + str(curr_AccZ) + "|" + packet_marker + "|" + curr_position + "|"
                encrypted_packet = self.encrypt_message_to_ultra96(curr_packet)
                newPadLength = 256 - len(encrypted_packet)
                for i in range(newPadLength):
                    encrypted_packet = " ".encode("utf-8") + encrypted_packet
                if PRINT_PACKETS:
                    print(f"sending this packet: {curr_packet}")
                    print(f"CURRENT TIME: {curr_time}, NTP_TIME_DIFF: {NTP_TIME_DIFF}, LAPTOP_TIME_DIFF: {LAPTOP_TIME_DIFF}, BLUNO_TIME_DIFF: {BLUNO_TIME_DIFF}")
                try:
                    print(f"Attempting to send data")
                    self.socket_ultra96.send(encrypted_packet)
                    msg_sent = True
                except Exception as e:
                    print("======")
                    print("Error in eccrypitng the packet from bluno 1 dance")
                    print(e)
                    self.socket_exception = True
                    #self.socket_ultra96.close()
                    #self.connect_to_ultra96()
                    print("======")

            if not self.main_data[1].empty():
                mData = self.main_data[1].get()
                # convert this into a packet
                curr_AccZ = mData["AccZ"]
                #package this data into a separate packet
                curr_packet = "#" + str(self.DANCER_CLIENT_ID) + "|" + str(1) + "|" + str(curr_AccZ) + "|"
                encrypted_packet = self.encrypt_message_to_ultra96(curr_packet)
                newPadLength = 256 - len(encrypted_packet)
                for i in range(newPadLength):
                    encrypted_packet = " ".encode("utf-8") + encrypted_packet
                if PRINT_PACKETS:
                    print(f"sending this packet: {curr_packet}")
                try:
                    self.socket_ultra96.send(encrypted_packet)
                    msg_sent = True
                except Exception as e:
                    print("exception caused by data from bluno 2 - position xx")
                    print("trying to create a new socket to re-establish a connection")
                    print(e)
                    self.initialize_ssh_tunneling()
                    self.connect_to_ultra96()
                    msg_sent = True
            sleep(0.1)

    def encrypt_message_to_ultra96(self, plain_text):
        iv = Random.new().read(AES.block_size)
        plain_text = plain_text.rjust(128, " ") # insert left padding
        aes = AES.new(LAPTOP_ULTRA96_SECRET_KEY.encode("utf-8"), AES.MODE_CBC, iv)
        cipher_text = aes.encrypt(plain_text.encode("utf-8"))
        encoded_message = base64.b64encode(cipher_text)
        return encoded_message

    def perform_time_sync(self):
        global BLUNO_TIME_DIFF
        global LAPTOP_TIME_DIFF
        global NTP_TIME_DIFF
        global RTT_BY_2
        global T1
        global T2
        global T3
        RTT_BY_2 = (T3 - T1) / 2
        BLUNO_TIME_DIFF = floor((T3 - RTT_BY_2) - T2)
        NTP_TIME_DIFF = BLUNO_TIME_DIFF - LAPTOP_TIME_DIFF


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

    '''
    Calculates the offset in millis between laptop time and ntp time.
    Return True when successful else returns False
    define offset: sys_time - ntp = offset
                   => ntp = (sys_time - offset) / 1000000  
    '''
    def time_sync_laptop_with_ntp(self):
        NTP_Client = ntplib.NTPClient()
        counter = 0
        is_success = False
        while counter < 10:
            try:
                ntp_request = NTP_Client.request(NTP_SERVER, version=3)
                ntp_time = datetime.fromtimestamp(ntp_request.orig_time, timezone.utc)
                sys_time = floor(time_ns() / 1000000)
                print("successfully gotten time timing")
                is_success = True
                break
            except Exception:
                print("failure")
                counter += 1
        if not is_success:
            return False
        # ntp_in_nanos = floor(self.convert_ntp_to_millis(str(ntp_time)) * 1000000)
        ntp_in_millis = self.convert_ntp_to_millis(str(ntp_time))
        # define offset: sys_time - ntp = offset 
        #                => ntp = (sys_time - offset) / 1000000 (in micros) 
        # self.laptop_time_offset = sys_time - ntp_in_nanos 
        global LAPTOP_TIME_DIFF
        LAPTOP_TIME_DIFF = sys_time - ntp_in_millis     
        return True        

    '''
    Clean up resources and
    Terminate the programme
    '''
    def stop(self):
        self.socket_ultra96.close()
        print("socket closed and system shutting down.")
        sys.exit()


    ### ADDITIONAL HELPER FUNCTIONS FOR DANCER CLIENT
    '''
    Converts the timestamp string from NTP server to millis.
    It rounds down to the nearest millis and returns that value
    '''
    def convert_ntp_to_millis(self, time_string):
        if len(str(time_string)) < 5:
            return 1
        time = time_string.split(" ")[1].split("+")[0]
        hour = int(time.split(":")[0])
        mins = int(time.split(":")[1])
        sec = floor(float(time.split(":")[2]))
        milli_sec = int(floor(int(time.split(".")[1]) / 1000))
        time_final = hour*60*60*1000 + mins*60*1000 + sec*1000 + milli_sec
        return time_final
        
    #fucntion to connect bluno
    def connectToBluno(self):
        index = 10
        print("Connecting to bluno ...")
        for addr in bt_addrs:
            #only connects to bluno registered in bt_addr, give them their respective indexes
            if (addr==glove_bt):
                index=0
            if (addr==position_bt):
                index=1
            p = btle.Peripheral(addr)
            connections[index]=p
            t = ConnectionHandlerThread(index, addr, self.main_data,False)
            #start thread
            t.start()
            connection_threads[index]=t

class MyDelegate(btle.DefaultDelegate):
    def __init__(self, connection_index):
        btle.DefaultDelegate.__init__(self)
        self.connection_index = connection_index
        self.ID=str(connection_index)

    def handleNotification(self, cHandle, data):
        data_string = clean_data(str(data))
        sleep(0.02)
        if crc_check(data_string):
            # PASS CRC
            BEETLE_ID = data_string[0]
            PACKET_ID = data_string[1]
            DATA = rm_symbol(data_string[2:-2])
            #info handle for ID 1
            if ((BEETLE_ID == self.ID)and (PACKET_ID == '8'and (DATA=="DANCE"))):
                connection_threads[self.connection_index].dance=True
            if ((BEETLE_ID == self.ID)and (PACKET_ID == '9')):
                connection_threads[self.connection_index].sync=True
                connection_threads[self.connection_index].millis=DATA
            if ((BEETLE_ID == self.ID)and (PACKET_ID == '1') and (DATA == "HANDSHAKE")):
                connection_threads[self.connection_index].handshake=True
            if ((BEETLE_ID == self.ID)and (PACKET_ID == '0') and (DATA == "ACK")):
                connection_threads[self.connection_index].ACK=True
            if ((BEETLE_ID == self.ID)and (PACKET_ID == '3')):
                text = DATA.split("|")
                connection_threads[self.connection_index].current_data["roll"]=text[0]
                connection_threads[self.connection_index].current_data["pitch"]=text[1]
            if ((BEETLE_ID == self.ID)and (PACKET_ID == '4')):
                text = DATA.split("|")
                connection_threads[self.connection_index].current_data["yaw"]=text[0]
                connection_threads[self.connection_index].current_data["AccX"]=text[1]
            if ((BEETLE_ID == self.ID)and (PACKET_ID == '5')):
                text = DATA.split("|")
                connection_threads[self.connection_index].current_data["AccY"]=text[0]
                connection_threads[self.connection_index].current_data["AccZ"]=text[1]
            if ((BEETLE_ID == self.ID)and (PACKET_ID == '6')):
                try:
                    text = DATA.split("|")
                    connection_threads[self.connection_index].current_data["millis"]=text[0]
                    connection_threads[self.connection_index].current_data["position"]=text[1]
                except:
                    connection_threads[self.connection_index].current_data["millis"]=DATA
            if ((BEETLE_ID == self.ID)and (PACKET_ID == '7')):
                connection_threads[self.connection_index].current_data["AccZ"]=DATA
        else:
            #FAIL CRC. doesnt matter as during data connecting if missing packet, err would be sent
            print("ERR in CRC")
            connection_threads[self.connection_index].err_count=connection_threads[self.connection_index].err_count+1
            sleep(0.01)


#Thread gnerating for each bluno.
class ConnectionHandlerThread(Thread):
    dance=False
    handshake = False
    ACK = False
    clear =False
    sync =False
    last_sync_time=0
    millis=0
    err_count=0
    current_data={
        "roll" : "#",
        "pitch" : "#",
        "yaw" : "#",
        "AccX" : "#",
        "AccY" : "#",
        "AccZ" : "#",
        "millis" : "#",
        "position" : "?"
    }
    def __init__(self,connection_index, addr,main_data, reconnect):
        print("connected to",addr,"\n")
        Thread.__init__(self)
        self.connection_index = connection_index
        self.addr = addr
        self.connection = (connections[self.connection_index])
        self.connection.setDelegate(MyDelegate(self.connection_index))
        self.main_data=main_data
        self.data=main_data[connection_index]
        self.reconnect=reconnect
        self.service=self.connection.getServiceByUUID(service_uuid)
        self.characteristic=self.service.getCharacteristics()[0]

    def run(self):
        while True:
            if (self.reconnect):
                sleep(1)
                print("reconnect")
                self.clear_proto(self.connection)
            try:
                #call handshake
                self.handshake_proto(self.connection)
                # call data collecting comms
                self.data_proto(self.connection)
            except BTLEException:
                #will only enter if problem with connection. IE disconnect
                self.connection.disconnect()
                #start a function to create new thread
                reconnect = Thread(target=reconnection(self.main_data,self.addr,self.connection_index))
                reconnect.start()
                #Current Thread END
                sys.exit(1)

    def clear_proto(self,p):
        while not self.handshake:
            self.characteristic.write(bytes("H", "utf-8"), withResponse=False)
            # Wait for Handshake packet from bluno 
            p.waitForNotifications(0.01)
        self.handshake=False


    def handshake_proto(self,p):
        # Send handshake packet
        print("HANDSHAKE INITIATED")
        self.characteristic.write(bytes("H", "utf-8"), withResponse=False)
        # Wait for Handshake packet from bluno 
        while (not self.handshake):
            p.waitForNotifications(2)
        self.handshake=False
        # Send back ACK
        print("HANDSHAKE RECIEVED, RETURN ACK")
        while (not self.ACK):
            sleep(0.5)
            self.characteristic.write(bytes("A", "utf-8"), withResponse=False)
            p.waitForNotifications(2)
        self.ACK=False
        #get millis
        self.time_sync(p)

    def data_proto(self,p):
        error = False
        self.err_count=0
        # recieve info for current data set
        while True:
            """
            #clear default data
            if (self.connection_index == 1):
                self.current_data={
                    "AccZ" : "#"
                }
                for x in range(2):
                    p.waitForNotifications(0.2)
                    # print(self.current_data)
                    if (self.current_data["AccZ"]!='#'):
                            break  
            else:
            """
            self.current_data={
                "roll" : "#",
                "pitch" : "#",
                "yaw" : "#",
                "AccX" : "#",
                "AccY" : "#",
                "AccZ" : "#",
                "millis" : "#",
                "position" : "?"
            }
            #some loops to ensure all packets supposed to be recieved    
            for x in range(6):
                p.waitForNotifications(0.12)
                # print(self.current_data)
                if (self.current_data["millis"]!='#'):
                        break
            #Check if all data recieved nicely
            for x in self.current_data:
                if (self.current_data[x]=='#'):
                    # #send back err
                    print("DATA ERR, RETURN ERROR")
                    self.characteristic.write(bytes("E", "utf-8"), withResponse=False)
                    error = True
                    #Buffer err with 0 instead
                    """
                    self.current_data={
                        "roll" : "0",
                        "pitch" : "0",
                        "yaw" : "0",
                        "AccX" : "0",
                        "AccY" : "0",
                        "AccZ" : "0",
                        "millis" : "0"
                        "position" : "?"
                    }
                    self.data.put(self.current_data)
                    """
                    break
            if error:
                if (self.err_count>5):
                    raise BTLEException("help la")
                self.err_count=self.err_count+1
                error =False
                continue
            self.err_count=0
            #Time SYNC HERE
            if (time()>self.last_sync_time+60):
                self.time_sync(p)
            #record dataset into queue
            self.data.put(self.current_data)
            print(self.connection_index, self.current_data)
            #send back ACK
            self.characteristic.write(bytes("A", "utf-8"), withResponse=False)

    #Req for millis at the bluno side, would be use for time-stamp calculation for data
    def time_sync(self,p):
        global T1
        global T3
        self.sync=False

        while (not self.sync):
            print("SEND SYNC REQ")
            T1 = floor(time_ns() / 1000000)
            self.characteristic.write(bytes("T", "utf-8"), withResponse=False)
            p.waitForNotifications(1)
        #self.millis -> is updated 
        self.last_sync_time=time()
        self.characteristic.write(bytes("A", "utf-8"), withResponse=False)
        T3 = floor(time_ns() / 1000000)
        global T2
        T2 = float(self.millis)
        print(f"{self.millis} and T2 is {T2}")

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
        sleep(60)
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
                sleep(0.2)
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
        sleep(60)
        num_dance_moves = 100
        num_data_per_move = 100
        for i in range(num_dance_moves):
            for j in range(num_data_per_move):
                current_data = {}
                current_data["AccZ"] = round(random.uniform(0,1), 2)
                self.laptop_queue.put(current_data)
                sleep(0.2)
            print("Sent one dance move worth of dummy positional data over")
        sleep(3)

    def get_time_millis(self):
        return floor((time() * 1000) % 10000000)

def main():
    # unique_laptop_id = get_unique_dancer_client_id()
    while True:
        dancer_num = int(input("Please enter your dancer number: \n"))
        if dancer_num >= 1 and dancer_num <= 3:
            break
    global glove_bt
    global position_bt
    global bt_addrs

    glove_bt = input("Please enter your dance glove letter: \n")
    # position_bt = input("Please enter your position glove letter: \n")
    glove_bt = mac_map[glove_bt]
    # position_bt = mac_map[position_bt]
    bt_addrs = [glove_bt]

    global TARGET_PORT
    TARGET_PORT = int(input("Please enter the target port for Laptop <-> Ultra96 socket connection (default is 15005): \n"))

    while True:
        dancer_client = Dancer_Client(dancer_num, glove_bt, position_bt)
        dancer_client.start()
        print("SOCKET EXCEPTION HAS OCCURRED, TRYING TO RECONNECT AGAIN")

'''
Returns a random number below 1000 which can be used as unique id
'''
def get_unique_dancer_client_id():
    random.seed(floor(time()))
    u_id = floor(random.random() * 1000)
    return 777
    return u_id

if __name__ == "__main__":
    main()
