#include <Wire.h>
#include <FaBo9Axis_MPU9250.h>

FaBo9Axis fabo_9axis;

void setup() {
  Serial.begin(9600);
  Serial.println("RESET");
  Serial.println();

  Serial.println("configuring device.");

  if (fabo_9axis.begin()) {
    Serial.println("configured FaBo 9Axis I2C Brick");
  } else {
    Serial.println("device error");
    while(1);
  }

  
}

void loop() {
  float ax,ay,az;
  float gx,gy,gz;
  float mx,my,mz;
  float temp;

  fabo_9axis.readAccelXYZ(&ax,&ay,&az);
  fabo_9axis.readGyroXYZ(&gx,&gy,&gz);
  fabo_9axis.readMagnetXYZ(&mx,&my,&mz);
  fabo_9axis.readTemperature(&temp);

  

  Serial.print("\tacceleration x: ");
  Serial.print(ax);
  Serial.print("\t acceleration y: \t");
  Serial.print(ay);
  Serial.print("\t acceleration z: ");
  Serial.println(az);
  
  Serial.println("");
  Serial.print("\tgyro x: ");
  Serial.print(gx);
  Serial.print("\t gyro y: ");
  Serial.print(gy);
  Serial.print("\t gyro z: ");
  Serial.println(gz);

  Serial.println("");
  Serial.print("\tmagnetism x: ");
  Serial.print(mx);
  Serial.print("\t magnetism y: ");
  Serial.print(my);
  Serial.print("\t magnetism z: ");
  Serial.println(mz);

  Serial.println("");
  Serial.print("\ttemprature: ");
  Serial.println(temp);
  Serial.println("");

  delay(0.1);
}

