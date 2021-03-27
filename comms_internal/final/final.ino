#include <CRCx.h>
#include <math.h>
//Set beetle_id
#define beetle_id '0'

// Power saving function
#define PRR_SPI_MASK 0b00000100
#define ADCSRA_ADC_MASK 0b10000000
#define PRR_ADC_MASK 0b00000001

//Preset data to be sent
char s_msg[] = "DANCE";
char h_msg[] = "HANDSHAKE";
char a_msg[] = "ACK";
//create variable to be used for packet and data processing
char temp_msg[17];
uint8_t data[17];
uint8_t packet[21];
//boolean checks for logic program
//check that data transfer has begin
bool data_started = false;
//check if receive error or handshake from laptop
//bool startDance_confirmed = false;
bool error = false;
bool handshake = false;
bool handshake_confirmed = false;
bool next_set = true;
byte temp;
int error_num = 0;
String time;
unsigned long time_out = 99999999;
bool ErrCheck = false;

float err_set[9];
float data_set[9];

/*
   Adapted from Arduino and MPU6050 Accelerometer and Gyroscope Sensor Tutorial
   by Dejan, https://howtomechatronics.com
   1 IMU
   Mean taken for acc threshold
   Auto updates starting position as reference
*/
#include <Wire.h>
const int MPU = 0x68;
float AccX = 0, AccY = 0, AccZ = 0;
float GyroX = 0, GyroY = 0, GyroZ = 0;
float accAngleX = 0, accAngleY = 0, gyroAngleX = 0, gyroAngleY = 0, gyroAngleZ = 0;
float roll = 0, pitch = 0, yaw = 0;
float AccErrorX = 0, AccErrorY = 0, GyroErrorX = 0, GyroErrorY = 0, GyroErrorZ = 0;
double tempX = 0, tempY = 0;
float ftempX = 0, ftempY = 0;
float elapsedTime = 0, currentTime = 0, previousTime = 0;
int c = 0, i = 0;
float AccXMean = 0.0, AccYMean = 0.0;
bool startDance = false;

void setup() {
  //Init Serial at 115200 baudrate
  setupPowerSaving();
  Serial.begin(115200);
  while (!Serial) {
  }
  //IMU
  Wire.begin();                     // Initialize communication

  Wire.beginTransmission(MPU);      // Start communication with MPU6050, 0x68
  Wire.write(0x6B);                 // Talk to the register 6B
  Wire.write(0);                    // Turn on MPU6050
  Wire.endTransmission();           // End the transmission

  Wire.beginTransmission(MPU);      // Config Accelerometer Sensitivity
  Wire.write(0x1C);                 // ACCEL_CONFIG register
  Wire.write(0x08);                 // +-4g
  Wire.endTransmission();

  Wire.beginTransmission(MPU);      // Configure Gyro Sensitivity
  Wire.write(0x1B);                 // GYRO_CONFIG register
  Wire.write(0x00);                 // 250deg/s full scale
  Wire.endTransmission();

  delay(500);
}

void runMPU(const int MPU) {
  // === Read acceleromter data === //
  Wire.beginTransmission(MPU);
  Wire.write(0x3B);               // ACCEL_XOUT_H
  Wire.endTransmission();
  Wire.requestFrom(MPU, 6, true); // Read 6 registers total, each axis value is stored in 2 registers

  //For a range of +-4g, we need to divide the raw values by 8192
  AccX = (Wire.read() << 8 | Wire.read()) / 8192.0; //ACCEL_XOUT_H, ACCEL_XOUT_L
  AccY = (Wire.read() << 8 | Wire.read()) / 8192.0; //ACCEL_YOUT_H, ACCEL_YOUT_L
  AccZ = (Wire.read() << 8 | Wire.read()) / 8192.0; //ACCEL_ZOUT_H, ACCEL_ZOUT_L

  // Calculating Roll and Pitch from the accelerometer data
  tempX = atan(AccY / sqrt(AccX * AccX + AccZ * AccZ));
  tempY = atan(-1 * AccX / sqrt(AccY * AccY + AccZ * AccZ));
  ftempX = float(tempX);
  ftempY = float(tempY);
  accAngleX = (ftempX * 57.29746) - AccErrorX;
  accAngleY = (ftempY * 57.29746) - AccErrorY;

  // === Read gyroscope data === //
  previousTime = currentTime;        // Previous time is stored before the actual time read
  currentTime = millis();            // Current time actual time read
  elapsedTime = (currentTime - previousTime) / 1000; // Divide by 1000 to get seconds

  Wire.beginTransmission(MPU);
  Wire.write(0x43);                // First address of the gyro data
  Wire.endTransmission();
  Wire.requestFrom(MPU, 6, true); // Read 4 registers total, each axis value is stored in 2 registers

  // Gyro data
  GyroX = (Wire.read() << 8 | Wire.read()) / 131.0; //GYRO_XOUT_H, GYRO_XOUT_L
  GyroY = (Wire.read() << 8 | Wire.read()) / 131.0; //GYRO_YOUT_H, GYRO_YOUT_L
  GyroZ = (Wire.read() << 8 | Wire.read()) / 131.0; //GYRO_ZOUT_H, GYRO_ZOUT_L

  // Correct the outputs with the calculated error values
  GyroX = GyroX - GyroErrorX;
  GyroY = GyroY - GyroErrorY;
  GyroZ = GyroZ - GyroErrorZ;

  // Raw values are in degrees per seconds, multiply by seconds to get the angle in degrees
  gyroAngleX = GyroX * elapsedTime; // deg/s * s = deg
  gyroAngleY = GyroY * elapsedTime;
  yaw =  yaw + GyroZ * elapsedTime;

  // Complementary filter - combine acceleromter and gyro angle values
  roll = (0.96 * gyroAngleX) + (0.04 * accAngleX);
  pitch = (0.96 * gyroAngleY) + (0.04 * accAngleY);

  //        Serial.print(roll); Serial.print(" ");
  //        Serial.print(pitch); Serial.print(" ");
  //        Serial.print(yaw); Serial.print(" ");
  //        Serial.print(displayAccXMean); Serial.print(" ");
  //        Serial.print(displayAccYMean); Serial.print(" ");
  //        Serial.print(AccZ); Serial.print(" ");
  //        Serial.println(currentTime);

  data_set[0] = convert_2dp(roll);
  data_set[1] = convert_2dp(pitch);
  data_set[2] = convert_2dp(yaw);
  data_set[3] = convert_2dp(AccX);
  data_set[4] = convert_2dp(AccY);
  data_set[5] = convert_2dp(AccZ);
}


