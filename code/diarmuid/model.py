import matplotlib
import os
import numpy as np
import scipy
import pycxsimulator
from pylab import *

# population parameters
def populationSize(n=1000):
    '''Returns the initial population size'''
    return int(n)

def numInfected(n=5):
    '''Returns the initial number of infected people'''
    return int(n)

def infectionRate(p=0.4):
    '''Returns the initial infection rate'''
    return float(p)

def recoveryRate(p=0.2):
    '''Returns the initial recovery rate'''
    return float(p)

# simulation parameters
def width(n=500):
    '''Returns the grid width'''
    return int(n)

def height(n=500):
    '''Returns the grid height'''
    return int(n)
    
def infectionDistance(n=10):
    '''Returns the infection proximity'''
    return int(n)

infectionDistanceSquared = infectionDistance() ** 2

# agents state variables
uninfected = 0
infected = 1
recovered = 2

# to be removed from the simulation
toBeRemoved = -1

def initialize():
    global time, agents
    
    time = 0
    
    # initialize agents
    agents = []
    for i in range(populationSize()):
        if i < numInfected():
            state = infected
        else:
            state = uninfected
        agents.append([uniform(0, width()), uniform(0, height()), state, 0])

def observe():
    cla()
    uninfectedX = [ag[0] for ag in agents if ag[2] == uninfected]
    uninfectedY = [ag[1] for ag in agents if ag[2] == uninfected]
    infectedX = [ag[0] for ag in agents if ag[2] == infected]
    infectedY = [ag[1] for ag in agents if ag[2] == infected]
    recoveredX = [ag[0] for ag in agents if ag[2] == recovered]
    recoveredY = [ag[1] for ag in agents if ag[2] == recovered]
    scatter(uninfectedX, uninfectedY, color = 'cyan')
    scatter(infectedX, infectedY, color = 'red')
    scatter(recoveredX, recoveredY, color = 'green')
    axis('scaled')
    axis([0, width(), 0, height()])
    title('t = ' + str(time))

def clip(a, amin, amax):
    if a < amin: return amin
    elif a > amax: return amax
    else: return a

def update():
    global time, agents

    time += 1

    # simulate random motion
    for ag in agents:
        ag[0] += normal(0, 1)
        ag[1] += normal(0, 1)
        ag[0] = clip(ag[0], 0, width())
        ag[1] = clip(ag[1], 0, height())

    # detect infection and change state
    x, y = 0, 1
    for i in range(len(agents)):
        if agents[i][2] == infected:
            for j in range(len(agents)):
                if agents[j][2] == uninfected and (agents[i][x]-agents[j][x])**2 + (agents[i][y]-agents[j][y])**2 < infectionDistanceSquared:
                    if random() < infectionRate():
                        agents[j][2] = infected
                        agents[j][3] = time

        if agents[i][2] == infected and random() < recoveryRate():
            agents[i][2] = recovered

    # remove "toBeRemoved" agents
    while toBeRemoved in [ag[2] for ag in agents]:
        for ag in agents:
            if ag[2] == toBeRemoved:
                agents.remove(ag)
                break

parameters = [
    # Simulation parameters
    height, width, populationSize, numInfected,
    infectionDistance, infectionRate, recoveryRate
]
pycxsimulator.GUI(parameterSetters=parameters).start(func=[initialize, observe, update])