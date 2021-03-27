import sys
import time
import json
from threading import Thread
import crc8
from bluepy import btle
from bluepy.btle import BTLEException

char_uuid = "0000dfb1-0000-1000-8000-00805f9b34fb"
service_uuid = "0000dfb0-0000-1000-8000-00805f9b34fb"

connections = {}
connection_threads = {}
connected_addr=[]
main_data={} 


#(a,b)(c,d)(e,f) <glove,position>
#listed all bluetooth MAC address.
a = "C8:DF:84:FE:43:70" #ok 
b = "34:15:13:22:A1:26" #ok
c = "34:15:13:22:A5:72"  #ok
d = "2C:AB:33:CC:17:46" #ok
e = "2C:AB:33:CC:68:D4" #ok 
f = "C8:DF:84:FE:52:77" #ok

mac_map = {
"a" : "C8:DF:84:FE:43:70", #ok 
"b" : "34:15:13:22:A1:26", #ok
"c" : "34:15:13:22:A5:72",  #ok
"d" : "2C:AB:33:CC:17:46", #ok
"e" : "2C:AB:33:CC:68:D4", #ok 
"f" : "C8:DF:84:FE:52:77", #ok
}

#define comms bluetooth
glove_bt = a
position_bt = c
#edit after each set
text_file_name = "move.txt"
#Set up initial state for bluno
bt_addrs = [glove_bt]

#fucntion to connect bluno
def connectToBluno():
    index = 10
    print("Connecting to bluno ...")
    for addr in bt_addrs:
        #only connects to bluno registered in bt_addr, give them their respective indexes
        if (addr==glove_bt):
            index=0
        if (addr==position_bt):
            index=1
        p = btle.Peripheral(addr)
        connections[index]=p
        t = ConnectionHandlerThread(index, addr, False)
        #start thread
        t.start()
        connection_threads[index]=t

#able to reconnect, but serials comms have junk inside
def reconnection(addr,index):
        print("reconnecting bluno")
        while True:
            try:
                p = btle.Peripheral(addr)
                connections[index]=p
                t = ConnectionHandlerThread(index, addr, True)
                #start thread
                t.start()
                connection_threads[index]=t
                break
            except Exception:
                time.sleep(1)

#data processing for incoming packets
def clean_data(info):
    return(info[2:-1])
#data processing for incoming packets
def rm_symbol(data):
    while True:
        if (data[0] == '#'):
            data = data[1:]
        else:
            return data

#Fucntion to check CRC match data receive
def crc_check(data_string):
    hash = crc8.crc8()
    crc = data_string[-2:]
    data_string = data_string[2:-2]
    hash.update(bytes(data_string, "utf-8"))
    if (hash.hexdigest() == crc):
        return True
    else:
        return False

class MyDelegate(btle.DefaultDelegate):
    def __init__(self, connection_index):
        btle.DefaultDelegate.__init__(self)
        self.connection_index = connection_index
        self.ID=str(connection_index)

    def handleNotification(self, cHandle, data):
        time.sleep(0.02)
        data_string = clean_data(str(data))
        # print(data_string)
        # print(data_string)
        if crc_check(data_string):
            # PASS CRC
            BEETLE_ID = data_string[0]
            PACKET_ID = data_string[1]
            DATA = rm_symbol(data_string[2:-2])
            # print(DATA)
            #info handle for ID 1
            # if ((BEETLE_ID == self.ID)and (PACKET_ID == '8')):
            # connection_threads[self.connection_index].dance=True
            if ((BEETLE_ID == self.ID)and (PACKET_ID == '9')):
                connection_threads[self.connection_index].sync=True
                connection_threads[self.connection_index].millis=DATA
            if ((BEETLE_ID == self.ID)and (PACKET_ID == '1') and (DATA == "HANDSHAKE")):
                connection_threads[self.connection_index].handshake=True
            if ((BEETLE_ID == self.ID)and (PACKET_ID == '0') and (DATA == "ACK")):
                connection_threads[self.connection_index].ACK=True
            if ((BEETLE_ID == self.ID)and (PACKET_ID == '3')):
                text = DATA.split("|")
                connection_threads[self.connection_index].current_data["roll"]=text[0]
                connection_threads[self.connection_index].current_data["pitch"]=text[1]
            if ((BEETLE_ID == self.ID)and (PACKET_ID == '4')):
                text = DATA.split("|")
                connection_threads[self.connection_index].current_data["yaw"]=text[0]
                connection_threads[self.connection_index].current_data["AccX"]=text[1]
            if ((BEETLE_ID == self.ID)and (PACKET_ID == '5')):
                text = DATA.split("|")
                connection_threads[self.connection_index].current_data["AccY"]=text[0]
                connection_threads[self.connection_index].current_data["AccZ"]=text[1]
            if ((BEETLE_ID == self.ID)and (PACKET_ID == '6')):
                try:
                    text = DATA.split("|")
                    connection_threads[self.connection_index].current_data["millis"]=text[0]
                    print(text[1])
                except:
                    connection_threads[self.connection_index].current_data["millis"]=DATA
            if ((BEETLE_ID == self.ID)and (PACKET_ID == '7')):
                connection_threads[self.connection_index].position_data=DATA
                print(DATA)
                print(time.time())
        else:
            #FAIL CRC. doesnt matter as during data connecting if missing packet, err would be sent
            print("ERR in CRC")
            time.sleep(0.01)


