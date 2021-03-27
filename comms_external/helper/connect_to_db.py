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
print("Establishing connection with SQL database")

FIRST_HOP_SSH_ADDRESS = "sunfire.comp.nus.edu.sg"
FIRST_HOP_SSH_USERNAME = "sdsamuel"
FIRST_HOP_SSH_PKEY = "~/.ssh/id_rsa"
FIRST_HOP_SSH_PASSWORD = "iLoveTeam18!"

other_ip1 = "137.132.84.43"
other_ip2 = "192.168.26.43"
other_ip3 = "172.25.107.67"
SECOND_HOP_SSH_ADDRESS = other_ip3
SECOND_HOP_SSH_USERNAME = "little_peter"
SECOND_HOP_PASSWORD = "+"

with SSHTunnelForwarder(
        ('192.168.26.43', ssh_port),
        ssh_username='little_peter',
        ssh_password='+',
        remote_bind_address=(sql_hostname, sql_port)) as tunnel:
        print("successfully tunnelled through")    
        connection = pymysql.connect(host='localhost', user=sql_username,
            passwd=sql_password, db=sql_main_database,
            port=tunnel.local_bind_port)
        print("Connected to the sql database")
        query = '''SELECT VERSION();'''
        data = pd.read_sql_query(query, connection)
        try:
                mySql_insert_query1 = """INSERT INTO rawSensorData
                                        VALUES 
                                        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                tuple1 = (1, "0.1", "0.1", "0.1", "0.1", "0.1", "0.1", 1, "2008-11-11", "2008-11-11")

                cursor = connection.cursor()
                cursor.execute(mySql_insert_query1, tuple1)
                connection.commit()
                print(cursor.rowcount, "record inserted")
                cursor.close()
        except mysql.connector.Error as error:
                print("Failed to insert record {}".format(error))
                print(f"Printed data: {data}")
        connection.close()



# tunnel_info = [
#     {"ssh_address_or_host": FIRST_HOP_SSH_ADDRESS,
#     "ssh_username": FIRST_HOP_SSH_USERNAME,
#     "ssh_pkey": FIRST_HOP_SSH_PKEY, # Note this refers to a local file on the machine that runs logic
#     "ssh_password": FIRST_HOP_SSH_PASSWORD, # If applicable
#     },
#     {"ssh_address_or_host": SECOND_HOP_SSH_ADDRESS,
#     "ssh_username": SECOND_HOP_SSH_USERNAME,
#     "ssh_password": SECOND_HOP_PASSWORD,
#     },
#     {
#      "ssh_address_or_host": sql_hostname,
#      "ssh_username": sql_username,
#      "ssh_password": sql_password,
#     }
# ]

# # with TunnelNetwork(tunnel_info=tunnel_info, target_ip=sql_hostname, target_port=sql_port) as tn:
# #         print(f"Tunnel available at localhost:{tn.local_bind_port}")

# #         # with SSHTunnelForwarder(
# #         #         (other_ip3, ssh_port),
# #         #         ssh_username='little_peter',
# #         #         ssh_password='+',
# #         #         remote_bind_address=(sql_hostname, sql_port)) as tunnel:
# #         #         print("successfully tunnelled through")    
# #         #         connection = pymysql.connect(host='localhost', user=sql_username,
# #         #         passwd=sql_password, db=sql_main_database,
# #         #         port=tunnel.local_bind_port)
# #         #         print("Connected to the sql database")
# #         #         query = '''SELECT VERSION();'''
# #         #         data = pd.read_sql_query(query, connection)
# #         #         try:
# #         #                 mySql_insert_query1 = """INSERT INTO rawSensorData
# #         #                                         VALUES 
# #         #                                         (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
# #         #                 tuple1 = (1, "0.1", "0.1", "0.1", "0.1", "0.1", "0.1", 1, "2008-11-11", "2008-11-11")

# #         #                 cursor = connection.cursor()
# #         #                 cursor.execute(mySql_insert_query1, tuple1)
# #         #                 connection.commit()
# #         #                 print(cursor.rowcount, "record inserted")
# #         #                 cursor.close()
# #         #         except mysql.connector.Error as error:
# #         #                 print("Failed to insert record {}".format(error))
# #         #                 print(f"Printed data: {data}")
# #         #         connection.close()
        
# #         while True:
# #                 print("inside")
# #                 # Use this tunnel
# #                 time.sleep(5)
