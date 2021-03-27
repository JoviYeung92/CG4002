import sys
import os
import time
import socket
import mysql
from pytunneling import TunnelNetwork
import threading

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
WEI_YANG_IP = '172.25.100.23'

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
            connection = mysql.connector.connect(host='localhost', user=sql_username,
                passwd=sql_password, db=sql_main_database,
                port=tunnel.local_bind_port)
            print("Connected to the sql database")
            query = '''SELECT VERSION();'''
            data = pd.read_sql_query(query, connection)
            print(data)
            counter = 200
            while counter < 300:
                data = self.socket_ultra96.recv(1024)
                if data:
                    data = data.decode("utf-8")
                    print(f"Received some data: {data}")
                    datas = data.split("|")
                    try:
                        mySql_insert_query1 = """INSERT INTO rawSensorData
                                                VALUES 
                                                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                        tuple1 = (counter, datas[0], datas[1], datas[2], datas[3], datas[4], datas[5], 1, "2008-11-11", "2008-11-11")
                        cursor = connection.cursor()
                        cursor.execute(mySql_insert_query1, tuple1)
                        connection.commit()
                        print(cursor.rowcount, "record inserted")
                        cursor.close()
                    except mysql.connector.Error as error:
                        print("Failed to insert record {}".format(error))
                        print(f"Printed data: {data}")
                    counter += 1
            connection.close()
                
def main():
    laptop_SQL_Connector = Laptop_SQL_Connector()
    laptop_SQL_Connector.start() # no idea wtf this does

if __name__ == "__main__":
    main()

