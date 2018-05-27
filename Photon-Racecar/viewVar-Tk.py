

host = "192.168.79.10"  # UIndy server
port = 49154


car_id = 100

import os
from Tkinter import *
import tkMessageBox
from socket import *
from unpackStruct import *
import time
import os.path
import thread


buf = 1024
addr = (host, port)
connected = False

  

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
    thread.start_new_thread( getPackets , ())
  else:
    logging = False
    connected = False
    time.sleep(0.5)
    TCPSock.close()
    TCPSock = None
    event.widget['text'] = "Connect"
  
def getPackets(event = None):
  global connect
  global connected
  global net_status
  global voltage_label
  data = ""
  if not connected:
    return
  while TCPSock:  # A disconnect will set this False
    rcv = TCPSock.recv(buf)
    if rcv == None:
      connect.widget['text'] = "Connect"
      connected = False
      tkMessageBox.showerror("Error", "Connection lost!");
      return
    data = data + rcv
    (data, r) = unpackStruct(data)
    while r != None:  # r will be None when there is no more packets to remove from the data buffer
      if ord(r['device_mac'][-1]) == car_id:
        voltage_label['text'] = 'Battery Voltage: %.02f' % ( r['battery_voltage_in']) 
      (data, r) = unpackStruct(data)
  
  
    

master = Tk()

connect = Button(master, text = "Connect")
connect.grid(column = 0, row = 0)
connect.bind('<Button>', connectClick)

net_status = Label(master, text = "")
net_status.grid(column = 1, row = 0)

voltage_label = Label(master, width=30, text = "Battery Voltage: ")
voltage_label.grid(column = 0, row = 1)


mainloop()




