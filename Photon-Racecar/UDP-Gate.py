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

port = 49154

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

host = ""
ir_last = 0
lapTime = 2
lapCount = 0
lapTimes = []
buf = 1024
addr = (host, port)
UDPSock = socket(AF_INET, SOCK_DGRAM)
UDPSock.bind(addr)
print("Waiting to receive message...")
ir_changes = 0
start_time = 0
numLaps = 4
while True:
  try:
    #(data, addr) = UDPSock.recvfrom(buf)
    #print(len(data), calcsize(struct_format))
    #(counter, throttle, throttle_out, steer, ir_changes, sig_strength, ax, ay, az, battery_voltage_in, battery_current_in,device_mac, local_ip, gateway_ip, subnet_mask, bssid, ssid) = unpack(struct_format, data)
    #print("IR_changes: ", ir_changes)
    if((ir_changes > 0.0) & (seconds == 0.0)):
      ir_last = ir_changes
      print("Starting")
      now = datetime.datetime.now()
      seconds = now.hour * 3600 + (now.minute * 60) + now.second + now.microsecond/1000000
      start_time = seconds
      lapCount = 1
      lapTimes.append(seconds)
    if(seconds > 0.0):
      now = datetime.datetime.now()
      seconds = now.hour * 3600 + (now.minute * 60) + now.second + now.microsecond/1000000
    if((ir_changes > ir_last) & (seconds > (start_time+lapTime))):
      print("Incrementing")
      lapCount = lapCount + 1
      lapTimes.append(seconds)
      ir_last = ir_changes
    if(lapCount == (numLaps)):
      print(lapTimes)
      break
  except KeyboardInterrupt:
    ir_changes = ir_changes + 1
    

    

    

'''

'''
