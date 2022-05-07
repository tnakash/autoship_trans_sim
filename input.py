import pandas as pd
import yaml

import random
import sys

homedir = ""
FILE_ERROR_MESSAGE = 'CANNOT FIND THE FILE'
UNCERTAINTY = 0

# Get info from yaml
def get_yml(filename):
    check = True
    folder_pass = homedir + 'yml/' #  cost/' # Google Colab用に変更
    while check:
        try:
            with open(folder_pass + filename + ".yml") as yml:
                dic_yml = yaml.load(yml,Loader = yaml.SafeLoader)
            check = False
        except:
            print(FILE_ERROR_MESSAGE)
            sys.exit()

    return dic_yml

# Set scenario by yaml
def get_scenario(scenario):
    column = ['Year', 'NumofShip', 'Newbuilding', 'Scrap']
    
    ship_initial = scenario['ship_demand']['initial_number']
    annual_growth = scenario['ship_demand']['annual_growth']
    ship_age = scenario['ship_age']
    start_year = scenario['sim_setting']['start_year']
    end_year = scenario['sim_setting']['end_year']

    Year = list(range(start_year, end_year+1))
    sim_years = len(Year)
    
    NumofShip = [0] * sim_years
    num_newbuilding_ship = [0] * sim_years
    Scrap = [0] * sim_years
    for i in range (sim_years):
        NumofShip[i] = int(NumofShip[i-1] * annual_growth) + random.randint(-UNCERTAINTY,UNCERTAINTY) if i>0 else ship_initial
        Scrap[i]= int(ship_initial/ship_age) if i <= ship_age else num_newbuilding_ship[i-ship_age]
        num_newbuilding_ship[i] = NumofShip[i] + Scrap[i] - NumofShip[i-1] if i>0 else int(ship_initial/ship_age)
    
    current_fleet = pd.DataFrame({'year': range(start_year-ship_age, start_year), 
                                  'config0': [ship_initial//ship_age] * ship_age,
                                  'config1': [0] * ship_age,
                                  'config2': [0] * ship_age,
                                  'config3': [0] * ship_age,
                                  'config4': [0] * ship_age,
                                  'config5': [0] * ship_age,
                                  'config6': [0] * ship_age,
                                  'config7': [0] * ship_age,
                                  'config8': [0] * ship_age,
                                  'config9': [0] * ship_age,
                                  'config10': [0] * ship_age,
                                  'config11': [0] * ship_age})

    num_newbuilding_year = list(range(start_year, end_year+1))
    num_newbuilding = pd.DataFrame({'year': num_newbuilding_year, 'ship': num_newbuilding_ship})

    return current_fleet, num_newbuilding

def set_scenario(casename, start_year, end_year, initial_number, annual_growth, ship_age):
    # with open(homedir + "yml/scenario/scenario_"+casename+".yml", "w") as yf: # Google Colab用に変更
    with open(homedir + "yml/scenario.yml", "w") as yf: # Google Colab用に変更
        yaml.dump({
            "sim_setting": {
                "start_year": start_year, 
                "end_year": end_year
            },
            "ship_demand": {
                "initial_number": initial_number,
                "annual_growth": annual_growth
            },
            "ship_age": ship_age
        }, yf, default_flow_style=False)

def set_tech(tech_integ_factor, integ_b, ope_safety_b, ope_TRL_factor, rd_need_TRL, randd_base, acc_reduction_full):
    # with open(homedir + "yml/scenario/scenario_"+casename+".yml", "w") as yf: # Google Colab用に変更
    with open(homedir + "yml/tech.yml", "w") as yf: # Google Colab用に変更
        yaml.dump({
            "Berth": {
                "min_cost": 34000, 
                "TRL_ini": 6,
                "accident": 96
            },
            "Navi": {
                "min_cost": 34000, 
                "TRL_ini": 3,
                "accident": 78
            },
            "Moni": {
                "min_cost": 136000, 
                "TRL_ini": 4,
                "accident": 32
            },
            "Others": {
                "tech_integ_factor": tech_integ_factor,
                "integ_a": 725333, # not in use
                "integ_b": integ_b,
                "ope_max": 10000, # [times (year*ship)] not in use
                "manu_max": 150, # [times (ship)] not in use
                "ope_safety_b": ope_safety_b, # ope_max -> 1/2
                "ope_TRL_factor": ope_TRL_factor, # [USD/times]
                "rd_TRL_factor": 1, # [USD/y]
                "rd_need_TRL": rd_need_TRL, # [USD/TRL]
                "randd_base": randd_base, # [USD/y]
                "acc_reduction_full": acc_reduction_full # Human Erron Rate [-]
            }
        }, yf, default_flow_style=False)
