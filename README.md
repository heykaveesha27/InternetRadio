<<<<<<< HEAD
# **ESP32 Proxy-Powered Internet Radio 📻**

A high-fidelity, stutter-free Wi-Fi internet radio built with a standard ESP32, a PCM5102 I2S DAC, and a local Python TCP proxy server.  
This project provides a reliable blueprint for streaming heavy HTTPS/SSL audio and dynamic metadata (ICY headers) on a standard ESP32 without relying on external PSRAM.

## **The Architecture: Bypassing the ESP32 Memory Bottleneck**

Standard ESP32 modules (without PSRAM) typically struggle to play high-bitrate secure web streams (https\://). The microcontroller's limited internal memory cannot handle heavy cryptographic SSL decryption while simultaneously buffering live audio, resulting in constant stuttering, buffer underruns, or fatal crashes.  
**The Solution:** This project utilizes a **Raw TCP Proxy Server** running locally on a host PC or Raspberry Pi.

* **The Proxy** acts as an invisible, high-performance middleman. It executes the SSL handshake, manages the stream connection, and extracts the ICY metadata. It then forwards the raw, unencrypted bytes directly to the ESP32 over the local network.  
* **The ESP32** acts strictly as the edge decoding and interface device. With the network decryption offloaded, its CPU is freed up to maintain a full audio buffer, drive the LCD interface, and respond instantly to hardware interrupts.

## **Hardware Requirements**

* **Standard ESP32 Development Board** (NodeMCU, WROOM-32, etc.)  
* **PCM5102 I2S DAC Module** (For hardware-decoded, line-level audio output)  
* **16x2 I2C LCD Display**  
* **Rotary Encoder** (Bare module for channel switching)  
* **10K Potentiometer** (For analog volume control)  
* Amplifier / Powered Speakers

## **Wiring Schematic**

| Component | Pin Function | ESP32 Connection | Notes |
| :---- | :---- | :---- | :---- |
| **PCM5102 DAC** | DIN | GPIO 26 | Data In |
|  | BCK | GPIO 27 | Bit Clock |
|  | LCK | GPIO 25 | Left/Right Clock |
|  | VIN / GND | 5V / GND |  |
| **16x2 LCD (I2C)** | SDA | GPIO 21 |  |
|  | SCL | GPIO 22 |  |
|  | VCC / GND | 5V / GND | Text requires 5V for contrast |
| **Rotary Encoder** | CLK | GPIO 32 | Configured with internal pull-up |
|  | DT | GPIO 33 | Configured with internal pull-up |
|  | GND | GND |  |
| **10K Potentiometer** | Middle (Wiper) | GPIO 35 | Analog input |
|  | Right | 3.3V | **CRITICAL:** Do not use 5V |
|  | Left | GND |  |

## **Software Setup & Installation**

### **1\. The Python Proxy Server**

You need a machine (PC, Mac, or Raspberry Pi) on the same local network as your ESP32 to run the middleman proxy.

1. Ensure Python 3.x is installed on your host machine.  
2. Clone this repository and navigate to the proxy directory.  
3. Edit proxy.py to add your preferred radio stations to the STATIONS dictionary.  
4. Run the proxy:  
   python proxy.py  
5. Note the local IPv4 address of this machine (e.g., 192.168.1.50 or 10.x.x.x).

### **2\. Flashing the ESP32**

1. Open the .ino file in the Arduino IDE.  
2. Install the required libraries via the Library Manager:  
   * **ESP32-audioI2S** by Schreibfaul1  
   * **LiquidCrystal I2C** by Frank de Brabander  
3. Update the Wi-Fi credentials:  
   C++  
   const char\* ssid \= "YOUR\_SSID";  
   const char\* password \= "YOUR\_PASSWORD";

4. Update the proxy IP address in the setup() and loop() functions to match your host machine running the Python script:  
   C++  
   String proxy \= "http\://YOUR\_PROXY\_IP:8000/" \+ String(currentChannel);

5. Upload the sketch to your ESP32.

## **Usage**

* **Boot:** Upon powering up, the ESP32 will connect to Wi-Fi, default to Channel 1, and request the stream from the local Python proxy.  
* **Channel Surfing:** Rotate the rotary encoder to change channels. A hardware interrupt instantly catches the rotation, debounces the signal, updates the LCD, and commands the proxy to switch the upstream source.  
* **Volume Control:** Turn the 10K potentiometer to adjust the software volume (0-21 scale). The ESP32 polls this analog pin and remaps it dynamically without interrupting the audio buffer.
=======
If you’ve ever tried building a standalone Wi-Fi radio using a standard ESP32 (without external PSRAM), you’ve likely hit the memory bottleneck: asking the microcontroller to handle heavy HTTPS/SSL decryption while simultaneously buffering high-bitrate audio usually results in constant stuttering or fatal crashes.
>>>>>>> b35cd2a28ab5a16923e970f0ea8fc3bd1f5ebab4
