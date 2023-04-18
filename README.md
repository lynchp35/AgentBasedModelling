# Agent Based Modelling Assignment
> Define and implement an Agent Based Model of a virus spread among a group or between groups of people

## About the Project
You can use an Agent based simulator, written in Python and covered during lectures, as a basis of your model (https://github.com/hsayama/PyCX), but you are also free to implement your own programme, in a programming language of choice. The only restrictions is that you cannot use any of the existing ABM frameworks listed in lecture materials and also here e.g. https://github.com/hsayama/PyCX

---
## Model Requirements
Your model needs to satisfy the following properties:
- [ ] A clear documentation outlining the model, its purpose and rules (how) and reasons (why) for underlying agent behaviour, as well as the intended output results of the simulation and the reason for tracking those. Tracking several output results is preferable. The documentation should also report results of running the model under several parameter scenarios and the observed outcomes.
- [ ] The code of the model should be well-structured and documented.
- [x] The model should have an easy to run command-line or GUI that allows for changing the initial values of simulation parameters (the more parameters investigated the better, within reason).
- [x] The model must have a graphical display (2D or 3D) that allows for visual simulation of agent behaviour over time.
- [ ] The model must have the ability to output results as time-based graphs (e.g. number of infected people over time or average vehicle speed over time, etc.).
- [ ] Your documentation should be professional, self-contained i.e. contain all the relevant information and outputs and it should not exceed 8 pages in total (any code can be uploaded on GitLab).
- [ ] Your final submission should contain report with all the details outlined above, link to the code and readme file explaining how to run the simulation.
---
## Project Highlights
1. To simulate a "realistic" scenario we analyzed real data based on the Irish population this includes (code: code/initial_population_stats.py, output: data/person_probabilities.json):
   1. Irish sex distribution (Probability of being female/male).
   2. Irish age distribution (Probability of being a certain age).
   3. Irish female fertility rate by age.
   4. Irish covid mortality rate by age.
   5. Vaccination rates by age including 1 booster as a time-series (**Isn't implemented into the ABM**)
2. code/Person.py script is used to randomly generate a person
   1. This randomly assigns the following features:
      1. Age
      2. Sex
   2. Assigns based on age:
      1. Covid mortality rate
      2. Fertility Rate (If female)
3. code/Person.py script can also generate a newborn if a female give birth.
   1. There is a 50/50 chance of the newborn being female/male.
   2. 100% chance of being 0 years old and having a mortality and fertility rate of 0.
4. Agent-Based Model is simulated in the code/model.py script, this includes the following:
   1. initialize:
      1. Randomly generates a population of size N using the Person class and the statistics found in part 1 and randomly places them inside the simulation.
      2. Assigns n people in the population as infected.
   2. observe:

---
### Recommended Steps:

1. Pass

---
## Project Directory Structure
```
./
├── .git
├── .gitignore
└── code
|    ├── initial_population_statistics.py
|    ├── Person.py
|    ├── model.py
|    ├── utils.py
|    └── ETC
└── Data
    ├── CSO_birthRate_2020.csv
    ├── CSO_census_2016.csv
    ├── CSO_vaccinationRate_2021_2023.csv
    ├── HSPC_covidDeath_2020_2023.csv
    ├── initial_population_characteristics.json
    └── vaccination_stats.csv
```
 
 Data can be found through the links below:
 1. [CSO 2020 Birth Data](https://data.cso.ie/table/VSA36)
 2. [CSO 2016 Census Data](https://data.cso.ie/table/E3001)
 3. [CSO 2021-2023 Vaccination Data](https://data.cso.ie/table/E3001)
 4. [HSPC 2020-2023 Covid Data](https://www.hpsc.ie/a-z/respiratory/coronavirus/novelcoronavirus/surveillance/covid-19deathsreportedinireland/COVID-19_Death_Report_Website_v1.8_06032023.pdf)
 