#Thread gnerating for each bluno.
class ConnectionHandlerThread(Thread):
    dance=False
    handshake = False
    ACK = False
    clear =False
    sync =False
    last_sync_time=0
    millis=0
    err_count=0
    current_data={
        "roll" : "#",
        "pitch" : "#",
        "yaw" : "#",
        "AccX" : "#",
        "AccY" : "#",
        "AccZ" : "#",
        "millis" : "#"
    }

    def __init__(self,connection_index, addr, reconnect):
        print("connected to",addr,"\n")
        Thread.__init__(self)
        self.connection_index = connection_index
        self.addr = addr
        self.connection = (connections[self.connection_index])
        self.connection.setDelegate(MyDelegate(self.connection_index))
        self.reconnect=reconnect
        self.service=self.connection.getServiceByUUID(service_uuid)
        self.characteristic=self.service.getCharacteristics()[0]
        self.global_counter = 0
        if self.connection_index==1:
            self.textfile = "position.txt"
        else:
            self.textfile = "move.txt"

    def run(self):
        while True:
            if (self.reconnect):
                time.sleep(1)
                print("reconnect")
                self.clear_proto(self.connection)
            try:
                #call handshake
                self.handshake_proto(self.connection)
                if (self.connection_index==0):
                    #call data collecting comms
                    self.data_proto(self.connection)
                else:
                    #call position collectiog comms
                    self.pos_proto(self.connection)
            except BTLEException:
                #will only enter if problem with connection. IE disconnect
                self.connection.disconnect()
                #start a function to create new thread
                reconnect = Thread(target=reconnection(self.addr,self.connection_index))
                reconnect.start()
                #Current Thread END
                sys.exit(1)

    def clear_proto(self,p):
        while not self.handshake:
            self.characteristic.write(bytes("H", "utf-8"), withResponse=False)
            # Wait for Handshake packet from bluno 
            p.waitForNotifications(0.01)
        self.handshake=False


    def handshake_proto(self,p):
        # Send handshake packet
        print("HANDSHAKE INITIATED")
        self.characteristic.write(bytes("H", "utf-8"), withResponse=False)
        # Wait for Handshake packet from bluno 
        while (not self.handshake):
            p.waitForNotifications(2)
        self.handshake=False
        # Send back ACK
        print("HANDSHAKE RE2C:AB:33:CC:17:4CIEVED, RETURN ACK")
        while (not self.ACK):
            time.sleep(0.5)
            self.characteristic.write(bytes("A", "utf-8"), withResponse=False)
            p.waitForNotifications(2)
        self.ACK=False
        #get millis
        self.time_sync(p)

    def pos_proto(self,p):
        while True:
            p.waitForNotifications(1)
            
    def data_proto(self,p):
        error = False
        # recieve info for current data set
        while True:
            self.current_data={
                "roll" : "#",
                "pitch" : "#",
                "yaw" : "#",
                "AccX" : "#",
                "AccY" : "#",
                "AccZ" : "#",
                "millis" : "#"
            }
            #some loops to ensure all packets supposed to be recieved     
            for x in range(6):
                p.waitForNotifications(0.1)
                # print(self.current_data)
                if (self.current_data["millis"]!='#'):
                        break  
            #Check if all data recieved nicely
            for x in self.current_data:
                if (self.current_data[x]=='#'):
                    # #send back err
                    print("DATA ERR, RETURN ERROR")
                    self.characteristic.write(bytes("E", "utf-8"), withResponse=False)
                    error = True
                    #Buffer err with 0 instead
                    
                    self.current_data={
                        "roll" : "0",
                        "pitch" : "0",
                        "yaw" : "0",
                        "AccX" : "0",
                        "AccY" : "0",
                        "AccZ" : "0",
                        "millis" : "#"
                    }
                    file1 = open(self.textfile,"a")
                    print(f"{self.global_counter} DATA: {self.current_data}")
                    self.global_counter += 1 
                    file1.write(json.dumps(self.current_data))
                    file1.write("\n")
                    file1.close()
                    
                    break
            if error:
                if (self.err_count>8):
                    raise BTLEException("help la")
                self.err_count=self.err_count+1
                error =False
                continue
            self.err_count=0
            #Time SYNC HERE
            # if (time.time()>self.last_sync_time+60):
            #     self.time_sync(p)
            #record data set into .txt file
            file1 = open(self.textfile,"a")
            print(f"{self.global_counter} DATA: {self.current_data}")
            self.global_counter += 1 
            file1.write(json.dumps(self.current_data))
            file1.write("\n")
            file1.close()
            # print(self.connection_index)
            #send back ACK
            self.characteristic.write(bytes("A", "utf-8"), withResponse=False)

    #Req for millis at the bluno side, would be use for time-stamp calculation for data
    def time_sync(self,p):
        self.sync=False
        print("SEND SYNC REQ")
        self.characteristic.write(bytes("T", "utf-8"), withResponse=False)
        while (not self.sync):
            p.waitForNotifications(1)
        #self.millis -> is updated 
        self.last_sync_time=time.time()
        file1 = open(self.textfile,"a") 
        file1.write(json.dumps(self.millis))
        file1.write("\n")
        file1.close()
        self.characteristic.write(bytes("A", "utf-8"), withResponse=False)
        print(self.millis)

def main():
    #only calls for connection for bluno
    global glove_bt
    glove_bt = input("Please enter your dance glove letter: \n")
    glove_bt = mac_map[glove_bt]
    # global bt_addrs
    bt_addrs = [glove_bt]
    connectToBluno()

if __name__ == "__main__":
    main()
