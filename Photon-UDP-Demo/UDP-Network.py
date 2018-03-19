'''
  UDP-Network-Photon.py
  Paul Talaga
  March 18, 2018
  Prints UDP packets send to this machine, port '8888'.  Unpackes a struct created on a
  Particle Photon with the following:

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

  See udp-wifi-streamer.ino for the Photon code.
'''

port = 8888

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
    (device_mac, local_ip, gateway_ip, subnet_mask, sig_strength, bssid, ssid, counter) = unpack("6s 16s 16s 16s i 6s 20s i", data)

    local_ip = local_ip.rstrip('\0')
    gateway_ip = gateway_ip.rstrip('\0')
    subnet_mask = subnet_mask.rstrip('\0')
    ssid = ssid.rstrip('\0')

    print "local: %s\ngateway: %s\nmask: %s\nstrength: %i\nssid: %s\ncounter: %i\nmac: %s\nbssid: %s\n" % (local_ip, gateway_ip, subnet_mask, sig_strength, ssid, counter, getMAS(device_mac), getMAS(bssid))
    #print unpacked
    #print("Received message (" + str(len(data)) + "): " + data)


'''

'''