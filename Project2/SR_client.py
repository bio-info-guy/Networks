# -*- coding: utf-8 -*-
"""SRclient.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1uz7Mu04AEewAfJI0b3pnMpDvraTN0x5Q
"""

import socket
import struct
from collections import OrderedDict
from threading import Thread, Lock
import math
import os
import time
import sys
import numpy as np 

def computeChecksum(data):
		sum = 0
		for i in range(0, len(data), 2):
			if i+1 < len(data):
				data16 = ord(data[i]) + (ord(data[i+1]) << 8)
				interSum = sum + data16
				sum = (interSum & 0xffff) + (interSum >> 16)
		return ~sum & 0xffff

#self.sockAddr.recvfrom(buffersize)

global window 
global windowLock
global SendComplete
window=OrderedDict()
windowLock=Lock()
SendComplete=False
class AckReciever(Thread):
  
  def __init__(self, sendsock, buffersize, maxseqnum):
    Thread.__init__(self)
    self.sock=sendsock
    self.buffersize=buffersize
    self.maxseqnum=maxseqnum
  def checkACK(self, ACK, checksum):
    return 1 if computeChecksum(str(ACK)) == checksum else 0
  
  def openPacket(self, packet):
    ACKnum=struct.unpack('I',packet[:4])[0]
    checksum=struct.unpack('H',packet[4:6])[0]
    return ACKnum, checksum
   
  def run(self):
    global window
    global windowLock
    while len(window) > 0 or not SendComplete:
      print("\nWaiting to recieve ACK")
      ACKpacket, _ = self.sock.recvfrom(self.buffersize)
      ACK, checksum = self.openPacket(ACKpacket)
      if ACK == self.maxseqnum+1:
        break
      if self.checkACK(ACK, checksum):
        with windowLock:
          window[ACK]=2 # 2 means it has been ACKed
          print ("\nACK recieved with sequence number: " + str(ACK))
          for i in window:
            if window[i] == 2: 
              del window[i]
            else:
              break

class ProcessFile(object):
  def __init__(self, filename, segmentSize, maxseqnum, Package_No):
    self.filename = filename
    self.segmentSize = segmentSize
    self.maxseqnum = maxseqnum
    self.Package_No = int(Package_No)
    SendComplete=False
  def fragmentation(self):
    data_list = []
    data_pre_list = []
    with open(self.filename, "rb") as f:
#      i = 0
      while True:
        data = f.read(self.segmentSize - 6)        
        if not data:
          break
        data_pre_list.append(data)
#        sequenceNumber = i % self.maxseqnum
 #       checksum = computeChecksum(data+str(sequenceNumber))
 #       data_list.append((sequenceNumber, checksum, data))
#        i += 1
    if len(data_pre_list) < self.Package_No:
      data_pre_list = data_pre_list * ((self.Package_No -len(data_pre_list))/len(data_pre_list)+1)
      data_pre_list = data_pre_list[0:self.Package_No] 
    else:
      data_pre_list=data_pre_list[0:self.Package_No]
    i = 0
    for x in data_pre_list:
      sequenceNumber = i % self.maxseqnum
      checksum = computeChecksum(x+str(sequenceNumber))
      data_list.append((sequenceNumber, checksum, x))
      i += 1
    return data_list
  def fragmentList(self):
    return self.fragmentation()
##### main process file -> segments -> SengSegments

class SendSegments(Thread):
  def __init__(self, sock, segments, timeout, maxwindowsize):
    Thread.__init__(self)
    self.sock=sock
    self.timeout=timeout
    self.segments = segments
    self.maxwindowsize = maxwindowsize
  def run(self):
    list = []
    global window
    global windowLock

    while self.segments:
      if len(window.keys()) < self.maxwindowsize:  # Base < nextsequencenumber
        segment=self.segments.pop(0)
        pkt=SendPacket(self.sock, segment, self.timeout)
        with windowLock:
          window[segment[0]] = 0 # 0 means is about to be sent
        pkt.start()
        list.append(pkt)
      else:
        continue
    

class SendPacket(Thread):
  
  def __init__(self,sock, segment,timeout, bit_error_probability=0.1):
    Thread.__init__(self)
    self.segment = segment
    self.timeout = timeout
    self.socket = sock
    self.bit_error_probability = bit_error_probability
    
  def send(self,packet): 
    self.socket.sendto(packet,(socket.gethostbyname("localhost"),55555))

  def modifyPacket(self, packet):
    sequenceNumber=packet[0]
    checksum=packet[1]
    data=packet[2]
    if np.random.rand() < self.bit_error_probability:
      print('\nOops, bit error accidentally generated.......')
      if np.random.rand < 0.5:
        d=bytearray(data)
        d[np.random.randint(len(d))]=np.random.randint(256)
        data=bytes(d)
      else:
        s=bytearray(sequenceNumber)
        s[np.random.randint(4)]=np.random.randint(256)
        sequenceNumber=bytes(s)
    return sequenceNumber+checksum+data

  def packpacket(self):
    
    sequenceNumber = struct.pack('=I', self.segment[0])
    checksum = struct.pack('=H', self.segment[1])
    data=self.segment[2].encode('UTF-8')

    return sequenceNumber, checksum, data
  def run(self):
    global window
    global windowLock
    packetTuple=self.packpacket() 
    packet=self.modifyPacket(packetTuple)
    with windowLock:
      self.send(packet)
      print ("\nSending package with sequence number: " + str(self.segment[0]))
     
      window[self.segment[0]] = 1 
# 1 means already sent but not ACKed
    self.timer=time.time()
    print ("\nTimer started")
    while True:
      with windowLock:
        try:
          if window[self.segment[0]] == 2:
            break
        except:
          break
      if time.time() - self.timer >= self.timeout:
        with windowLock:
          print ("\nResending package with sequence number: " + str(self.segment[0]))
          packet=self.modifyPacket(packetTuple)
          self.send(packet)
          window[self.segment[0]] = 1
        self.timer=time.time()
        print ("\nTimer started")

















