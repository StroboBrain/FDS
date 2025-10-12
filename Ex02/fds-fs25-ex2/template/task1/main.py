import os
import time
import threading
from enum import Enum
import random

nodes = []
buffer = {} # items are in the form 'node_id': [(msg_type, value)]

class Node:
    class NodeState(Enum):
        FOLLOWER = 1
        CANDIDATE = 2
        LEADER = 3
        # added state CRASHED for clarity
        CRASHED = 4
    
    class MsgType(Enum):
        VOTE_REQUEST = 1
        VOTE = 2
        HEARTBEAT = 3
    
    # rudimentary timekeeper, would be nicer with events
    class Timer():
        def __init__(self, wait_time):
            self.wait_time = wait_time
            self.end_time = time.time() + wait_time
            self.time_limit_exeeded = False

        def set_wait_time(self,new_wait_time):
            self.wait_time = new_wait_time
            self.end_time = time.time() + new_wait_time
            # reset flag when creating a new deadline
            self.time_limit_exeeded = False
        
        def new_wait_time(self):
            self.end_time = time.time() + self.wait_time
            # reset flag for the new deadline
            self.time_limit_exeeded = False

        def check_time_limit_exeeded(self):
            if time.time() > self.end_time:
                self.time_limit_exeeded = True
            return self.time_limit_exeeded
    
    class VoteTimer():
        def __init__(self):
            self.vote_time_duration = 2

        def start(self):
            self.start_time = time.time()

        def vote_time_exceeded(self):
            return (time.time() - self.start_time) >= self.vote_time_duration
    
    class VoteCounter():
        def __init__(self):
            self.votes = 0
            self.other_votes = 0

        def add_vote(self):
            self.votes += 1
        
        def add_other_vote(self):
            self.other_votes += 1
        
        def has_won(self):
            total = self.votes + self.other_votes
            # wins if strictly more than half of observed votes
            return self.votes > total // 2

        def reset(self):
            self.votes = 0
            self.other_votes = 0
    

    class HeartbeatTimerTimeOutCounter():
        def __init__(self):
            self.timeout_limit = 1.0
            self.last_heartbeat = time.time()
            self.timeout_reached = False
        
        def set_heartbeat_timer(self):
            # reset last heartbeat and clear timeout flag
            self.last_heartbeat = time.time()
            self.timeout_reached = False

        def check_heartbeat_time_exceeded(self):
            if (time.time() - self.last_heartbeat) >= self.timeout_limit:
                self.timeout_reached = True
            return self.timeout_reached
        
    class RandomWaitTimer():
        def __init__(self, min_wait, max_wait):
            self.min_wait = min_wait
            self.max_wait = max_wait
            self.wait_time_duration = 0
            self.generate_random_waittime()            
            
        def generate_random_waittime(self):
            self.wait_time_duration = random.uniform(self.min_wait, self.max_wait)
            return self.wait_time_duration
    
        def return_random_waittime(self):
            return self.generate_random_waittime()

    # Node __init
    def __init__(self,id):
        buffer[id] = []
        self.id = id
        self.working = True
        # initial state
        self.reset_node()

    
    def start(self):
        print(f'node {self.id} started')
        threading.Thread(target=self.run, daemon=True).start()
    
    def reset_node(self):
        self.state = self.NodeState.FOLLOWER
        self.vote_timer = self.VoteTimer()
        self.vote_counter = self.VoteCounter()
        self.heartbeat_timer = self.HeartbeatTimerTimeOutCounter()
        self.random_wait_timer = self.RandomWaitTimer(1.0,3.0)
        self.time_out_detected = False
        self.is_voting = False
        # keeps track of the time between waves
        self.heartbeat_wave_maker = self.Timer(0.5)
        self.vote_delay = self.Timer(1.0)
        
    def run(self):
        while True:
            while buffer[self.id]:
                msg_type, value = buffer[self.id].pop(0)
                if self.working:
                    self.deliver(msg_type,value)
            if self.working:
                if self.NodeState.LEADER == self.state:
                    if self.heartbeat_wave_maker.check_time_limit_exeeded():
                        self.heartbeat_wave_maker.new_wait_time()
                        self.broadcast_heartbeat()
                # logic for non leaders
                elif not self.is_voting:
                    if self.heartbeat_timer.check_heartbeat_time_exceeded() and not self.time_out_detected:
                        self.time_out_detected = True
                        random_waittime = self.random_wait_timer.generate_random_waittime()
                        self.vote_delay.set_wait_time(random_waittime)
                    if self.time_out_detected and self.vote_delay.check_time_limit_exeeded():
                        self.is_voting = True
                        self.start_voting()
            time.sleep(0.1)

    def broadcast(self, msg_type, value):
        if self.working:
            for node in nodes:
                buffer[node.id].append((msg_type,value))
    
    def crash(self):
        if self.working:
            self.working = False
            buffer[self.id] = []
            # change state to crashed
            self.state = self.NodeState.CRASHED
    
    def recover(self):
        if not self.working:
            buffer[self.id] = []
            self.working = True
            # upon recovery, reset the node
            self.reset_node()

    def deliver(self, msg_type, value):
        match msg_type:
            case self.MsgType.VOTE_REQUEST:
                self.handle_vote_request(value)    
                pass
            case self.MsgType.VOTE:
                self.handle_vote(value)
                pass
            case self.MsgType.HEARTBEAT:
                self.heartbeat(value)
    
    def handle_vote_request(self, value):
        # leader ignores vote request, that might still be in the system
        if self.working and self.state != self.NodeState.LEADER:
            self.is_voting = True
            # vote for the candidate
            self.vote(value)
    
    def handle_vote(self, value):
        # when a VOTE message arrives to non leaders, it votes
        if value == self.id:
            self.vote_counter.add_vote()
            # ignore other votes, when already the leader            
            if self.state!= self.NodeState.LEADER and self.vote_counter.has_won():
                self.state = self.NodeState.LEADER
                self.is_voting = False
                self.time_out_detected = False
                self.heartbeat_timer.set_heartbeat_timer()
                print(f'node {self.id} became leader')
                self.broadcast_heartbeat()
        else:
            self.vote_counter.add_other_vote()

    def heartbeat(self, value):
        if self.working and self.state != self.NodeState.LEADER:
            # stop being a candidate
            self.state = self.NodeState.FOLLOWER
            self.is_voting = False
            self.time_out_detected = False
            # reset heartbeat
            self.heartbeat_timer.set_heartbeat_timer()
    
    def vote(self, candidate_id):
        if candidate_id < self.id:
            # vote for the smaller-id candidate
            self.broadcast(self.MsgType.VOTE, candidate_id)
            print(f'node {self.id} voted for candidate {candidate_id}') 
        else:
            # actually become candidate (stay candidate)
            self.state = self.NodeState.CANDIDATE
            self.broadcast(self.MsgType.VOTE, self.id)
            if candidate_id == self.id:
                print(f'I love myself and voted {self.id}')
            else:
                print(f'node {self.id} voted for {candidate_id}')
    
    def broadcast_heartbeat(self):
        # Only working leaders can broadcast a heartbeat
        if self.working and self.state == self.NodeState.LEADER:
            self.broadcast(self.MsgType.HEARTBEAT, self.id)
    
    def start_voting(self):
        self.vote_counter.reset()
        self.vote_timer.start()
        self.broadcast(self.MsgType.VOTE_REQUEST, self.id)
        print(f"{self.id} started a vote")


def initialize(N):
    global nodes
    nodes = [Node(i) for i in range(N)]
    for node in nodes:
        node.start()

if __name__ == "__main__":
    os.system('clear')
    N = 4
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