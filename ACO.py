#convergent
#Autor: Oliver Nemček

class Point:
    def __init__(self, name, x, y, distances, pheromones):
        self.name = name
        self.distances = distances
        self.pheromones = pheromones
        self.x = x
        self.y = y

class Ant:
    visitedPoints = []
    currentPoint = 0
        
    def __init__(self, startingPoint):
        self.currentPoint = startingPoint
        self.visitedPoints = []
        self.visitedPoints.append(self.currentPoint)
    def move(self):
        totalSum = 0
        generated = np.random.rand()
        probabilities = {}
        for distance in self.currentPoint.distances.items():                        #vypocita celkovy pocet vzdialenosti a feromonov na okolitych cestach
            #iba pre body ktore este neboli navstivene
            visited = False
            for visitedPoint in self.visitedPoints:
                if visitedPoint.name == distance[0]:
                    visited = True
                    break
            
            if not visited:
                totalSum += ((1/distance[1]) ** BETA) * (self.currentPoint.pheromones[distance[0]] ** ALPHA)      

        for distance in self.currentPoint.distances.items():                        #vypocite pravdepodobnosti zvolenia jednotlivych ciest
            #iba pre body ktore este neboli navstivene
            visited = False
            for visitedPoint in self.visitedPoints:
                if visitedPoint.name == distance[0]:
                    visited = True
                    break
            
            if not visited:
                probability = ((1/distance[1]) ** BETA) * (self.currentPoint.pheromones[distance[0]] ** ALPHA) / totalSum
                probabilities[distance[0]] = probability
            else:
                probabilities[distance[0]] = 0                                      #ak uz bod bol navstiveny

        # Vyberie cestu podla pravdepodobnosti
        combinedProbabilities = 0
        for probability in probabilities.items():
            combinedProbabilities += probability[1]
            if generated < combinedProbabilities:                                  #bola zvolena cesta
                #print("moving from ", self.currentPoint.name, " to ", probability[0])
                self.currentPoint = getPointByName(probability[0])
                self.visitedPoints.append(self.currentPoint)
                break
        
        if(combinedProbabilities == 0):
            #ak uz navstivil vsetky body, vrati sa na zaciatocny bod
            #print("moving from ", self.currentPoint.name, " to ", self.visitedPoints[0].name)
            self.currentPoint = self.visitedPoints[0]           
            self.visitedPoints.append(self.currentPoint)

    def apply_pheromones(self):
        #vypocita celkovu prejdenu vzdialenost mravenca
        i = 0
        distanceTravelled = 0
        while i < len(self.visitedPoints) - 1:
            distanceTravelled += self.visitedPoints[i].distances[self.visitedPoints[i+1].name]
            i+= 1

        #prida prislusne mnozstvo feromonov na trasy medzi bodmi
        pheromones = PHEROMONE_COUNT
        i = 0
        while i<len(self.visitedPoints) - 1:        #prida feromony na cestu medzi aktualnym a nasledujucim bodom (pre obidva body)
            #self.visitedPoints[i].pheromones[self.visitedPoints[i+1].name] += pheromones * self.visitedPoints[i].distances[self.visitedPoints[i+1].name] / distanceTravelled
            #self.visitedPoints[i+1].pheromones[self.visitedPoints[i].name] += pheromones * self.visitedPoints[i+1].distances[self.visitedPoints[i].name] / distanceTravelled
            self.visitedPoints[i].pheromones[self.visitedPoints[i+1].name] += pheromones / distanceTravelled
            self.visitedPoints[i+1].pheromones[self.visitedPoints[i].name] += pheromones / distanceTravelled
            #print("added ", pheromones / distanceTravelled, " pheromones to path between", self.visitedPoints[i].name, " and ", self.visitedPoints[i+1].name)
            i+=1

def getPointByName(name):
    for point in points:
        if name == point.name:
            return point
    return False

def singleAntCycle(antsCount):
    ants = []
    for i in range(0, antsCount):
        ants.append(Ant(random.choice(points)))

    j = 0
    for j in range(0, len(points)):
        for ant in ants:
            ant.move()

    for ant in ants:
        ant.apply_pheromones()
        ant.visitedPoints = []

    evaporatePheromones()


