import json
from Person import Person, NewBorn, return_random_choice
from pylab import *
import numpy as np

width = 200
height = 200

initial_population = 300
initial_covidrate = 0.01

mortality_factor = 5 # Increase the probability of someone dying by 2
covid_spread_factor = 10 # Increase the chances of getting covid by 10

catching_covid_probability = 0.05

initial_infectionDistance = 4
IDsquared = initial_infectionDistance ** 2
NoiseLevel = 4

fontdict={"size":8}

# Importing population_characteristics used to generate a population with similar statistics as the Irish population
input_file = open("../data/person_probabilities.json", "r")
population_characteristics = json.load(input_file)
input_file.close()

def initialize():
    global time, population, dead_population, infected, hdata, idata, bdata, ddata

    time = 0
    # Health/Infected/Births/Deaths population throughout time 
    hdata, idata, bdata, ddata = [], [], [], []
    
    population, dead_population, infected = {}, {}, {}

    # Used to random give people in the population covid, 0 = not infected, 1 = infected
    initial_covid_probability = {0:1.0-initial_covidrate,
                                 1:initial_covidrate}
    for i in range(initial_population):
        # Create person using Person class in Person.py file
        P = Person(**population_characteristics)
        # Add to dictionary with the PID as the key
        population[P.id] = P
        # Person spawn in random location on the grid
        population[P.id].x, population[P.id].y = uniform(0, width), uniform(0, height)
        # Randomly assign covid to people in the population based on the covid rate
        population[P.id].infected = return_random_choice(initial_covid_probability)
    
def observe():
    global population, hdata, idata, bdata, ddata
    subplot(3, 1, 1)
    cla()
    # Plot scatterplot by healthy/infected
    health_x = []
    health_y = []
    infected_x = []
    infected_y = []
    if population != {}:
        for ag in population.values():
            if ag.infected == 0:
                health_x.append(ag.x)
                health_y.append(ag.y)
            else:
                infected_x.append(ag.x)
                infected_y.append(ag.y)
        if len(health_x) > 0:
            scatter(health_x, health_y, color = 'green')
        if len(infected_x) > 0:
            scatter(infected_x, infected_y, color = 'blue')
        legend({"Health":"green", "Infected":"blue"})
    
    # Plot a timeseries of number of health/infected
    ax1 = subplot(3, 1, 2)
    cla()
    ax2 = ax1.twinx()

    ax1.set_xlabel('Days Since Patient Zero', fontdict=fontdict)
    ax1.set_ylabel('Number of Health', color='g', fontdict=fontdict)
    ax2.set_ylabel('Number of Infected', color='b', fontdict=fontdict)
    ax1.plot(hdata, 'g-')
    ax2.plot(idata, 'b-')

    # Plot a timeseries of deaths/births
    ax1 = subplot(3, 1, 3)
    cla()
    ax2 = ax1.twinx()

    ax1.set_xlabel('Days Since Patient Zero', fontdict=fontdict)
    ax1.set_ylabel('Number of Births', color='red', fontdict=fontdict)
    ax2.set_ylabel('Number of Deaths', color='black', fontdict=fontdict)
    ax1.plot(np.array(bdata).cumsum(), 'r-')
    ax2.plot(np.array(ddata).cumsum())


def clip(a, amin, amax):
    # Bound the person's x,y to the min and max of the grid
    return min(max(amin,a),amax)

def update():
    global time, population, infected, newly_infected, hdata, idata, bdata, ddata, mortality_factor

    time += 1
    hdata.append(0)
    idata.append(0)
    new_deaths = []
    newly_infected = []
    new_borns = {}
    # simulate random motion
    for personID in population:
        # Random movement
        population[personID].x += normal(0, NoiseLevel)
        population[personID].y += normal(0, NoiseLevel)
        population[personID].x = clip(population[personID].x, 0, width)
        population[personID].y = clip(population[personID].y, 0, height)
        if population[personID].infected == 0:
            hdata[-1] += 1
            # If healthy the person has a chance of giving birth based on fertility rates by age
            new_borns = give_birth(personID, new_borns)
        else: # Infected
            idata[-1] += 1
            spread_covid(personID) # Checks if people are close to the infected person to catch covid
            if (population[personID].mortality_rate * mortality_factor) > random(): # Chance of person with covid dying
                dead_population[personID] = population[personID]
                new_deaths.append(personID)
            else:
                update_infected_dict(personID) # Increase infected day counter and become health again
        
    bdata.append(len(new_borns))
    ddata.append(len(new_deaths))
    update_agent(new_borns,new_deaths,newly_infected)

