import sys
import os

import pandas as pd
import yaml

homedir = ""
FILE_ERROR_MESSAGE = 'CANNOT FIND THE FILE'

# Get info from yaml
def get_yml(filename):
    check = True
    folder_pass = homedir + 'yml/'
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
def get_scenario(scenario, fleet, ship_types, fleet_type):
    start_year = scenario['sim_setting']['start_year']
    end_year = scenario['sim_setting']['end_year']

    ship_initial = [0] * len(ship_types)
    annual_growth = [0] * len(ship_types)
    ship_age = [0] * len(ship_types)
    ship_size = [0] * len(ship_types)
    for h in range(len(ship_types)):
        ship_initial[h] = fleet[ship_types[h]]['initial_number']
        annual_growth[h] = fleet[ship_types[h]]['annual_growth']
        ship_age[h] = fleet[ship_types[h]]['ship_age']
        ship_size[h] = fleet[ship_types[h]]['ship_size']

    sim_years = len(list(range(start_year, end_year+1)))
    NumofShip = [[0] * sim_years for _ in range(len(ship_types))]
    num_newbuilding_ship = [[0] * sim_years for _ in range(len(ship_types))]
    Scrap = [[0] * sim_years for _ in range(len(ship_types))]
    for h in range(len(ship_types)):
        for i in range (sim_years):
            if i == 0:
                NumofShip[h][i] = ship_initial[h]
            elif i > 10 and fleet_type == 'domestic': # To Be Deleted
                NumofShip[h][i] = NumofShip[h][i-1]
            else:
                NumofShip[h][i] = int(NumofShip[h][i-1] * annual_growth[h])
            
            Scrap[h][i]= int(ship_initial[h]/ship_age[h]) if i <= ship_age[h] else num_newbuilding_ship[h][i-ship_age[h]]
            num_newbuilding_ship[h][i] = NumofShip[h][i] + Scrap[h][i] - NumofShip[h][i-1] if i>0 else int(ship_initial[h]/ship_age[h])

    columns = ['year', 'ship_id', 'year_built', 'ship_type', 'DWT', 'berthing', 'navigation', 'monitoring', 'config', 'is_operational', 'misc', 'owner']    
    current_fleet = pd.DataFrame(columns=columns)

    ship_id = 0
    for h in range(len(ship_types)):
        for i in range(ship_age[h]):
            for j in range(ship_initial[h]//ship_age[h]):
                ship_id += 1
                new_row = pd.Series({'year': start_year, 'ship_id': ship_id, 'year_built': start_year-ship_age[h]+i, 'ship_type': ship_types[h], 'DWT': ship_size[h], 'berthing': 0, 'navigation': 0, 'monitoring': 0, 'config': 'NONE', 'is_operational': True, 'misc': 'default', 'owner': 'default'})
                current_fleet.loc[len(current_fleet)] = new_row

    num_newbuilding_year = list(range(start_year, end_year+1))
    num_newbuilding = [0] * len(ship_types)
    for h in range(len(ship_types)):
        temp = pd.DataFrame({'year': num_newbuilding_year, 'DWT': ship_size[h], 'ship': num_newbuilding_ship[h]})
        if h == 0:
            num_newbuilding = temp
        else:
            num_newbuilding = pd.concat([num_newbuilding, temp])

    return current_fleet, num_newbuilding, ship_age, ship_size


def set_scenario(start_year, end_year, economy, safety, estimated_loss, subsidy_randd, subsidy_adoption, TRL_regulation, Manu_loop, Ope_loop_TRL, Ope_loop_Safety):
    with open(homedir + "yml/scenario.yml", "w") as yf:
        yaml.dump({
            "sim_setting": {
                "start_year": start_year, 
                "end_year": end_year
            },
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
            }
        }, yf, default_flow_style=False)


def save_uploaded_file(uploaded_file, save_folder):
    file_path = os.path.join(save_folder, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path
