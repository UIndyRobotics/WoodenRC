/*
    udp-wifi-streamer.ino
    Paul Talaga
    March 18, 2018
    
    Demo of sending data via a UDP packet.
    The data consists of network configuration values, plus an increasing counter.
    
    See the first lines below for the destination IP and port to send the packet
    to.
*/


// Send UDP packets to this IP & Port
IPAddress remoteIP(192, 168, 1, 166);
int port = 8888;


// What we'll send
struct network_info_t{
  byte device_mac[6];
  char local_ip[16];
  char gateway_ip[16];
  char subnet_mask[16];
  int sig_strength;
  byte access_point_BSSID[6];
  char ssid[20];
  
  int counter;
};

UDP Udp;
int counter;

network_info_t network; 

void setup() {
    WiFi.on();
    Udp.begin(port);
    Serial.begin(9600);
    
    pinMode(D7, OUTPUT);
    
    counter = 0;
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
    
    if ( Udp.sendPacket((byte*)&network, sizeof(network), remoteIP, port) < 0) {
        Serial.println("Error");
    }
    
    // Flash the blue led to signify activity
    if(counter % 30 == 0){
        digitalWrite( D7, HIGH);
    }else{
        digitalWrite( D7, LOW);
    }
    
    // TODO: remove this delay and put into a much larger loop with timings
    delay(50);
    
    
    
}