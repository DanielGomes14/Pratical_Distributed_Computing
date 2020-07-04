# Echo client program
import socket
import sys
import json 
from datetime import datetime
import selectors
import fcntl
import os
   
class Client:
    def __init__(self):
        self.mode=True
        self.flagC=True
        self.ask=True
        self.HOST = 'localhost'      # Address of the host running the server  
        self.PORT = 5001    # The same port as used by the server
        self.to=""
        self.msg=""
        self.s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.HOST, self.PORT))
       # self.s.setblocking(False)
    def encodeJSON(self, to, msg):
        now = datetime.now()
        timemessage=now.strftime("%d/%m/%Y %H:%M:%S")
        init={"from":sys.argv[1],"to": to, "timestamp":timemessage,"msg":msg}
        init=json.dumps(init)
        init=init.encode('utf-8')
        return init
    def decodeJSON(self,data):
        data=data.decode('utf-8')
        usrdata=json.loads(data)
        frm=usrdata["from"]
        to=usrdata["to"]
        msg=usrdata["msg"]
        timemessage=usrdata["timestamp"]
        return frm,to,timemessage,msg
    def is_json(self,myjson):
        try:
            json_object = json.loads(myjson)
        except ValueError as e:
            return False
        return True 
    def decodeErrorMessage(self,data):
        data=data.decode('utf-8')
        print (data)
        
    def sendMsg(self):
        data= c.encodeJSON(self.to, self.msg)
        msgsize=str(len(data))
        msgsize="{:>5}".format(msgsize)
        msgsize=msgsize.encode('utf-8')
        self.s.send(msgsize)
        self.s.send(data)

    def write(self, stdin,mask):
        if self.ask:
            if stdin.read().rstrip()=="S":
                self.mode=True
            else:
                self.mode=False
            self.ask=False
        else:
            if self.mode:
                if self.flagC:
                    self.to=stdin.read().rstrip()
                    if self.to in '\r\n':
                        sys.exit(0)
                    self.to="channel//"+self.to
                    self.flagC=False
                else:
                    self.msg=stdin.read().rstrip()
                    if self.msg in '\r\n':
                        sys.exit(0)
                    self.sendMsg()
                    self.flagC=True
                    self.ask=True
            else:           
                if self.flagC:
                    self.to=stdin.read().rstrip()
                    if self.to in '\r\n':
                        sys.exit(0)
                    self.to=self.to
                    self.flagC=False
                else:
                    self.msg=stdin.read().rstrip()
                    if self.msg in '\r\n':
                        sys.exit(0)
                    self.sendMsg()
                    self.flagC=True
                    self.ask=True
    
    def read(self, conn,mask):
        nBytes=conn.recv(5)
        nBytes=int(nBytes.decode())
        data = conn.recv(nBytes)
        if data and not self.is_json(data):
            sys.stdout.write("\033[F") #back to previous line
            sys.stdout.write("\033[K")
            self.decodeErrorMessage(data)
            return
        if data:
            frm,to,timemessage,msg=c.decodeJSON(data)
            if to.split("//")[0]=="channel":
                chan=to.split("//")[1]
                print("Channel:{} ({}) From: {} Message: {}".format(chan, timemessage,frm,msg))
            else:
                print("({}) From: {} Message: {}".format(timemessage,frm,msg))
        else:
            print("Connection to Server Lost!", conn)
            sel.unregister(conn)
            return


sel = selectors.DefaultSelector()
orig_fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
fcntl.fcntl(sys.stdin, fcntl.F_SETFL, orig_fl | os.O_NONBLOCK)
# function to be called when enter is pressed

# register event
c=Client()
init=c.encodeJSON("", sys.argv[1])
c.s.send(init)
sel.register(c.s, selectors.EVENT_READ, c.read)
sel.register(sys.stdin, selectors.EVENT_READ, c.write)

while True:
    if c.ask:
        print("Pretende mandar para um canal? [S/N] \n", end='', flush=True) #meter logo a false
    else:
        if c.mode: #para channels
            if c.flagC:
                print("Insira channel para comunicar: \n", end='', flush=True)
            else:
                print("Insira conteudo da mensagem: \n", end='', flush=True) # meter ask a true
        else: #para dest
            if c.flagC:
                print("Insira destinatário da mensagem: \n", end='', flush=True)
            else:
                print("Insira conteudo da mensagem: \n", end='', flush=True) # meter ask a true
    for k, mask in sel.select():
        callback = k.data
        callback(k.fileobj,mask)