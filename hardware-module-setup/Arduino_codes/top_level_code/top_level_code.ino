/* 
// Top level code to run on Arduino
// It handles sending sensor info to Raspberry Pi and executes commands received from Raspberry Pi
*/

#include <DHT.h>
#include <DHT_U.h>
#include <SoftwareSerial.h>

// sensor pin numbers
#define MQ_9_PIN A0
#define YL_1_PIN A1
#define YL_2_PIN A2
#define YL_3_PIN A3
#define YL_4_PIN A4
#define YL_5_PIN A5
#define YL_6_PIN A6
#define YL_7_PIN A6
#define DHT_PIN 2
#define WATER_LEVEL_PIN 3

// actuator pin numbers
#define TOO_MUCH_SMOKE_LED_PIN 4
#define WATER_SHORTAGE_LED_PIN 5
#define FAN_RELAY_PIN 6
#define PUMP_1_RELAY_PIN 7
#define PUMP_2_RELAY_PIN 8
#define IDLE_RELAY_PIN 9

// constant initial XBee message bytes:
#define FD 0xfd
#define NUMS_COUNT 0x0b
#define RASP_PI_ADDR_1 0x00
#define RASP_PI_ADDR_2 0x01

// General constants
#define DHTTYPE DHT11
#define TEMP_DEF_YL_VALUE 100
#define MESSAGE_SIZE 15
#define INIT_XBEE_BYTE_SIZE 4
#define COMMANDS_SIZE 6

struct GreenhouseData {
  char YL_1_value;
  char YL_2_value;
  char YL_3_value;
  char YL_4_value;
  char YL_5_value;
  char YL_6_value;
  char YL_7_value;
  char temp_value;
  char humidity_value;
  char MQ_9_value;
  char water_level_value;
};

GreenhouseData data;
char message [MESSAGE_SIZE];
bool prev_commands [COMMANDS_SIZE];

SoftwareSerial XBeeSer (11, 12); // (RX, TX)
DHT dht_sensor (DHT_PIN, DHTTYPE);

// *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
// *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
// *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

void setup() {
  Serial.begin(9600);
  XBeeSer.begin(9600);
  
  pinMode(YL_1_PIN, INPUT);
  pinMode(YL_2_PIN, INPUT);
  pinMode(YL_3_PIN, INPUT);
  pinMode(YL_4_PIN, INPUT);
  pinMode(YL_5_PIN, INPUT);
  pinMode(YL_6_PIN, INPUT);
  pinMode(YL_7_PIN, INPUT);
  pinMode(MQ_9_PIN, INPUT);
  pinMode(DHT_PIN, INPUT);
  pinMode(WATER_LEVEL_PIN, INPUT);
  
  pinMode(WATER_SHORTAGE_LED_PIN, OUTPUT); digitalWrite(WATER_SHORTAGE_LED_PIN, LOW);
  pinMode(TOO_MUCH_SMOKE_LED_PIN, OUTPUT); digitalWrite(TOO_MUCH_SMOKE_LED_PIN, LOW);
  pinMode(FAN_RELAY_PIN, OUTPUT); digitalWrite(FAN_RELAY_PIN, HIGH);
  pinMode(PUMP_1_RELAY_PIN, OUTPUT); digitalWrite(PUMP_1_RELAY_PIN, HIGH);
  pinMode(PUMP_2_RELAY_PIN, OUTPUT); digitalWrite(PUMP_2_RELAY_PIN, HIGH);
  pinMode(IDLE_RELAY_PIN, OUTPUT); digitalWrite(IDLE_RELAY_PIN, HIGH);
  
  message[0] = FD;
  message[1] = NUMS_COUNT;
  message[2] = RASP_PI_ADDR_1;
  message[3] = RASP_PI_ADDR_2;

  prev_commands[0] = false;
  prev_commands[1] = false;
  prev_commands[2] = false;
  prev_commands[3] = false;
}

