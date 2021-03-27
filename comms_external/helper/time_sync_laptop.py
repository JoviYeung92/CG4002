import time
import ntplib
from datetime import datetime, timezone
from math import floor

'''
Attempts to sync laptop clock with ntp clock
so that we don't have to keep calling NTP server
all the time
'''
NTP_SERVER = "uk.pool.ntp.org"


# performing the time correction on laptop with ntp

'''
Key idea:
Let ntp timing be defined as: (microseconds passed since start of day at midnight)
convert laptop time_ns -> ntp timing 
need to check if using midnight timing is okay

need to come up with function that can convert laptop timing to ntp timing in seconds
'''

def calculate_offset():
    NTP_Client = ntplib.NTPClient()

    counter = 0
    is_success = False
    while counter < 10:
        try:
            ntp_request = NTP_Client.request(NTP_SERVER, version=3)
            ntp_time = datetime.fromtimestamp(ntp_request.orig_time, timezone.utc)
            sys_time = time.time_ns()
            is_success = True
            break;
        except Exception:
            counter += 1
    if not is_success:
        return 0
    ntp_in_nanos = floor(convert_ntp_to_millis(str(ntp_time)) * 1000000)
    # define offset: sys_time - ntp = offset 
    #                => ntp = (sys_time - offset) / 1000 (in micros) 
    offset = sys_time - ntp_in_nanos
    print(f"converted ntp_in_millis: {ntp_in_nanos}")
    print(f"system time: {sys_time}")
    print(f"offset calculated: {offset}")
    return offset

    
def convert_ntp_to_millis(time_string):
    if len(str(time_string)) < 5:
        return 1
    time = time_string.split(" ")[1].split("+")[0]
    hour = int(time.split(":")[0])
    mins = int(time.split(":")[1])
    sec = floor(float(time.split(":")[2]))
    milli_sec = int(floor(int(time.split(".")[1]) / 1000))
    time_final = hour*60*60*1000 + mins*60*1000 + sec*1000 + milli_sec
    return time_final

def test_offset(offset):
    NTP_Client = ntplib.NTPClient()
    counter = 0
    while counter < 10:
        curr_sys_time = time.time_ns()
        ntp_time_calc_millis = floor((curr_sys_time - offset) / 1000000)
        try:
            actual_ntp = convert_ntp_to_millis(str(datetime.fromtimestamp(NTP_Client.request(NTP_SERVER, version=3).orig_time, timezone.utc)))
        except Exception:
            actual_ntp = 0
            print("could not retrieve timing from ntp server")
        print(f"calculated time is: {ntp_time_calc_millis}")
        print(f"actual ntp: {actual_ntp}\n")
        print(f"difference [actual - calculated in millis]: {actual_ntp - ntp_time_calc_millis}")
        counter += 1
        time.sleep(3)

def get_time_seconds():
    counter = 0
    while counter < 5:
        time_in_millis = time.time() * 1000;
        # i want the first 7 digits
        time_in_millis %= 10000000
        time_in_millis = floor(time_in_millis)
        print(f"current time: {time_in_millis}")
        counter += 1
        time.sleep(1)




BLUNO_TIME_DIFF = 0
NTP_TIME_DIFF = 0

# 2020-10-24 14:34:07.861584+00:00
def convert_ntp_to_millis(time_string):
    if len(str(time_string)) < 5:
        return -1
    time = time_string.split(" ")[1].split("+")[0]
    hour = int(time.split(":")[0])
    mins = int(time.split(":")[1])
    sec = floor(float(time.split(":")[2]))
    milli_sec = int(floor(int(time.split(".")[1]) / 1000))
    time_final = hour*60*60*1000 + mins*60*1000 + sec*1000 + milli_sec
    return time_final

