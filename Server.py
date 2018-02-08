#Server Side
import socket
import os.path
from threading import Thread
import socket
import os
import sys
import re
class Server:
    def __init__(self,  port, connect="localhost"):
        self.s= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.connect=connect
        self.port=port
        self.s.bind((self.connect, port))
        self.s.listen(5)
        self.connections = []
    def close(self):
        self.s.close()
    def multiThreadClientHandler(self):
        try:
            while True:
                (conn, addr) = self.s.accept()
                self.connections.append((conn, addr))
                print("\nSuccessfully connected to: "+addr[0]+":"+str(addr[1]))
                print("This is a new connection\n")
                clientp=ClientProcess(conn, addr)
                clientp.daemon = True
                clientp.start()
                
        except KeyboardInterrupt:
            print("Now shutting down server gently\n")
            for (conn, addr) in self.connections:
                conn.send(str.encode("SHUTDOWN 9"))
            self.close()
            raise
        
class ClientProcess(Thread):
    def CMDparser(self, cmd):
        msg=self.conn.recv(4096).decode()
        print(msg)
        if msg[:3] == "GET":
            command="GET"
        elif msg[:3] == "PUT":
            command="PUT"
        filename=msg.split(" ")[1]
        return command, filename
    
    def __init__(self, conn, addr):
        Thread.__init__(self)
        self.conn=conn
        self.addr=addr
        self.cmd, self.file=self.CMDparser(conn)
    
    def GET(self):
        if self.file == "/" or not os.path.isfile(self.file):
            self.conn.sendall(str.encode("HTTP/1.1 400 NOT FOUND"))
            self.conn.send(str.encode("DONE"))
            print("\nNo filename was given for GET or can not find the file")
            print("Connection DONE\n#######################################\n")
        else:
            msg="HTTP/1.1 200 OK"
            print("Sending file to client")
            self.conn.send(msg.encode())
            packet_num=0
            f=open(self.file, "rb")
            l = f.read(2048)
            while (l):
                packet_num +=1
                self.conn.send(l)
                print("Sent: "+str(packet_num)+" to "+str(self.addr[0])+":"+str(self.addr[1]))
                l = f.read(2048)
            self.conn.send(str.encode("DONE"))
            f.close()
            print("Connection DONE\n#######################################\n")
            
    def PUT(self):
        if self.file == "/":
            self.conn.sendall(str.encode("No filename was given for PUT"))
            print("\nNo filename was given for PUT")
        else:
            print ("\nPut connection is OK!")
            self.conn.send(str.encode("Put connection is OK!"))
            f=open(filename,"a")
            while 1:
                l=self.conn.recv(1024)
                if str(l.decode()) == "DONE":
                    break
                elif str(l.decode()) == "File Error":
                    print ("File error")
                    break
                f.write(l.decode())
            f.close()
            self.conn.send(str.encode("200 OK File Created"))
            print("Connection DONE\n#######################################\n")
                        
    def run(self):
        if(self.cmd == "PUT"):
            self.PUT()
        elif (self.cmd == "GET"):
            self.GET()
arguments = sys.argv[1:]    
try:
    if len(arguments) != 1 or not re.match(r"^[0-9]+$",arguments[0]):
        raise ValueError
except ValueError:
    print ("Usage: server port")
    sys.exit()        
myServer=Server(port=int(arguments[0]))
myServer.multiThreadClientHandler()

