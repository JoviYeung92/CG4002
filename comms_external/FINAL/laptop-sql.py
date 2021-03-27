import sys
import os
import time
import socket
import mysql
from pytunneling import TunnelNetwork
import threading
from Crypto.Cipher import AES
import base64
import datetime
import pytz

FIRST_HOP_SSH_ADDRESS = "sunfire.comp.nus.edu.sg"
FIRST_HOP_SSH_USERNAME = "sdsamuel"
FIRST_HOP_SSH_PKEY = "~/.ssh/id_rsa"
FIRST_HOP_SSH_PASSWORD = "iLoveTeam18!"

SECOND_HOP_SSH_ADDRESS = "137.132.86.241"
SECOND_HOP_SSH_USERNAME = "xilinx"
SECOND_HOP_PASSWORD = "xilinx"

TARGET_IP = SECOND_HOP_SSH_ADDRESS
TARGET_PORT = 5678
SECRET_KEY = "abcdefghijklmnop"


import mysql.connector
import sshtunnel
import pymysql
import paramiko
import pandas as pd
from paramiko import SSHClient
from sshtunnel import SSHTunnelForwarder
from os.path import expanduser
from pytunneling import TunnelNetwork
import time

sql_hostname = 'localhost'
sql_username = 'capstone'
sql_password = 'capstone'
sql_main_database = 'CG4002'
sql_port = 3306
ssh_host = 'little_peter'

ssh_user = 'little-peter'
ssh_port = 22
sql_ip = 'localhost'
ssh_address = '172.25.107.67'
WEI_YANG_IP = '172.25.104.54'

tunnel_info = [
    {"ssh_address_or_host": FIRST_HOP_SSH_ADDRESS,
    "ssh_username": FIRST_HOP_SSH_USERNAME,
    "ssh_pkey": FIRST_HOP_SSH_PKEY, # Note this refers to a local file on the machine that runs logic
    "ssh_password": FIRST_HOP_SSH_PASSWORD, # If applicable
    },
    {"ssh_address_or_host": SECOND_HOP_SSH_ADDRESS,
    "ssh_username": SECOND_HOP_SSH_USERNAME,
    "ssh_password": SECOND_HOP_PASSWORD,
    }
]

SQL_SECRET_KEY = "abcdefghijklmnop"

DATA_TYPE_REAL_TIME = 1
DATA_TYPE_PREDICTION = 2
DATA_FINAL_PREDICTION = 3

