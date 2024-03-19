import numpy as np
import pandas as pd
import warnings

scaling_factor = 10 # Assume 10% of ships

warnings.simplefilter('ignore', FutureWarning)

def calculate_cost(ship_spec, cost, year, tech, acc_navi_semi, config_list, fuel_rate, crew_cost_rate, insurance_rate, ship_per_scccrew):
    tech_list = ['Berth', 'Navi', 'Moni']
    crew_list = ['NaviCrew', 'EngiCrew', 'Steward', 'NaviCrewSCC', 'EngiCrewSCC']
    cost_list = ['OPEX', 'CAPEX', 'VOYEX', 'AddCost']
    opex_list = ['crew_cost', 'store_cost', 'maintenance_cost', 'insurance_cost', 'general_cost', 'dock_cost']
    capex_list = ['material_cost', 'integrate_cost', 'add_eq_cost']
    voyex_list = ['port_call', 'fuel_cost_ME', 'fuel_cost_AE']
    addcost_list = ['SCC_Capex', 'SCC_Opex', 'SCC_Personal', 'Mnt_in_port']
    accident_list = ['accident_berth', 'accident_navi', 'accident_moni']

    column = ['year', 'config'] + tech_list + crew_list + opex_list + capex_list + voyex_list + addcost_list + ['subsidy'] + cost_list + accident_list

    years = [year] * len(ship_spec)
    config = [''] * len(ship_spec)
    Berth = [0] * len(ship_spec)
    Navi = [0] * len(ship_spec)
    Moni = [0] * len(ship_spec)

    num_navi = [0] * len(ship_spec)       
    num_engi = [0] * len(ship_spec)
    num_cook = [0] * len(ship_spec)
    
    num_navi_scc = [0] * len(ship_spec)       
    num_engi_scc = [0] * len(ship_spec)
        
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
    
    berth_pilot_save = cost['Others']['berth_pilot_save']
    
    num_crew_navi = cost['Others']['num_crew_navi']
    num_crew_moni = cost['Others']['num_crew_moni']
    num_crew_cook = cost['Others']['num_crew_cook']
    num_crew_all = num_crew_navi + num_crew_moni + num_crew_cook
    
    num_crew_navi_scc = cost['Others']['num_crew_navi_scc']
    num_crew_moni_scc = cost['Others']['num_crew_moni_scc']
    
    navi_crew_factor = cost['Others']['navi_crew_factor']
    moni_crew_factor = cost['Others']['moni_crew_factor']
    cook_crew_factor = cost['Others']['cook_crew_factor']
    mainte_amount = cost['Others']['mainte_amount']
    accom_reduce_navi = cost['Others']['accom_reduce_navi']
    accom_reduce_moni = cost['Others']['accom_reduce_moni']
    TRLgap_semi = cost['Others']['TRLgap_semi']
    
    ME_no_bridge_rate = cost['Others']['ME_no_bridge_rate']
    AE_crew_rate = cost['Others']['AE_crew_rate']
    
    for i in range(len(ship_spec)):
        config[i] = config_list[i]
        Berth[i] = ship_spec[config[i]]['Berth']
        Navi[i] = ship_spec[config[i]]['Navi']
        Moni[i] = ship_spec[config[i]]['Moni']
        
        # 本来は実際の人数を考慮し，結びつける必要がある
        num_navi[i] = 0 if Navi[i] == 2 else num_crew_navi / 2 if Navi[i] == 1 else num_crew_navi
        num_engi[i] = 0 if Moni[i] == 1 else num_crew_moni
        num_cook[i] = 0 if Navi[i] == 2 and Moni[i] == 1 else num_crew_cook
        num_navi_scc[i] = 0 if Navi[i] == 0 else num_crew_navi_scc * (3. / ship_per_scccrew)
        num_engi_scc[i] = 0 if Moni[i] == 0 else num_crew_moni_scc * (3. / ship_per_scccrew)
        
        crew_cost[i] = cost['OPEX']['crew_cost'] * crew_cost_rate  # May change based on the number
        store_cost[i] = cost['OPEX']['store_cost']
        maintenance_cost[i] = cost['OPEX']['maintenance_cost']
        insurance_cost[i] = cost['OPEX']['insurance_cost']
        general_cost[i] = cost['OPEX']['general_cost']
        dock_cost[i] = cost['OPEX']['dock_cost']
        
        material_cost[i] = cost['CAPEX']['material_cost']
        integrate_cost[i] = cost['CAPEX']['integrate_cost'] * (1
                          + Berth[i] * (tech.integ_factor[0] - 1)
                          + Navi[i] * (tech.integ_factor[1] - 1) * 0.5
                          + Moni[i] * (tech.integ_factor[2] - 1))
        add_eq_cost[i] = tech.tech_cost[0] * Berth[i] + tech.tech_cost[1] * Navi[i] * 0.5 + tech.tech_cost[2] * Moni[i]
        
        port_call[i] = cost['VOYEX']['port_call']
        fuel_cost_ME[i] = cost['VOYEX']['fuel_cost_ME'] * fuel_rate
        fuel_cost_AE[i] = cost['VOYEX']['fuel_cost_AE'] * fuel_rate
        
        SCC_Capex[i] = 0
        SCC_Opex[i] = 0
        SCC_Personal[i] = 0
        Mnt_in_port[i] = 0
        
        # Rewrite afterwards...
        acc_ratio_berth[i] = tech.accident_ratio_ini[0]
        acc_ratio_navi[i] = tech.accident_ratio_ini[1]
        acc_ratio_moni[i] = tech.accident_ratio_ini[2]
        
        if Berth[i] == 1:
            port_call[i] -= berth_pilot_save * trl_rate(tech.TRL[0])
            acc_ratio_berth[i] = tech.accident_ratio[0]
            if insurance_rate > 0:
                insurance_cost[i] -= cost['OPEX']['insurance_cost'] * (acc_ratio_berth[i]/tech.accident_ratio_ini[0]) * insurance_rate

        if Navi[i] == 1:
            crew_cost[i] -= cost['OPEX']['crew_cost'] * navi_crew_factor * 0.5 * trl_rate(tech.TRL[1]+TRLgap_semi) * crew_cost_rate
            maintenance_cost[i] -= mainte_amount * num_crew_navi/num_crew_all * 0.5 * trl_rate(tech.TRL[1]+TRLgap_semi)
            material_cost[i] -= cost['CAPEX']['material_cost'] * accom_reduce_navi * 0.5 * trl_rate(tech.TRL[1]+TRLgap_semi)
            integrate_cost[i] -= cost['CAPEX']['integrate_cost'] * accom_reduce_navi * 0.5 * trl_rate(tech.TRL[1]+TRLgap_semi)
            SCC_Capex[i] += cost['AddCost']['SCC_Capex'] * 0.5
            SCC_Opex[i] += cost['AddCost']['SCC_Opex'] * 0.5
            SCC_Personal[i] += cost['AddCost']['SCC_Personal'] * 0.5 * (3. / ship_per_scccrew)
            acc_ratio_navi[i] = acc_navi_semi  # Tentativeな例外処理
            fuel_cost_AE[i] -= cost['VOYEX']['fuel_cost_AE'] * fuel_rate * AE_crew_rate * num_crew_navi/num_crew_all * 0.5 * trl_rate(tech.TRL[1]+TRLgap_semi)
            # insurance_cost[i] -= cost['OPEX']['insurance_cost'] * (acc_ratio_navi[i] /tech.accident_ratio_ini[1]) * insurance_rate
            if insurance_rate > 0:
                insurance_cost[i] -= cost['OPEX']['insurance_cost'] * (acc_ratio_navi[i] /tech.accident_ratio_ini[1]) * insurance_rate
            
        elif Navi[i] == 2:
            crew_cost[i] -= cost['OPEX']['crew_cost'] * navi_crew_factor * trl_rate(tech.TRL[1]) * crew_cost_rate
            maintenance_cost[i] -= mainte_amount * num_crew_navi/num_crew_all * trl_rate(tech.TRL[1])
            material_cost[i] -= cost['CAPEX']['material_cost'] * accom_reduce_navi * trl_rate(tech.TRL[1])
            integrate_cost[i] -= cost['CAPEX']['integrate_cost'] * accom_reduce_navi * trl_rate(tech.TRL[1])
            SCC_Capex[i] += cost['AddCost']['SCC_Capex']
            SCC_Opex[i] += cost['AddCost']['SCC_Opex']
            SCC_Personal[i] += cost['AddCost']['SCC_Personal'] * (3. / ship_per_scccrew)
            acc_ratio_navi[i] = tech.accident_ratio[1]
            fuel_cost_ME[i] -= cost['VOYEX']['fuel_cost_ME'] * fuel_rate * ME_no_bridge_rate
            fuel_cost_AE[i] -= cost['VOYEX']['fuel_cost_AE'] * fuel_rate * AE_crew_rate * num_crew_navi/num_crew_all * trl_rate(tech.TRL[1])
            if insurance_rate > 0:
                insurance_cost[i] -= cost['OPEX']['insurance_cost'] * (acc_ratio_navi[i] /tech.accident_ratio_ini[1]) * insurance_rate
        
        if Moni[i] == 1:
            crew_cost[i] -= cost['OPEX']['crew_cost'] * moni_crew_factor * crew_cost_rate * trl_rate(tech.TRL[2])
            maintenance_cost[i] -= mainte_amount * num_crew_moni/num_crew_all * trl_rate(tech.TRL[2])
            material_cost[i] -= cost['CAPEX']['material_cost'] * accom_reduce_moni * trl_rate(tech.TRL[2])
            integrate_cost[i] -= cost['CAPEX']['integrate_cost'] * accom_reduce_moni * trl_rate(tech.TRL[2])
            Mnt_in_port[i] += cost['AddCost']['Mnt_in_port']
            SCC_Capex[i] += cost['AddCost']['SCC_Capex']
            SCC_Opex[i] += cost['AddCost']['SCC_Opex']
            SCC_Personal[i] += cost['AddCost']['SCC_Personal'] * (3. / ship_per_scccrew)
            acc_ratio_moni[i] = tech.accident_ratio[2]
            fuel_cost_AE[i] -= cost['VOYEX']['fuel_cost_AE'] * fuel_rate * AE_crew_rate * num_crew_moni/num_crew_all * trl_rate(tech.TRL[2])
            if insurance_rate > 0:
                insurance_cost[i] -= cost['OPEX']['insurance_cost'] * (acc_ratio_moni[i] /tech.accident_ratio_ini[2]) * insurance_rate
            # else:
            #     insurance_cost[i] -= cost['OPEX']['insurance_cost'] * insurance_rate # TBD

        
        if Navi[i] == 2 and Moni[i] == 1:  # Berthing not considered
            crew_cost[i] -= cost['OPEX']['crew_cost'] * cook_crew_factor * crew_cost_rate
    
        Opex[i] = crew_cost[i] + store_cost[i] + maintenance_cost[i] + insurance_cost[i] + general_cost[i] + dock_cost[i] 
        Capex[i] = material_cost[i] + integrate_cost[i] + add_eq_cost[i]
        Voyex[i] = port_call[i] + fuel_cost_ME[i] + fuel_cost_AE[i] 
        AddCost[i] = SCC_Capex[i] + SCC_Opex[i] + SCC_Personal[i] + Mnt_in_port[i]
    
    spec = pd.DataFrame(zip(years, config, Berth, Navi, Moni, num_navi, num_engi, num_cook,
                            num_navi_scc, num_engi_scc, 
                            crew_cost, store_cost, maintenance_cost, insurance_cost, general_cost, dock_cost, 
                            material_cost, integrate_cost, add_eq_cost,
                            port_call, fuel_cost_ME, fuel_cost_AE, 
                            SCC_Capex, SCC_Opex, SCC_Personal, Mnt_in_port, subsidy,
                            Opex, Capex, Voyex, AddCost,
                            acc_ratio_berth, acc_ratio_navi, acc_ratio_moni), columns = column)
    
    return spec

