import sys
import os
import time
import socket
from pytunneling import TunnelNetwork
import threading

class Xilinx_SQL_Connector(threading.Thread):
    def __init__(self):
        super(Xilinx_SQL_Connector, self).__init__()
        print("Starting up...")
        self.init_connection_to_laptop_sql_connector()
        self.connect_to_laptop_sql_connector()
        
    # establish connection with the sql 
    def init_connection_to_laptop_sql_connector(self):
        self.xilinx_sql_connector_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.xilinx_ip_addr = "137.132.86.241"
        self.xilinx_sql_connector_socket.bind((self.xilinx_ip_addr, 5678))
        self.xilinx_sql_connector_socket.listen(1)

    def connect_to_laptop_sql_connector(self):
        laptop_socket, laptop_address = self.xilinx_sql_connector_socket.accept()
        print(f"Connection to laptop sql connector established at {laptop_address}")
        while True:
            # self.xilinx_sql_connector_socket.send(data.encode("utf-8"))
            # time.sleep(1)
            data = "Hello this is some dummy data for you"
            data = laptop_socket.send(data.encode("utf-8"))
            time.sleep(1)

def main():
    xilinx_SQL_Connector = Xilinx_SQL_Connector()
    xilinx_SQL_Connector.start()

if __name__ == "__main__":
    main()
