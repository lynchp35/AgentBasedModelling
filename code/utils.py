import random
from Person import NewBorn

def spread_covid(infected_personID, population, catching_covid_probability, newly_infected, IDsquared):
    """
    This function checks if there are any people within the infection radius of an infected person.
    If they are, there is a probability that they also become infected. 
    """

    for personID in population:
        # Checks if person is not already infected, then if they are within the radius
        if population[personID].infected != 1 and personID not in newly_infected and within_radius(population[personID], population[infected_personID], IDsquared):
            # Decrease chance of getting covid by half if the person has recovered from covid
            catching_covid_probability = catching_covid_probability if population[personID].infected == 0 else (catching_covid_probability*0.5)
            if catching_covid_probability > random.random():
                newly_infected.append(personID)
    return newly_infected

def update_newly_infected(newly_infected, population, infected):
    """
    This function is used to update the population with the newly infected people.
    """

    for personID in newly_infected:
        # Infection status 1, number of days infected 0
        try:
            population[personID].infected = 1

            infected[personID] = 0
        except KeyError:
            print(personID)
    return population, infected

def update_infected_dict(personID, population, infected):

    """
    This function is used to increase the infected persons day counter and 
    to check if they have recovered from covid.

    Currently takes a minimum of 14 days to recover and 25% chance of recovering per day after.
    """

    # If person is already infected increase day counter else assign the value of 0
    infected[personID] = infected.get(personID,-1) + 1
    # Become health after two weeks
    if infected.get(personID,0) >= 14 and random.random() > 0.7:
        # Infected value of 2 means recovered, chances of getting sick again reduced 
        population[personID].infected = 2
        infected.pop(personID)
    
    return population, infected

def update_deaths(new_deaths, population, infected):
    """
    This function is used to remove people who have died from covid from:
    -population dict
    -infected dict

    I will add a dead dict for future analysis
    """

    for personID in new_deaths:
        population.pop(personID)
        infected.pop(personID)
    return population, infected

def give_birth(population, personID, newborns, fertility_factor, width, height):
    """
    This function
    """

    # Reduced fertility rate by a factor due to large number of births
    if (population[personID].fertility_rate*fertility_factor) > random.random():
        P = NewBorn()
        # Add to dictionary with the PID as the key
        newborns[P.id] = P
        # Person spawn in random location on the grid
        newborns[P.id].x, newborns[P.id].y = random.uniform(0, width), random.uniform(0, height)
    return newborns

def add_newborns(newborns, population):
    """
    After giving birth newborns are added to the population
    """
    for personID in newborns:
        population[personID] = newborns[personID]
    
    return population

def clip(a, amin, amax):
    # Bound the person's x,y to the min and max of the grid
    return min(max(amin,a),amax)

def within_radius(person1, person2, IDsquared):
    """Returns True if two people are within the infection radius else False"""
    return IDsquared > (person1.x-person2.x)**2 + (person1.y-person2.y)**2

def return_random_choice(probability_dict):
    """
    Takes a dictionary with a person's characteristics as the keys and the probability as the values.
    Returns a random choice of the characteristics based on the probabilities.  
    """
    return random.choices(list(probability_dict.keys()), weights=list(probability_dict.values()), k=1)[0]