void loop() {
//  Sending greenhouse info to Raspberry Pi
  Serial.println("PHASE I: COLLECTING AND SENDING DATA");
  data = read_sensor_data();
  form_message(message, data);
  print_message(message);
  delay(100);
  send_message(message);

//  Receiving Raspberry Pi response and acting accordingly before sending data again
  Serial.println("PHASE II: RECEIVING AND EXECUTING COMMANDS");
  Serial.print("BEFORE: "); print_commands();
  read_raspberry_commands();
  exec_raspberry_commands();
  Serial.print("AFTER: "); print_commands();

  delay(5000);
  Serial.println();
  Serial.println();
}

/* 
 * Helper functions for interactions with Raspberry Pi 
 * i.e. sending sensor info as well as receiving and executing commands
 */

GreenhouseData read_sensor_data(){
  /* 
   *  reads sensor data and returns an instance of the 
   *  GreenhouseData struct containing these data
   */
   
  GreenhouseData res;
  res.YL_1_value = analogRead(YL_1_PIN) / 4;
  res.YL_2_value = analogRead(YL_2_PIN) / 4;
  res.YL_3_value = analogRead(YL_3_PIN) / 4;
  res.YL_4_value = analogRead(YL_4_PIN) / 4;
  res.YL_5_value = analogRead(YL_5_PIN) / 4;
  res.YL_6_value = analogRead(YL_6_PIN) / 4;
  res.YL_7_value = analogRead(YL_7_PIN) / 4;
  
  res.temp_value = dht_sensor.readTemperature();
  res.humidity_value = dht_sensor.readHumidity();
  res.MQ_9_value = analogRead(MQ_9_PIN);
  res.water_level_value = digitalRead(WATER_LEVEL_PIN);

  Serial.println("##### ==> sensor data collected");
  return res;
}

void form_message(char message[], GreenhouseData data){
  /* 
   *  receieves data collected from sensors and embeds them
   *  inside the char array defining the message to be sent
   */
   
  message[4] = data.temp_value;
  message[5] = data.humidity_value;
  message[6] = data.MQ_9_value;
  message[7] = data.water_level_value;
  message[8] = data.YL_1_value;
  message[9] = data.YL_2_value;
  message[10] = data.YL_3_value;
  message[11] = data.YL_4_value;
  message[12] = data.YL_5_value;
  message[13] = data.YL_6_value;
  message[14] = data.YL_7_value;
  
  Serial.println("##### ==> message formed");
  return;
}

void print_message(char message[]){
  /* 
   *  prints the message to be sent for debugging purposes
   */
   
  Serial.print("Message to be sent: ");
  for (int i = 0; i < MESSAGE_SIZE; i++){
    Serial.print(int(message[i]));
    Serial.print(" ");
  }
  Serial.println();
  return;
}

void send_message(char message[]){
  /* 
   *  receives an array of char (message) and sends them using
   *  the XBee board connected to a SoftwareSerial 
   */
   
  for (int i = 0; i < MESSAGE_SIZE; i++){
    XBeeSer.print(message[i]);
  }
  
  Serial.println("##### ==> message sent");
  return;
}

void read_raspberry_commands() {
  /* 
   *  reads a XBee message sent by the controlling Raspberry Pi containing 4 commands
   *  which determine the state of fan and pump as well as the those of the LEDs    
   *  representing the status for smoke concentration and reservoir water level  
   */
   
  while(true) {
    if (XBeeSer.available() <= 0)
      continue;

    while (XBeeSer.available() > 0) {
      // Reading the initial 4 XBee bytes (fd, message size, and destination addr)
      for (int ind = 0; ind < INIT_XBEE_BYTE_SIZE; ind++){
        int dummy = int(XBeeSer.read());
        delay(5);
//        Serial.print("dummy --------> "); Serial.println(dummy);
      } 

      // Reading the message bytes
      for (int ind = 0; ind < COMMANDS_SIZE; ind++){
        int received_byte = int(XBeeSer.read());
        if (received_byte == 0) {prev_commands[ind] = false;}
        else {prev_commands[ind] = true;}
//        Serial.print("byte --------> "); Serial.println(received_byte);
      }

      // Reading the origin address bytes
      int addr1 = int(XBeeSer.read());
      int addr2 = int(XBeeSer.read());
//      Serial.print("addr1 --------> "); Serial.println(addr1);
//      Serial.print("addr2 --------> "); Serial.println(addr2);
      break;
    }
    
    break; 
  }
  
  Serial.println("$$$$$ ==> finished READING Raspberry commands");
}

