import pandas as pd
import yaml
import itertools

homedir = ""
FILE_ERROR_MESSAGE = 'CANNOT FIND THE FILE'

# Set scenario by yaml
def get_scenario(scenario='scenario_1'):
    check = True
    # folder_pass = 'yml/scenario/'
    folder_pass = homedir + 'yml/scenario/' # Google Colab用に変更
    while check:
        try:
            with open(folder_pass + scenario + ".yml") as yml:
                scenario = yaml.load(yml,Loader = yaml.SafeLoader)
            check = False
        except:
            print(FILE_ERROR_MESSAGE)

    column = ['Year', 'NumofShip', 'Newbuilding', 'Scrap']
    
    ship_initial = scenario['ship_demand']['initial_number']
    annual_growth = scenario['ship_demand']['annual_growth']
    ship_age = scenario['ship_age']
    start_year = scenario['sim_setting']['start_year']
    end_year = scenario['sim_setting']['end_year']

    Year = list(range(start_year, end_year+1))
    sim_years = len(Year)
    
    NumofShip = [0] * sim_years
    Newbuilding = [0] * sim_years
    Scrap = [0] * sim_years    
    for i in range (sim_years):
        NumofShip[i] = int(NumofShip[i-1] * annual_growth) if i>0 else ship_initial
        Scrap[i]= int(ship_initial/ship_age) if i <= ship_age else Newbuilding[i-ship_age]
        Newbuilding[i] = NumofShip[i] + Scrap[i] - NumofShip[i-1] if i>0 else int(ship_initial/ship_age)

    df_demand = pd.DataFrame(zip(Year, NumofShip, Newbuilding, Scrap), columns = column)
    return df_demand, ship_age

# Set cost time series by yaml
def get_cost(Year, cost='cost_1'):
    check = True
    # folder_pass = 'yml/cost/' 
    folder_pass = homedir + 'yml/cost/' # Google Colab用に変更
    while check:
        try:
            with open(folder_pass + cost + ".yml") as yml:
                cost = yaml.load(yml,Loader = yaml.SafeLoader)
            check = False
        except:
            print(FILE_ERROR_MESSAGE)
    
    column = ['Year','Seafarer','ShoreOperator','ExpLoss','CS','Comm','Situ','Plan','Exec','RemOpe','RemMon','Fuel']
    
    sf_cost_initial = cost['seafarer_cost']['initial_number']
    sf_cost_growth = cost['seafarer_cost']['annual_growth']
    so_cost_initial = cost['shore_operator_cost']['initial_number']
    so_cost_growth = cost['shore_operator_cost']['annual_growth']
    loss_initial = cost['exp_loss']['initial_number']
    loss_growth = cost['exp_loss']['annual_growth']
    cs_initial = cost['opex_cyber_security']['initial_number']
    cs_growth = cost['opex_cyber_security']['annual_growth']
    com_initial = cost['opex_communication']['initial_number']
    com_growth = cost['opex_communication']['annual_growth']
    sa_initial = cost['capex_situation_awareness']['initial_number']
    sa_growth = cost['capex_situation_awareness']['annual_growth']
    pl_initial = cost['capex_planning']['initial_number']
    pl_growth = cost['capex_planning']['annual_growth']
    ex_initial = cost['capex_execution']['initial_number']
    ex_growth = cost['capex_execution']['annual_growth']
    ro_initial = cost['capex_remote_operation']['initial_number']
    ro_growth = cost['capex_remote_operation']['annual_growth']
    rm_initial = cost['capex_remote_monitoring']['initial_number']
    rm_growth = cost['capex_remote_monitoring']['annual_growth']
    fc_initial = cost['fuel_cost']['initial_number']
    fc_growth = cost['fuel_cost']['annual_growth']

    sim_years = len(Year)
    Seafarer = [0] * sim_years
    ShoreOperator = [0] * sim_years
    ExpLoss = [0] * sim_years  
    CS = [0] * sim_years
    Comm = [0] * sim_years
    Situ = [0] * sim_years
    Plan = [0] * sim_years
    Exec = [0] * sim_years
    RemOpe = [0] * sim_years
    RemMon = [0] * sim_years   
    Fuel = [0] * sim_years   

    for i in range (sim_years):
        Seafarer[i] = int(Seafarer[i-1] * sf_cost_growth) if i>0 else sf_cost_initial
        ShoreOperator[i] = int(ShoreOperator[i-1] * so_cost_growth) if i>0 else so_cost_initial
        ExpLoss[i] = int(ExpLoss[i-1] * loss_growth) if i>0 else loss_initial
        CS[i] = int(CS[i-1] * cs_growth) if i>0 else cs_initial
        Comm[i] = int(Comm[i-1] * com_growth) if i>0 else com_initial
        Situ[i] = int(Situ[i-1] * sa_growth) if i>0 else sa_initial
        Plan[i] = int(Plan[i-1] * pl_growth) if i>0 else pl_initial
        Exec[i] = int(Exec[i-1] * ex_growth) if i>0 else ex_initial
        RemOpe[i] = int(RemOpe[i-1] * ro_growth) if i>0 else ro_initial
        RemMon[i] = int(RemMon[i-1] * rm_growth) if i>0 else rm_initial
        Fuel[i] = int(Fuel[i-1] * fc_growth) if i>0 else fc_initial
    
    df_cost = pd.DataFrame(zip(Year, Seafarer, ShoreOperator, ExpLoss, CS, Comm, Situ, Plan, Exec, RemOpe, RemMon,Fuel), columns = column)
    return df_cost

