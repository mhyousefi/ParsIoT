/* 
// implementing send and receive capabilities for ZigBee module 
// DRF1605H using SoftwareSerial
// See helper functions
*/

#include <SoftwareSerial.h>

SoftwareSerial XBeeSer(8,9); // RX, TX

int DELAY_TIME = 2000;
int YL_69_PIN = A0;
char YL_69_Value = 0x00;
char data[10];
int dataCount;
char message[20];

//char bytE;

void setup() {
  pinMode(YL_69_PIN, INPUT);
  Serial.begin(9600);
  XBeeSer.begin(9600);
//  Serial.println("Testing");
//  char s = "fd";
//  Serial.println(int(s));
}

void loop() {
  delay(DELAY_TIME);
//  If we are to read sent data:
//  if (XBeeSer.available() > 0){
//    Serial.println(int(XBeeSer.read()));
//  }
//  else {
//    Serial.println("NOTHING!!");
//  }  

  // If we are to send some data
  data[0] = 0xab;
  data[1] = 0xcd;
  dataCount = 2;
  form_message(message, 0xfd, 0x02, 0x14, 0x3e, data);
  print_message(message, 4 + dataCount);
  send_message(message, 4 + dataCount);

}

/* 
 * Helper functions 
 */
 
void form_message(char message[], char firstChar, char byteCount, char addr1, char addr2, char data[]){
  message[0] = firstChar;
  message[1] = byteCount;
  message[2] = addr1;
  message[3] = addr2;
  int dataLength = int(byteCount);
  Serial.print("Number of data bytes = ");
  Serial.println(dataLength);
  for (int i = 0; i < dataLength; i++){
    message[4 + i] = data[i];
  }
}

void print_message(char message[], int messageLength){
  for (int i = 0; i < messageLength; i++){
    Serial.print(int(message[i]));
    Serial.print(" ");
  }
  Serial.println();
}

void send_message(char message[], int messageLength){
  for (int i = 0; i < messageLength; i++){
    XBeeSer.print(message[i]);
  }
}



