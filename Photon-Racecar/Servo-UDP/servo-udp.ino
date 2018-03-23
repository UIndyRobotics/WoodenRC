/*
    servo-udp.ino
    Paul Talaga
    March 19, 2018

    Passes servo signals through to racecar, and sends data over UDP to the
    specified address/port.

    See the first lines below for the destination IP and port to send the packet
    to.
*/


// Send UDP packets to this IP & Port
//IPAddress remoteIP(192, 168, 1, 166);
IPAddress remoteIP(10,18,100,23);
int port = 8888;

// Pin assignments
int steer_in = D2;
int throttle_in = D3;
int steer_out = D0;
int throttle_out = D1;

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

  // Wifi parameters
  int sig_strength;
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

}

void loop(){

    counter++;

    // pull in all network info into struct
    WiFi.macAddress(network.device_mac);
    strcpy(network.local_ip, WiFi.localIP().toString() );
    strcpy(network.gateway_ip, WiFi.gatewayIP().toString() );
    strcpy(network.subnet_mask, WiFi.subnetMask().toString() );
    network.sig_strength = WiFi.RSSI();
    WiFi.BSSID(network.access_point_BSSID);
    strcpy(network.ssid, WiFi.SSID());
    network.counter = counter;

    // Read and write servos
    // TODO Investigate if pulseIn is the best here
    // Maps pwm pulse width to degrees, which the Servo library likes.
    network.throttle_pos = map(pulseIn(throttle_in, HIGH), 1105, 1897, 0, 180);
    network.steer_pos = map(pulseIn(steer_in, HIGH), 1105, 1897, 0, 180);

    myservos[0].write(network.steer_pos);
    // Apply a throttle linear shift around middle (90)
    network.throttle_out = map(network.throttle_pos, 0, 180, throttle_min, 180-throttle_min);
    myservos[1].write(network.throttle_out);

    // TODO Verify car is still drivable when Wifi is lost
    if( Wifi.ready()){
      Udp.sendPacket((byte*)&network, sizeof(network), remoteIP, port);
    }

    // Flash the blue led to signify activity
    if(counter % 30 == 0){
        digitalWrite( D7, HIGH);
    }else{
        digitalWrite( D7, LOW);
    }

    // TODO: remove this delay and put into a much larger loop with timings
    delay(20);



}
