import pandas as pd

# Later goes to YML file ...
navi_crew_factor = 0.39 # Just to confirm
moni_crew_factor = 0.56
cook_crew_factor = 0.05

mainte_amount = 67000
capex_material_ratio = 0.667

accom_reduce_navi = 0.025 # Just to ßconfirm
accom_reduce_moni = 0.025

num_crew_navi = 4
num_crew_moni = 14
num_crew_cook = 2
num_crew_all = num_crew_navi + num_crew_moni + num_crew_cook

ope_TRL_factor = 0.4 # [USD/times]
rd_TRL_factor = 1 # [USD/y]
rd_need_TRL = 20000000 # [USD/TRL]
randd_base = 1000000 # [USD/y]

berth_pilot_save = 60000 # [USD]
acc_ratio_min = 0.1 # reducing ratio of human error

ope_safety_b = 0.075 # ope_max -> 1/2
ope_max = 10000 # [times (year*ship)]

integ_a = 725333 # [USD]
integ_b = 0.138 # 
tech_integ_factor = 1.2 # MAX
manu_max = 150 # [times (ship)]

TRLgap_semi = 3
acc_reduction_full = 0.9

def calculate_cost(ship_spec, cost, year, tech):

    tech_list = ['Berth', 'Navi', 'Moni']
    crew_list = ['NaviCrew', 'EngiCrew', 'Cook']
    cost_list = ['OPEX', 'CAPEX', 'VOYEX', 'AddCost']
    opex_list = ['crew_cost', 'store_cost', 'maintenance_cost', 'insurance_cost', 'general_cost', 'dock_cost']
    capex_list = ['material_cost', 'integrate_cost', 'add_eq_cost']
    voyex_list = ['port_call', 'fuel_cost_ME', 'fuel_cost_AE']
    addcost_list = ['SCC_Capex', 'SCC_Opex', 'SCC_Personal', 'Mnt_in_port']
    accident_list = ['accident_berth', 'accident_navi', 'accident_moni']

    column = ['year', 'config'] + tech_list + crew_list + opex_list + capex_list + voyex_list + addcost_list + ['subsidy'] + cost_list + accident_list

    years = [year] * len(ship_spec)
    config = [''] * len(ship_spec)
    Berth = [0] * len(ship_spec) #  May change to TECH
    Navi = [0] * len(ship_spec)
    Moni = [0] * len(ship_spec)

    num_navi = [0] * len(ship_spec)       
    num_engi = [0] * len(ship_spec)
    num_cook = [0] * len(ship_spec)
        
    crew_cost = [0] * len(ship_spec)
    store_cost = [0] * len(ship_spec)
    maintenance_cost = [0] * len(ship_spec)
    insurance_cost = [0] * len(ship_spec)
    general_cost = [0] * len(ship_spec)
    dock_cost = [0] * len(ship_spec)

    material_cost = [0] * len(ship_spec)
    integrate_cost = [0] * len(ship_spec)
    add_eq_cost = [0] * len(ship_spec)

    port_call = [0] * len(ship_spec)
    fuel_cost_ME = [0] * len(ship_spec)
    fuel_cost_AE = [0] * len(ship_spec)
    
    SCC_Capex = [0] * len(ship_spec)
    SCC_Opex = [0] * len(ship_spec)
    SCC_Personal = [0] * len(ship_spec)
    Mnt_in_port = [0] * len(ship_spec)
    
    subsidy = [0] * len(ship_spec)

    Capex = [0] * len(ship_spec)
    Opex = [0] * len(ship_spec)
    Voyex = [0] * len(ship_spec)
    AddCost = [0] * len(ship_spec)

    acc_ratio_berth = [0] * len(ship_spec)
    acc_ratio_navi = [0] * len(ship_spec)
    acc_ratio_moni = [0] * len(ship_spec)
    
    for i in range(len(ship_spec)):
        config[i] = 'Config'+str(i)
        Berth[i] = ship_spec[config[i]]['Berth'] #  May change to TECH
        Navi[i] = ship_spec[config[i]]['Navi']
        Moni[i] = ship_spec[config[i]]['Moni']
        
        num_navi[i] = 0 if Navi == 2 else num_crew_navi/2 if Navi == 1 else num_crew_navi
        num_engi[i] = 0 if Moni == 1 else num_crew_moni
        num_cook[i] = 0 if Navi == 2 and Moni == 1 else num_crew_cook
        
        crew_cost[i] = cost['OPEX']['crew_cost'] # May change based on the number
        store_cost[i] = cost['OPEX']['store_cost']
        maintenance_cost[i] = cost['OPEX']['store_cost']
        insurance_cost[i] = cost['OPEX']['store_cost']
        general_cost[i] = cost['OPEX']['store_cost']
        dock_cost[i] = cost['OPEX']['store_cost']
        
        # material_cost[i] = cost['CAPEX']['production_cost'] * capex_material_ratio / ship_age
        # integrate_cost[i] = cost['CAPEX']['production_cost'] * (1-capex_material_ratio) / ship_age
        material_cost[i] = cost['CAPEX']['material_cost']
        integrate_cost[i] = cost['CAPEX']['integrate_cost'] * (1
                          + Berth[i] * (tech.integ_factor[0]-1)
                          + Navi[i] * (tech.integ_factor[1]-1)
                          + Moni[i] * (tech.integ_factor[2]-1))
        add_eq_cost[i] = tech.tech_cost[0] * Berth[i] + tech.tech_cost[1] * Navi[i] + tech.tech_cost[2] * Moni[i]
        
        port_call[i] = cost['VOYEX']['port_call']
        fuel_cost_ME[i] = cost['VOYEX']['fuel_cost_ME']
        fuel_cost_AE[i] = cost['VOYEX']['fuel_cost_AE']
        
        SCC_Capex[i] = 0
        SCC_Opex[i] = 0
        SCC_Personal[i] = 0
        Mnt_in_port[i] = 0
        
        # Hmm... too dirty ...
        acc_ratio_berth[i] = tech.accident_ratio_ini[0]
        acc_ratio_navi[i] = tech.accident_ratio_ini[1]
        acc_ratio_moni[i] = tech.accident_ratio_ini[2]
        
        if Berth[i] == 1:
            port_call[i] -= berth_pilot_save * trl_rate(tech.TRL[0])
            acc_ratio_berth[i] = tech.accident_ratio[0]

        if Navi[i] == 1:
            crew_cost[i] -= cost['OPEX']['crew_cost'] * navi_crew_factor * 0.5 * trl_rate(tech.TRL[1]+TRLgap_semi)
            maintenance_cost[i] -= mainte_amount * num_crew_navi/num_crew_all * 0.5 * trl_rate(tech.TRL[1]+TRLgap_semi)
            material_cost[i] -= cost['CAPEX']['material_cost'] * accom_reduce_navi * 0.5 * trl_rate(tech.TRL[1]+TRLgap_semi)
            integrate_cost[i] -= cost['CAPEX']['integrate_cost'] * accom_reduce_navi * 0.5 * trl_rate(tech.TRL[1]+TRLgap_semi)
            SCC_Capex[i] += cost['AddCost']['SCC_Capex']*0.5
            SCC_Opex[i] += cost['AddCost']['SCC_Opex']*0.5
            SCC_Personal[i] += cost['AddCost']['SCC_Personal']*0.5
            acc_ratio_navi[i] = (tech.accident_ratio_base[1]+tech.accident_ratio[1]) * 0.5  # Need to Change
        elif Navi[i] == 2:
            crew_cost[i] -= cost['OPEX']['crew_cost'] * navi_crew_factor * trl_rate(tech.TRL[1])
            maintenance_cost[i] -= mainte_amount * num_crew_navi/num_crew_all * trl_rate(tech.TRL[1])
            material_cost[i] -= cost['CAPEX']['material_cost'] * accom_reduce_navi * trl_rate(tech.TRL[1])
            integrate_cost[i] -= cost['CAPEX']['integrate_cost'] * accom_reduce_navi * trl_rate(tech.TRL[1])
            SCC_Capex[i] += cost['AddCost']['SCC_Capex']
            SCC_Opex[i] += cost['AddCost']['SCC_Opex']
            SCC_Personal[i] += cost['AddCost']['SCC_Personal']
            acc_ratio_navi[i] = tech.accident_ratio[1]
        
        if Moni[i] == 1:
            crew_cost[i] -= cost['OPEX']['crew_cost'] * moni_crew_factor
            maintenance_cost[i] -= mainte_amount * num_crew_moni/num_crew_all * trl_rate(tech.TRL[2])
            material_cost[i] -= cost['CAPEX']['material_cost'] * accom_reduce_moni * trl_rate(tech.TRL[2])
            integrate_cost[i] -= cost['CAPEX']['integrate_cost'] * accom_reduce_moni * trl_rate(tech.TRL[2])
            Mnt_in_port[i] += cost['AddCost']['Mnt_in_port']
            SCC_Capex[i] += cost['AddCost']['SCC_Capex']
            SCC_Opex[i] += cost['AddCost']['SCC_Opex']
            SCC_Personal[i] += cost['AddCost']['SCC_Personal']
            acc_ratio_moni[i] = tech.accident_ratio[2]
            
        if Navi[i] == 2 and Moni[i] == 1: # Berthing not considered
            crew_cost[i] -= cost['OPEX']['crew_cost'] * cook_crew_factor
    
        Opex[i] = crew_cost[i] + store_cost[i] + maintenance_cost[i] + insurance_cost[i] + general_cost[i] + dock_cost[i] 
        Capex[i] = material_cost[i] + integrate_cost[i] + add_eq_cost[i]
        Voyex[i] = port_call[i] + fuel_cost_ME[i] + fuel_cost_AE[i] 
        AddCost[i] = SCC_Capex[i] + SCC_Opex[i] + SCC_Personal[i] + Mnt_in_port[i]
    
    spec = pd.DataFrame(zip(years, config, Berth, Navi, Moni, num_navi, num_engi, num_cook, 
                            crew_cost, store_cost, maintenance_cost, insurance_cost, general_cost, dock_cost, 
                            material_cost, integrate_cost, add_eq_cost,
                            port_call, fuel_cost_ME, fuel_cost_AE, 
                            SCC_Capex, SCC_Opex, SCC_Personal, Mnt_in_port, subsidy,
                            Opex, Capex, Voyex, AddCost,
                            acc_ratio_berth, acc_ratio_navi, acc_ratio_moni), columns = column)
    
    return spec

