#!/usr/bin/python
import sys, getopt
import socket
import commands
import thread
import time
import os

as_server = True
port = 27563
ssh_login_info = None

def trace_log(msg):
    if as_server :
        sys.stdout.write(msg+"\n")
    else :
        print(msg)

def usage() :
    print('''
    --server, -s: run as ssh server provide host
    --client, -c: run as ssh client host
    --port=, -p: specify connect port , default is 27563
    --sshLogin=, -l: info choose host login, like userName@hostName
    ''')

options,args = getopt.getopt(sys.argv[1:],"hscp:l:",["sshLogin=","port=","server","client"])
for opt, value in options :
    if opt == '-h' :
        usage()
        exit(0)
    elif opt == '-p' or opt == '--port':
        port = int(value)
    elif opt == '-l' or opt == '--sshLogin':
        ssh_login_info = value
    elif opt == '--server' or opt == '-s':
        as_server = True
    elif opt == '--client' or opt == '-c':
        as_server = False
    else :
        usage()
        exit(0)

run_desc="run as" + \
(" server," if as_server else " client,") + \
" port:"+ str(port) + \
(" sshUser:"+ssh_login_info if ssh_login_info != None else "")

trace_log(run_desc)

def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

host_name = socket.gethostname()
host_ip = get_host_ip()
host_info = host_name+"@"+host_ip

class SocketAble:
    
    def start(self):
        assert True , "should overwrite method!"

class Server(SocketAble):
    __port = None
    def __init__(self,port):
        #super().__init__(self,port)
        #SocketAble.__init__(self)
        self.__port = port

    def start(self):
        server_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        server_socket.bind(('',self.__port))
        trace_log("server socket listening, host_name:"+str(host_name)+" host_ip:"+str(host_ip)+" port:"+str(self.__port))

        while True:
            data,addr = server_socket.recvfrom(65535)
            trace_log('revice from:'+str(addr)+" data:"+data)
            
            if data.startswith("addr_application") :
                to_addr = (addr[0],self.__port)
                server_socket.sendto(host_info,to_addr)
                trace_log("reply:"+host_info+" to addr:"+str(to_addr))

def broadcast(port,maxCount) :
    count = 0
    while count < maxCount :
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        client_socket.sendto("addr_application", ('<broadcast>', port))
        count += 1
        trace_log("broadcast times:"+str(count))
        time.sleep(count)

class Client(SocketAble):
    __port = None
    def __init__(self,port):
        #super().__init__(self,port)
        #SocketAble.__init__(self,port)
        self.__port = port

    def start(self):
        sshUser = None
        sshHost = None

        if ssh_login_info != None :
            strs = ssh_login_info.split("@")
            assert len(strs) == 2 , 'ssh login info must be userName@hostName'
            sshUser = strs[0]
            sshHost = strs[1]

        s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.bind(('',self.__port))
        trace_log("reply listening...")
        
        thread.start_new_thread(broadcast, (self.__port, 6))
        
        while True:
            data,addr = s.recvfrom(65535)
            if addr[0] != host_ip:
                trace_log('receive reply>> '+data)
                if(sshUser != None):
                    infos = data.split("@")
                    if len(infos) == 2 and infos[0] == sshHost :
                        cmd = "ssh "+sshUser+"@"+infos[1]
                        trace_log('try ssh login, cmd:'+cmd)
                        os.execlp("ssh", "/user/bin/ssh",sshUser+"@"+infos[1])


socket_able = None
if as_server :
    socket_able = Server(port)
else:
    socket_able = Client(port)

socket_able.start()


