#Server Side
import socket
import os.path
from threading import Thread
class Server:
    def __init__(self,  port, connect='localhost'):
        self.s= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.connect=connect
        self.port=port
        self.s.bind((self.connect, port))
        self.s.listen(5)
    def close(self):
        self.s.close()
    def multiThreadClientHandler(self):
        try:
            while True:
                conn, addr = self.s.accept()
                print('Now connected to: '+addr[0]+":"+str(addr[1]))
                print('this is a new connection')
                clientp=ClientProcess(conn, addr)
                clientp.daemon = True
                clientp.start()
                
        except KeyboardInterrupt:
            print('Now shutting down server gently\n')
            self.close()
            raise
        


class ClientProcess(Thread):
    def CMDparser(self, cmd):
        msg=self.conn.recv(4096).decode()
        print(msg.split(" "))
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
            print("\nNo filename was given for GET\n")
        else:
            msg='HTTP/1.1 200 OK'
            self.conn.send(msg.encode())
            packet_num=0
            f=open(self.file, 'rb')
            l = f.read(2048)
            while (l):
                packet_num +=1
                self.conn.send(l)
                print("Sent: "+str(packet_num)+" to "+str(self.addr[0])+":"+str(self.addr[1]))
                l = f.read(2048)
            self.conn.send(str.encode("DONE"))
            f.close()
            print("DONE")
            
    def PUT(self):
        if self.file == "/":
            self.conn.sendall(str.encode("No filename was given for PUT"))
            print("\nNo filename was given for PUT\n")
        else:
            packet_num=0
            f=open(self.file,'a')
            data=self.conn.recv(1024)
            while data:
                packet_num +=1
                f.write(data.decode())
                print("Recieved: "+str(packet_num)+" from "+str(self.addr[0])+":"+str(self.addr[1]))
            f.close()
            self.conn.send(str.encode("File: "+self.file+" recieved"))

            
    def run(self):
        if(self.cmd == "PUT"):
            self.PUT()
        elif (self.cmd == "GET"):
            print("\nthis is GET\n")
            self.GET()
            
myServer=Server(port=15000)
myServer.multiThreadClientHandler()

