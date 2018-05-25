
#define Duty_Cycle 40  //in percent (10->50), usually 33 or 50
//actual duty cycle will be relative close to set value, depending on carrier freq

#define Carrier_Frequency 38000   //usually one of 38000, 40000, 36000, 56000, 33000, 30000
// PERIOD is 26.3usec for 38khz

#define PERIOD    (1000000+Carrier_Frequency/2)/Carrier_Frequency

#define HIGHTIME  PERIOD*Duty_Cycle/100
#define LOWTIME   PERIOD - HIGHTIME
#define txPinIR   D6   //IR carrier output pin

#define LED D7

unsigned long sigLastStop = 0; //use in mark & space functions to keep track of time


void setup() {
   //WiFi.on();
  //  Serial.begin(57600);
  pinMode(txPinIR, OUTPUT);
  pinMode(LED, OUTPUT);

  pinMode(10, OUTPUT);
  digitalWrite(10, LOW);
  
  //make sure there is enough time to reflash.
  delay(1000);
  
  sigLastStop = micros();

}

void loop() {
  for (int i=0;i<7500;i++){ // should finish every second
    mark(1000);
    space(500);
  }
}


void mark(unsigned long mLen) {
  sigLastStop += mLen; //allows for rolling time adjustment due to code execution delays
  while (micros()  < sigLastStop) { //just wait here until time is up
    digitalWrite(txPinIR, HIGH); // 30u-sec
    delayMicroseconds(HIGHTIME - 3);
    digitalWrite(txPinIR, LOW);  // 40u-sec
    delayMicroseconds(LOWTIME - 4);
    digitalWrite(txPinIR, HIGH); // 30u-sec
    delayMicroseconds(HIGHTIME - 3);
    digitalWrite(txPinIR, LOW);  // 40u-sec
    delayMicroseconds(LOWTIME - 4);
    digitalWrite(txPinIR, HIGH); // 30u-sec
    delayMicroseconds(HIGHTIME - 3);
    digitalWrite(txPinIR, LOW);  // 40u-sec
    delayMicroseconds(LOWTIME - 5);
  }
}

void space(unsigned long mLen) { //uses sigTime as end parameter
  sigLastStop += mLen; //allows for rolling time adjustment due to code execution delays
  while (micros()  < sigLastStop);// { //just wait here until time is up
}