void exec_raspberry_commands() {
  /* 
   *  uses the received Raspberry Pi commands to determine the status of
   *  fan, pump, and the LEDs representing the status for smoke concentration 
   *  and reservoir water level  
   */
   
  if (prev_commands[0] == true) digitalWrite(TOO_MUCH_SMOKE_LED_PIN, HIGH);
  else                          digitalWrite(TOO_MUCH_SMOKE_LED_PIN, LOW);
  
  if (prev_commands[1] == true) digitalWrite(WATER_SHORTAGE_LED_PIN, HIGH);
  else                          digitalWrite(WATER_SHORTAGE_LED_PIN, LOW);
  
  if (prev_commands[2] == true) digitalWrite(FAN_RELAY_PIN, LOW);
  else                          digitalWrite(FAN_RELAY_PIN, HIGH);
  
  if (prev_commands[3] == true) digitalWrite(PUMP_1_RELAY_PIN, LOW);
  else                          digitalWrite(PUMP_1_RELAY_PIN, HIGH);

  if (prev_commands[4] == true) digitalWrite(PUMP_2_RELAY_PIN, LOW);
  else                          digitalWrite(PUMP_2_RELAY_PIN, HIGH);

  if (prev_commands[5] == true) digitalWrite(IDLE_RELAY_PIN, LOW);
  else                          digitalWrite(IDLE_RELAY_PIN, HIGH);

  Serial.println("$$$$$ ==> finished EXECUTING Raspberry commands");
}

void print_commands() {
  /* 
   *  prints the current status of received Rapsberry Pi commands 
   */
   
  Serial.print ("[");
  for (int ind = 0; ind < COMMANDS_SIZE; ind++) {
    if (prev_commands[ind] == true) Serial.print("1");
    else Serial.print("0");
  }
  Serial.println("]");
}
/* 
// Top level code to run on Arduino
// It handles sending sensor info to Raspberry Pi and executes commands received from Raspberry Pi
*/

#include <DHT.h>
#include <DHT_U.h>
#include <SoftwareSerial.h>

// sensor pin numbers
#define MQ_9_PIN A0
#define YL_1_PIN A1
#define YL_2_PIN A2
#define YL_3_PIN A3
#define YL_4_PIN A4
#define YL_5_PIN A5
#define YL_6_PIN A6
#define YL_7_PIN A6
#define DHT_PIN 2
#define WATER_LEVEL_PIN 3

// actuator pin numbers
#define TOO_MUCH_SMOKE_LED_PIN 4
#define WATER_SHORTAGE_LED_PIN 5
#define FAN_RELAY_PIN 6
#define PUMP_1_RELAY_PIN 7
#define PUMP_2_RELAY_PIN 8
#define IDLE_RELAY_PIN 9

// constant initial XBee message bytes:
#define FD 0xfd
#define NUMS_COUNT 0x0b
#define RASP_PI_ADDR_1 0x00
#define RASP_PI_ADDR_2 0x01

// General constants
#define DHTTYPE DHT11
#define TEMP_DEF_YL_VALUE 100
#define MESSAGE_SIZE 15
#define INIT_XBEE_BYTE_SIZE 4
#define COMMANDS_SIZE 6

struct GreenhouseData {
  char YL_1_value;
  char YL_2_value;
  char YL_3_value;
  char YL_4_value;
  char YL_5_value;
  char YL_6_value;
  char YL_7_value;
  char temp_value;
  char humidity_value;
  char MQ_9_value;
  char water_level_value;
};

GreenhouseData data;
char message [MESSAGE_SIZE];
bool prev_commands [COMMANDS_SIZE];

SoftwareSerial XBeeSer (11, 12); // (RX, TX)
DHT dht_sensor (DHT_PIN, DHTTYPE);

// *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
// *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
// *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

