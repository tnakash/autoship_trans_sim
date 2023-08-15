import random
import sys

import pandas as pd
import yaml

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
    # column = ['Year', 'NumofShip', 'Newbuilding', 'Scrap']
    
    ship_initial = scenario['ship_demand']['initial_number']
    annual_growth = scenario['ship_demand']['annual_growth']
    ship_age = scenario['ship_age']
    start_year = scenario['sim_setting']['start_year']
    end_year = scenario['sim_setting']['end_year']
    
    # config_list = ['NONE', 'B', 'N1', 'N2', 'M', 'BN1', 'BN2', 'BM', 'N1M', 'N2M', 'BN1M', 'FULL']
    
    sim_years = len(list(range(start_year, end_year+1)))    
    NumofShip = [0] * sim_years
    num_newbuilding_ship = [0] * sim_years
    Scrap = [0] * sim_years
    for i in range (sim_years):
        NumofShip[i] = int(NumofShip[i-1] * annual_growth) + random.randint(-UNCERTAINTY,UNCERTAINTY) if i>0 else ship_initial
        Scrap[i]= int(ship_initial/ship_age) if i <= ship_age else num_newbuilding_ship[i-ship_age]
        num_newbuilding_ship[i] = NumofShip[i] + Scrap[i] - NumofShip[i-1] if i>0 else int(ship_initial/ship_age)
    
    # current_fleet = pd.DataFrame({'year': range(start_year-ship_age, start_year), 
    #                               config_list[0]: [ship_initial//ship_age] * ship_age,
    #                               config_list[1]: [0] * ship_age,
    #                               config_list[2]: [0] * ship_age,
    #                               config_list[3]: [0] * ship_age,
    #                               config_list[4]: [0] * ship_age,
    #                               config_list[5]: [0] * ship_age,
    #                               config_list[6]: [0] * ship_age,
    #                               config_list[7]: [0] * ship_age,
    #                               config_list[8]: [0] * ship_age,
    #                               config_list[9]: [0] * ship_age,
    #                               config_list[10]: [0] * ship_age,
    #                               config_list[11]: [0] * ship_age})

    ship_size = scenario['ship_size']
    columns = ['year', 'ship_id', 'year_built', 'DWT', 'berthing', 'navigation', 'monitoring', 'config', 'is_operational', 'misc', 'owner']    
    current_fleet = pd.DataFrame(columns=columns)
    ship_id = 0
    for i in range(ship_age):
        for j in range(ship_initial//ship_age):
            ship_id += 1
            new_row = pd.Series({'year': start_year, 'ship_id': ship_id, 'year_built': start_year-ship_age+i, 'DWT': ship_size, 'berthing': 0, 'navigation': 0, 'monitoring': 0, 'config': 'NONE', 'is_operational': True, 'misc': 'default', 'owner': 'default'})
            # current_fleet = pd.concat([current_fleet, new_row], ignore_index=True)
            current_fleet.loc[len(current_fleet)] = new_row

    num_newbuilding_year = list(range(start_year, end_year+1))
    num_newbuilding = pd.DataFrame({'year': num_newbuilding_year, 'ship': num_newbuilding_ship})

    return current_fleet, num_newbuilding

def set_scenario(start_year, end_year, initial_number, annual_growth, ship_age, economy, safety, estimated_loss, subsidy_randd, subsidy_adoption, TRL_regulation, Manu_loop, Ope_loop_TRL, Ope_loop_Safety, ship_size):
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
            "ship_age": ship_age,
            "Operator": {
                "economy": economy,
                "safety": safety,
                "estimated_loss": estimated_loss
            },
            "Regulator": {
                "subsidy_randd": subsidy_randd,
                "subsidy_adoption": subsidy_adoption,
                "TRL_regulation": TRL_regulation
            },
            "Loop": {
                "Manu_loop": Manu_loop,
                "Ope_loop_TRL": Ope_loop_TRL,
                "Ope_loop_Safety": Ope_loop_Safety
            },
            "ship_size": ship_size,
        }, yf, default_flow_style=False)

def set_tech(ope_safety_b, ope_TRL_factor):
    with open(homedir + "yml/tech.yml", "w") as yf: # Google Colab用に変更
        yaml.dump({
            "Berth": {
                "min_cost": 34000, 
                "TRL_ini": 6,
                "accident": 0.0064
            },
            "Navi": {
                "min_cost": 34000, 
                "TRL_ini": 3,
                "accident": 0.0094
            },
            "Moni": {
                "min_cost": 136000, 
                "TRL_ini": 4,
                "accident": 0.029
            },
            "Others": {
                "tech_integ_factor": 1.33,
                "integ_a": 725333, # not in use
                "integ_b": 0.05,
                "ope_max": 10000, # [times (year*ship)] not in use
                "manu_max": 150, # [times (ship)] not in use
                "ope_safety_b": ope_safety_b, # ope_max -> 1/2
                "ope_TRL_factor": ope_TRL_factor, # [USD/times]
                "rd_TRL_factor": 1, # [USD/y]
                "rd_need_TRL": 20000000, # [USD/TRL]
                "randd_base": 0, # [USD/y]
                "acc_reduction_full": 0.8 # Human Erron Rate [-]
            }
        }, yf, default_flow_style=False)
