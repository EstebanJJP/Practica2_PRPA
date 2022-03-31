"""
Esteban Joaquín Jiménez Párraga
Daniel Carretero Álvarez
Carlos Adolfo Gallego Gallego

Nuestra solución consiste en valorar si un coche en una dirección puede pasar (
viendo que no haya ningún coche en la otra dirección en el túnel) 
y decidir a qué coches da paso, para ello cuenta la cantidad de coches esperando en cada dirección 
y da paso al que tenga más esperando. Con monitores y semáforos nos aseguramos de que se solucione 
la exclusión mutua, además de que no haya problemas de inanición ni de bloqueos pues los coches siempre 
salen y es una solución con relativa justicia pues los coches se ceden el paso según en cual haya 
más esperando hasta la nueva comprobación de cuantos han pasado por el túnel y se han generado durante ese tiempo.
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
        self.in_tunel = self.manager.list()
        self.pasa_n = Condition(self.mutex)
        self.pasa_s = Condition(self.mutex)
    
    def more_waiting_n(self):
        num_north = self.waiting.count(NORTH)
        num_south = self.waiting.count(SOUTH)
        return num_north >= num_south
    
    def more_waiting_s(self):
        return not self.more_waiting_n
    
    def no_s_in_tunel(self):
        return self.in_tunel.count(SOUTH)==0
    
    def no_n_in_tunel(self):
        return self.in_tunel.count(NORTH)==0


    def wants_enter(self, direction):
        self.mutex.acquire()
        self.waiting.append(direction)
        if direction == NORTH:
            self.pasa_n.wait_for(self.more_waiting_n and self.no_s_in_tunel) #SI es tu turno de pasar y PUEDES pasar, pasa
        else:
            self.pasa_s.wait_for(self.more_waiting_s and self.no_n_in_tunel)
        self.waiting.remove(direction)
        self.in_tunel.append(direction)
        self.mutex.release()

    def leaves_tunnel(self, direction):
        self.mutex.acquire()
        self.in_tunel.remove(direction)
        self.pasa_n.notify_all()
        self.pasa_s.notify_all()        
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

if __name__ == '__main__':
    main()
