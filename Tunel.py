"""
Solution to the one-way tunnel
"""
import time
import random
from multiprocessing import Lock, Condition, Process, Manager
from multiprocessing import Value

SOUTH = "north"
NORTH = "south"

NCARS = 100

class Monitor():
    def __init__(self,manager):
        self.mutex = Lock()
        self.manager = manager
        self.waiting = self.manager.list()
        self.pasa_n = Condition(self.mutex)
        self.pasa_s = Condition(self.mutex)
    
    def more_waiting_n(self):
        num_north = self.waiting.count(NORTH)
        num_south = self.waiting.count(SOUTH)
        return num_north >= num_south
    
    def more_waiting_s(self):
        return not self.more_waiting_n


    def wants_enter(self, direction):
        self.mutex.acquire()
        self.waiting.append(direction)
        if direction == NORTH:
            self.pasa_n.wait_for(self.more_waiting_n)
        else:
            self.pasa_s.wait_for(self.more_waiting_s)
        self.mutex.release()

    def leaves_tunnel(self, direction):
        self.mutex.acquire()
        self.mutex.release()

def delay(n=3):
    time.sleep(random.random()*n)

def car(cid, direction, monitor):
    print(f"car {cid} direction {direction} created")
    delay(6)
    print(f"car {cid} heading {direction} wants to enter")
    monitor.wants_enter(direction)
    print(f"car {cid} heading {direction} enters the tunnel")
    delay(3)
    print(f"car {cid} heading {direction} leaving the tunnel")
    monitor.leaves_tunnel(direction)
    print(f"car {cid} heading {direction} out of the tunnel")



def main():
    manager = Manager()
    monitor = Monitor(manager)
    cid = 0
    for _ in range(NCARS):
        direction = NORTH if random.randint(0,1)==1  else SOUTH
        cid += 1
        p = Process(target=car, args=(cid, direction, monitor))
        p.start()
        time.sleep(random.expovariate(1/0.5)) # a new car enters each 0.5s
        
''' hola '''