# rewrite awterwards
def trl_rate(trl):
    trl_rate = 0.25 if trl == 7 else 0.5 if trl == 8 else 1 if trl >= 9 else 0
    # trl_rate = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0.25, 8: 0.5, 9: 1}
    return trl_rate

def get_tech_ini(tech_yml, uncertainty, trl_b = 0, trl_n = 0, trl_m = 0):
    tech_list = ['Berth', 'Navi', 'Moni'] # ideally from yml
    column = ['tech_name', 'tech_cost', 'integ_factor', 'integ_factor_ini', 'TRL', 'Rexp', 'Mexp', 'Oexp', 'tech_cost_min', 'accident_ratio', 'accident_ratio_base', 'accident_ratio_ini']

    tech_cost = [0] * len(tech_list)
    tech_cost_min = [0] * len(tech_list)
    integ_factor = [0] * len(tech_list)
    integ_factor_ini = [0] * len(tech_list)
    TRL = [0] * len(tech_list)  # May change to TECH
    Rexp = [0] * len(tech_list)
    Mexp = [0] * len(tech_list)
    Oexp = [0] * len(tech_list)
    accident_ratio_ini = [0] * len(tech_list)
    accident_ratio_base = [0] * len(tech_list)
    accident_ratio = [0] * len(tech_list)
    
    ope_max = tech_yml['Others']['ope_max']
    manu_max = tech_yml['Others']['manu_max']
    acc_reduction_full = tech_yml['Others']['acc_reduction_full']
    ope_TRL_factor = tech_yml['Others']['ope_TRL_factor']
    ope_safety_b = tech_yml['Others']['ope_safety_b']
    randd_base = tech_yml['Others']['randd_base']
    rd_TRL_factor = tech_yml['Others']['rd_TRL_factor']

    rd_need_TRL = [0] * len(tech_list)
    # Introduce Uncertainty
    if uncertainty:
        rd_need_TRL[0] = trl_b
        rd_need_TRL[1] = trl_n
        rd_need_TRL[2] = trl_m
        # for i in range(3):
        #     rd_need_TRL[i] = np.random.normal(tech_yml['Others']['rd_need_TRL'], tech_yml['Others']['rd_need_TRL']/3)
        #     rd_need_TRL[i] = 0 if rd_need_TRL[i] < 0 else rd_need_TRL[i] 
    else:
        for i in range(3):
            rd_need_TRL[i] = tech_yml['Others']['rd_need_TRL']

    integ_b = tech_yml['Others']['integ_b']
    # Rewrite afterwards... 
    param = pd.Series({
        'ope_max': ope_max,
        'manu_max': manu_max,
        'acc_reduction_full': acc_reduction_full,
        'ope_TRL_factor': ope_TRL_factor,
        'ope_safety_b': ope_safety_b,
        'randd_base': randd_base,
        'rd_TRL_factor': rd_TRL_factor,
        'rd_need_TRL': rd_need_TRL,
         'integ_b': integ_b
         }, index = [
             'ope_max',
             'manu_max',
             'acc_reduction_full',
             'ope_TRL_factor',
             'ope_safety_b',
             'randd_base',
             'rd_TRL_factor',
             'rd_need_TRL',
             'integ_b'
             ]
         )

    for i in range(len(tech_list)):
        s = tech_list[i]
        tech_cost_min[i] = tech_yml[s]['min_cost']
        integ_factor_ini[i] = tech_yml['Others']['tech_integ_factor']
        integ_factor[i] = integ_factor_ini[i]
        TRL[i] = tech_yml[s]['TRL_ini']
        tech_cost[i] = tech_cost_min[i] # * (10 - TRL[i])
        accident_ratio_ini[i] = tech_yml[s]['accident']
        accident_ratio_base[i] = accident_ratio_ini[i]
        accident_ratio[i] = accident_ratio_base[i]
    
    tech_df = pd.DataFrame(zip(tech_list, tech_cost, integ_factor, integ_factor_ini, TRL, Rexp, Mexp, Oexp, tech_cost_min, accident_ratio, accident_ratio_base, accident_ratio_ini), columns = column)
    
    return tech_df, param

