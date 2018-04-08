'''
  TCP-Network-Photon.py
  Paul Talaga
  April 6, 2018
  Connects via TCP to a a UDP repeater (UDP-Repeater) running in the cloud, which
  streams information sent to it via UDP.

  Unpackes a struct created on a
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

struct_format = 'IiiiIifffff6s16s16s16s6s20s4s'
throttle = -1
steer = -1

import os
from socket import *
from struct import *

def getMAS(mac):
  return "%x:%x:%x:%x:%x:%x" % unpack("BBBBBB",mac)


buf = 1024
addr = (host, port)
TCPSock = socket(AF_INET, SOCK_STREAM)
TCPSock.connect(addr)
print("Waiting to receive message...")
data = ""
start_counter = -1
packets_so_far = 0

while True:
    data = data + TCPSock.recv(buf)
    # TODO: Look for DEADBEEF at the end of the packet
    if len(data) < calcsize(struct_format):
      continue
    if len(data) > calcsize(struct_format):
      data = data[-calcsize(struct_format):]
    #print(len(data), calcsize(struct_format))
    #(device_mac, local_ip, gateway_ip, subnet_mask, sig_strength, bssid, ssid, counter, throttle, steer) = unpack("6s16s16s16si6s20siii", data)
    (counter, throttle, throttle_out, steer, ir_changes, sig_strength, ax, ay, az, battery_voltage_in, battery_current_in,device_mac, local_ip, gateway_ip, subnet_mask, bssid, ssid, terminator) = unpack(struct_format, data)

    # Attemp to print how many lost packets we've seen
    if start_counter == -1:
      start_counter = counter
    packets_so_far += 1
    

    print("\n   Missed Packets: %d" % (packets_so_far - (counter - start_counter)))
    print("local: %s\ngateway: %s\nmask: %s\nstrength: %i\nssid: %s\ncounter: %i\nmac: %s\nbssid: %s\nthrottle: %s\nthrottle_out: %s\nsteer: %s" % (local_ip, gateway_ip, subnet_mask, sig_strength, ssid, counter, getMAS(device_mac), getMAS(bssid), throttle, throttle_out, steer))
    print("ax: ", ax)
    print("ay: ", ay)
    print("az: ", az)
    print("Battery Voltage: ", battery_voltage_in)
    print("Battery Current: ", battery_current_in)
    print("IR_changes: ", ir_changes)
    #print unpacked
    #print("Received message (" + str(len(data)) + "): " + data)


'''

'''
