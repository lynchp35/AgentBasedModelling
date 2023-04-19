import random
import datetime
import pandas as pd
import json
from Person import NewBorn

vaccine_data = pd.read_csv("../data/vaccination_stats.csv", index_col=0, parse_dates=[0])

def spread_covid(infected_personID, population, catching_covid_probability, newly_infected, IDsquared):
    """
    This function checks if there are any people within the infection radius of an infected person.
    If they are, there is a probability that they also become infected. 
    """

    for personID in population:
        # Checks if person is not already infected, then if they are within the radius
        if population[personID].infected != 1 and personID not in newly_infected and within_radius(population[personID], population[infected_personID], IDsquared):

            # Decrease chance of getting covid by half if the person has recovered from covid
            covid_factors = 1 if population[personID].infected == 0 else 0.5
            # Probability of getting covid drops if someone is vaccinated or has the booster
            if population[personID].vaccinated == 1:
                covid_factors = covid_factors * 0.4 
            elif population[personID].vaccinated == 2:
                covid_factors = covid_factors * 0.2

            if population[personID].age < 1:
                covid_factors = 0.001
            if (catching_covid_probability * covid_factors) > random.random():
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
    if infected.get(personID,0) >= 14 and random.random() > 0.3:
        # Infected value of 2 means recovered, chances of getting sick again reduced 
        population[personID].infected = 2
        infected.pop(personID)
    
    return population, infected

def get_vaccinated(personID, population, time, start_date, vaccination_start_date):
    current_date = start_date + datetime.timedelta(days=time)
    if current_date >= vaccination_start_date:

        if population[personID].vaccinated == 0: # No vaccination
            vaccine_type = "V1_"
        elif population[personID].vaccinated == 1: # Vaccinated but no booster
            vaccine_type = "V2_"
        else: # Fully vaccinated
            return 
        if population[personID].age >= 12:
            vaccine_type = f"{vaccine_type}12+"
        else:
            vaccine_type = f"{vaccine_type}11-"

        vp = vaccine_data[vaccine_data.index < current_date][vaccine_type][-1]

        vaccination_probability = {population[personID].vaccinated:1-vp,
                                   population[personID].vaccinated+1:vp}
        population[personID].vaccinated = return_random_choice(vaccination_probability)

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

def create_files(directory_path, sep):
    """
    This function takes in a filepath and creates three text files:
    - location, this contains the x,y values for each person split by \n\n for each time point
    - composition, this contains the age of each person in the population split by \n\n for each time point
    - death, this contains the age and vaccine status of each person who die at that time point split by \n\n
    """
    filepath = f"{directory_path}{sep}"
    for filename in ["location", "composition", "death"]:
        # Opens each file and write an empty string to create a blank document
        output_file= open(file=f"{filepath}{filename}_data.txt", mode="w", encoding="utf-8") 
        output_file.write("")
        output_file.close()

def save_files(directory_path, sep, population, death_dict):
    """
    This function is used to write out new data as the simulation runs:
    This contains the data for the files:
    - location, this contains the x,y values for each person split by \n\n for each time point
    - composition, this contains the age of each person in the population split by \n\n for each time point
    - death, this contains the age and vaccine status of each person who die at that time point split by \n\n
    """
    
    filepath = f"{directory_path}{sep}"

    for filename in ["location", "composition", "death"]:
        # Appends to the blank document
        output_file= open(file=f"{filepath}{filename}_data.txt", mode="a", encoding="utf-8")
        if filename == "location":
            for i in range(0,3):
                # Save peoples x, y and split them into three groups, healthy, infected and recovered split by \n
                output_file.write(str([[population[pID].x,population[pID].y] for pID in population if population[pID].infected == i])+"\n")

        elif filename == "composition":
            for sex in ["Female", "Male"]:
                # Save peoples age and split them into two groups, female and male split by \n
                output_file.write(str([population[pID].age for pID in population if population[pID].sex == sex])+"\n")
        else:
            # Save dead peoples age and vaccine status
            output_file.write(str([death_dict[pID] for pID in death_dict])+"\n")
            # output_file.write(str([[population[pID].age, population[pID].vaccinated] for pID in new_deaths if pID in population])+"\n")
        # Used to split time points with an extra \n
        output_file.write("\n")
        output_file.close()

def extract_location_data(path):
    """
    This function is used to extract the location data from the text and store it in an easier to use json format.
    """
    # Read data in from txt file
    output_file= open(file=path, mode="r", encoding="utf-8") 
    data = output_file.read()
    output_file.close()

    reformated_data = {}
    # The three groups used and time points are split by \n\n
    people_type = ["healthy", "infected", "recovered"]
    split_data = data.split("\n\n")
    for time in range(len(split_data)):
        current_data = split_data[time].split("\n")
        reformated_data[time] = {}
        for i in range(3):
            reformated_data[time][people_type[i]] = {"x":[],
                                            "y":[]}
            try:                              
                for point in current_data[i][2:-2].split("], ["):
                    if len(point.split(", ")) > 1:
                        try:
                            reformated_data[time][people_type[i]]["x"].append(float(point.split(", ")[0]))
                            reformated_data[time][people_type[i]]["y"].append(float(point.split(", ")[1]))
                        except ValueError:
                            pass
            except IndexError:
                print(f"Missing data on day {time}, current value {current_data}")
                print(f"May be due to error at the end of the data.")
        updated_path = path[:-3]+"json"
    save_dictionary(updated_path, reformated_data)

def extract_death_data(path):
    """
    This function is used to extract the location data from the text and store it in an easier to use json format.
    """
    # Read data in from txt file
    output_file= open(file=path, mode="r", encoding="utf-8") 
    data = output_file.read()
    output_file.close()

    reformated_data = {"age":[], "vaccinated":[]}
    split_data = data.split("\n\n")
    for i in range(len(split_data)):
        current_data = split_data[i][2:-2].split("], [")
        if len(current_data) > 1:
            for values in current_data:
                age, vaccinated = values.split(", ")
                reformated_data["age"].append(age)
                reformated_data["vaccinated"].append(vaccinated)

    updated_path = path[:-3]+"json"
    save_dictionary(updated_path, reformated_data)

def extract_composition_data(path):
    """
    This function is used to extract the location data from the text and store it in an easier to use json format.
    """
    # Read data in from txt file
    output_file= open(file=path, mode="r", encoding="utf-8") 
    data = output_file.read()
    output_file.close()

    reformated_data = {}
    split_data = data.split("\n\n")
    for i in range(len(split_data)):
        current_data = split_data[i].split("\n")
        if len(current_data) > 1:
            reformated_data[i] = {"female":[age for age in current_data[0][1:-1].split(", ")], 
                            "male":[age for age in current_data[1][1:-1].split(", ")]}

    updated_path = path[:-3]+"json"
    save_dictionary(updated_path, reformated_data)

def save_dictionary(updated_path, data):
    # Save dictionary to a json file
    output_file = open(updated_path, 'w', encoding='utf-8')
    json.dump(data, output_file, indent=4)
    output_file.close()