void setup() {
  Serial.begin(9600);
  XBeeSer.begin(9600);
  
  pinMode(YL_1_PIN, INPUT);
  pinMode(YL_2_PIN, INPUT);
  pinMode(YL_3_PIN, INPUT);
  pinMode(YL_4_PIN, INPUT);
  pinMode(YL_5_PIN, INPUT);
  pinMode(YL_6_PIN, INPUT);
  pinMode(YL_7_PIN, INPUT);
  pinMode(MQ_9_PIN, INPUT);
  pinMode(DHT_PIN, INPUT);
  pinMode(WATER_LEVEL_PIN, INPUT);
  
  pinMode(WATER_SHORTAGE_LED_PIN, OUTPUT); digitalWrite(WATER_SHORTAGE_LED_PIN, LOW);
  pinMode(TOO_MUCH_SMOKE_LED_PIN, OUTPUT); digitalWrite(TOO_MUCH_SMOKE_LED_PIN, LOW);
  pinMode(FAN_RELAY_PIN, OUTPUT); digitalWrite(FAN_RELAY_PIN, HIGH);
  pinMode(PUMP_1_RELAY_PIN, OUTPUT); digitalWrite(PUMP_1_RELAY_PIN, HIGH);
  pinMode(PUMP_2_RELAY_PIN, OUTPUT); digitalWrite(PUMP_2_RELAY_PIN, HIGH);
  pinMode(IDLE_RELAY_PIN, OUTPUT); digitalWrite(IDLE_RELAY_PIN, HIGH);
  
  message[0] = FD;
  message[1] = NUMS_COUNT;
  message[2] = RASP_PI_ADDR_1;
  message[3] = RASP_PI_ADDR_2;

  prev_commands[0] = false;
  prev_commands[1] = false;
  prev_commands[2] = false;
  prev_commands[3] = false;
}

void loop() {
//  Sending greenhouse info to Raspberry Pi
  Serial.println("PHASE I: COLLECTING AND SENDING DATA");
  data = read_sensor_data();
  form_message(message, data);
  print_message(message);
  delay(100);
  send_message(message);

//  Receiving Raspberry Pi response and acting accordingly before sending data again
  Serial.println("PHASE II: RECEIVING AND EXECUTING COMMANDS");
  Serial.print("BEFORE: "); print_commands();
  read_raspberry_commands();
  exec_raspberry_commands();
  Serial.print("AFTER: "); print_commands();

  delay(5000);
  Serial.println();
  Serial.println();
}

/* 
 * Helper functions for interactions with Raspberry Pi 
 * i.e. sending sensor info as well as receiving and executing commands
 */

GreenhouseData read_sensor_data(){
  /* 
   *  reads sensor data and returns an instance of the 
   *  GreenhouseData struct containing these data
   */
   
  GreenhouseData res;
  res.YL_1_value = analogRead(YL_1_PIN) / 4;
  res.YL_2_value = analogRead(YL_2_PIN) / 4;
  res.YL_3_value = analogRead(YL_3_PIN) / 4;
  res.YL_4_value = analogRead(YL_4_PIN) / 4;
  res.YL_5_value = analogRead(YL_5_PIN) / 4;
  res.YL_6_value = analogRead(YL_6_PIN) / 4;
  res.YL_7_value = analogRead(YL_7_PIN) / 4;
  
  res.temp_value = dht_sensor.readTemperature();
  res.humidity_value = dht_sensor.readHumidity();
  res.MQ_9_value = analogRead(MQ_9_PIN);
  res.water_level_value = digitalRead(WATER_LEVEL_PIN);

  Serial.println("##### ==> sensor data collected");
  return res;
}

void form_message(char message[], GreenhouseData data){
  /* 
   *  receieves data collected from sensors and embeds them
   *  inside the char array defining the message to be sent
   */
   
  message[4] = data.temp_value;
  message[5] = data.humidity_value;
  message[6] = data.MQ_9_value;
  message[7] = data.water_level_value;
  message[8] = data.YL_1_value;
  message[9] = data.YL_2_value;
  message[10] = data.YL_3_value;
  message[11] = data.YL_4_value;
  message[12] = data.YL_5_value;
  message[13] = data.YL_6_value;
  message[14] = data.YL_7_value;
  
  Serial.println("##### ==> message formed");
  return;
}