// Calculate accelerometer and gyro data error, place IMU flat to get the proper values
void calculate_IMU_error(int MPU) {
  // Read accelerometer values 200 times
  AccErrorX = 0;
  while (c < 200) {
    // Take accelerometer reading
    Wire.beginTransmission(MPU);
    Wire.write(0x3B);               // First address of the accelerometer data
    Wire.endTransmission(false);
    Wire.requestFrom(MPU, 6, true); // Read 6 registers total, each axis value is stored in 2 registers
    AccX = (Wire.read() << 8 | Wire.read()) / 8192.0 ; //+-4g, 8192 LSB/g (sensitivity)
    AccY = (Wire.read() << 8 | Wire.read()) / 8192.0 ;
    AccZ = (Wire.read() << 8 | Wire.read()) / 8192.0 ;

    // Sum all acc error readings
    tempX = atan(AccY / sqrt(AccX * AccX + AccZ * AccZ));
    tempY = atan(-1 * AccX / sqrt(AccY * AccY + AccZ * AccZ));
    ftempX = float(tempX);
    ftempY = float(tempY);
    AccErrorX = AccErrorX + (ftempX * 57.29746);
    AccErrorY = AccErrorY + (ftempY * 57.29746);
    c++;
  }
  //Divide the sum by 300 to get the error value
  AccErrorX = AccErrorX / 200;
  AccErrorY = AccErrorY / 200;
  c = 0;

  // Read gyro values 300 times
  while (c < 300) {
    // Take gyro reading
    Wire.beginTransmission(MPU);
    Wire.write(0x43); // First address of the gyroscope data
    Wire.endTransmission(false);
    Wire.requestFrom(MPU, 6, true); // Read 6 registers total, each axis value is stored in 2 registers
    GyroX = (Wire.read() << 8 | Wire.read()) / 131.0; // +-250degrees/s
    GyroY = (Wire.read() << 8 | Wire.read()) / 131.0;
    GyroZ = (Wire.read() << 8 | Wire.read()) / 131.0;
    // Sum all readings
    GyroErrorX = GyroErrorX + GyroX;
    GyroErrorY = GyroErrorY + GyroY;
    GyroErrorZ = GyroErrorZ + GyroZ;
    c++;
  }

  //Divide the sum by 300 to get the error value
  GyroErrorX = GyroErrorX / 300;
  GyroErrorY = GyroErrorY / 300;
  GyroErrorZ = GyroErrorZ / 300;
}

//Add # into data as buffer till 16 char.
void data_prepare(char msg[]) {
  int len = strlen(msg);
  int j = 0;
  for (int i = 0; i < 16; i = i + 1) {
    if (16 - i >  len ) {
      data[i] = '#';
    } else {
      data[i] = msg[j];
      j = j + 1;
    }
  }
}


//Attach packet_id, packet_no and crc to data
void packet_prepare(char packet_id) {
  uint8_t result8 = crcx::crc8(data, 16);
  String temp = String(result8, HEX);
  char crc[3];
  temp.toCharArray(crc, 3);
  int j = 0;
  packet[0] = beetle_id;
  packet[1] = packet_id;
  for (int i = 2; i < 18; i = i + 1) {
    packet[i] = data[j];
    j = j + 1;
  }
  if (strlen(crc) == 1) {
    packet[18] = '0';
    packet[19] = crc[0];
  } else {
    packet[18] = crc[0];
    packet[19] = crc[1];
  }
}

