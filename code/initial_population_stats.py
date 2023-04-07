import random
import numpy as np
import pandas as pd
import json

class CollectProbabilities():

    """
    This class finds the following probabilities:
    - Sex: a dictionary with the probability of Male and Female
    - Age: a dictionary with the probability of a person being a certain age [0-85]
    - Fertility: a dictionary with the probability of a female becoming pregnant by age [15-45]

    All the probabilities calculated are based on csv files downloaded from the CSO website
    """

    def __init__(self)-> None:
        # Read CSO data
        self.census_data = pd.read_csv("../data/CSO_census_2016.csv")[["Age Group","Sex","VALUE"]]
        self.birth_data = pd.read_csv("../data/CSO_birthRate_2020.csv")[["Age Group of Mother","VALUE"]].rename(
            columns={"Age Group of Mother":"Age Group"})
        # Read HSPC data
        self.death_data = pd.read_csv("../data/HSPC_covidDeath_2020_2023.csv")[["Age Group","VALUE"]]
        
        self.total_population = self.census_data["VALUE"].sum()

        # Calculate the probability dictionary
        self.find_sex_probability()
        self.find_age_probability()
        self.find_fertility_rate()
        self.find_mortality_rate()

        # Save the dictionaries as a single JSON file
        self.save_dictionaries()

    def find_sex_probability(self) -> None:
        # Finds the probability of a person being female or male (rounded to 4 decimal places)
        # Sex Count
        self.sex_probability = (self.census_data.groupby("Sex").sum()[["VALUE"]]/self.total_population).to_dict()["VALUE"]
        # Sex Probability
        self.sex_probability["Female"] =  np.round(self.sex_probability["Female"],4)
        self.sex_probability["Male"] =  np.round(1 - self.sex_probability["Female"],4)

    def find_age_dict(self, dataframe:pd.DataFrame) -> dict:
        # This function takes in a dataframe and returns a dictionary with the age as the key and count as the value.
        age_dict = {}
        # Group by age
        for age_group, value in zip(dataframe.groupby("Age Group").sum()[["VALUE"]].index, dataframe.groupby("Age Group").sum()[["VALUE"]].values):
            # CSO stores the data in age groups e.g. 10 - 14 years
            years = age_group.split(" - ")
            if len(years) > 1: 
                # example values: start_age, end_age = 10, 14
                start_age, end_age = int(years[0]), int(years[1].split(" ")[0])
                age_gap = (end_age + 1) - start_age
                # Uniform distribution for ages in the age range
                for age in range(start_age, end_age + 1):
                    age_dict[age] = value[0]/age_gap
            else: # Some age groups are in a different format e.g. 45 years or older
                age = int(years[0].split(" ")[0])
                # example value: assigning the full count of 45 years or older to the 45
                age_dict[age] = value[0]
        return age_dict

    def find_age_probability(self) -> None:
        """
        This function calculates the probability of a person being a certain age [0-85].
        It does this by getting the number of people for each possible age and dividing by the total population.
        """
        self.age_probability = {}
        # The count for each age.
        self.population_by_age_dict = self.find_age_dict(self.census_data)
        for age, value in self.population_by_age_dict.items():
            self.age_probability[age] = np.round((value / self.total_population),4)

    def find_fertility_rate(self)-> None:
        """
        This function calculates the fertility probability of a female at different ages [15-45].
        It does this by getting the number of birth for each possible age and dividing by the number of females that age.
        """
        # The count of females at different ages.
        age_dict = self.find_age_dict(self.census_data[self.census_data["Sex"] == "Female"])
        # The 2020 birth counts per age.
        births_per_age = self.find_age_dict(self.birth_data)
        self.fertility_rate = {}
        for age in age_dict.keys():
            # The fertility_rate per age, returns 0 if their wasn't any births for the age
            self.fertility_rate[age] = np.round((births_per_age.get(age, 0) / age_dict.get(age)),4)

    def find_mortality_rate(self) -> None:
        """
        This function calculates the mortality probability of a person at different ages [0-85].
        It does this by getting the number of death people for each possible age and dividing by the total population of that age.
        """
        self.mortality_rate = {}
        # The count for each age.
        age_dict = self.find_age_dict(self.death_data)
        for age, value in self.population_by_age_dict.items():
            self.mortality_rate[age] = np.round((age_dict.get(age, 0) / value),10)

    def save_dictionaries(self):
        # Create a super-dictionary, the previous dictionaries as sub-dictionaries
        complete_probabilities = {"sex_probability":self.sex_probability,
                                "age_probability":self.age_probability,
                                "fertility_rate":self.fertility_rate,
                                "mortality_rate":self.mortality_rate,
                                }
        # Save dictionary to a json file
        output_file = open('../data/person_probabilities.json', 'w', encoding='utf-8')
        json.dump(complete_probabilities, output_file, indent=4)
        output_file.close()

def convert_to_datetime(x):
    return pd.to_datetime(x)

def find_vaccination_stats():
    # Read vaccine data, convert nulls to 0 and divide by 100 to get it as a fraction.
    vaccination_rate = pd.read_csv("../data/CSO_vaccinationRate_2021_2023.csv").groupby(["Statistic Label", "Month", "Age Group"])[["VALUE"]].mean().fillna(0) / 100

    # Reformat index to convert month to datetime format
    vaccination_rate.index = vaccination_rate.reindex(
    [(vaccine_type, convert_to_datetime(month), age_group) for vaccine_type, month, age_group in zip(
    vaccination_rate.index.get_level_values(0),
    vaccination_rate.index.get_level_values(1),
    vaccination_rate.index.get_level_values(2))]).index

    separated_vaccine = pd.DataFrame(index=pd.date_range(start="2020-01-01", end="2023-02-01", freq="MS"))

    short_hand_dict = {"Primary Course Completed":"V1",
                "Booster 1":"V2",
                "5 - 11 years":"11-",
                "12 years and over":"12+"}
            
    for vaccine_type in ["Primary Course Completed", "Booster 1"]:
        for age_group in ["5 - 11 years", "12 years and over"]:
            separated_vaccine = separated_vaccine.join(
                vaccination_rate.loc[vaccine_type,:, age_group].sort_index().rename(
                columns={"VALUE":f"{short_hand_dict[vaccine_type]}_{short_hand_dict[age_group]}"}))
    separated_vaccine.fillna(0).to_csv("../data/vaccination_stats.csv", index=True)
    
if __name__ =="__main__":
    # Runs the CollectProbabilities class and saves data to 
    # ../data/person_probabilities.json file 
    CP = CollectProbabilities()
    print("Finished processing population characteristics \nFile saved to \
the file ../data/person_probabilities.json")
    # Reformats vaccination stats and saves the data to 
    # ../data/vaccination_stats.csv
    find_vaccination_stats()
    print("Finished processing vaccination statistics \nFile saved to \
the file ../data/vaccination_stats.csv")
