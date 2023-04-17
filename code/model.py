import json
from Person import Person
from utils import *
from pylab import *
import numpy as np
import pandas as pd
import datetime

# Size of grid
width = 200
height = 200

initial_population = 300
initial_covidrate = 0.01 # Expected number of infected = initial_population*initial_covidrate

fertility_factor = 0.2 # Decrease the probability of a female giving birth 
mortality_factor = 4 # Increase the probability of someone dying by 5

catching_covid_probability = 0.75 # Probability of getting covid if someone near you has it

initial_infectionDistance = 4 # Max distance that you can catch covid from
IDsquared = initial_infectionDistance ** 2
NoiseLevel = 10

fontdict={"size":8} # Font size for plots

start_date = pd.to_datetime("2020-01-01")
vaccination_start_date = pd.to_datetime("2021-01-01")



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
            if ag.infected != 1:
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


def update():
    global time, population, infected, newly_infected, hdata, idata, bdata, ddata, mortality_factor

    time += 1
    hdata.append(0)
    idata.append(0)
    new_deaths, newly_infected = [], []
    newborns = {}
    # simulate random motion
    for personID in population:
        # Random movement
        population[personID].x += normal(0, NoiseLevel)
        population[personID].y += normal(0, NoiseLevel)
        population[personID].x = clip(population[personID].x, 0, width)
        population[personID].y = clip(population[personID].y, 0, height)
        if population[personID].infected == 1: # Infected
            idata[-1] += 1
            newly_infected = spread_covid(personID, population, catching_covid_probability, newly_infected, IDsquared) # Checks if people are close to the infected person to catch covid
            if (population[personID].mortality_rate * mortality_factor) > random(): # Chance of person with covid dying
                dead_population[personID] = population[personID]
                new_deaths.append(personID)
            else:
                # Increase infected day counter and become health again
                population, infected = update_infected_dict(personID, population, infected) 
        else: # Not infected
            hdata[-1] += 1
            # If healthy the person has a chance of giving birth based on fertility rates by age
            newborns = give_birth(population, personID, newborns, fertility_factor, width, height)
           
        # People can get vaccinated after the vaccination_start_date based on data found on the CSO website
        get_vaccinated(personID, population, time, start_date, vaccination_start_date)
            
        
    bdata.append(len(newborns))
    ddata.append(len(new_deaths))
    update_agent(newborns,new_deaths,newly_infected)


def update_agent(newborns,new_deaths,newly_infected):
    """
    This functions updates the following aspects of the population:
    -adds newborns to population
    -removes the dead from the population
    -updates peoples infection status

    It does this through the functions below and defined in utils.py.
    """

    global population, infected
    prior_len = len(population)
    population = add_newborns(newborns, population)
    assert(len(population) == prior_len + len(newborns))

    population, infected = update_newly_infected(newly_infected, population, infected)
    
    prior_len = len(population)
    population, infected = update_deaths(new_deaths, population, infected)
    assert(len(population) == prior_len - len(new_deaths))



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

def fertilityFactor (val = fertility_factor):
    '''
    Number of particles.
    Make sure you change this parameter while the simulation is not running,
    and reset the simulation before running it. Otherwise it causes an error!
    '''
    global fertility_factor
    fertility_factor = float(val)
    return val


def catchingCovidProbability (val = catching_covid_probability):
    '''
    Number of particles.
    Make sure you change this parameter while the simulation is not running,
    and reset the simulation before running it. Otherwise it causes an error!
    '''
    global catching_covid_probability
    catching_covid_probability = float(val)
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
                                      fertilityFactor, 
                                      catchingCovidProbability,
                                      infection_radius]
                                      ).start(func=[initialize, observe, update])