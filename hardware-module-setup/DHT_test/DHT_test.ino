#include <DHT.h>
#include <DHT_U.h>

#define DHTPIN 2
#define DHTTYPE DHT11

int temp;
int hum;
int temp_upper_threshold = 25;
int temp_lower_threshold = 17;
int fan_pin = 3;

DHT dht_sensor(DHTPIN,DHTTYPE);

void setup() {
  Serial.begin(9600);
  pinMode(fan_pin, OUTPUT);
  dht.begin();
}

void loop() {
  delay(500);
  temp=dht_sensor.readTemperature();
  hum=dht_sensor.readHumidity();
  Serial.println(temp);
  if (temp > temp_upper_threshold) {
    digitalWrite(fan_pin, HIGH);
  }
  if (temp == temp_lower_threshold){ 
      digitalWrite(fan_pin,LOW);
    }
  else {
     digitalWrite(fan_pin, LOW);
  }
}
