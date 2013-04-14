#!/usr/bin/python

#########################################################################
#			     NetEBCDICat                                #
#########################################################################
# Script to communicate with netcat on OMVS (z/OS IBM Mainframe UNIX)	#
#                                                               	#
# Requirements: Python, netcat-omvs running on a mainframe      	#
# Created by: Soldier of Fortran (@mainframed767)               	#
# Usage: This script will listen for or connect to a z/OS OMVS  	#
# mainframe netcat session and translate the data from 			#
# ASCII to EBCDIC and back						#
#                                                               	#
# Copyright GPL 2012                                             	#
#########################################################################
###
# # Lots of help from http://4thmouse.com/index.php/2008/02/22/netcat-clone-in-three-languages-part-ii-python/
###


from select import select
import socket
import signal
import sys
import argparse #needed for argument parsing


#EBCDIC/ASCII converter, customize by me for use here
# from http://www.pha.com.au/kb/index.php/Ebcdic.py
a2e = [
      0,  1,  2,  3, 55, 45, 46, 47, 22,  5, 21, 11, 12, 13, 14, 15,
     16, 17, 18, 19, 60, 61, 50, 38, 24, 25, 63, 39, 28, 29, 30, 31,
     64, 79,127,123, 91,108, 80,125, 77, 93, 92, 78,107, 96, 75, 97,
    240,241,242,243,244,245,246,247,248,249,122, 94, 76,126,110,111,
    124,193,194,195,196,197,198,199,200,201,209,210,211,212,213,214,
    215,216,217,226,227,228,229,230,231,232,233, 74,224, 90, 95,109,
    121,129,130,131,132,133,134,135,136,137,145,146,147,148,149,150,
    151,152,153,162,163,164,165,166,167,168,169,192,106,208,161,  7,
     32, 33, 34, 35, 36, 21,  6, 23, 40, 41, 42, 43, 44,  9, 10, 27,
     48, 49, 26, 51, 52, 53, 54,  8, 56, 57, 58, 59,  4, 20, 62,225,
     65, 66, 67, 68, 69, 70, 71, 72, 73, 81, 82, 83, 84, 85, 86, 87,
     88, 89, 98, 99,100,101,102,103,104,105,112,113,114,115,116,117,
    118,119,120,128,138,139,140,141,142,143,144,154,155,156,157,158,
    159,160,170,171,172,173,174,175,176,177,178,179,180,181,182,183,
    184,185,186,187,188,189,190,191,202,203,204,205,206,207,218,219,
    220,221,222,223,234,235,236,237,238,239,250,251,252,253,254,255
    ]

e2a = [
      0,  1,  2,  3,156,  9,134,127,151,141, 11, 11, 12, 13, 14, 15,
     16, 17, 18, 19,157, 10,  8,135, 24, 25,146,143, 28, 29, 30, 31,
    128,129,130,131,132, 10, 23, 27,136,137,138,139,140,  5,  6,  7,
    144,145, 22,147,148,149,150,  4,152,153,154,155, 20, 21,158, 26,
     32,160,161,162,163,164,165,166,167,168, 91, 46, 60, 40, 43, 33,
     38,169,170,171,172,173,174,175,176,177, 93, 36, 42, 41, 59, 94,
     45, 47,178,179,180,181,182,183,184,185,124, 44, 37, 95, 62, 63,
    186,187,188,189,190,191,192,193,194, 96, 58, 35, 64, 39, 61, 34,
    195, 97, 98, 99,100,101,102,103,104,105,196,197,198,199,200,201,
    202,106,107,108,109,110,111,112,113,114,203,204,205,206,207,208,
    209,126,115,116,117,118,119,120,121,122,210,211,212,213,214,215,
    216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,
    123, 65, 66, 67, 68, 69, 70, 71, 72, 73,232,233,234,235,236,237,
    125, 74, 75, 76, 77, 78, 79, 80, 81, 82,238,239,240,241,242,243,
     92,159, 83, 84, 85, 86, 87, 88, 89, 90,244,245,246,247,248,249,
     48, 49, 50, 51, 52, 53, 54, 55, 56, 57,250,251,252,253,254,255
]