def update_infected_dict(personID):
    global population, infected, newly_infected
    # If person is already infected increase day counter else assign the value of 0
    infected[personID] = infected.get(personID,-1) + 1
    # Become health after two weeks
    if infected[personID] >= 14 and random() > 0.75:
        population[personID].infected = 0
        infected.pop(personID)

def spread_covid(infected_personID):
    global population, infected, covid_spread_factor
    for personID in population:
        if population[personID].infected == 0 and personID not in newly_infected and within_radius(population[personID], population[infected_personID]):
            if (catching_covid_probability *covid_spread_factor) > random():
                newly_infected.append(personID)

def update_agent(new_borns,new_deaths,newly_infected):
    add_newborns(new_borns)
    update_deaths(new_deaths)
    update_newly_infected(newly_infected)

def update_deaths(new_deaths):
    global population, infected
    for personID in new_deaths: # Remove new deaths from population
        population.pop(personID)
        infected.pop(personID)

def update_newly_infected(newly_infected):
    global population, infected
    for personID in newly_infected:
        population[personID].infected = 1
        infected[personID] = 0

def give_birth(personID, new_borns):
    # Reduced fertility rate by a factor 2 due to large number of births
    if (population[personID].fertility_rate/2) > random():
        P = NewBorn()
        # Add to dictionary with the PID as the key
        new_borns[P.id] = P
        # Person spawn in random location on the grid
        new_borns[P.id].x, new_borns[P.id].y = uniform(0, width), uniform(0, height)
    return new_borns
    
def add_newborns(new_borns):
    """
    After giving birth new borns are added to the population
    """
    global population
    for personID in new_borns:
        population[personID] = new_borns[personID]

def within_radius(person1, person2):
    """Returns True if two people are within the infection radius else False"""
    return IDsquared > (person1.x-person2.x)**2 + (person1.y-person2.y)**2

# Adjustable parameters below

def population (val = initial_population):
    '''
    Number of particles.
    Make sure you change this parameter while the simulation is not running,
    and reset the simulation before running it. Otherwise it causes an error!
    '''
    global initial_population
    initial_population = int(val)
    return val

def starting_covid_rate (val = initial_covidrate):
    '''
    Number of particles.
    Make sure you change this parameter while the simulation is not running,
    and reset the simulation before running it. Otherwise it causes an error!
    '''
    global initial_covidrate
    initial_covidrate = float(val)
    return val

def mortalityFactor (val = mortality_factor):
    '''
    Number of particles.
    Make sure you change this parameter while the simulation is not running,
    and reset the simulation before running it. Otherwise it causes an error!
    '''
    global mortality_factor
    mortality_factor = float(val)
    return val

def covidSpreadFactor (val = covid_spread_factor):
    '''
    Number of particles.
    Make sure you change this parameter while the simulation is not running,
    and reset the simulation before running it. Otherwise it causes an error!
    '''
    global covid_spread_factor
    covid_spread_factor = float(val)
    return val

def infection_radius(val = initial_infectionDistance):
    '''
    Number of particles.
    Make sure you change this parameter while the simulation is not running,
    and reset the simulation before running it. Otherwise it causes an error!
    '''
    global IDsquared
    IDsquared = float(val)**2
    return val
    
# Code to run simulation
import pycxsimulator
pycxsimulator.GUI(parameterSetters = [population, 
                                      starting_covid_rate, 
                                      mortalityFactor, 
                                      covidSpreadFactor,
                                      infection_radius]
                                      ).start(func=[initialize, observe, update])