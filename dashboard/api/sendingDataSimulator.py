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
connection = mysql.connector.connect(host='localhost',
                                    database='CG4002',
                                    port=3306,
                                    user='capstone',
                                    password='capstone')
random_numbers = []
moves = ['WINDOWS', 'PUSHBACK', 'ROCKET', 'ELBOW_LOCK', 'SCARECROW','SHOULDER_SHRUG']
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

p_counter = 0
index = 1
for i in range(500):
    time.sleep(1)
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

        if (i%5 == 0):
            mySql_insert_query4 = """INSERT INTO predictions
                                    VALUES 
                                    (%s, %s, %s, %s, %s, %s)"""
            mySql_insert_query5 = """INSERT INTO predictions
                                    VALUES 
                                    (%s, %s, %s, %s, %s, %s)"""
            mySql_insert_query6 = """INSERT INTO predictions
                                    VALUES 
                                    (%s, %s, %s, %s, %s, %s)"""
            tuple4 = (p_counter, moves[random.randint(0, 5)], random.randint(1,3), random.randint(1, 3), random_datetime[random.randint(0, 100)], random_datetime[random.randint(0, 100)])
            tuple5 = (p_counter+1, moves[random.randint(0, 5)], random.randint(1,3), random.randint(1, 3), random_datetime[random.randint(0, 100)], random_datetime[random.randint(0, 100)])
            tuple6 = (p_counter+2, moves[random.randint(0, 5)], random.randint(1,3), random.randint(1,3), random_datetime[random.randint(0, 100)], random_datetime[random.randint(0, 100)])
            # cursor = connection.cursor()
            cursor.execute(mySql_insert_query4, tuple4)
            cursor.execute(mySql_insert_query5, tuple5)
            cursor.execute(mySql_insert_query6, tuple6)
            connection.commit()
            print(cursor.rowcount, "record inserted [prediction]")
            cursor.close()
            p_counter += 3
    except mysql.connector.Error as error:
        print("Failed to insert record {}".format(error))

if (connection.is_connected()):
    connection.close()
    print("MySQL connection is closed")