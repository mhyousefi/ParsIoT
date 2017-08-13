/* 
// Top level code to run on Arduino
// It handles sending sensor info to Raspberry Pi and executes commands received from Raspberry Pi
*/

#include <DHT.h>
#include <DHT_U.h>
#include <SoftwareSerial.h>

#define DHTTYPE DHT11
// pin numbers
#define MQ_9_PIN A0
#define YL_1_PIN A1
#define YL_2_PIN A2 
#define DHT_PIN 3
#define WATER_LEVEL_PIN 4
#define FAN_RELAY_PIN 6
#define PUMP_RELAY_PIN 7
// Constant initial XBee message bytes:
#define FD 0xfd
#define NUMS_COUNT 0x06
#define RASP_PI_ADDR_1 0x14
#define RASP_PI_ADDR_2 0x3e

SoftwareSerial XBeeSer (8, 9); // (RX, TX)
DHT dht_sensor (DHT_PIN, DHTTYPE);

struct GreenhouseData {
  char YL_1_value;
  char YL_2_value;
  char temp_value;
  char humidity_value;
  char MQ_9_value;
  char water_level_value;
};

struct RaspCommands {
  bool fan;
  bool pump;
};

GreenhouseData data;
int data_count = 6;
char message [10];

void setup() {
  Serial.begin(9600);
  XBeeSer.begin(9600);
  
  pinMode(YL_1_PIN, INPUT);
  pinMode(YL_2_PIN, INPUT);
  pinMode(MQ_9_PIN, INPUT);
  pinMode(DHT_PIN, INPUT);
  pinMode(WATER_LEVEL_PIN, INPUT);
  pinMode(FAN_RELAY_PIN, OUTPUT);
  pinMode(PUMP_RELAY_PIN, OUTPUT);
}

void loop() {
  delay(500);
  
  // Sending greenhouse info to Raspberry Pi
  data = read_sensor_data();
  form_message(message, data);
  print_message(message, data_count + 4);
  send_message(message, data_count + 4);

  // Receiving Raspberry Pi response and acting accordingly before sending data again  
  RaspCommands commands = read_raspberry_commands();
  exec_raspberry_commands(commands);
}

/* 
 * Helper functions for sending info to Raspberry Pi 
 */

void send_message(char message[], int messageLength){
  for (int i = 0; i < messageLength; i++){
    XBeeSer.print(message[i]);
  }
}

GreenhouseData read_sensor_data(){
  GreenhouseData res;
  res.YL_1_value = analogRead(YL_1_PIN) / 4;
  res.YL_2_value = analogRead(YL_2_PIN) / 4;
  res.temp_value = dht_sensor.readTemperature();
  res.humidity_value = dht_sensor.readHumidity();
  res.MQ_9_value = digitalRead(MQ_9_PIN);
  res.water_level_value = 0xa;
  return res;
}
 
void form_message(char message[], GreenhouseData data){
  // constant bytes
  message[0] = FD;
  message[1] = NUMS_COUNT;
  message[2] = RASP_PI_ADDR_1;
  message[3] = RASP_PI_ADDR_2;

  // dynamic bytes
  message[4] = data.temp_value;
  message[5] = data.humidity_value;
  message[6] = data.MQ_9_value;
  message[7] = data.water_level_value;
  message[8] = data.YL_1_value;
  message[9] = data.YL_2_value;
}

void print_message(char message[], int message_length){
  Serial.println("Printing greenhouse data:");
  for (int i = 0; i < message_length; i++){
    Serial.print(int(message[i]));
    Serial.print(" ");
  }
  Serial.println();
  Serial.println("**********************");
}

/* 
 * Helper functions for receiving info from Raspberry Pi and executing commands
 */

void exec_raspberry_commands(RaspCommands commands) {
  if (commands.fan == true){
    digitalWrite(FAN_RELAY_PIN, HIGH);
  }
  else {
    digitalWrite(FAN_RELAY_PIN, LOW);
  }

  if (commands.pump == true){
    digitalWrite(PUMP_RELAY_PIN, HIGH);
  }
  else {
    digitalWrite(PUMP_RELAY_PIN, LOW);
  }
}

RaspCommands read_raspberry_commands() {
  while(true){
    if (XBeeSer.available() <= 0){
      continue;
    }
    for (int i = 0; i < 4; i++){
      int dummy = int(XBeeSer.read());
    }
    RaspCommands commands;
    commands.fan = (int(XBeeSer.read()) == 0) ? false : true;
    commands.pump = (int(XBeeSer.read()) == 0) ? false : true;
    return commands;
  }
}

