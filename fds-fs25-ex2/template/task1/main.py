import enum
import os
import random
import time
import threading


nodes = []
buffer = {} # items are in the form 'node_id': [(msg_type, value)]

class State(enum.Enum):
    Leader = 1
    Follower = 2
    Candidate = 3
    
class Msg_Type(enum.Enum):
    Heartbeat = 1
    Candidacy = 2
    Vote = 3

class Node:
    def __init__(self,id):
        buffer[id] = []
        self.id = id
        self.working = True
        self.voted = False
        self.votesReceived = 0
        #self.state = 'unknown'
        self.state = State.Follower
        self.lastHeartbeatTime = 0
        self.electionStartTime = 0
        self.electionEndTime = 0

    def start(self):
        print(f'node {self.id} started')
        threading.Thread(target=self.run).start()

    def run(self):
        while True:
            #if self.id == 0 and round(time.time()) % 10 == 0:
                #print("Process 0 is working", self.working, "and has status", self.state)
            if self.working:
                while buffer[self.id]:
                    msg_type, value = buffer[self.id].pop(0)
                    #if self.working:
                    self.deliver(msg_type, value)
                if self.state == State.Leader and self.lastHeartbeatTime + 0.5 < time.time():
                    self.broadcast(Msg_Type.Heartbeat, time.time())
                    self.lastHeartbeatTime = time.time()
                elif self.lastHeartbeatTime + 1 < time.time():
                    # Infer that leader crashed. Wait 1-3 seconds, then enter candidacy.
                    if self.state == State.Candidate and self.electionEndTime < time.time() and self.voted:
                        if self.votesReceived / sum([n.isWorking() for n in nodes]) > 0.5:
                            self.state = State.Leader
                            print("node", self.id, "won the election")
                            self.broadcast(Msg_Type.Heartbeat, time.time())
                            self.voted = False
                            self.votesReceived = 0
                    elif self.state == State.Candidate and self.electionStartTime < time.time() and not self.voted:
                        # send candidacy messages
                        self.broadcast(Msg_Type.Candidacy, self.id)
                        print("node", self.id, " broadcasted its candidacy")
                        self.broadcast(Msg_Type.Vote, (self.id, self.id))
                        self.voted = True
                    elif self.state == State.Follower: # start waiting periode for candidacy # self.state == State.Follower
                        self.state = State.Candidate
                        print("node", self.id, "change its state to", self.state)
                        self.electionStartTime = time.time() + random.uniform(1,3)
                        self.electionEndTime = self.electionStartTime + 2
                time.sleep(0.1)
            else:     
                time.sleep(0.25)

    def broadcast(self, msg_type: Msg_Type, value):
        if self.working:
            for node in nodes:
                buffer[node.id].append((msg_type, value))
    
    def crash(self):
        if self.working:
            self.working = False
            self.state = State.Follower
            buffer[self.id] = []
    
    def recover(self):
        if not self.working:
            buffer[self.id] = []
            self.working = True

    def deliver(self, msg_type, value):
        if msg_type == Msg_Type.Heartbeat and not self.state == State.Leader:
            self.lastHeartbeatTime = value
            self.voted = False
            self.votesReceived = 0
            if not self.state == State.Follower:
                self.state = State.Follower
                print("node", self.id, "changed its state to", self.state) 
        elif msg_type == Msg_Type.Candidacy and not value == self.id:
            if not self.voted:
                self.broadcast(Msg_Type.Vote, (self.id, value))  # value == id of candidate
                print("node", self.id, "voted for", value)
                self.voted = True
            self.votesReceived = 0
            self.state = State.Follower
        elif msg_type == Msg_Type.Vote and value[1] == self.id:
            self.votesReceived += 1
    
    def isWorking(self):
        if self.working:
            return 1
        else:
            return 0


def initialize(N):
    global nodes
    nodes = [Node(i) for i in range(N)]
    for node in nodes:
        node.start()

if __name__ == "__main__":
    os.system('clear')
    N = 3
    initialize(N)
    print('actions: state, crash, recover')
    while True:
        act = input('\t$ ')
        if act == 'crash' : 
            id = int(input('\tid > '))
            if 0<= id and id<N: nodes[id].crash()
        elif act == 'recover' : 
            id = int(input('\tid > '))
            if 0<= id and id<N: nodes[id].recover()
        elif act == 'state':
            for node in nodes:
                print(f'\t\tnode {node.id}: {node.state}')

