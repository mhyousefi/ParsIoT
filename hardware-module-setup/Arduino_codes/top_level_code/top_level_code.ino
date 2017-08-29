
/* 
// Top level code to run on Arduino
// It handles sending sensor info to Raspberry Pi and executes commands received from Raspberry Pi
*/

#include <DHT.h>
#include <DHT_U.h>
#include <SoftwareSerial.h>

#define DHTTYPE DHT11

// sensor pin numbers
#define MQ_9_PIN A6
#define YL_1_PIN A5
#define YL_2_PIN A4 
#define DHT_PIN 7
#define WATER_LEVEL_PIN 8

// actuator pin numbers
#define WATER_SHORTAGE_LED_PIN 5
#define TOO_MUCH_SMOKE_LED_PIN 4
#define FAN_RELAY_PIN 3
#define PUMP_RELAY_PIN 2

// constant initial XBee message bytes:
#define FD 0xfd
#define NUMS_COUNT 0x06
#define RASP_PI_ADDR_1 0x00
#define RASP_PI_ADDR_2 0x01

SoftwareSerial XBeeSer (11, 12); // (RX, TX)
DHT dht_sensor (DHT_PIN, DHTTYPE);

struct GreenhouseData {
  char YL_1_value;
  char YL_2_value;
  char temp_value;
  char humidity_value;
  char MQ_9_value;
  char water_level_value;
};

GreenhouseData data;
int data_count = 6;
char message [10];
bool prev_commands [4];

// *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
// *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
// *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

void setup() {
  Serial.begin(9600);
  XBeeSer.begin(9600);
  
  pinMode(YL_1_PIN, INPUT);
  pinMode(YL_2_PIN, INPUT);
  pinMode(MQ_9_PIN, INPUT);
  pinMode(DHT_PIN, INPUT);
  pinMode(WATER_LEVEL_PIN, INPUT);
  pinMode(WATER_SHORTAGE_LED_PIN, OUTPUT);
  pinMode(TOO_MUCH_SMOKE_LED_PIN, OUTPUT);
  pinMode(FAN_RELAY_PIN, OUTPUT);
  pinMode(PUMP_RELAY_PIN, OUTPUT);
  
  digitalWrite(FAN_RELAY_PIN, LOW);
  digitalWrite(PUMP_RELAY_PIN, LOW);
  digitalWrite(WATER_SHORTAGE_LED_PIN, LOW);
  digitalWrite(TOO_MUCH_SMOKE_LED_PIN, LOW);

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
  print_message(message, data_count + 4);
  send_message(message, data_count + 4);

//  Receiving Raspberry Pi response and acting accordingly before sending data again
  Serial.println("PHASE II: RECEIVING AND EXECUTING COMMANDS");
  read_raspberry_commands();
  exec_raspberry_commands();
  
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
  res.temp_value = dht_sensor.readTemperature();
  res.humidity_value = dht_sensor.readHumidity();
  res.MQ_9_value = digitalRead(MQ_9_PIN);
  res.water_level_value = digitalRead(WATER_LEVEL_PIN);
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
  Serial.println("##### ==> message formed");
  return;
}

void print_message(char message[], int message_length){
  /* 
   *  prints the message to be sent for debugging purposes
   */
   
  Serial.print("Message to be sent: ");
  for (int i = 0; i < message_length; i++){
    Serial.print(int(message[i]));
    Serial.print(" ");
  }
  Serial.println();
  return;
}

void send_message(char message[], int messageLength){
  /* 
   *  receives an array of char (message) and sends them using
   *  the XBee board connected to a SoftwareSerial 
   */
   
  for (int i = 0; i < messageLength; i++){
    XBeeSer.print(message[i]);
  }
  Serial.println("##### ==> sensor data sent");
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
      for (int init_ind = 0; init_ind < 4; init_ind++){
        int dummy = int(XBeeSer.read());
        delay(3);
//        Serial.print("dummy --------> "); Serial.println(dummy);
      } 
      
      for (int command_ind = 0; command_ind < 4; command_ind++){
        int received_byte = int(XBeeSer.read());
//        Serial.print("byte --------> "); Serial.println(received_byte);
        if (received_byte == 0) {prev_commands[command_ind] = false;}
        else {prev_commands[command_ind] = true;}
      }

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
   
  if (prev_commands[0] == true) digitalWrite(PUMP_RELAY_PIN, HIGH);
  else                          digitalWrite(PUMP_RELAY_PIN, LOW);
  
  if (prev_commands[1] == true) digitalWrite(FAN_RELAY_PIN, HIGH);
  else                          digitalWrite(FAN_RELAY_PIN, LOW);
  
  if (prev_commands[2] == true) digitalWrite(TOO_MUCH_SMOKE_LED_PIN, HIGH);
  else                          digitalWrite(TOO_MUCH_SMOKE_LED_PIN, LOW);
  
  if (prev_commands[3] == true) digitalWrite(WATER_SHORTAGE_LED_PIN, HIGH);
  else                          digitalWrite(WATER_SHORTAGE_LED_PIN, LOW);

  Serial.println("$$$$$ ==> finished EXECUTING Raspberry commands");
}

void print_commands() {
  /* 
   *  prints the current status of received Rapsberry Pi commands 
   */
   
  Serial.print ("[");
  for (int i = 0; i < 4; i++) {
    if (prev_commands[i] == true) Serial.print("1");
    else Serial.print("0");
  }
  Serial.println("]");
}







