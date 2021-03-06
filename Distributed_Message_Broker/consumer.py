import sys
import argparse
import middleware
import time
class Consumer:
    def __init__(self, datatype, port):
        self.type = datatype
        self.port = port
        self.queue = middleware.XMLQueue(f"/{self.type}", middleware.MiddlewareType.CONSUMER, port)

    @classmethod
    def datatypes(self): 
        return ["temp", "msg", "weather","/"]    

    def run(self, length=10):
        try:
            self.queue.listTopics()
            while True:
                topic, data = self.queue.pull()
                print(topic,data)
        except KeyboardInterrupt:
                self.queue.cancelSub(self.queue.topic)        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", help="type of producer: [temp, msg, weather,/]", default="temp")
    parser.add_argument("--port",help="port of broker",default=8000)
    args = parser.parse_args()

    if args.type not in Consumer.datatypes():
        print("Error: not a valid producer type")
        sys.exit(1)

    p = Consumer(args.type, args.port)

    p.run()