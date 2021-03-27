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
import sshtunnel
from paramiko import SSHClient

FIRST_HOP_SSH_ADDRESS = "sunfire.comp.nus.edu.sg"
FIRST_HOP_SSH_USERNAME = "sdsamuel"
FIRST_HOP_SSH_PKEY = "~/.ssh/id_rsa"
FIRST_HOP_SSH_PASSWORD = "iLoveTeam18!"

SECOND_HOP_SSH_ADDRESS = "137.132.86.241"
SECOND_HOP_SSH_USERNAME = "xilinx"
SECOND_HOP_PASSWORD = "xilinx"

TARGET_IP = SECOND_HOP_SSH_ADDRESS
TARGET_PORT = 5436
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

def start_tunnel():
    tunnel1 = sshtunnel.open_tunnel(
        ssh_address_or_host = ('sunfire.comp.nus.edu.sg', 22),
        remote_bind_address = ('137.132.86.241', 22),
        ssh_username = 'sdsamuel',
        ssh_password = 'iLoveTeam18!',
        block_on_close = False
    )
    tunnel1.start()
    print("Tunnelled into sunfire")
    tunnel2 = sshtunnel.open_tunnel(
        ssh_address_or_host=('localhost', tunnel1.local_bind_port),
        remote_bind_address=('137.132.86.241', 14899),
        ssh_username = "xilinx",
        ssh_password = "xilinx",
        #local_bind_address = ('127.0.0.1', 14899),
        block_on_close = False
    )
    tunnel2.start()
    print("Tunnelled into xilinx")
    return tunnel1.local_bind_port

def connect_to_ultra96(LOCAL_PORT):
    socket_ultra96 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # addr = (socket.gethostbyname(socket.gethostname()), LOCAL_PORT)
    socket_ultra96.connect(('127.0.0.1', LOCAL_PORT))
    print("successfully connected to xilinx!!!!")
    return socket_ultra96

def initialize_ssh_tunneling():
    tn = TunnelNetwork(tunnel_info=tunnel_info, target_ip=TARGET_IP, target_port=TARGET_PORT).__enter__()
    LOCAL_PORT = tn.local_bind_port
    print(f"Tunnel available at localhost:{LOCAL_PORT}")
    return LOCAL_PORT

# LOCAL_PORT = start_tunnel()
LOCAL_PORT = initialize_ssh_tunneling()
sleep(2)
u96_socket = connect_to_ultra96(LOCAL_PORT)
while True:
    print("sending hello world")
    u96_socket.send("Hello world".encode('utf-8'))
    sleep(0.05)


