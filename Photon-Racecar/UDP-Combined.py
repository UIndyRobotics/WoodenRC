'''
  UDP-Network-Photon.py
  Clayton Winders
  March 29, 2018
  Prints UDP packets send to this machine, port '8081'.  Unpackes a struct created on a
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

};

  See udp-wifi-streamer.ino for the Photon code.
'''

port = 49154

struct_format = 'IiiiIifffff6s16s16s16s6s20s'
throttle = -1
steer = -1

import os
from socket import *
from struct import *

def getMAS(mac):
  return "%x:%x:%x:%x:%x:%x" % unpack("BBBBBB",mac)

host = ""

buf = 1024
addr = (host, port)
UDPSock = socket(AF_INET, SOCK_DGRAM)
UDPSock.bind(addr)
print("Waiting to receive message...")
while True:
    (data, addr) = UDPSock.recvfrom(buf)
    #data = data.decode('utf-8')
    print(len(data), calcsize(struct_format))
    #(device_mac, local_ip, gateway_ip, subnet_mask, sig_strength, bssid, ssid, counter, throttle, steer) = unpack("6s16s16s16si6s20siii", data)
    (counter, throttle, throttle_out, steer, ir_changes, sig_strength, ax, ay, az, battery_voltage_in, battery_current_in,device_mac, local_ip, gateway_ip, subnet_mask, bssid, ssid) = unpack(struct_format, data)

#     local_ip = local_ip.rstrip('\0')
#     gateway_ip = gateway_ip.rstrip('\0')
#     subnet_mask = subnet_mask.rstrip('\0')
#     ssid = ssid.rstrip('\0')

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
