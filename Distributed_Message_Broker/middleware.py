from enum import Enum
import socket
import selectors
import json
import pickle
import xml.etree.ElementTree as ET
from broker import Broker

class MiddlewareType(Enum):
    CONSUMER = 1
    PRODUCER = 2

class Queue:
    def __init__(self, topic, type=MiddlewareType.CONSUMER, port=8000):
        self.topic = topic
        self.HOST = 'localhost'     # Address of the message broker 
        self.PORT = int(port)            # The same port as used by the message broker
        self.s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.HOST, self.PORT))
        self.type=type
        serialization=str(self.__class__.__name__).encode('utf-8') #Get the class name, because it's the serial. mechanism
        msgsize='{:>5}'.format(str(len(serialization))).encode()
        self.s.send(msgsize)
        self.s.send(serialization)
        if self.type==MiddlewareType.CONSUMER:
            #subscribe to the topic passed as a command line argument, for example : --type weather or --type /
            self.subscribe(self.topic)

    def push(self, value):
        print(value)
        self.sendMsg('PUBLISH', value)
    def pull(self):
        nBytes2=self.s.recv(5)
        nBytes2=int(nBytes2.decode('utf-8'))
        data = self.s.recv(nBytes2)
        #receives info from broker
        if data:
            method,topic,msg=self.decode(data)
            if method=="LIST_ACK" or method=="LIST_NACK":
                msg=msg.replace("\\n","\n").replace("\\t","\t")
                topic=topic.replace("\\n","\n")
            return topic, msg
        else:
            return topic, "No data :("   

    def subscribe(self,topic):
        self.sendMsg('SUBSCRIBE',topic)    
    def sendMsg(self, method, data):
        #send message to Broker encoding the method ( operation to be done),the topic to be processed and the message
        data=self.encode(method,self.topic,data)
        #send message size before the message itself..
        msgsize=str(len(data))
        msgsize="{:>5}".format(msgsize)
        msgsize=msgsize.encode('utf-8')
        self.s.send(msgsize)
        self.s.send(data)
    def cancelSub(self,topic):
        self.sendMsg('CANCEL_SUB',topic)
    def listTopics(self):
        self.sendMsg('LIST','')
        
class JSONQueue(Queue):
    def __init__(self, topic, type=MiddlewareType.CONSUMER, port=8000):  
        super().__init__(topic, type, port)
    def decode(self, data):
        data=data.decode('utf-8')
        msg=json.loads(data)
        op=msg['method']
        topic=msg['topic']
        msg=msg['msg']
        return op,topic,msg  
    def encode(self, method, topic,msg):
        init={'method':method,'topic':topic,'msg':msg}
        init=json.dumps(init)
        init=init.encode('utf-8')
        return init   

class XMLQueue(Queue):
    def __init__(self, topic, type=MiddlewareType.CONSUMER, port=8000):
        super().__init__(topic, type, port)
    def encode(self,method,topic,msg):
        init={'method':method,'topic':topic,'msg':msg}
        init=('<?xml version="1.0"?><data method="%(method)s" topic="%(topic)s"><msg>%(msg)s</msg></data>' % init)
        init=init.encode('utf-8')
        return init
    def decode(self,data):
        init=data.decode('utf-8')
        init=ET.fromstring(init)
        init2=init.attrib
        op=init2['method']
        topic=init2['topic']
        msg=init.find('msg').text
        return op,topic,msg

class PickleQueue(Queue):
    def __init__(self, topic, type=MiddlewareType.CONSUMER,port=8000):
        super().__init__(topic, type, port)
    def encode(self,method, topic,msg):
        init={'method':method,'topic':topic,'msg':msg}
        init=pickle.dumps(init)
        return init
    def decode(self,data):
        msg=pickle.loads(data)
        op=msg['method']
        topic=msg['topic']
        msg=msg['msg']
        return op,topic,msg