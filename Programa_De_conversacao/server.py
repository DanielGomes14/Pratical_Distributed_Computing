# Echo server program
import socket
import selectors
import json
import time
sel = selectors.DefaultSelector()
json_users={}
channels={}

def get_key(val, dic): 
    for key, value in dic.items(): 
         if val == value: 
             return key 
    return "key doesn't exist"           
def decodeJSON(data):
    data=data.decode('utf-8')
    usrdata=json.loads(data)
    to=usrdata["to"]
    timemessage=usrdata["timestamp"]
    msg=usrdata["msg"]
    return to,timemessage,msg
def sendErrorMessage(sock,to):
    msg="User  "+ to + " Not Found!"
    msg=msg.encode('utf-8')
    msgsize=str(len(msg))
    msgsize="{:>5}".format(msgsize)
    msgsize=msgsize.encode('utf-8')
    sock.send(msgsize)
    sock.send(msg)
def encodeJSON(sender,to,timemessage,msg):
    init={"from":sender,"to":to,"timestamp":timemessage,"msg": msg}
    print(init)
    init=json.dumps(init)
    init=init.encode('utf-8')
    return init
def accept(sock, mask):
    conn, addr = sock.accept()  # Should be ready
    print('accepted', conn, 'from', addr)
    #conn.setblocking(False)
    data=conn.recv(1000)
    to,timemessage,msg=decodeJSON(data)
    if msg not in json_users:
        json_users[msg]=conn
    else:
        print("Nome de Utilizador ja em uso")
        return
    sel.register(conn, selectors.EVENT_READ, read)
def sendMsg(sender, to, timemessage, msg, sock):
    sendmsg=encodeJSON(sender,to,timemessage,msg)
    msgsize=str(len(sendmsg))
    msgsize="{:>5}".format(msgsize)
    msgsize=msgsize.encode('utf-8')
    sock.send(msgsize)
    sock.send(sendmsg)
def read(conn, mask):
    nBytes=conn.recv(5)
    if nBytes:
        nBytes=int(nBytes.decode())
        data=conn.recv(nBytes)
        if data:
            print('echoing', repr(data), 'to', conn)
            to, timemessage, msg = decodeJSON(data)
            sender=get_key(conn, json_users)
            if to.split("//")[0]=="channel":
                chan=to.split("//")[1]
                sentlist=chan.split(",")
                for i in sentlist:
                    if i in channels:
                        for user in channels[i]:
                            if conn not in channels[i]:
                                channels[i].append(conn)
                            if user != conn:
                                to="channel//"+i
                                sendMsg(sender, to, timemessage, msg, user)
                    else:
                        channels[i]=[conn]
                        sender="Sender"
                        to=get_key(conn, json_users)
                        msg="Channel "+i+" criado com sucesso."
                        sendMsg(sender, to, timemessage, msg, conn)
            else:
                sentlist=to.split(",") # case contains multiple persons to send..
                for i in sentlist:
                    if i not in json_users:
                        sendErrorMessage(conn,i)
                        print("User not Found!")
                        continue
                    if i != get_key(conn, json_users):
                        sendMsg(sender,i,timemessage,msg, json_users[i])   
    else:
        print('closing', conn)
        rmvkey=get_key(conn, json_users)
        json_users.pop(rmvkey)
        temparr=[]
        for ch in channels:
            if conn in channels[ch]:
                channels[ch].remove(conn)
                if len(channels[ch])==0:
                    temparr.append(ch)    
        for i in temparr:
            del channels[i]   
        sel.unregister(conn)
        conn.close()

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 5001               # Arbitrary non-privileged port

sock = socket.socket()
sock.bind((HOST, PORT))
sock.listen(100)
#sock.setblocking(False)
sel.register(sock, selectors.EVENT_READ, accept)
while True:
    events = sel.select()
    for key, mask in events:
        callback = key.data
        callback(key.fileobj, mask)