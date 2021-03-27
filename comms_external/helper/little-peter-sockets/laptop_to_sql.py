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
sql_password = 'CG4002Weiyang1997!'
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
def init_connection():
    connection = mysql.connector.connect(host='ec2-52-91-189-192.compute-1.amazonaws.com', user=sql_username,
        passwd=sql_password, db=sql_main_database,
        port=5001)
    print("Connected to the sql database")
    query = '''SELECT VERSION();'''
    data = pd.read_sql_query(query, connection)
    print(data)
    counter = 1
    data = ["0.1", "0.1","0.1","0.1","0.1","0.1"]
    mySql_insert_query1 = """INSERT INTO rawSensorData
                            VALUES 
                            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    tuple1 = (counter, data[0], data[1], data[2], data[3], data[4], data[5], 1, "2008-11-11", "2008-11-11")
    connection.close()
                
def main():
    init_connection()

if __name__ == "__main__":
    main()