void print_message(char message[]){
  /* 
   *  prints the message to be sent for debugging purposes
   */
   
  Serial.print("Message to be sent: ");
  for (int i = 0; i < MESSAGE_SIZE; i++){
    Serial.print(int(message[i]));
    Serial.print(" ");
  }
  Serial.println();
  return;
}

void send_message(char message[]){
  /* 
   *  receives an array of char (message) and sends them using
   *  the XBee board connected to a SoftwareSerial 
   */
   
  for (int i = 0; i < MESSAGE_SIZE; i++){
    XBeeSer.print(message[i]);
  }
  
  Serial.println("##### ==> message sent");
  return;
}

void read_raspberry_commands() {
  /* 
   *  reads a XBee message sent by the controlling Raspberry Pi containing 4 commands
   *  which determine the state of fan and pump as well as the those of the LEDs    
   *  representing the status for smoke concentration and reservoir water level  
   */
   
  while(true) {
    if (XBeeSer.available() <= 0)
      continue;

    while (XBeeSer.available() > 0) {
      // Reading the initial 4 XBee bytes (fd, message size, and destination addr)
      for (int ind = 0; ind < INIT_XBEE_BYTE_SIZE; ind++){
        int dummy = int(XBeeSer.read());
        delay(5);
//        Serial.print("dummy --------> "); Serial.println(dummy);
      } 

      // Reading the message bytes
      for (int ind = 0; ind < COMMANDS_SIZE; ind++){
        int received_byte = int(XBeeSer.read());
        if (received_byte == 0) {prev_commands[ind] = false;}
        else {prev_commands[ind] = true;}
//        Serial.print("byte --------> "); Serial.println(received_byte);
      }

      // Reading the origin address bytes
      int addr1 = int(XBeeSer.read());
      int addr2 = int(XBeeSer.read());
//      Serial.print("addr1 --------> "); Serial.println(addr1);
//      Serial.print("addr2 --------> "); Serial.println(addr2);
      break;
    }
    
    break; 
  }
  
  Serial.println("$$$$$ ==> finished READING Raspberry commands");
}

void exec_raspberry_commands() {
  /* 
   *  uses the received Raspberry Pi commands to determine the status of
   *  fan, pump, and the LEDs representing the status for smoke concentration 
   *  and reservoir water level  
   */
   
  if (prev_commands[0] == true) digitalWrite(TOO_MUCH_SMOKE_LED_PIN, HIGH);
  else                          digitalWrite(TOO_MUCH_SMOKE_LED_PIN, LOW);
  
  if (prev_commands[1] == true) digitalWrite(WATER_SHORTAGE_LED_PIN, HIGH);
  else                          digitalWrite(WATER_SHORTAGE_LED_PIN, LOW);
  
  if (prev_commands[2] == true) digitalWrite(FAN_RELAY_PIN, LOW);
  else                          digitalWrite(FAN_RELAY_PIN, HIGH);
  
  if (prev_commands[3] == true) digitalWrite(PUMP_1_RELAY_PIN, LOW);
  else                          digitalWrite(PUMP_1_RELAY_PIN, HIGH);

  if (prev_commands[4] == true) digitalWrite(PUMP_2_RELAY_PIN, LOW);
  else                          digitalWrite(PUMP_2_RELAY_PIN, HIGH);

  if (prev_commands[5] == true) digitalWrite(IDLE_RELAY_PIN, LOW);
  else                          digitalWrite(IDLE_RELAY_PIN, HIGH);

  Serial.println("$$$$$ ==> finished EXECUTING Raspberry commands");
}

void print_commands() {
  /* 
   *  prints the current status of received Rapsberry Pi commands 
   */
   
  Serial.print ("[");
  for (int ind = 0; ind < COMMANDS_SIZE; ind++) {
    if (prev_commands[ind] == true) Serial.print("1");
    else Serial.print("0");
  }
  Serial.println("]");
}

