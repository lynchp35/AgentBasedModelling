import json
from Person import Person
from utils import *
from pylab import *
import numpy as np
import pandas as pd
import os
import sys

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

save_model_data = False

# Importing population_characteristics used to generate a population with similar statistics as the Irish population
input_file = open("../data/person_probabilities.json", "r")
population_characteristics = json.load(input_file)
input_file.close()

def initialize():
    global time, population, infected, hdata, idata, bdata, ddata, death_dict

    time = 0
    # Health/Infected/Births/Deaths population throughout time 
    hdata, idata, bdata, ddata, new_deaths = [], [], [], [], []
    
    population, infected, death_dict = {}, {}, {}

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

    if save_model_data:
        global directory_path, sep
        directory_path = f"..\data\Pop{initial_population}_ICR{initial_covidrate}_Fert{fertility_factor}_Mort{mortality_factor}_CCP{catching_covid_probability}_Dist{initial_infectionDistance}"
        # If folder doesn't exist, then create it.
        try:
            sep = "\\"
            if not os.path.isdir(directory_path):
                os.makedirs(directory_path)
        except:
            sep = "/"
            directory_path = directory_path.replace("\\","/")
            if not os.path.isdir(directory_path):
                os.makedirs(directory_path)
        print("Data saved to the directory : ", directory_path)
        
        create_files(directory_path, sep)

def observe():
    global population, hdata, idata, bdata, ddata
    subplot(2, 2, 1)
    cla()
    # Plot scatterplot by healthy/infected

    if population != {}:
        health_x = [ag.x for ag in population.values() if ag.infected != 1]
        health_y = [ag.y for ag in population.values() if ag.infected != 1]
        infected_x = [ag.x for ag in population.values() if ag.infected == 1]
        infected_y = [ag.y for ag in population.values() if ag.infected == 1]
        if len(health_x) > 0:
            scatter(health_x, health_y, color = 'green')
        if len(infected_x) > 0:
            scatter(infected_x, infected_y, color = 'blue')
        legend({"Health":"green", "Infected":"blue"},loc='upper right')
    
    # Plot a timeseries of number of health/infected
    ax = subplot(2, 2, 2)
    cla()

    ax.set_xlabel('Days Since Patient Zero', fontdict=fontdict)
    ax.plot(hdata, color='g', label='Healthy')
    ax.plot(idata, color='b', label='Infected')
    if len(hdata) != 0: ax.set_ylim(0,max([max(list(hdata)),max(list(idata))]))
    ax.legend(loc='lower right')

    # Plot a timeseries of deaths/births
    ax = subplot(2, 2, 3)
    cla()

    ax.set_xlabel('Days Since Patient Zero', fontdict=fontdict)
    ax.plot(np.array(bdata).cumsum(), 'yellow', label='Births')
    ax.plot(np.array(ddata).cumsum(), 'black', label='Deaths')
    if len(hdata) != 0: ax.set_ylim(0,max([max(np.array(ddata).cumsum()),max(np.array(bdata).cumsum())])+10)
    ax.legend(loc='upper left')

    # Plot a timeseries of deaths/births
    ax = subplot(2, 2, 4)
    cla()

    ax.set_xlabel('Number of Health', color='g', fontdict=fontdict)
    ax.set_ylabel('Number of Infected', color='b', fontdict=fontdict)
    limit = len(population)
    ax.set_xlim(0,limit)
    ax.set_ylim(0,limit)
    ax.plot(hdata, idata, 'cyan')
    if save_model_data:
        global directory_path, sep
        save_files(directory_path, sep, population, death_dict)
    

def update():
    global time, population, infected, newly_infected, hdata, idata, bdata, ddata, mortality_factor, new_deaths, death_dict

    time += 1
    hdata.append(0)
    idata.append(0)
    new_deaths, newly_infected = [], []
    newborns, death_dict = {}, {}
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
                new_deaths.append(personID)
                death_dict[personID] = [population[personID].age, population[personID].vaccinated]
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

def Population (val = initial_population):
    '''
    Adjust the initial population.

    Make sure you change this parameter while the simulation is not running,
    and reset the simulation before running it. Otherwise it causes an error!
    '''
    try:
        global initial_population
        initial_population = int(val)
        return val
    except ValueError:
        print(f"{val} is not an int")


def StartingCovidRate (val = initial_covidrate):
    '''
    Adjust the initial covid rate.
    Expected initial numbers of covid in the population is initial_population * initial_covidrate.

    Make sure you change this parameter while the simulation is not running,
    and reset the simulation before running it. Otherwise it causes an error!
    '''
    try:
        global initial_covidrate
        initial_covidrate = float(val)
        return val
    except ValueError:
        print(f"{val} is not a float")

def MortalityFactor (val = mortality_factor):
    '''
    Change the probability of someone dying by a factor.
    For visual effects this is set greater than 1 so that more people die than expected in the real population.

    Make sure you change this parameter while the simulation is not running,
    and reset the simulation before running it. Otherwise it causes an error!
    '''
    try:
        global mortality_factor
        mortality_factor = float(val)
        return val
    except ValueError:
        print(f"{val} is not a float")


def FertilityFactor (val = fertility_factor):
    '''
    Change the probability of someone giving birth by a factor.
    Due to the naive implementation this value should be < 1 to avoid huge population growth.   
    
    Make sure you change this parameter while the simulation is not running,
    and reset the simulation before running it. Otherwise it causes an error!
    '''
    try:
        global fertility_factor
        fertility_factor = float(val)
        return val
    except ValueError:
        print(f"{val} is not a float")



def CatchingCovidProbability (val = catching_covid_probability):
    '''
    The probability of catching covid if an agent is within the radius of an infected agent.

    Make sure you change this parameter while the simulation is not running,
    and reset the simulation before running it. Otherwise it causes an error!
    '''

    try:
        global catching_covid_probability
        catching_covid_probability = float(val)
        assert(catching_covid_probability <= 1)
        assert(catching_covid_probability >= 0)
        return val
    except ValueError:
        print(f"{val} is not a float")


def InfectionRadius(val = initial_infectionDistance):
    '''
    The maximum distance an agent can catch covid from.

    Make sure you change this parameter while the simulation is not running,
    and reset the simulation before running it. Otherwise it causes an error!
    '''
    try:
        global IDsquared
        IDsquared = float(val)**2
        return val
    except ValueError:
        print(f"{val} is not a float")


def SaveModelData(val=save_model_data):
    '''
    True or False to save the following data:
    - Population
    - 

    Make sure you change this parameter while the simulation is not running,
    and reset the simulation before running it. Otherwise it causes an error!
    '''
    global save_model_data
    if type(val) == str:
        val = eval(val)
    save_model_data = val
    return val
    


# Code to run simulation
import pycxsimulator
pycxsimulator.GUI(parameterSetters = [Population, 
                                      StartingCovidRate, 
                                      MortalityFactor,
                                      FertilityFactor, 
                                      CatchingCovidProbability,
                                      InfectionRadius,
                                      SaveModelData]
                                      ).start(func=[initialize, observe, update])
