USAGE:
GO-Back-N: 
python Client.py GBN.test 55556 20
python Server.py GBN.test 55555

Selective Repeat: 
python Client.py SR.test 55556 20
python Server.py SR.test 55555


Notes:
1. For Go-Back-N, the ACK number is the next expected sequence number.
2. For bit error/checksum simulation, sometimes the data is changed and sometimes the sequence number is changed. So probably an abnormal sequence number will be displayed on the screen. 
3. If the window size is invalid, a default window size will be used.
4. The timeout value is set to 4 sec. 
5. Please wait until all packets are sent. Then the server and client will be terminated by themselves. 

Author:
Yangqi Su
Jing Chen