# Set spec of each ship by yaml
def get_spec(spec='spec_1'):
    check = True
    # folder_pass = 'yml/spec/' 
    folder_pass = homedir + 'yml/spec/' # Google Colab用に変更
    while check:
        try:
            with open(folder_pass + spec + ".yml") as yml:
                spec = yaml.load(yml,Loader = yaml.SafeLoader)
            check = False
        except:
            print(FILE_ERROR_MESSAGE)

    options = len(spec['SituationAwareness']) * len(spec['Control']) * len(spec['Control']) * len(spec['Remote'])
    column = ['ship_type', 'Control', 'Planning', 'SituationAwareness', 'Remote', 'sec_cost', 'com_cost', 'acc_ratio', 'sa_cost', 'pl_cost', 'ex_cost', 'ro_cost', 'rm_cost', 'num_sf', 'num_so', 'foc']
    
    ship_type = [''] * options
    Control = [''] * options
    Planning = [''] * options
    SituationAwareness = [''] * options
    Remote = [''] * options
    sec_cost = [0] * options
    com_cost = [0] * options
    acc_ratio = [0] * options
    sa_cost = [0] * options
    pl_cost = [0] * options
    ex_cost = [0] * options
    ro_cost = [0] * options
    rm_cost = [0] * options
    num_sf = [0] * options
    num_so = [0] * options
    foc = [0] * options

    CPSR = list(itertools.product(spec['Control'], spec['Planning'], spec['SituationAwareness'],spec['Remote']))
    Control, Planning, SituationAwareness, Remote = [r[0] for r in CPSR], [r[1] for r in CPSR], [r[2] for r in CPSR], [r[3] for r in CPSR]
    
    for i in range(options):
        ship_type[i] = 'ship_' + str(i+1) 
        sec_cost[i] = spec['Control'][Control[i]]['sec_cost']+spec['Planning'][Planning[i]]['sec_cost']+spec['SituationAwareness'][SituationAwareness[i]]['sec_cost']+spec['Remote'][Remote[i]]['sec_cost']-4
        com_cost[i] = spec['Control'][Control[i]]['com_cost']+spec['Planning'][Planning[i]]['com_cost']+spec['SituationAwareness'][SituationAwareness[i]]['com_cost']+spec['Remote'][Remote[i]]['com_cost']-4
        acc_ratio[i] = spec['Control'][Control[i]]['acc_ratio']*spec['Planning'][Planning[i]]['acc_ratio']*spec['SituationAwareness'][SituationAwareness[i]]['acc_ratio']
        sa_cost[i] = spec['SituationAwareness'][SituationAwareness[i]]['sa_cost']
        pl_cost[i] = spec['Planning'][Planning[i]]['pl_cost']
        ex_cost[i] = spec['Control'][Control[i]]['ex_cost']
        ro_cost[i] = spec['Remote'][Remote[i]]['ro_cost']
        rm_cost[i] = spec['Remote'][Remote[i]]['rm_cost']
        num_sf_tmp = spec['Control'][Control[i]]['num_sf']+spec['Planning'][Planning[i]]['num_sf']+spec['SituationAwareness'][SituationAwareness[i]]['num_sf']
        num_so[i] = int(num_sf_tmp*spec['Remote'][Remote[i]]['num_so_ratio'])
        num_sf[i] = num_sf_tmp - num_so[i]
        foc[i] = (1 - (8 - num_sf[i])/200) if num_sf[i] >0 else 0.9 # Assume max seafarer = 8
    
    spec = pd.DataFrame(zip(ship_type, Control, Planning, SituationAwareness, Remote, sec_cost, com_cost, acc_ratio, sa_cost, pl_cost, ex_cost, ro_cost, rm_cost, num_sf, num_so, foc), columns = column)
    return spec

