'''
  TCP-Network-Photon.py
  Paul Talaga
  April 6, 2018
  Connects via TCP to a a UDP repeater (UDP-Repeater) running in the cloud, which
  streams information sent to it via UDP.

  
'''

host = "18.217.55.123"  # IP address of Talaga's EC2 repeater
port = 49154


throttle = -1
steer = -1

import os
from Tkinter import *
import tkMessageBox
from socket import *
from unpackStruct import *
import time
import os.path
import csv




buf = 1024
addr = (host, port)


data = ""
logging = False
connected = False
cars = {}
fhandle = False
chandle = False

def saveData(filename, data):
  global fhandle
  global chandle
  columns = data.keys()
  columns = sorted(columns)
  if not fhandle:
    if os.path.isfile(filename) and False:  # Always write header, no csv append!
      # already exists
      fhandle = open(filename, "wb+")
      chandle = csv.writer(fhandle)
    else:
      fhandle = open(filename,"wb")
      chandle = csv.writer(fhandle)
      chandle.writerow(columns)

  # write data!
  row = []
  for c in columns:
    row.append(data[c])
  chandle.writerow(row)
  

def connectClick(event = None):
  global connected
  global TCPSock
  global logging
  if(not connected):
    event.widget['text'] = "Connecting..."
    TCPSock = socket(AF_INET, SOCK_STREAM)
    TCPSock.connect(addr)
    event.widget['text'] = "Connected!"
    connected = True
    connect.after(50, getPackets)
  else:
    logging = False
    connected = False
    time.sleep(0.5)
    TCPSock.close()
    TCPSock = None
    event.widget['text'] = "Connect"
  
def getPackets(event = None):
  global logging
  global data
  global connect
  global connected
  global log
  global net_status
  global car_display
  global car_filter
  global output_filename
  global fhandle
  global chandle
  if logging:
    log['text'] = 'Logging to file...'
  else:
    log['text'] = 'Log Data'
    if fhandle:
      fhandle.close()
    fhandle = False
    chandle = False
  if not connected:
    return
  rcv = TCPSock.recv(buf)
  if rcv == None:
    connect.widget['text'] = "Connect"
    connected = False
    logging = False
    print "here"
    return
  data = data + rcv
  lastlen = 0
  while len(data) != lastlen:
    (data, r) = unpackStruct(data)
    lastlen = len(data)
    if 'counter' in r.keys():
      net_status['text'] = str(r['counter'])
      car_num = ord(r['device_mac'][-1])
      if car_num not in cars.keys():
        cars[car_num] = 0
      else:
        cars[car_num] += 1
      car_display['text'] = "car #:packets\n" + str(cars)
      if logging:
        if car_filter.get() != "" and int(car_filter.get()) not in cars.keys():
          tkMessageBox.showerror("Error", "Enter your car number to log or invalid car");
          logging = False
        elif car_num == int(car_filter.get()):
          #print r
          if output_filename.get() == "":
            tkMessageBox.showerror("Error", "No filename given");
            logging = False
          else:
            saveData(output_filename.get(), r)
  connect.after(50, getPackets)
  
def logButton(event = None):
  global logging
  global connect
  global connected
  if not logging and not connected:
    tkMessageBox.showerror("Error", "You must connect first");
    return
  logging = not logging
  
    

master = Tk()

connect = Button(master, text = "Connect")
connect.grid(column = 0, row = 0)
connect.bind('<Button>', connectClick)

net_status = Label(master, text = "")
net_status.grid(column = 1, row = 0)

output_filename = Entry(master)
output_filename.grid(column = 0, row = 1)

car_filter = Entry(master)
car_filter.grid(column = 1, row = 1)

filter_status = Label(master, text = "")
filter_status.grid(column = 3, row = 1)

log = Button(master, text = "Log Data", command = logButton)
log.grid(column = 2, row = 1)

car_display = Label(master, text = "Available cars:")
car_display.grid(column = 1, row = 2)

mainloop()