def trl_rate(trl):
    a = 1/4 if trl == 7 else 1/2 if trl == 8 else 1 if trl >= 9 else 0
    return a

def get_tech_ini(tech_yml):
    tech_list = ['Berth', 'Navi', 'Moni'] # ideally from yml
    column = ['tech_name', 'tech_cost', 'integ_factor', 'TRL', 'Rexp', 'Mexp', 'Oexp', 'tech_cost_min', 'accident_ratio', 'accident_ratio_base', 'accident_ratio_ini']

    tech_name = [''] * len(tech_list)
    tech_cost = [0] * len(tech_list)
    tech_cost_min = [0] * len(tech_list)
    integ_factor = [0] * len(tech_list)
    TRL = [0] * len(tech_list) #  May change to TECH
    Rexp = [0] * len(tech_list)
    Mexp = [0] * len(tech_list)
    Oexp = [0] * len(tech_list)
    accident_ratio_ini = [0] * len(tech_list)
    accident_ratio_base = [0] * len(tech_list)
    accident_ratio = [0] * len(tech_list)

    for i in range(len(tech_list)):
        s = tech_list[i]
        tech_cost_min[i] = tech_yml[s]['min_cost']
        integ_factor[i] = tech_integ_factor
        TRL[i] = tech_yml[s]['TRL_ini']
        Rexp[i] = tech_yml[s]['R&D_exp']
        Mexp[i] = tech_yml[s]['Man_exp']
        Oexp[i] = tech_yml[s]['Ope_exp']
        tech_cost[i] = tech_cost_min[i] * (10 - TRL[i])
        accident_ratio_ini[i] = tech_yml[s]['accident']
        accident_ratio_base[i] = accident_ratio_ini[i]
        accident_ratio[i] = accident_ratio_base[i]
    
    tech_df = pd.DataFrame(zip(tech_list, tech_cost, integ_factor, TRL, Rexp, Mexp, Oexp, tech_cost_min, accident_ratio, accident_ratio_base, accident_ratio_ini), columns = column)
    
    return tech_df

