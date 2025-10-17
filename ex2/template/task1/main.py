import os
import time
import threading
import random
import math

HEARTBEAT_INTERVAL = 0.5 #leader sends heatbeat every 0.5s
HEARTBEAT_TIMEOUT  = 1.0 #timeout cap if no heartbeat is detected of followers
BACKOFF_MIN, BACKOFF_MAX = 1.0, 3.0 #waiting time before starting as a candidate
VOTE_COLLECTION_WINDOW = 2.0 #waining time to collect votes


nodes = []
buffer = {} # items are in the form 'node_id': [(msg_type, value)]

class Node:
    def __init__(self,id):
        buffer[id] = []
        self.id = id
        self.working = True
        self.state = 'unknown'
        self.lastHeartbeat = time.time() #use now time so it new node does not instantly start a voting
        self._lastHbSent = 0.0 #0 to imediately send a heatbeat if node becomes leader
        self.hasVoted = False
        self.voteCount = 0
        self.electionEnd = None #used to show no voting active and used to count with now+2s
        self.backoffDeadline = None #random value on how long one has to wait to start voting
        self.seenForeignCandidacy = False #if we see another candidacy during backoff, we don't start our own candidacy

    #each node starts with follower status and starts checking with heartbeat if a leader exists. 
    #daemon = True to make the threads not blockthe exit of the code
    def start(self):
        print(f'node {self.id} started')
        self.state = 'follower'
        self.hasVoted = False
        self.voteCount = 0
        self.lastHeartbeat = time.time()
        threading.Thread(target=self.run, daemon=True).start()

    def run(self):
        while True:
            while buffer[self.id]:
                msg_type, value = buffer[self.id].pop(0)
                if self.working: 
                    self.deliver(msg_type,value)
            time.sleep(0.1)

            if self.working:
                now = time.time()

                if self.state == 'leader':
                    if now - self._lastHbSent >= HEARTBEAT_INTERVAL:
                        self.broadcast('heartbeat', {'leader_id': self.id})
                        self._lastHbSent = now

                elif self.state == 'follower':
                    if now - self.lastHeartbeat > HEARTBEAT_TIMEOUT:
                        if self.backoffDeadline is None:
                            delay = random.uniform(BACKOFF_MIN, BACKOFF_MAX)
                            self.backoffDeadline = now + delay
                            self.seenForeignCandidacy = False
                        if self.backoffDeadline is not None and now >= self.backoffDeadline and not self.seenForeignCandidacy:
                            self.state = 'candidate'
                            self.voteCount = 0
                            self.electionEnd = now + VOTE_COLLECTION_WINDOW
                            self.backoffDeadline = None
                            self.hasVoted = False
                            self.broadcast('candidacy', {'candidate_id': self.id})
                            self.broadcast('vote', {'voter_id': self.id, 'candidate_id': self.id})
                            self.voteCount += 1

                elif self.state == 'candidate':
                    if self.electionEnd is not None and now >= self.electionEnd:
                        need = majority(len(nodes))
                        if self.voteCount >= need:
                            self.state = 'leader'
                            self._lastHbSent = 0.0
                            self.broadcast('leader', {'leader_id': self.id})
                        else:
                            self.state = 'follower'
                            self.hasVoted = False
                            self.voteCount = 0
                            self.electionEnd = None
                            self.backoffDeadline = None
                            self.seenForeignCandidacy = False
                            self.lastHeartbeat = time.time()

            time.sleep(0.1)

    def broadcast(self, msg_type, value):
        if self.working:
            for node in nodes:
                buffer[node.id].append((msg_type,value))
    
    def crash(self):
        if self.working:
            self.working = False
            buffer[self.id] = []
            self.state = 'crashed'
    
    def recover(self):
        if not self.working:
            buffer[self.id] = []
            self.working = True
            self.state = 'follower'
            self.hasVoted = False
            self.voteCount = 0
            self.electionEnd = None
            self.backoffDeadline = None
            self.seenForeignCandidacy = False
            self.lastHeartbeat = time.time()

    def deliver(self, msg_type, value):
        now = time.time()
        if msg_type == 'heartbeat':
            self.lastHeartbeat = now
            if self.state in ('follower','candidate'):
                self.state = 'follower'
                self.hasVoted = False
                self.voteCount = 0
                self.electionEnd = None
                self.backoffDeadline = None
                self.seenForeignCandidacy = False
        elif msg_type == 'candidacy':
            cand = value['candidate_id']
            if cand != self.id:
                self.seenForeignCandidacy = True
                if self.state == 'follower' and not self.hasVoted:
                    self.hasVoted = True
                    self.broadcast('vote', {'voter_id': self.id, 'candidate_id': cand})
        elif msg_type == 'vote':
            if self.state == 'candidate' and self.electionEnd is not None:
                if value.get('candidate_id') == self.id:
                    self.voteCount += 1
        elif msg_type == 'leader':
            leader_id = value['leader_id']
            if leader_id == self.id:
                self.state = 'leader'
                self._lastHbSent = 0.0
            else:
                self.state = 'follower'
                self.hasVoted = False
                self.voteCount = 0
                self.electionEnd = None
                self.backoffDeadline = None
                self.seenForeignCandidacy = False
                self.lastHeartbeat = now

#a new leader needs more that half of the votes to become leader.
def majority(n: int) -> int:
    return math.floor(n/2) + 1

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