class Laptop_SQL_Connector(threading.Thread):
    def __init__(self):
        super(Laptop_SQL_Connector, self).__init__()
        self.initialize_ssh_tunneling()
        self.connect_to_ultra96()
        self.connect_to_sql_database()

    def initialize_ssh_tunneling(self):
        print("Tunneling...")
        self.tn = TunnelNetwork(tunnel_info=tunnel_info, target_ip=TARGET_IP, target_port=TARGET_PORT).__enter__()
        self.LOCAL_PORT = self.tn.local_bind_port
        time.sleep(2)
        print(f"Tunnel available at localhost:{self.LOCAL_PORT}")

    def connect_to_ultra96(self):
        print("Connecting to xilinx")
        self.socket_ultra96 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        addr = (socket.gethostbyname(socket.gethostname()), self.LOCAL_PORT)
        self.socket_ultra96.connect(addr)
        print("connected to xilinx")
    
    def connect_to_sql_database(self):
        print("Attempting to connect to the mysql server")
        with SSHTunnelForwarder(
        (WEI_YANG_IP, ssh_port),
        ssh_username='little_peter',
        ssh_password='+',
        remote_bind_address=(sql_hostname, sql_port)) as tunnel:
            print("successfully tunnelled through")    
            self.connection = mysql.connector.connect(host='localhost', user=sql_username,
                password=sql_password, database=sql_main_database,
                port=3306)
            self.cursor = self.connection.cursor()
            print("Connected to the sql database")
            query = '''SELECT VERSION();'''
            data = pd.read_sql_query(query, self.connection)
            print(data)
            
            # First clear all existing data in the database
            try:
                mySql_delete_query1 = """delete from predictions"""
                mySql_delete_query2 = """delete from rawSensorData"""
                mySql_delete_query3 = """delete from finalpredictions"""
                self.cursor.execute(mySql_delete_query1)
                self.cursor.execute(mySql_delete_query2)
                self.cursor.execute(mySql_delete_query3)
                self.cursor.close()
            except Exception as e:
                print("Could not delete the initial data from mysql database")
                print(e)

            # start receiving and inserting data
            predictions_p_key = 1
            rawSensorData_p_key = 1
            final_prediction_key = 1
            while True:
                data = self.socket_ultra96.recv(512)
                if data:
                    try:
                        self.cursor = self.connection.cursor()
                        data = self.decrypt_message(data)
                        # identify type of data
                        data_type = int(data.split(",")[0][1:])
                        if data_type == DATA_TYPE_REAL_TIME:
                            # print(f"Received some raw sensor data: {data}")
                            data = data[1:len(data)-1]
                            data = data.split(",")
                            try:
                                mySql_insert_query1 = """INSERT INTO rawSensorData
                                                        VALUES 
                                                        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                                mydate = datetime.datetime.now(pytz.timezone('Asia/Singapore')).strftime('%Y-%m-%d %H:%M:%S')
                                tuple1 = (rawSensorData_p_key, data[1], data[2], data[3], data[4], data[5], data[6], data[7], mydate, mydate)
                                rawSensorData_p_key+=1
                                self.cursor.execute(mySql_insert_query1, tuple1)
                                self.connection.commit()
                            except mysql.connector.Error as error:
                                print("Failed to insert record {}".format(error))
                                print("======")
                        elif data_type == DATA_TYPE_PREDICTION:
                            print(f"Received some mini prediction data: {data}")
                            data = data[1:len(data)-1]
                            data = data.split(", ")
                            try:
                                mySql_insert_query1 = """INSERT INTO predictions
                                                        VALUES 
                                                        (%s, %s, %s, %s, %s, %s)"""
                                tuple1 = (predictions_p_key, data[1][1:len(data[1])-1], data[2], data[3], mydate, mydate)
                                predictions_p_key +=1
                                self.cursor.execute(mySql_insert_query1, tuple1)
                                self.connection.commit()
                            except mysql.connector.Error as error:
                                print("Failed to insert record {}".format(error))
                                print(f"Printed data: {data}")
                            self.cursor.close()
                        elif data_type == DATA_FINAL_PREDICTION:
                            print(f"Received some final prediction data: {data}")
                            data = data[1:len(data) - 1]
                            data = data.split(",")
                            position_data = data[2].split("-")
                            dancer1_pos = int(position_data[0][2:])
                            dancer2_pos = int(position_data[1])
                            dancer3_pos = int(position_data[2][:-1])
                            try:
                                mySql_delete_query3 = """INSERT INTO finalpredictions VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                                mydate = datetime.datetime.now(pytz.timezone('Asia/Singapore')).strftime('%Y-%m-%d %H:%M:%S')
                                danceMove = data[3][1:len(data[3])-1].upper()
                                tuple1 = (final_prediction_key, data[3][2:len(data[3])-1], data[3][2:len(data[3])-1], data[3][2:len(data[3])-1], dancer1_pos, dancer2_pos, dancer3_pos, float(data[1][2:len(data[1])-1]), float(data[4]), mydate, mydate)
                                final_prediction_key += 1
                                self.cursor.execute(mySql_delete_query3, tuple1)
                                self.connection.commit()
                            except mysql.connector.Error as error:
                                print("Failed to insert record {}".format(error))
                                print(f"Printed data: {data}")
                            self.cursor.close()
                    except Exception as e:
                        print("===========")
                        print("Some exception has occured while attempting to insert data")
                        print(e)
                        print("===========")
            self.connection.close()
    
    def decrypt_message(self, message):
        message = message.decode("utf-8").strip()
        #message = message.strip()
        decoded_message = base64.b64decode(message)
        iv = decoded_message[:16]
        secret_key = bytes(SQL_SECRET_KEY, encoding="utf-8")
        cipher = AES.new(secret_key, AES.MODE_CBC, iv)
        decrypted_message = cipher.decrypt(decoded_message[16:]).strip()
        decrypted_message = decrypted_message.decode("utf8")
        return decrypted_message     


def main():
    global TARGET_PORT
    TARGET_PORT = int(input("Please enter the target port for SQL <--> Ultra96 socket connection (default is 5678): "))
    laptop_SQL_Connector = Laptop_SQL_Connector()
    laptop_SQL_Connector.start() # no idea wtf this does

if __name__ == "__main__":
    main()

