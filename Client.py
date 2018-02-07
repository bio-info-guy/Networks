import socket 
import sys
import re
import struct
import os

def socket_client():
    # get arguments
    arguments = sys.argv[1:]
    hostname = arguments[0] 
    port = arguments[1]
    command = arguments[2]
    filename = arguments[3]

    # validate arguments 
    try:
        if len(arguments) != 4 or not re.match(r"^[0-9]+$",port) or not re.match(r"[A-Za-z]+",command):
            raise ValueError
    except ValueError:
        print "Usage: client hostname port command filename"
        sys.exit()

    # use ipv4/ipv6 and TCP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as err:
        print "socket creation failed with error %s" %(err)

    # get ip from hostname
    try:
        host_ip = socket.gethostbyname(hostname)
    except socket.gaierror:
        print "there was an error resolving the host"
        sys.exit()

    # connecting to the server
    s.connect((host_ip,int(port)))
    print "\nSuccessfully connected to host on port: %s" %(host_ip)

    # method GET and PUT

    if command == "GET":
        data = "GET "+"/"+filename +" HTTP/1.1\r\nHost: "+hostname+ "\r\n\r\n"
        buffer = []
        s.send(data)
        response = s.recv(1024)
        while(True):
            if response == "DONE" or response == "SHUTDOWN 9":
                break
            print response
            response = s.recv(1024)
        s.close()
    if command == "PUT":
        data = "PUT "+"/"+filename +" HTTP/1.1\r\nHost: "+hostname+ "\r\n\r\n"
        s.send(data)
        print s.recv(1024)
        try:
            f = open("/"+filename,"rb")
        except IOError:
            print ("Can not find the file!")
            s.send("File Error")
            sys.exit()        
        l = f.read(1024)
        while (l):
            #print "SENT"
            s.send(l)
            l = f.read(1024)
        s.send("DONE")
        #print("SENT DONE")
        while(True):
            response = s.recv(1024)
            if response == "200 OK File Created" or response == "SHUTDOWN 9":
                print response 
                break
        s.close()
if __name__ == "__main__":
    socket_client()