def test_ntp_lib():
    NTP_Client = ntplib.NTPClient()
    counter = 0
    while counter < 10:
        counter += 1
        while counter < 10:
            try:
                t1 = convert_ntp_to_millis(str(datetime.fromtimestamp((NTP_Client.request(NTP_SERVER, version=3)).orig_time, timezone.utc)))
                print(t1)
                break
            except Exception as e:
                print(e)
                counter += 1
        time.sleep(1)

def time_sync_laptop_with_ntp():
    NTP_Client = ntplib.NTPClient()
    counter = 0
    is_success = False
    while counter < 10:
        try:
            ntp_request = NTP_Client.request(NTP_SERVER, version=3)
            ntp_time = datetime.fromtimestamp(ntp_request.orig_time, timezone.utc)
            sys_time = floor(time.time_ns() / 1000000)
            print("successfully gotten time timing")
            print(f"Sys time: {sys_time}")
            is_success = True
            break
        except Exception:
            print("failure")
            counter += 1
    if not is_success:
        return False
    # ntp_in_nanos = floor(self.convert_ntp_to_millis(str(ntp_time)) * 1000000)
    ntp_in_millis = convert_ntp_to_millis(str(ntp_time))
    print(f"Ntp in millis: {ntp_in_millis}")
    # define offset: sys_time - ntp = offset 
    #                => ntp = (sys_time - offset) / 1000000 (in micros) 
    # self.laptop_time_offset = sys_time - ntp_in_nanos 
    LAPTOP_TIME_DIFF = sys_time - ntp_in_millis     
    print(f"Laptop time diff: {LAPTOP_TIME_DIFF}")
    return True, LAPTOP_TIME_DIFF    

def handshake():
    return floor((time.time() * 1000) % 10000000)

def driver():
    hasSynced = False
    while not hasSynced:
        hasSynced, LAPTOP_TIME_DIFF = time_sync_laptop_with_ntp()
    t1 = floor(time.time_ns() / 1000000)
    t2 = handshake()
    t3 = floor(time.time_ns() / 1000000)
    RTT_BY_TWO = (t3 - t1) / 2
    BLUNO_TIME_DIFF = floor((t3 - RTT_BY_TWO) - t2)
    NTP_TIME_DIFF = BLUNO_TIME_DIFF - LAPTOP_TIME_DIFF

    print(f"bluno time diff: {BLUNO_TIME_DIFF}")
    print(f"laptop time diff: {LAPTOP_TIME_DIFF}")
    print(f"ntp time diff: {NTP_TIME_DIFF}")

    counter = 0
    NTP_Client = ntplib.NTPClient()
    while counter < 10:
        try:
            time_final = floor(handshake() + NTP_TIME_DIFF)
            start = time.time()
            print(f"corrected bluno timing: {time_final}")
            ntp_request = NTP_Client.request(NTP_SERVER, version=3)
            ntp_time = datetime.fromtimestamp(ntp_request.orig_time, timezone.utc)
            ntp_in_millis = convert_ntp_to_millis(str(ntp_time))
            end = time.time()
            print(f"actual ntp timing: {ntp_in_millis}")
            print(f"operation time: {end - start}")
            counter += 1
            time.sleep(2)
        except Exception as e:
            print(e)


def main():
    driver()
    # test_ntp_lib()
    #test_offset(calculate_offset())
    #get_time_seconds()



if __name__ == "__main__":
    main()

# NTP_Client = ntplib.NTPClient()
# counter = 0
# while counter < 5:
#     ntp_request = 
#     t1 = datetime.fromtimestamp(ntp_request.orig_time, timezone.utc)
#     t2 = datetime.fromtimestamp(ntp_request.tx_time, timezone.utc)
#     t3 = time.time_ns()
#     t4 = ntp_request.offset

    
#     print(f"orig_time: {t1}")
#     print(f"tx_time: {t2}")
#     print(f"time_ns: {t3}")
#     print(f"ntp time offset: {t4}")
#     counter += 1
#     time.sleep(2)



