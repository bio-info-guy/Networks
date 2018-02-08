HTTP Client and Server

##################################
#        Auther                  #
#       Yangqi Su                #
#       Jing Chen                #
##################################

------ Usage ------
Server:
python3 Server.py port

Client:
python2 Client.py hostname port command filename 

------ Example ------
Server:
python3 Server.py 15000\n

Client:
python2 Client.py localhost 15000 GET Hallo_world.txt

------ Note ------
If python3 is not avaliable, please add:

from __future__ import *

to the first line of the Server.py file. 
