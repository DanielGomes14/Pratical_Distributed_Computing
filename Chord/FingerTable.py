class FingerTable():
        def __init__(self,m,p):
           self.m=m
           self.lst=[(None,None)]*self.m
           self.p=p
           self.counter=1

        def set_succ(self,id,addr):
           self.lst[1]=(id,addr)

        def getFirstEntry(self):
            return self.lst[1]
 
        def getKey(self):
            ith_entry=(self.p+2**(self.counter-1))%1024
            return ith_entry

        def update(self,node_id,node_addr):
            self.lst[self.counter]=(node_id,node_addr)
            self.counter=self.counter+1
            if self.counter==self.m:
                self.counter=1
            
        def finger_get(self, key_hash):
            keys=[x for x in self.lst if x!=(None,None)]
            keys=sorted(keys)
            for i in range(len(keys)-1, -1, -1):
                if keys[i][0] <= key_hash:
                    return keys[i]
            return keys[len(keys)-1]            