#po kazdom cykle zmensi pocet feromonov o EVAPORATION_RATE
def evaporatePheromones():
    l = 0
    while l < len(points):
        m = 0
        while m < len(pheromones):
            points[l].pheromones[chr(m+65)] = points[l].pheromones[chr(m+65)] * (1 - EVAPORATION_RATE)
            m += 1
        l += 1



import numpy as np
import sys
import random
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib import pyplot as plt, animation


START_PHEROMONES = 0.1
ALPHA = 4
BETA = 1
EVAPORATION_RATE = 0.01
PHEROMONE_COUNT = 10
ITERATION_COUNT = 3000

graph=nx.Graph()

#argument parse
input = sys.argv[1].replace(" ", "").replace("[", " ").replace("]", " ").replace(",", ' ').split()

if len(input)%2 != 0:
    print("Invalid number of parameters")
    exit(0)

inputPoints = []
i = 0
while i < len(input):
    point=[]
    point.append(float(input[i]))
    point.append(float(input[i+1]))
    inputPoints.append(point)
    i+=2

i = 0
points = []
for point in inputPoints:                #vytvorenie objektov pre jednotlive body grafu
    distances = {}
    pheromones = {}
    j = 0
    while j < len(inputPoints):          #pre vsetky body vypocita vzdialenost a zada zaciatocne mnozstvo feromonov
        distances[chr(j+65)] = np.sqrt((point[0] - inputPoints[j][0]) ** 2 + (point[1] - inputPoints[j][1]) ** 2)
        pheromones[chr(j+65)] = START_PHEROMONES
        j+=1

    #graph
    graph.add_node(chr(i+65),pos=(point[0], point[1]))
    for pointa in points:
        graph.add_edge(chr(i+65),pointa.name, weight=0.5)

    newPoint = Point(chr(i+65), point[0], point[1], distances, pheromones)
    points.append(newPoint)
    i+=1
    

#program
pheromone_history = []
for i in range(0,ITERATION_COUNT):
    singleAntCycle(1)
    for point in points:
        for pheromone in point.pheromones.values():
            #print(pheromone)
            #print("-------------CYCLE", i)
            pheromone_history.append(pheromone)
            #print(pheromone_history)

#print("--------------------------------")
#print(pheromone_history) #historia urciteho bodu v urcitom cykle

#graph
pos=nx.get_node_attributes(graph,'pos')
weights = nx.get_edge_attributes(graph,'weight').values()

fig = plt.figure()
plt.margins(0)
plt.gca().invert_yaxis()


cycle = 0

def animate(frame):
   global cycle
   global pheromone_history
   if ITERATION_COUNT * (len(points)**2) - len(points) > cycle * len(points)**2 + len(points) ** 2 + len(points):
    #modifikacia width
    fig.clear()
    for i in range(0, len(points)):      #novy bod
            currentPheromones = []
            for j in range(0, len(points)):      #feromony na cestach pre jednotlive body
                currentPheromones.append(pheromone_history[j + len(points) * i + cycle * len(points)**2])
            maxPheromone = max(currentPheromones)           # najvyssia hodnota feromonov pre dany bod
            minPheromone = min(currentPheromones)
            for j in range(0, len(points)):      #feromony na cestach pre jednotlive body
                if chr(i+65) != chr(j+65):
                    print("menim width medzi ", chr(i+65), " a ", chr(j+65), " na hodnotu ", pheromone_history[j + len(points) * i + cycle * len(points)**2] / (maxPheromone/3))
                    graph[chr(i+65)][chr(j+65)]['weight'] = pheromone_history[j + len(points) * i + cycle * len(points)**2] / (maxPheromone/3)
                #print("i ", i, " j ", j, "len points ", len(points), "cycle ", cycle)
                print(j + len(points) * i + cycle * len(points)**2)
            
        

   #print("novy cyklus-------------------------")
   cycle += 1
   weights = nx.get_edge_attributes(graph,'weight').values()
   nx.draw(graph,pos,with_labels=True,node_color="red",node_size=1000,font_color="white",font_size=10,font_family="Times New Roman", width=list(weights),edge_color="black")

ani = animation.FuncAnimation(fig, animate, frames=6, interval=10, repeat=True)

plt.show()