def calculate_tech(tech, ship_fleet, share_rate_O, share_rate_M, current_year):
    tech.loc[0, ["Oexp"]] += ((ship_fleet['berthing'] == 1) & (ship_fleet['year'] == current_year) & (ship_fleet['is_operational'] == True)).sum() * share_rate_O * scaling_factor
    tech.loc[0, ["Mexp"]] += ((ship_fleet['berthing'] == 1) & (ship_fleet['year'] == current_year) & (ship_fleet['year_built'] == current_year)).sum() * share_rate_M * scaling_factor
    tech.loc[1, ["Oexp"]] += ((ship_fleet['navigation'] == 1) & (ship_fleet['year'] == current_year) & (ship_fleet['is_operational'] == True)).sum() * 0.5 * share_rate_O * scaling_factor
    tech.loc[1, ["Mexp"]] += ((ship_fleet['navigation'] == 1) & (ship_fleet['year'] == current_year) & (ship_fleet['year_built'] == current_year)).sum() * 0.5 * share_rate_M * scaling_factor
    tech.loc[1, ["Oexp"]] += ((ship_fleet['navigation'] == 2) & (ship_fleet['year'] == current_year) & (ship_fleet['is_operational'] == True)).sum() * share_rate_O * scaling_factor
    tech.loc[1, ["Mexp"]] += ((ship_fleet['navigation'] == 2) & (ship_fleet['year'] == current_year) & (ship_fleet['year_built'] == current_year)).sum() * share_rate_M * scaling_factor
    tech.loc[2, ["Oexp"]] += ((ship_fleet['monitoring'] == 1) & (ship_fleet['year'] == current_year) & (ship_fleet['is_operational'] == True)).sum() * share_rate_O * scaling_factor
    tech.loc[2, ["Mexp"]] += ((ship_fleet['monitoring'] == 1) & (ship_fleet['year'] == current_year) & (ship_fleet['year_built'] == current_year)).sum() * share_rate_M * scaling_factor

    return tech

    # ship_working = ship_fleet[-ship_age:]
        
    # berth_list = ['B', 'BN1', 'BN2', 'BM', 'BN1M', 'FULL']
    # navi1_list = ['N1', 'BN1', 'N1M', 'BN1M']
    # navi2_list = ['N2', 'BN2', 'N2M', 'FULL']
    # moni_list = ['M', 'BM', 'N1M', 'N2M', 'BN1M', 'FULL']

    # for i in berth_list:
    #     tech.loc[0, ["Oexp"]] += ship_working[i].sum() * share_rate_O
    #     tech.loc[0, ["Mexp"]] += ship_working.iloc[-1][i] * share_rate_M
    # for i in navi1_list:
    #     tech.loc[1, ["Oexp"]] += ship_working[i].sum() * 0.5 * share_rate_O
    #     tech.loc[1, ["Mexp"]] += ship_working.iloc[-1][i] * 0.5 * share_rate_M
    # for i in navi2_list:
    #     tech.loc[1, ["Oexp"]] += ship_working[i].sum() * share_rate_O
    #     tech.loc[1, ["Mexp"]] += ship_working.iloc[-1][i] * share_rate_M
    # for i in moni_list:
    #     tech.loc[2, ["Oexp"]] += ship_working[i].sum() * share_rate_O
    #     tech.loc[2, ["Mexp"]] += ship_working.iloc[-1][i] * share_rate_M



