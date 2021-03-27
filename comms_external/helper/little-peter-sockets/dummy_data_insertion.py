import mysql.connector 
from mysql.connector import Error
from mysql.connector import errorcode
from csv import reader
import time
import random 
import datetime
import time

dancer1_tuple = None
dancer2_tuple = None
dancer3_tuple = None

# with open('/home/peter/CG4002_B18/dashboard/api/dummyData/dancer1dummy.csv', 'r') as read_obj:
#     csv_reader = reader(read_obj)
#     dancer1_tuple = list(map(tuple, csv_reader))
# with open('/home/peter/CG4002_B18/dashboard/api/dummyData/dancer2dummy.csv', 'r') as read_obj:
#     csv_reader = reader(read_obj)
#     dancer2_tuple = list(map(tuple, csv_reader))
# with open('/home/peter/CG4002_B18/dashboard/api/dummyData/dancer3dummy.csv', 'r') as read_obj:
#     csv_reader = reader(read_obj)
#     dancer3_tuple = list(map(tuple, csv_reader))
connection = mysql.connector.connect(host='ec2-52-91-189-192.compute-1.amazonaws.com',
                                    database='CG4002',
                                    user='capstone',
                                    port=5001,
                                    password='CG4002Weiyang1997!')
random_numbers = []

for i in range(1001):
    random_numbers.append(random.uniform(-100, 100))

random_datetime = []
start_date = datetime.date(2020, 1, 1)
end_date = datetime.date(2020, 11, 1)

time_between_dates = end_date - start_date
days_between_dates = time_between_dates.days

for i in range(501):
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + datetime.timedelta(days=random_number_of_days)
    random_datetime.append(random_date.strftime('%Y-%m-%d %H:%M:%S'))

index = 1
for i in range(500):
    time.sleep(2)
    try:
        mySql_insert_query1 = """INSERT INTO rawSensorData
                            VALUES 
                             (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        tuple1 = (index, random_numbers[random.randint(0,1000)], random_numbers[random.randint(0,1000)], random_numbers[random.randint(0,1000)], random_numbers[random.randint(0,1000)], random_numbers[random.randint(0,1000)], random_numbers[random.randint(0,1000)], 1, random_datetime[random.randint(0, 100)], random_datetime[random.randint(0, 100)])
        index += 1
        mySql_insert_query2 = """INSERT INTO rawSensorData
                            VALUES 
                             (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        tuple2 = (index, random_numbers[random.randint(0,1000)], random_numbers[random.randint(0,1000)], random_numbers[random.randint(0,1000)], random_numbers[random.randint(0,1000)], random_numbers[random.randint(0,1000)], random_numbers[random.randint(0,1000)], 2, random_datetime[random.randint(0, 100)], random_datetime[random.randint(0, 100)]) 
        index += 1
        mySql_insert_query3 = """INSERT INTO rawSensorData
                            VALUES 
                             (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        tuple3 = (index, random_numbers[random.randint(0,1000)], random_numbers[random.randint(0,1000)], random_numbers[random.randint(0,1000)], random_numbers[random.randint(0,1000)], random_numbers[random.randint(0,1000)], random_numbers[random.randint(0,1000)], 3, random_datetime[random.randint(0, 100)], random_datetime[random.randint(0, 100)])
        index += 1

        cursor = connection.cursor()
        cursor.execute(mySql_insert_query1, tuple1)
        cursor.execute(mySql_insert_query2, tuple2)
        cursor.execute(mySql_insert_query3, tuple3)
        connection.commit()
        print(cursor.rowcount, "record inserted")
        cursor.close()
    except mysql.connector.Error as error:
        print("Failed to insert record {}".format(error))

if (connection.is_connected()):
    connection.close()
    print("MySQL connection is closed")