def set_scenario(casename, start_year, end_year, initial_number, annual_growth, ship_age):
    with open(homedir + "yml/scenario/scenario_"+casename+".yml", "w") as yf: # Google Colab用に変更
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

def reset_spec(casename):
    with open(homedir + "yml/spec/spec_"+casename+".yml", "w") as yf: # Google Colab用に変更
        yaml.dump({
            "SituationAwareness": {
                "FullAuto": {
                    "num_sf": 0,
                    "sec_cost": 10,
                    "com_cost": 10,
                    "acc_ratio": 0.5,
                    "sa_cost": 1
                },
                "SemiAuto": {
                    "num_sf": 1,
                    "sec_cost": 3,
                    "com_cost": 3,
                    "acc_ratio": 0.75,
                    "sa_cost": 0.5
                },
                "AsIs": {
                    "num_sf": 2,
                    "sec_cost": 1,
                    "com_cost": 1,
                    "acc_ratio": 1,
                    "sa_cost": 0
                }
            },
            "Planning": {
                "FullAuto": {
                    "num_sf": 0,
                    "sec_cost": 10,
                    "com_cost": 10,
                    "acc_ratio": 0.4,
                    "pl_cost": 1
                },
                "SemiAuto": {
                    "num_sf": 2,
                    "sec_cost": 3,
                    "com_cost": 3,
                    "acc_ratio": 0.6,
                    "pl_cost": 0.5
                },
                "AsIs": {
                    "num_sf": 4,
                    "sec_cost": 1,
                    "com_cost": 1,
                    "acc_ratio": 1,
                    "pl_cost": 0
                }
            },
            "Control": {
                "FullAuto": {
                    "num_sf": 0,
                    "sec_cost": 10,
                    "com_cost": 10,
                    "acc_ratio": 0.5,
                    "ex_cost": 1
                },
                "SemiAuto": {
                    "num_sf": 1,
                    "sec_cost": 3,
                    "com_cost": 3,
                    "acc_ratio": 0.75,
                    "ex_cost": 0.5
                },
                "AsIs": {
                    "num_sf": 2,
                    "sec_cost": 1,
                    "com_cost": 1,
                    "acc_ratio": 1,
                    "ex_cost": 0
                }
            },
            "Remote": {
                "Control": {
                    "num_so_ratio": 1,
                    "sec_cost": 10,
                    "com_cost": 10,
                    "ro_cost": 1,
                    "rm_cost": 0
                },
                "Monitor": {
                    "num_so_ratio": 0.5,
                    "sec_cost": 3,
                    "com_cost": 3,
                    "ro_cost": 0,
                    "rm_cost": 1
                },
                "NaN": {
                    "num_so_ratio": 0,
                    "sec_cost": 1,
                    "com_cost": 1,
                    "ro_cost": 0,
                    "rm_cost": 0
                }
            }
        }, yf, default_flow_style=False)
        