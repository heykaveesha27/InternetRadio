#include <LiquidCrystal_I2C.h>

#include <WiFi.h>
#include "Audio.h"
#include "esp_bt.h"

// ----Wi-Fi Credentials ----
const char* ssid = "your ssid";
const char* password = "wifi password";

//---PCM5102 i2s pins
#define I2S_DOUT 26 // DIN on PCM5102
#define I2S_BCLK 27 // BCK on PCM5102
#define I2S_LRC  25 //LCRK on PCM 5102

#define CLK_PIN 32 //left pin of potentiometer
#define DT_PIN 33 //right pin of potentiometer

volatile int currentChannel = 1;
int lastChannel = 1;
volatile unsigned long lastInterrupt = 0;

void IRAM_ATTR readEncoder(){
  unsigned long interruptTime = millis();
  //50ms software debounce to prevent accidental double-skips
  if (interruptTime-lastInterrupt>50){
    if(digitalRead(DT_PIN)==HIGH) currentChannel++;
    else currentChannel--;

    //Loop channels between 1 and 5
    if (currentChannel > 5) currentChannel = 1;
    if (currentChannel < 1) currentChannel = 5;

    lastInterrupt = interruptTime;
  }
}

const int POT_PIN = 35;
int currentVolume = -1;


LiquidCrystal_I2C lcd(0x27, 16, 2);

Audio audio;

void setup(){

  esp_bt_controller_disable();
  delay(100);

  Serial.begin(115200);

  lcd.init();
  lcd.backlight();
  lcd.setCursor(0,0);
  lcd.print("WiFi Radio");
  lcd.setCursor(0,1);
  lcd.print("Connecting...");

  pinMode(CLK_PIN, INPUT_PULLUP);
  pinMode(DT_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(CLK_PIN),readEncoder,FALLING);


  //connect to wifi
  Serial.println("Connecting to Wifi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED){
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.println("WiFi connected");

  audio.setPinout(I2S_BCLK, I2S_LRC, I2S_DOUT);
  audio.setVolume(21); //0 to 21
  audio.forceMono(true);
  audio.setConnectionTimeout(2000, 7200);


  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("Connecting...");


  String proxy = "http://10.248.120.239:8000/"+String(currentChannel);


  audio.connecttohost(proxy.c_str());
  

 
}

void loop(){
  audio.loop();

  if(currentChannel != lastChannel){
    lastChannel = currentChannel;

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Tuning Channel:");
    lcd.print(currentChannel);

    String url = "http://10.248.120.239:8000/" + String(currentChannel);
    audio.connecttohost(url.c_str());
  }

  //Read the volume knob every 100ms
  static unsigned long lastPotRead = 0;
  if (millis()-lastPotRead > 100){
    lastPotRead = millis();

    //Read the analog pin (0 to 4095)
    int potValue = analogRead(POT_PIN);

    //convert to library volume scale(0 to 21)
    int mappedVolume = map(potValue,0,4095,21,0);

    //Only update the audio library if the knob actually moved
    if (mappedVolume != currentVolume){
      currentVolume = mappedVolume;
      audio.setVolume(currentVolume);
      Serial.print("Volume set to:");
      Serial.println(currentVolume);
      lcd.setCursor(0, 1);
      lcd.print("Volume: ");
      lcd.print(currentVolume);
    }
  }

  static unsigned long lastPrint=0;
  if (millis()-lastPrint > 1000){
    lastPrint=millis();

    uint32_t filledBytes = audio.inBufferFilled();
    uint32_t freeBytes = audio.inBufferFree();
    
    Serial.print("Buffer Filled: ");
    Serial.print(filledBytes);
    Serial.print(" bytes | Free: ");
    Serial.print(freeBytes);
    Serial.println(" bytes");
      }
}

// optional callbacks for the serial monitor

//Fires when the station broadcast its name
void audio_showstation(const char *info){
  Serial.print("Station: ");
  Serial.println(info);

  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("Name: ");
  String station = String(info);
  lcd.print(station.substring(0,10));
  
  
}

//Fires when the station broadcasts the curent song title

//Fires for general library debugging info
void audio_info(const char *info){
  Serial.print("Info: ");
  Serial.println(info);
}