def AsciiToEbcdic(s):
    if type(s) != type(""):
        raise "Bad data", "Expected a string argument"

    if len(s) == 0:  return s

    new = ""

    for i in xrange(len(s)):
	#print s[i],":",ord(s[i])
        new += chr(a2e[ord(s[i])])

    return new

def EbcdicToAscii(s):
    if type(s) != type(""):
        raise "Bad data", "Expected a string argument"

    if len(s) == 0:  return s

    new = ""

    for i in xrange(len(s)):
	#print s[i],":",ord(s[i])	
        new += chr(e2a[ord(s[i])])

    return new

##Nice colours for us to use
class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.BLUE = ''
        self.GREEN = ''
        self.YELLOW = ''
        self.RED = ''
        self.ENDC = ''

# catch the ctrl-c to exit and say something instead of Punt!
def signal_handler(signal, frame):
        print 'Kick!'
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
#################################################################

#start argument parser
parser = argparse.ArgumentParser(description='Script to communicate with netcat on OMVS (z/OS IBM Mainframe UNIX)',epilog='Damn you EBCDIC!')
parser.add_argument('-l','--listen',help='listen for incomming connections', default=False,dest='server',action='store_true')
parser.add_argument('-i','--ip', help='remote host IP address',dest='ip')
parser.add_argument('-p','--port', help='Port to listen on or to connect to',required=True,dest='port')
parser.add_argument('-d','--dinologo',help='display cool ass logo', default=False,dest='logo',action='store_true')
args = parser.parse_args()
results = parser.parse_args() # put the arg results in the variable results

#print logo
if results.logo:
	print bcolors.GREEN + '''                       .       .
                      / `.   .' \\
              .---.  <    > <    >  .---.
              |    \  \ - ~ ~ - /  /    |
               ~-..-~             ~-..-~
           \~~~\.'                    `./~~~/
            \__/                        \__/
             /                  .-    .   \\
      _._ _.-    .-~ ~-.       /       }   \/~~~/
  _.-'q  }~     /       }     {        ;    \__/
 {'__,  /      (       /      {       /      `. ,~~|   .     .
  `''..='~~-.__(      /_      |      /- _      `..-'   \\\   //
              / \   =/  ~~--~~{    ./|    ~-.     `-..__\\\_//_._
             {   \  +\         \  =\ (        ~ - . _ _ _..--~'"
             |  | {   }         \   \_\\
            '---.o___,'       .o___,' \n''' + bcolors.BLUE + "\t\tnetEBCDICat by" +bcolors.YELLOW+ " Soldier of Fortran" + bcolors.ENDC

if not results.server:
	try:
		MFsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		MFsock.connect( (results.ip, int(results.port)) )
	except Exception, e:
    		print  bcolors.RED + "[ERR] could not connect to ",results.ip,":",results.port,"" + bcolors.ENDC
		print bcolors.RED + "",e,"" + bcolors.ENDC
		sys.exit(0)

else:
	if not results.ip == "":
		print bcolors.YELLOW + "[WARN] You defined IP address", results.ip, "but are in listening mode. Ignored." + bcolors.ENDC
	try:
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		server.bind((socket.gethostname(), int(results.port))) 
		server.listen(1)
		MFsock, address = server.accept()
	except Exception, e:
    		print bcolors.RED + "[ERR] could not open server on port:", results.port,"" + bcolors.ENDC
		print bcolors.RED + "",e,"" + bcolors.ENDC
		sys.exit(0)

MFsock.setblocking(0)
while(1):
	r, w, e = select(
		[MFsock, sys.stdin], 
		[], 
		[MFsock, sys.stdin])
	try:
		buffer = MFsock.recv(128)
		while( buffer  != ''):
			ascii_out = EbcdicToAscii(buffer)
			print ascii_out,
			buffer = MFsock.recv(128)
                if(buffer == ''):
			break;
	except socket.error:
                pass
	
	while(1):
		r, w, e = select([sys.stdin],[],[],0)
		if(len(r) == 0):
			break;
		c = raw_input()
		if(c == ''):
			break;
		c += "\n"
		command = AsciiToEbcdic(c)
		if(MFsock.sendall(command) != None):
			break;
