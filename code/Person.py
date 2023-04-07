import json
import random

class Person():
    """
    This class set ups the initial values for agents in our system.
    """
    global PersonID
    PersonID = 1
    def __init__(self, sex_probability:dict, age_probability:dict, fertility_rate:dict, mortality_rate:dict) -> None:
        global PersonID
        self.id = PersonID
        # Assigns a random age and sex based on the Irish population census data
        self.age = return_random_choice(age_probability) 
        self.sex = return_random_choice(sex_probability)
        # Assigns the fertility_rate, mortality_rate based on the average for a person that age.
        self.fertility_rate = 0 if self.sex == "Male" else fertility_rate.get(self.age, 0)
        self.mortality_rate = mortality_rate.get(self.age, 0)

        # Covid Variables
        self.vaccinated = 0 # unvaccinated, vaccinated, one booster = 0, 1, 2
        self.infected = 0 # uninfected, is infected, was infected = 0, 1, 2
        
        # Position of Person in grid
        self.x = random.uniform(0, 999)
        self.y = random.uniform(0, 999)

        # Other variables ? mobility?
        # self.mobility = could be a random int or a fixed variable

        
        
        PersonID += 1
    
    def __str__(self):
        return f"Person {self.id} is a {self.age} year old {self.sex}.\n\
They have the fertility_rate {self.fertility_rate} and the mortality_rate {self.mortality_rate}\n"

class NewBorn(Person):
    """
    NewBorn is a subclass of Person and inheritance from the Person class.
    The range of characteristics is more limited. 
    50/50 chance of being male/female.
    100% chance of being 0 years old and having a fertility and mortality rate of 0. 
    """
    def __init__(self) -> None:
         super().__init__(sex_probability={"Female":0.5, "Male":0.5}, 
                          age_probability={0:1}, 
                          fertility_rate={0:0}, 
                          mortality_rate={0:0})

def return_random_choice(probability_dict):
    """
    Takes a dictionary with a person's characteristics as the keys and the probability as the values.
    Returns a random choice of the characteristics based on the probabilities.  
    """
    return random.choices(list(probability_dict.keys()), weights=list(probability_dict.values()), k=1)[0]


if __name__ == "__main__":
    print("Testing Person class")

    # Importing population_characteristics
    input_file = open("../data/person_probabilities.json", "r")
    population_characteristics = json.load(input_file)
    input_file.close()

    population = {}
    # Creating 10 people
    for i in range(10):
        P = Person(**population_characteristics)
        print(P)
        population[P.id] = P
    
    print("New Born:")
    P = NewBorn()
    print(P)
    population[P.id] = P
    
    #print(population)
