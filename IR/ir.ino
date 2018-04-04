
#define Duty_Cycle 50  //in percent (10->50), usually 33 or 50
//actual duty cycle will be relative close to set value, depending on carrier freq

#define Carrier_Frequency 38000   //usually one of 38000, 40000, 36000, 56000, 33000, 30000


#define PERIOD    (1000000+Carrier_Frequency/2)/Carrier_Frequency
#define HIGHTIME  PERIOD*Duty_Cycle/100
#define LOWTIME   PERIOD - HIGHTIME
#define txPinIR   D6   //IR carrier output pin

#define LED D7



unsigned long sigTime = 0; //use in mark & space functions to keep track of time

//RAW NEC signal -32 bit with 1 repeat - make sure buffer starts with a Mark
unsigned int NEC_RAW[] = {9000, 4500, 560, 560, 560, 560, 560, 1690, 560, 560, 560, 560, 560, 560, 560, 560, 560, 560, 560, 1690, 560, 1690, 560, 560, 560, 1690, 560, 1690, 560, 1690, 560, 1690, 560, 1690, 560, 560, 560, 560, 560, 1690, 560, 560, 560, 560, 560, 560, 560, 1690, 560, 560, 560, 1690, 560, 1690, 560, 560, 560, 1690, 560, 1690, 560, 1690, 560, 560, 560, 1690, 560, 39980, 9000, 2232, 560}; //AnalysIR Batch Export (IRremote) - RAW

//RAW Mitsubishi 88 bit signal  - make sure buffer starts with a Mark
unsigned int Mitsubishi_RAW[] = {3172, 1586, 394, 394, 394, 1182, 394, 394, 394, 394, 394, 1182, 394, 394, 394, 1182, 394, 394, 394, 394, 394, 1182, 394, 1182, 394, 1182, 394, 394, 394, 1182, 394, 394, 394, 1182, 394, 1182, 394, 1182, 394, 394, 394, 394, 394, 394, 394, 394, 394, 1182, 394, 1182, 394, 394, 394, 1182, 394, 1182, 394, 394, 394, 394, 394, 1182, 394, 394, 394, 394, 394, 1182, 394, 394, 394, 394, 394, 1182, 394, 1182, 394, 394, 394, 1182, 394, 1182, 394, 1182, 394, 1182, 394, 1182, 394, 1182, 394, 1182, 394, 1182, 394, 1182, 394, 1182, 394, 394, 394, 394, 394, 394, 394, 394, 394, 394, 394, 394, 394, 394, 394, 394, 394, 1182, 394, 1182, 394, 1182, 394, 1182, 394, 1182, 394, 1182, 394, 394, 394, 1182, 394, 394, 394, 394, 394, 394, 394, 394, 394, 394, 394, 394, 394, 1182, 394, 394, 394, 394, 394, 1182, 394, 1182, 394, 1182, 394, 1182, 394, 1182, 394, 394, 394, 1182, 394, 1182, 394, 394, 394, 394, 394, 394, 394, 394, 394, 394, 394, 1182, 394, 394, 394}; //AnalysIR Batch Export (IRremote) - RAW


void setup() {
  //  Serial.begin(57600);
  pinMode(txPinIR, OUTPUT);
  pinMode(LED, OUTPUT);

  pinMode(10, OUTPUT);
  digitalWrite(10, LOW);
  
  //make sure there is enough time to reflash.
  delay(1000);
  delay(1000);
  delay(1000);
  delay(1000);
  delay(1000);
  delay(1000);
  delay(1000);
  delay(1000);
  delay(1000);

}

void loop() {

  //First send the NEC RAW signal above
  digitalWrite(LED,HIGH);
  sigTime = micros(); //keeps rolling track of signal time to avoid impact of loop & code execution delays
  for (int i = 0; i < sizeof(NEC_RAW) / sizeof(NEC_RAW[0]); i++) {
    mark(NEC_RAW[i++]); //also move pointer to next position
    if (i < sizeof(NEC_RAW) / sizeof(NEC_RAW[0])) space(NEC_RAW[i]); //pointer will be moved by for loop
  }
  digitalWrite(LED,LOW);
  delay(5000); //wait 5 seconds between each signal (change to suit)


  //Next send the Mitsubishi AC RAW signal above
  digitalWrite(LED,HIGH);
  sigTime = micros(); //keeps rolling track of signal time to avoid impact of loop & code execution delays
  for (int i = 0; i < sizeof(Mitsubishi_RAW) / sizeof(Mitsubishi_RAW[0]); i++) {
    mark(Mitsubishi_RAW[i++]);  //also move pointer to next position
    if (i < sizeof(Mitsubishi_RAW) / sizeof(Mitsubishi_RAW[0])) space(Mitsubishi_RAW[i]); //pointer will be moved by for loop
  }
  digitalWrite(LED,LOW);
  delay(5000); //wait 5 seconds between each signal (change to suit)
  //Serial.println("******");

}

void mark(unsigned int mLen) { //uses sigTime as end parameter
  sigTime+= mLen; //mark ends at new sigTime
  unsigned long now = micros();
  unsigned long dur = sigTime - now; //allows for rolling time adjustment due to code execution delays
  if (dur == 0) return;
  while ((micros() - now) < dur) { //just wait here until time is up
    digitalWrite(txPinIR, HIGH);
    delayMicroseconds(HIGHTIME - 3);
    digitalWrite(txPinIR, LOW);
    delayMicroseconds(LOWTIME - 4);
  }
}

void space(unsigned int sLen) { //uses sigTime as end parameter
  sigTime+= sLen; //space ends at new sigTime
  unsigned long now = micros();
  unsigned long dur = sigTime - now; //allows for rolling time adjustment due to code execution delays
  if (dur == 0) return;
  while ((micros() - now) < dur) ; //just wait here until time is up
}