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

SQL_TARGET_PORT = 6971

def main():
    print("Starting program")
    xilinx_sql_connector_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    xilinx_ip_addr = "137.132.86.241"
    xilinx_sql_connector_socket.bind((xilinx_ip_addr, SQL_TARGET_PORT))
    xilinx_sql_connector_socket.listen(1)

    while True:
        sql_socket, sql_laptop_address = xilinx_sql_connector_socket.accept()
        
        while True:
            data = "hi there wei yang"
            try:
                print(f"sending this data {data}")
                sql_socket.send(data.encode("utf-8"))
            except Exception as e:
                print("Error occurred while sending real time data to sql socket")
                print(e)   

if __name__ == "__main__":
    main()

