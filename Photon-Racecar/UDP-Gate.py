'''
  UDP-Network-Photon.py
  Clayton Winders
  March 29, 2018
  Prints UDP packets send to this machine and port.  Unpackes a struct created on a
  Particle Photon with the following:

  struct network_info_t{
    int counter; // increasing value to verify new packets

    int throttle_pos; // signal from controller
    int throttle_out; // modified signal to car
    int steer_pos;  // signal from controller and to car

    unsigned ir_changes;

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
    char terminator[4];
};

  See udp-wifi-streamer.ino for the Photon code.
'''
host = "18.217.55.123"  # IP address of Talaga's EC2 repeater
port = 49154
addr = (host, port)
struct_format = 'IiiiIifffff6s16s16s16s6s20s4s'
throttle = -1
steer = -1

import os
from socket import *
from struct import *
import datetime, time

seconds = 0
def getMAS(mac):
  return "%x:%x:%x:%x:%x:%x" % unpack("BBBBBB",mac)

ir_last = 0
lapTime = 2.0*1000
lapCount = 0
lapTimes = []
buf = 1024
TCPSock = socket(AF_INET, SOCK_STREAM)
TCPSock.connect(addr)
print("Waiting to receive message...")
ir_changes = 0
start_time = 0
numLaps = 4
data = ""
total = 0
currentMilliTime = lambda: int(round(time.time() * 1000))
while True:
    data = data + TCPSock.recv(buf)
    if len(data) < calcsize(struct_format):
      continue
    if len(data) > calcsize(struct_format):
      data = data[-calcsize(struct_format):]
    #print(len(data), calcsize(struct_format))
    (counter, throttle, throttle_out, steer, ir_changes, sig_strength, ax, ay, az, battery_voltage_in, battery_current_in,device_mac, local_ip, gateway_ip, subnet_mask, bssid, ssid, terminator) = unpack(struct_format, data)
    #print("IR_changes: ", ir_changes)
    
    if((ir_changes > 0.0) and (lapCount == 0)):
      ir_last = ir_changes
      start_time = currentMilliTime()
      print("Starting", currentMilliTime(), ir_changes)
      lapCount = 1
      lapTimes.append(currentMilliTime())
    if((ir_changes > ir_last) and (currentMilliTime() > (lapTimes[-1]+lapTime))):
      lapCount = lapCount + 1
      lapTimes.append(currentMilliTime())
      ir_last = ir_changes
      print("Incrementing", currentMilliTime(), ir_changes )
    if(lapCount == (numLaps)):
      laps = 0
      for lap in lapTimes:
        if laps == 0:
          print(0)
          old = lap
          laps = laps + 1
        else:
          this = (lap-old)/1000.0
          print(this)
          old = lap
          total = total + this
      print(total)
      break

    

    

    

'''

'''
