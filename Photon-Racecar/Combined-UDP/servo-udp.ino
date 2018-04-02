#include <MPU9250.h>
#include <quaternionFilters.h>

/*
    servo-udp.ino
    Clayton Winders
    March 29, 2018

    This program packs data from the various sensors on the
    car into a UDP packet and sends it to the remoteIP where
    we listen for the packet using a python program to unpack
    it and print the data.
    
    Sensors:
        Gyro - Can get acceleration, gravity and magnetism in the
            x, y, and z axis. 
        Battery Monitoring - Get voltage and current the battery
            is producing with an inline sensor.
        Motor - Get the steering and motor control as a pass through
            system.
*/

#define VCONVERT 4.37
#define ACONVERT 62.5
// Send UDP packets to this IP & Port
//IPAddress remoteIP(192, 168, 1, 166);
//IPAddress remoteIP(34,198,243,87);
IPAddress remoteIP(18,217,55,123); // Talaga EC2
int port = 49154;
// Define our Gyro sensors unit
/*
Particle ---- Gyro
 D0            SDA
 D1            SCL
 3.3v/VIN      VCC
 GND           GND
*/
MPU9250 myIMU;
// Pin assignments
int steer_in = D5;
int throttle_in = D6;
int steer_out = D3;
int throttle_out = D4;

int battery_voltage_in = A0;
int battery_current_in = A1;

// Performs a linear shift of throttle response.  90 is middle (no power),
// so setting this to 80 means it will range from 80 to 100 for the full
// controller movement.
// TODO Research motor controller modes and apply expo
int throttle_min = 80;

/************************************************/

// What we'll send over udp
struct network_info_t{
  int counter; // increasing value to verify new packets

  int throttle_pos; // signal from controller
  int throttle_out; // modified signal to car
  int steer_pos;  // signal from controller and to car

  int sig_strength;
  // Data from sensors
  float ax;
  float ay;
  float az;
  float battery_voltage_in;
  float battery_current_in;
  // Wifi parameters
  byte device_mac[6];
  char local_ip[16];
  char gateway_ip[16];
  char subnet_mask[16];
  byte access_point_BSSID[6];
  char ssid[20];

};

Servo myservos[2] = {};
UDP Udp;
int counter;
network_info_t network;


int ch_throttle(String val);

void setup() {
    WiFi.on();
    Udp.begin(port);
    //Serial.begin(9600);

    pinMode(D7, OUTPUT); // To blink blue light during transmit

    pinMode(steer_in, INPUT);
    pinMode(throttle_in, INPUT);

    counter = 0;

    myservos[0].attach(steer_out);
    myservos[1].attach(throttle_out);
    
    Particle.variable("throttle_min", throttle_min);
    Particle.function("ch_throttle", ch_throttle);

}

void loop(){
    myIMU.readAccelData(myIMU.accelCount);
    myIMU.getAres();
    counter++;
    myIMU.ax = (float)myIMU.accelCount[0] * myIMU.aRes; // - myIMU.accelBias[0];
    myIMU.ay = (float)myIMU.accelCount[1] * myIMU.aRes; // - myIMU.accelBias[1];
    myIMU.az = (float)myIMU.accelCount[2] * myIMU.aRes; // - myIMU.accelBias[2];
    network.ax = myIMU.ax;
    network.ay = myIMU.ay;
    network.az = myIMU.az;
    // pull in all network info into struct
    WiFi.macAddress(network.device_mac);
    strcpy(network.local_ip, WiFi.localIP().toString() );
    strcpy(network.gateway_ip, WiFi.gatewayIP().toString() );
    strcpy(network.subnet_mask, WiFi.subnetMask().toString() );
    network.sig_strength = WiFi.RSSI();
    WiFi.BSSID(network.access_point_BSSID);
    strcpy(network.ssid, WiFi.SSID());
    network.counter = counter;

    // Battery info
    network.battery_voltage_in = analogRead(battery_voltage_in) * (float)3.3 * VCONVERT / 4095;
    network.battery_current_in = analogRead(battery_current_in) / (float)ACONVERT;
    
    // Read and write servos
    // TODO Investigate if pulseIn is the best here
    // Maps pwm pulse width to degrees, which the Servo library likes.
    // TODO: figure out how not to block when it isn't getting a PWM signal
//network.throttle_pos = map(pulseIn(throttle_in, HIGH), 1105, 1897, 0, 180);
//network.steer_pos = map(pulseIn(steer_in, HIGH), 1105, 1897, 0, 180);

    myservos[0].write(network.steer_pos);
    // Apply a throttle linear shift around middle (90)
    network.throttle_out = map(network.throttle_pos, 0, 180, throttle_min, 180-throttle_min);
    myservos[1].write(network.throttle_out);
    myIMU.updateTime();
    MahonyQuaternionUpdate(myIMU.ax, myIMU.ay, myIMU.az, myIMU.gx * DEG_TO_RAD,
                         myIMU.gy * DEG_TO_RAD, myIMU.gz * DEG_TO_RAD, myIMU.my,
                         myIMU.mx, myIMU.mz, myIMU.deltat);
    // TODO Verify car is still drivable when Wifi is lost
    if(WiFi.ready()){
      Udp.sendPacket((byte*)&network, sizeof(network), remoteIP, port);
    }

    // Flash the blue led to signify activity
    if(counter % 30 == 0){
        digitalWrite( D7, HIGH);
    }else{
        digitalWrite( D7, LOW);
    }

    // TODO: remove this delay and put into a much larger loop with timings
    delay(10);
}

int ch_throttle(String val){
    int value = val.toInt();
    if(value <= 90 && value >= 0){
        throttle_min = value;
        // Format example
        // Particle.publish(const char *eventName, const char *data);
        // Particle.publish(String eventName, String data);
        Particle.publish("Throttle min changed: ", val);
        // Let it know that we were successful
        return 1;
    } else {
        // Let the console know it was unsuccessful
        return -1;
    }
}