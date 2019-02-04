'''
  UDP-Network-Photon.py
  Clayton Winders
  March 29, 2018
  Prints UDP packets send to this machine and port.  Unpackes a struct created on a
  Particle Photon with the following:

  Keeps a buffer of cross_time_max_ms length and looks for an increase of cross_min_increase in that 
  buffer to trigger a crossing.  If a crossing is detected, the buffer is cleared, thus taking time
  to fill again.
  Time is given in ms, relative to the car, so no network delay should be present
'''
#host = "18.217.55.123"  # IP address of Talaga's EC2 repeater
host = "192.168.79.10"  # UIndy server
port = 49154
addr = (host, port)

import os
from socket import *
from struct import *
import datetime, time
from unpackStruct import *



cross_time_max_ms = 500
cross_min_increase = 30
pause_after_cross_ms = 2000  

currentMilliTime = lambda: int(round(time.time() * 1000))

maxIR = []

def ms2Time(ms):
  ms = int(ms)
  minutes = ms/ 1000 / 60
  min_string = ""
  if minutes == 0:
    min_string = ""
  else:
    min_string = str(minutes)
  seconds = (ms - minutes * 1000 * 60) / 1000
  ms_final = ms - minutes * 1000 * 60 - seconds * 1000
  return "%s%d.%d" % (min_string, seconds, ms_final)
  

def printStatus(cars):
  print "%d Cars" % (len(cars))
  for cnum in sorted(cars.keys()):
    c = cars[cnum]
    lap_detail = ""
    total_time = 0.0
    # c.laps is an array of float times
    for lnum in range(len(c['laps'])):
      total_time += c['laps'][lnum]
      lap_detail += "L%d: %s (%s)   " % (lnum ,ms2Time(c['laps'][lnum]), ms2Time(total_time))
    print "%s %d laps:  %s" % (c["name"], len(c['laps']), lap_detail)
  print "\n\n"



def updateTimingData(full_ir, info):
  full_ir.append( (r['time'],r['ir_changes']) )
  full_ir = filter( lambda (t,_): t > r['time'] - cross_time_max_ms, full_ir)
  return full_ir
  
def detectCross(full_ir, last_cross = 0):
  global maxIR
  if len(full_ir) <= 1:
    return (full_ir, False, -1)
  (start_ms, start_ir) = full_ir[0]
  (end_ms, end_ir) = full_ir[-1]
  # Don't detect until after pause_after_cross_ms
  if end_ms < last_cross + pause_after_cross_ms:
    return (full_ir, False, -1)
  # print the last max value to help with tuning
  maxIR.append(end_ir - start_ir)
  while len(maxIR) > 50:
    maxIR = maxIR[1:]
  #
  print "Diff %d  Max %d ir: %d" % (end_ir - start_ir, max(maxIR), end_ir) 
  if end_ir - start_ir > cross_min_increase:
    return ([], True, end_ms)
  else:
    return (full_ir, False, -1)

buf = 1024
TCPSock = socket(AF_INET, SOCK_STREAM)
TCPSock.connect(addr)
data = ""
cars = {}

while True:
    data = data + TCPSock.recv(buf)
    
    (data, r) = unpackStruct(data)
    while r != None:
      car_num = ord(r['device_mac'][-1])
      if car_num not in cars.keys():
        cars[car_num] = {'name': car_num, 'laps':[], 'ir':[], 'lap_ms': 0, 'started': False}
    # append timing data
    
      cars[car_num]['ir'] = updateTimingData(cars[car_num]['ir'], r )
      (cars[car_num]['ir'], cross, end_ms) = detectCross(cars[car_num]['ir'], cars[car_num]['lap_ms'])
      if cross and len(cars[car_num]['laps']) == 0:
        print "Started"
        cars[car_num]['lap_ms'] = end_ms
        cars[car_num]['started'] = True
        cars[car_num]['laps'].append(0)
      elif cross:
        print "Lap"
        cars[car_num]['laps'].append(end_ms - cars[car_num]['lap_ms'])
        cars[car_num]['lap_ms'] = end_ms
      (data, r) = unpackStruct(data)
    
    printStatus(cars)
    

    

    

    

'''

'''