//function to send 1 dataset
void dance_data() {
  runMPU(MPU);
  for (int i = 0; i < 6; i++) {
    err_set[i] = data_set[i];
  }
  String pac;
  int set_no = 0;
  int pid = 51; // 3 in ASCII
  String front;
  String back;
  char pac_msg[17];
  //loop 3 times due to 3 packets per data set
  while (set_no < 6) {
    front = String (data_set[set_no]);
    back = String (data_set[set_no + 1]);
    pac = front + "|" + back;
    pac.toCharArray(temp_msg, 17);
    data_prepare(temp_msg);
    packet_prepare(char(pid));
    Serial.print((char*)packet);
    Serial.flush();
    memset(temp_msg, 0, 17);
    memset(data, 0, 17);
    memset(data_set, 0, sizeof(float));
    set_no = set_no + 2;
    pid++;
  }
  //last packet to be send as timestamp
  time = String(millis());
  err_set[6] = millis();
  time.toCharArray(temp_msg, 17);
  data_prepare(temp_msg);
  packet_prepare('6');
  Serial.print((char*)packet);
  Serial.flush();
  memset(temp_msg, 0, 17);
  memset(data, 0, 17);
}

//function to send 1 dataset
void dance_err() {
  String pac;
  int set_no = 0;
  int pid = 51; // 3 in ASCII
  String front;
  String back;
  char pac_msg[17];
  //loop 3 times due to 3 packets per data set
  while (set_no < 6) {
    front = String (err_set[set_no]);
    back = String (err_set[set_no + 1]);
    pac = front + "|" + back;
    pac.toCharArray(temp_msg, 17);
    data_prepare(temp_msg);
    packet_prepare(char(pid));
    Serial.print((char*)packet);
    Serial.flush();
    memset(temp_msg, 0, 17);
    memset(data, 0, 17);
    memset(data_set, 0, sizeof(float));
    set_no = set_no + 2;
    pid++;
  }
  //last packet to be send as timestamp
  time = String((int)err_set[6]);
  time.toCharArray(temp_msg, 17);
  data_prepare(temp_msg);
  packet_prepare('6');
  Serial.print((char*)packet);
  Serial.flush();
  memset(temp_msg, 0, 17);
  memset(data, 0, 17);
}
//Function to ensure all data_set max 2dp?
float convert_2dp (float big) {
  int x10;
  float num;
  x10 = (int)(big * 100.0);
  num = x10 / 100.0;
  return num;
}

void loop() {
  if (!ErrCheck) {
    // Call this function if you need to get the IMU error values for your module
    calculate_IMU_error(MPU);
    ErrCheck = true;
  }
  if (Serial.available()) {
    byte cmd = Serial.read();
    switch (cmd) {
      case 'A': //Recieve ACK
        data_prepare(a_msg);
        packet_prepare('0');
        Serial.print((char*)packet);
        Serial.flush();
        memset(data, 0, 17);
        if (data_started) {
          next_set = true;
          error = false;
          error_num = 0;
        }
        if (handshake_confirmed) {
          startDance = true;
        }
        if (handshake) {
          error = false;
          handshake = false;
          handshake_confirmed = true;
        }
        break;
      case 'H'://Recieve Handshake request
        data_prepare(h_msg);
        packet_prepare('1');
        Serial.print((char*)packet);
        Serial.flush();
        memset(data, 0, 17);
        //Reset all boolean to default
        startDance = false;
        error = false;
        handshake = true;
        handshake_confirmed = false;
        next_set = false;
        error_num = 0;
        //        startDance_confirmed = false;
        break;
      case 'T'://Recieve request for timesync, send millis()
        time = String(millis());
        time.toCharArray(temp_msg, 17);
        data_prepare(temp_msg);
        packet_prepare('9');
        Serial.print((char*)packet);
        Serial.flush();
        memset(temp_msg, 0, 17);
        memset(data, 0, 17);
        break;
      case 'E': //Recieve err
        Serial.flush();
        error = true;
        break;
    }

    //if dont recieve ACK from laptop, send the next set
    if (millis() > time_out) {
      error = true;
    }

    //if dance start send 1 dataset in 3 packets. if issue with any 3, resend packet. if error more than 3 skip current data set.
    if (startDance && handshake_confirmed) {
      //if one of the 3 packets have issue resend all 3 again.
      if (error) {
        if (error_num > 1) {
          next_set = true;
          error_num = 0;
        } else {
          //Call function to resend err_set
          dance_err();
          error_num++;
        }
        error = false;
      }

      data_started = true;
      //Only send next set if ack or err received
      if (next_set) {
        time_out = millis() + 5000;
        //Call function to send data_set
        dance_data();
        next_set = false;
      }
    }
  }
}

// Power saving function
void WDT_off(void)
{
  cli();  // Disable global interrupt
  MCUSR &= ~(1 << WDRF); // Clear WDRF in MCUSR
  WDTCSR |= (1 << WDCE) | (1 << WDE);
  WDTCSR = 0x00;  // Turn off WDT
  sei();
}

void setupPowerSaving()
{
  WDT_off();                  // Turn off the Watchdog Timer
  PRR |= PRR_SPI_MASK;        // Shut down SPI
  ADCSRA |= ADCSRA_ADC_MASK;  // Disable ADC
  PRR |= PRR_ADC_MASK;        // Shut down ADC
}
