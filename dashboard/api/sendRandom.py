import random
import datetime
import mysql.connector 
from mysql.connector import Error
from mysql.connector import errorcode
from csv import reader
import time

dance_move = ["WINDOWS", "PUSHBACK", "ROCKET", "ELBOW_LOCK", "HAIR", "SCARECROW", "ZIGZAG", 
               "SHOULDER_SHRUG"]
dance_move_prediction = [1, 0]
random_numbers = []

for i in range(1000):
    random_numbers.append(random.uniform(-100, 100))

random_datetime = []
start_date = datetime.date(2020, 1, 1)
end_date = datetime.date(2020, 11, 1)

time_between_dates = end_date - start_date
days_between_dates = time_between_dates.days

for i in range(500):
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + datetime.timedelta(days=random_number_of_days)
    random_datetime.append(random_date.strftime('%Y-%m-%d %H:%M:%S'))

statistics = []
name = ["chenchao", "weiyang"]
for i in range(2000):
    statistics.append((i, "shreyas", random.choice(dance_move_prediction), random.choice(dance_move), 
                        random.choice(random_numbers), random.choice(random_numbers), random.choice(random_numbers),
                        random.choice(random_numbers), random.choice(random_numbers), random.choice(random_numbers),
                        random.choice(random_datetime), random.choice(random_datetime)))

connection = mysql.connector.connect(host='localhost',
                                    database='CG4002',
                                    port=3306,
                                    user='capstone',
                                    password='capstone')

for i in range(500):
    try:
        mySql_insert_query1 = """INSERT INTO statistics
                            VALUES 
                             (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        tuple1 = statistics[i]

        cursor = connection.cursor()
        cursor.execute(mySql_insert_query1, tuple1)
        connection.commit()
        print(cursor.rowcount, "record inserted")
        cursor.close()
    except mysql.connector.Error as error:
        print("Failed to insert record {}".format(error))

if (connection.is_connected()):
    connection.close()
    print("MySQL connection is closed")