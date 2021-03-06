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
            
    particle compile photon
    particle flash CarXXX
*/

#define VCONVERT  341 //488
#define ACONVERTM 0.0074
#define ACONVERTB -5.00
#define SMOOTH_LEN 5
#define PACKET_PERIOD_MS 100  // 10hz
#define NETWORK_UPDATE_PERIOD_MS 1000 // 1hz

#define YACCEL_GRANNY_MODE 100  // 100 to disable, 0.55 regular
#define GRANNY_TIMEOUT 5000

// Send UDP packets to this IP & Port
//IPAddress remoteIP(192, 168, 1, 166);
//IPAddress remoteIP(34,198,243,87);
//IPAddress remoteIP(18,217,55,123); // Talaga EC2
IPAddress remoteIP(192,168,79,10); // Talaga EC2
int port = 49154;
// Define our Gyro sensors unit
/*
Particle ---- Gyro
 D0            SDA
 D1            SCL
 3.3v/VIN      VCC
 GND           GND
*/

// Pin assignments
int steer_in = D5;
int throttle_in = D6;
int steer_out = A5;
int throttle_out = A4;

int battery_voltage_in = A0;
int battery_current_in = A1;

int IR_detect_in = A2;

// Performs a linear shift of throttle response.  90 is middle (no power),
// so setting this to 80 means it will range from 80 to 100 for the full
// controller movement.
// TODO Research motor controller modes and apply expo
int throttle_min = 0;//55;  // normal 83
int steering_min = 40;

unsigned frames_per_packet = 0;
unsigned millis_to_reenable = 0;
float last_ay = 0;

/************************************************/
MPU9250 myIMU;

// What we'll send over udp
struct network_info_t{
  unsigned counter; // increasing value to verify new packets
  unsigned milli_time;

  int throttle_pos; // signal from controller
  int throttle_out; // modified signal to car
  int steer_pos;  // signal from controller and to car
  int steer_out;
  
  unsigned ir_changes;

  int sig_strength;
  // Data from sensors
  float ax;
  float ay;
  float az;
  float battery_voltage_in;
  float battery_current_in;
  float battery_current_sum;

  // Wifi parameters
  byte device_mac[6];
  char local_ip[16];
  char gateway_ip[16];
  char subnet_mask[16];
  byte access_point_BSSID[6];
  char ssid[20];
  char terminator[4];
};

Servo myservos[2] = {};
UDP Udp;
unsigned counter;
unsigned packet_counter;
unsigned last_packet_sent_at;
unsigned last_network_update_at;
network_info_t network;

unsigned current_smoother[SMOOTH_LEN] = {}; // to smooth the current 
unsigned voltage_smoother[SMOOTH_LEN] = {}; // to smooth the current
float amp_sum = 0;
unsigned last_millis = 0;

// IR trigger
volatile unsigned ir_changes;

void ir_trigger(){
    ir_changes++;
}


//int ch_throttle(String val);
void updateNetworkStats(); 

int multiMap(int val, int* _in, int* _out, uint8_t size);  // fancy map for expo


STARTUP(WiFi.selectAntenna(ANT_AUTO));  // continually switches at high speed between antennas
//STARTUP(WiFi.selectAntenna(ANT_INTERNAL)); // selects the CHIP antenna
//STARTUP(WiFi.selectAntenna(ANT_EXTERNAL)); // selects the u.FL 

void setup() {
    WiFi.on();
    Udp.begin(port);
    //Serial.begin(9600);

    pinMode(D7, OUTPUT); // To blink blue light during transmit

    pinMode(steer_in, INPUT);
    pinMode(throttle_in, INPUT);

    counter = 0;
    packet_counter = 0;
    last_millis = millis();

    myservos[0].attach(steer_out);
    myservos[1].attach(throttle_out);
    
    //Particle.variable("throttle_min", throttle_min);
    //Particle.function("ch_throttle", ch_throttle);
    
    // IR pit and ISR setup
    ir_changes = 0;
    pinMode(IR_detect_in, INPUT_PULLUP);
    attachInterrupt(IR_detect_in, ir_trigger, FALLING);
    
    // Timers for periodic net update and packet sending
    last_packet_sent_at = 0;
    last_network_update_at = 0;
    
    // set the termination string at the end of the struct
    network.terminator[0] = 0xDE;
    network.terminator[1] = 0xAD;
    network.terminator[2] = 0xBE;
    network.terminator[3] = 0xEF;
}