def calculate_TRL_cost(tech, param, Mexp_to_production_loop, Oexp_to_TRL_loop, Oexp_to_safety_loop):
    TRL_need = [0] * 3
    for i in range(3):
        TRL_need[i] = param.rd_need_TRL[i]
        if Oexp_to_TRL_loop:
            if (tech.Oexp[i] * param.ope_TRL_factor + tech.Rexp[i] * param.rd_TRL_factor) - TRL_need[i] > 0 and tech.TRL[i] < 9:
                tech.loc[i, ["TRL"]] += 1
                tech.loc[i, ["accident_ratio_base"]] = tech.accident_ratio_ini[i] * (1 - param.acc_reduction_full * trl_rate(tech.TRL[i]))
                tech.loc[i, ["Rexp"]] = tech.Rexp[i] - param.rd_need_TRL[i] if tech.Rexp[i] - param.rd_need_TRL[i] > 0 else 0
        else:
            if (tech.Rexp[i] * param.rd_TRL_factor) - TRL_need[i] > 0 and tech.TRL[i] < 9:
                tech.loc[i, ["TRL"]] += 1
                tech.loc[i, ["accident_ratio_base"]] = tech.accident_ratio_ini[i] * (1 - param.acc_reduction_full * trl_rate(tech.TRL[i]))
                tech.loc[i, ["Rexp"]] = tech.Rexp[i] - param.rd_need_TRL[i] if tech.Rexp[i] - param.rd_need_TRL[i] > 0 else 0

        tech.loc[i, ["Rexp"]] += param.randd_base
        if Mexp_to_production_loop:
            tech.loc[i, ["integ_factor"]] = tech.integ_factor_ini[i]*(tech.Mexp[i]+1)**(-param.integ_b) # if param.manu_max > tech.Mexp[i] else 1
            if tech.integ_factor[i] < 1:
                tech.loc[i, ["integ_factor"]] = 1
        
        if Oexp_to_safety_loop:
            tech.loc[i, ["accident_ratio"]] = tech.accident_ratio_base[i] * (tech.Oexp[i]+1) ** (-param.ope_safety_b)
        else:
            tech.loc[i, ["accident_ratio"]] = tech.accident_ratio_base[i]

    if Oexp_to_safety_loop:
        acc_navi_semi = tech.accident_ratio_ini[1] * (1 - param.acc_reduction_full * trl_rate(tech.TRL[1]+3) / 2) * (tech.Oexp[1]+1) ** (-param.ope_safety_b)
        # acc_navi_semi = tech.accident_ratio_ini[1] * (1 - param.acc_reduction_full * trl_rate(tech.TRL[1]+3)) * (tech.Oexp[1]+1) ** (-param.ope_safety_b)
    else:
        acc_navi_semi = tech.accident_ratio_ini[1] * (1 - param.acc_reduction_full * trl_rate(tech.TRL[1]+3) / 2)                                                                                                                                                                            
        # acc_navi_semi = tech.accident_ratio_ini[1] * (1 - param.acc_reduction_full * trl_rate(tech.TRL[1]+3))                                                                                                                                                                            

    return tech, acc_navi_semi