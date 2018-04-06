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
from threading import Thread

class TCPThread(Thread):
  def __init__(self, con_list):
    Thread.__init__(self)
    self.con_list = con_list
    print("Waiting for TCP connections")
    
  def run(self):
    tcpServer = socket(AF_INET, SOCK_STREAM)
    tcpServer.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    tcpServer.bind( ('0.0.0.0', TCP_port) )
    while True:
      tcpServer.listen(4)
      (con, (ip, port)) = tcpServer.accept()
      print("Got a new connection! %s %s" % (str(ip), str(port)) )
      self.con_list.append(con)
      

host = ""

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
    (data, addr) = UDPSock.recvfrom(buf)
    (counter) = unpack('i', data[0:4]) # pull the first integer off
#    print("Got UDP len: %d id: %d listeners: %d" % ( len(data), counter[0], len(con_list)))
    #print "%d" % (counter[0])
    # Loop through all the connections and send to each client
    # TODO: This may cause a slowdown, investigate, and possibly multithread.
    for c in con_list:
      # If connection is invalid, (they disconnected, remove from the list)
      try:
        c.send(data)
      except socket.error as e:
        print "Removing TCP client"
        con_list.remove(c)
        

tcp_thread.join()