void loop(){
    myIMU.readAccelData(myIMU.accelCount);
    myIMU.getAres();
    counter++;
    myIMU.ax = (float)myIMU.accelCount[0] * myIMU.aRes; // - myIMU.accelBias[0];
    myIMU.ay = (float)myIMU.accelCount[1] * myIMU.aRes; // - myIMU.accelBias[1];
    myIMU.az = (float)myIMU.accelCount[2] * myIMU.aRes; // - myIMU.accelBias[2];
    network.ax =+ myIMU.ax;
    network.ay =+ myIMU.ay;
    network.az =+ myIMU.az;
    frames_per_packet++;
    

    // Battery info
    // do voltage smoothing
    voltage_smoother[counter % SMOOTH_LEN] = analogRead(battery_voltage_in);
    unsigned i = 0;
    float v_temp = 0.0;
    //network.battery_voltage_in = analogRead(battery_voltage_in) * (float)3.3 * VCONVERT / 4095;
    for(i = 0; i < SMOOTH_LEN; i++){
        v_temp += voltage_smoother[i];
    }
    network.battery_voltage_in = v_temp / SMOOTH_LEN / VCONVERT;
    
    // do current smoothing
    current_smoother[counter % SMOOTH_LEN] = analogRead(battery_current_in);
    //network.battery_current_in = analogRead(battery_current_in) / (float)ACONVERT;
    float a_temp = 0.0;
    
    for(i = 0; i < SMOOTH_LEN; i++){
        a_temp += current_smoother[i];
    }
    network.battery_current_in = (a_temp / SMOOTH_LEN ) * ACONVERTM + ACONVERTB;
    // Coulum count in units of mAh
    network.battery_current_sum += network.battery_current_in * (millis() - last_millis) / 60 / 60;
    last_millis = millis();
    
    // Read and write servos
    // TODO Investigate if pulseIn is the best here
    // Maps pwm pulse width to degrees, which the Servo library likes.
    // TODO: figure out how not to block when it isn't getting a PWM signal
    network.throttle_pos = map(pulseIn(throttle_in, HIGH), 1105, 1897, 0, 180);
    network.steer_pos = map(pulseIn(steer_in, HIGH), 1105, 1897, 0, 180);
    
    // Steering map
    network.steer_pos = map(network.steer_pos, 0, 180, steering_min, 180-steering_min);
    int in[]  = {29,39,49,59,69,79,89,99,109,119,129,139,149}					;
    //int out[]  = {30,48,63,74,83,88,90,91,96,104,115,129,147}					; // expo of 2
    int out[] = {30,55,72,82,88,90,90,90,92,97,106,121,145}		;  // expo of 3
    network.steer_out = multiMap(network.steer_pos, in, out, 13);  // <------------------------------------
    //network.steer_out = network.steer_pos; // linear
    myservos[0].write(network.steer_out);   // Send it to the servo!
    
    // Apply a throttle linear shift around middle (90)
    // Note ESC zeros when it is turned on, so be sure transmitter is on first!
    network.throttle_out = map(network.throttle_pos, 0, 180, throttle_min, 180-throttle_min);
    int in_th[]  = {29,39,49,59,69,79,89,99,109,119,129,139,149};
    int out_th[]  = {30,48,63,74,83,88,90,91,96,104,115,129,147};
    network.throttle_out = multiMap(network.throttle_out, in_th, out_th, 13); // <------------------------------------
    
    network.throttle_out = network.throttle_out - 10; // Not centered?!?!
    network.throttle_out = max(network.throttle_out, 68); // Limit reverse speed
    
    if(millis_to_reenable > millis()){
        network.throttle_out = map(network.throttle_out, 0, 180, 65, 180-65);
    }
    myservos[1].write(network.throttle_out);    // Send it to the motor
    
    myIMU.updateTime();
    MahonyQuaternionUpdate(myIMU.ax, myIMU.ay, myIMU.az, myIMU.gx * DEG_TO_RAD,
                         myIMU.gy * DEG_TO_RAD, myIMU.gz * DEG_TO_RAD, myIMU.my,
                         myIMU.mx, myIMU.mz, myIMU.deltat);
                         
                         
    network.ir_changes = ir_changes;
    
    // Don't update network settings so fast
    if( millis() > last_network_update_at + NETWORK_UPDATE_PERIOD_MS){
        updateNetworkStats();
        last_network_update_at = millis();
    }
    
    // TODO Verify car is still drivable when Wifi is lost
    if(WiFi.ready() && millis() > last_packet_sent_at + PACKET_PERIOD_MS){
        network.counter = packet_counter++;
        network.milli_time = millis();
        network.ax = network.ax / frames_per_packet;
        network.ay = network.ay / frames_per_packet;
        network.az = network.az / frames_per_packet;
        Udp.sendPacket((byte*)&network, sizeof(network), remoteIP, port);
        last_packet_sent_at = millis();
        // Check bump
        if(abs(network.ay - last_ay) > YACCEL_GRANNY_MODE){
            millis_to_reenable = millis() + GRANNY_TIMEOUT; // disable for GRANNY_TIMEOUT ms
        }
        last_ay = network.ay;
        network.ax = 0;
        network.ay = 0;
        network.az = 0;
        frames_per_packet = 0;
    }

    // Flash the blue led to signify activity
    if(counter % 30 == 0){
        digitalWrite( D7, HIGH);
    }else{
        digitalWrite( D7, LOW);
    }

    // TODO: remove this delay and put into a much larger loop with timings
    delay(5);
}

/*
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
*/


void updateNetworkStats(){
    // pull in all network info into struct
    WiFi.macAddress(network.device_mac);
    strcpy(network.local_ip, WiFi.localIP().toString() );
    strcpy(network.gateway_ip, WiFi.gatewayIP().toString() );
    strcpy(network.subnet_mask, WiFi.subnetMask().toString() );
    network.sig_strength = WiFi.RSSI();
    WiFi.BSSID(network.access_point_BSSID);
    strcpy(network.ssid, WiFi.SSID());
}

// note: the _in array should have increasing values
int multiMap(int val, int* _in, int* _out, uint8_t size)
{
  // take care the value is within range
  // val = constrain(val, _in[0], _in[size-1]);
  if (val <= _in[0]) return _out[0];
  if (val >= _in[size-1]) return _out[size-1];

  // search right interval
  uint8_t pos = 1;  // _in[0] allready tested
  while(val > _in[pos]) pos++;

  // this will handle all exact "points" in the _in array
  if (val == _in[pos]) return _out[pos];

  // interpolate in the right segment for the rest
  return (val - _in[pos-1]) * (_out[pos] - _out[pos-1]) / (_in[pos] - _in[pos-1]) + _out[pos-1];
}