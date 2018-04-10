'''
  UDP-Repeater.py
  Paul Talaga
  March 31, 2018

  Receives UDP packets from UDP_port below.  
  Accepts TCP connections to TCP_port, and for every UDP packet
  received, send it to all TCP connections.
'''

UDP_port = 49154
TCP_port = 49154

import os
from socket import *
from struct import *
import select
from threading import Thread
import time

currentMilliTime = lambda: int(round(time.time() * 1000))

class TCPThread(Thread):
  def __init__(self, con_list):
    Thread.__init__(self)
    self.con_list = con_list
    print("Waiting for TCP connections")
    
  def run(self):
    tcpServer = socket(AF_INET, SOCK_STREAM)
    tcpServer.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    tcpServer.bind( ('0.0.0.0', TCP_port) )
#    tcpServer.setsockopt(SOL_SOCKET, SO_KEEPALIVE, 1)
#    tcpServer.setsockopt(SOL_TCP, TCP_KEEPIDLE, 1)
#    tcpServer.setsockopt(SOL_TCP, TCP_KEEPINTVL, 1)
#    tcpServer.setsockopt(SOL_TCP, TCP_KEEPCNT, 1)
    while True:
      tcpServer.listen(4)
      (con, (ip, port)) = tcpServer.accept()
      print("Got a new connection! %s %s" % (str(ip), str(port)) )
      self.con_list.append(con)
      

host = ""

packet_capture = []
start_play_time = -1
mode = 0
playback_i = 0
# 0 = no
# 1 = recording - 'record' - clears old data
# 2 = playback  - 'play'

buf = 1024
udp_addr = (host, UDP_port)
UDPSock = socket(AF_INET, SOCK_DGRAM)
UDPSock.bind(udp_addr)

con_list = []

tcp_thread = TCPThread(con_list)
tcp_thread.daemon = True
tcp_thread.start()

print("Waiting to receive message...")
while True:
    if mode == 0 or mode == 1: #no recording or recording
      (data, addr) = UDPSock.recvfrom(buf)
      (counter) = unpack('i', data[0:4]) # pull the first integer off
      #    print("Got UDP len: %d id: %d listeners: %d" % ( len(data), counter[0], len(con_list)))
      #print "%d %d" % (counter[0], len(con_list))
      # Loop through all the connections and send to each client
      # TODO: This may cause a slowdown, investigate, and possibly multithread.
    elif mode == 2: #playback
      (t, data) = packet_capture[playback_i]
      while t + start_play_time > currentMilliTime():
        pass
      playback_i += 1
      if playback_i >= len(packet_capture):
        print("End of playback")
        mode = 0

    if mode == 1:
      packet_capture.append( (currentMilliTime() - start_play_time, data) )
      print(len(packet_capture))

    if len(packet_capture) > 100000:
      print("Too much data recorded")
      mode = 0
    # Send data

    for c in con_list:
      (r,w,e) = select.select((c,), (), (), 0)
      # select r returns an empty list if the socket is ready to send.

      # No data coming in on TCP
      if len(r) == 0:
        c.send(data)
      if len(r) == 1:
        user_input = c.recv(buf)
        if len(user_input) == 0:
          print("Removing TCP client")
          con_list.remove(c)
        else:
          c.send(data)
          if 'record' in user_input:
            print("Recording")
            packet_capture = []
            packet_capture.append( (0 , data) ) # tuples of (time from start of capture, data)
            start_play_time = currentMilliTime()
            mode = 1
          elif 'play' in user_input:
            print("Playback")
            mode = 2
            playback_i = 0
            start_play_time = currentMilliTime()
          else:
            print("%s not understoon!" % (user_input))

tcp_thread.join()

