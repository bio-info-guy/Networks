import socket 
import sys
import re

# get arguments
arguments = sys.argv[1:]
hostname = arguments[0] 
port = arguments[1]
command = arguments[2]
filename = arguments[3]

# validate arguments 
try:
    if len(arguments) != 4 or not re.match(r'\w',hostname) or not re.match(r'^[0-9]+$',port) or not re.match(r'[A-Za-z]+',command) or not re.match(r'\w',filename) :
        raise ValueError
except ValueError:
    print "Usage: client hostname port command filename"
    sys.exit()

# use ipv4/ipv6 and TCP
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print "Socket successfully created"
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
print "the socket has successfully connected to host \
on port == %s" %(host_ip)

# method GET and PUT
if command == "GET":
    data = "GET "+"/"+filename +" HTTP/1.1\r\nHost: "+hostname+ "\r\n\r\n"
    print data
    s.send(data)
    response = s.recv(4098)
    print response
elif command == "PUT":
    data = "PUT /"+ filename +" HTTP/1.\1r\nHost: "+hostname+ "\r\n\r\n"

s.close()