def calculate_tech(tech, ship_fleet, ship_age):
    ship_working = ship_fleet[-ship_age:]
    # print(ship_working)
    berth_list = ['config1', 'config5', 'config6', 'config7', 'config10', 'config11']
    navi1_list = ['config2', 'config5', 'config8', 'config10']
    navi2_list = ['config3', 'config6', 'config9', 'config11']
    moni_list = ['config4', 'config7', 'config8', 'config9', 'config10', 'config11']

    for i in berth_list:
        tech.Oexp[0] += ship_working[i].sum()
        tech.Mexp[0] += ship_working.iloc[-1][i]
    for i in navi1_list:
        tech.Oexp[1] += ship_working[i].sum() * 0.5
        tech.Mexp[1] += ship_working.iloc[-1][i] * 0.5
    for i in navi2_list:
        tech.Oexp[1] += ship_working[i].sum()
        tech.Mexp[1] += ship_working.iloc[-1][i]
    for i in moni_list:
        tech.Oexp[2] += ship_working[i].sum() 
        tech.Mexp[2] += ship_working.iloc[-1][i]
        
    for i in range(len(tech.Oexp)):
        tech.Oexp[i] = ope_max if tech.Oexp[i] > ope_max else tech.Oexp[i]
        tech.Mexp[i] = manu_max if tech.Mexp[i] > manu_max else tech.Mexp[i]
    
    return tech

def calculate_TRL_cost(tech):
    TRL_need = [0] * 3
    for i in range(3):
        TRL_need[i] = rd_need_TRL # * tech.TRL[i]
        if (tech.Oexp[i] * ope_TRL_factor + tech.Rexp[i] * rd_TRL_factor) - TRL_need[i] > 0 and tech.TRL[i] < 9:
            tech.TRL[i] += 1
            tech.accident_ratio_base[i] -= acc_reduction_full * trl_rate(tech.TRL[i])
            tech.Rexp[i] = tech.Rexp[i] - rd_need_TRL if tech.Rexp[i] - rd_need_TRL > 0 else 0

        tech.Rexp[i] += randd_base # Base investment (TBD)    
        tech.tech_cost[i] = (10 - tech.TRL[i]) * tech.tech_cost_min[i]
        tech.integ_factor[i] = 1+(tech_integ_factor-1)*(manu_max-tech.Mexp[i])/manu_max if manu_max > tech.Mexp[i] else 1
        tech.accident_ratio[i] = tech.accident_ratio_base[i] * (tech.Oexp[i]+1) ** (-ope_safety_b)

    return tech