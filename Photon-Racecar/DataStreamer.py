'''
  TCP-Network-Photon.py
  Paul Talaga
  April 6, 2018
  Connects via TCP to a a UDP repeater (UDP-Repeater) running in the cloud, which
  streams information sent to it via UDP.

  
'''

#host = "18.217.55.123"  # IP address of Talaga's EC2 repeater
host = "192.168.79.10"  # UIndy server
port = 49154


throttle = -1
steer = -1

import os
from socket import *

from unpackStruct import *


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
    (data, r) = unpackStruct(data)
    while r != None:
      
      print "backlog: %d" % (len(data))
      print data
      # Attemp to print how many lost packets we've seen
      if start_counter == -1:
        start_counter = r['counter']
      packets_so_far += 1
    

      print("\n   Missed Packets: %d" % (packets_so_far - (r['counter'] - start_counter)))
      print("local ip: ", r['local_ip'])
      print("gateway: ", r['gateway_ip'])
      print("mask: ", r['subnet_mask'])
      print("strength: ", r['sig_strength'])
      print("ssid: ", r['ssid'])
      print("counter: ", r['counter'])
      print("mac: ", r['device_mac'])
      print("bssid: ", r['bssid'])
      print("throttle: ", r['throttle'])
      print("throttle out: ", r['throttle_out'])
      print("steer: ", r['steer'])
      print("ax: ", r['ax'])
      print("ay: ", r['ay'])
      print("az: ", r['az'])
      print("Battery Voltage: ", r['battery_voltage_in'])
      print("Battery Current: ", r['battery_current_in'])
      print("Battery Currentsum:", r['battery_current_sum'])
      print("IR_changes: ", r['ir_changes'])
      print("milli time: ", r['time'])
      print("wheel pos: ", r['wheel'])
      (data, r) = unpackStruct(data)
    #print unpacked
    #print("Received message (" + str(len(data)) + "): " + data)

