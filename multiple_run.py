'''''
Multiple run for making tradespace 
'''''
import copy
import itertools
import os

import pandas as pd
from Agent import Investor, PolicyMaker, ShipOwner
from calculate import calculate_cost, calculate_tech, calculate_TRL_cost, get_tech_ini
from input import get_scenario, get_yml, set_scenario, set_tech
from output import show_tradespace_for_multiple_color, show_tradespace_for_multiple_color_notext, make_dataframe_for_output

sim_name = '230821'
DIR = 'result/'+'multiple/'+sim_name
if not os.path.exists(DIR):
    os.makedirs(DIR)

crew_list = ['NaviCrew', 'EngiCrew', 'Cook']
cost_list = ['OPEX', 'CAPEX', 'VOYEX', 'AddCost']
opex_list = ['crew_cost', 'store_cost', 'maintenance_cost', 'insurance_cost', 'general_cost', 'dock_cost']
capex_list = ['material_cost', 'integrate_cost', 'add_eq_cost']
voyex_list = ['port_call', 'fuel_cost_ME', 'fuel_cost_AE']
addcost_list = ['SCC_Capex', 'SCC_Opex', 'SCC_Personal', 'Mnt_in_port']
cost_detail_list = opex_list + capex_list + voyex_list + addcost_list 
accident_list = ['accident_berth', 'accident_navi', 'accident_moni']
# config_list = ['config0', 'config1', 'config2', 'config3', 'config4', 'config5', 'config6', 'config7', 'config8', 'config9', 'config10', 'config11']
config_list = ['NONE', 'B', 'N1', 'N2', 'M', 'BN1', 'BN2', 'BM', 'N1M', 'N2M', 'BN1M', 'FULL']
# tech_list = ['berthing', 'navigation', 'monitoring']

def multiple_run():
    '''
    Settings
    '''    
    start_year, end_year = 2022, 2050
    numship_init = 344 # 44 # 3441
    ship_age = 25
    dt_year = 50

    economy = 1
    estimated_loss = 34000000
    invest_amount = 5000000
    trial_times = 1

    Mexp_to_production_loop = True
    Oexp_to_TRL_loop = True
    Oexp_to_safety_loop = True

    '''
    Control Parameters
    '''    
    sub = ('ExpAdo',) #'R&D' #, 'Exp')
    reg = ('Relax') # 'Asis', 'Relax')
    # inv = ('All',) #, 'Berth', 'Navi', 'Moni')
    # ope = ('Profit',) #'Safety', 'Profit')
    share = ('Close', 'Open') #0.1, 1.0)
    # share = (0, 0.5, 1.0)    
    # insurance = ('Asis', 'Considered') #(0.0, 1.0)
    insurance = ('Asis', 'Considered', 'Treated') #(0.0, 1.0)

    control_cases_list = list(itertools.product(sub, reg, share, insurance))

    '''
    Uncertain Factors
    '''
    uncertainty = True
    monte_carlo = 1
    
    growth_list = (0.99, 1.00, 1.01) #0.99
    TRL_Berth_list = (1.5, 2, 2.5) #, 3)
    TRL_Navi_list = (1.5, 2, 2.5) #, 3)
    TRL_Moni_list = (1.5, 2, 2.5) #, 3)
    crew_cost_list = (1.0, 1.5, 2.0)
    
    uncertainty_cases = len(list(itertools.product(growth_list, TRL_Berth_list, TRL_Navi_list, TRL_Moni_list, crew_cost_list)))
    
    ope_safety_b = 0.2
    ope_TRL_factor = 50000 #(3, 4)
    fuel_rate = 1

    '''
    Other Parameters
    '''
    ship_size = 499
    cost = 'cost_' + str(ship_size)

    share_rate_M = 1.0

    retrofit = True
    retrofit_cost = 30000
    retrofit_limit = 34 # 300

    cases = list(itertools.product(sub, reg, share, insurance, 
                                   growth_list, TRL_Berth_list, TRL_Navi_list, TRL_Moni_list, crew_cost_list))
                                #    range(monte_carlo)))    
    # cases = list(itertools.product(sub, reg, inv, ope, range(monte_carlo)))
        
    list_intro_auto = [0] * len(cases)
    list_intro_full = [0] * len(cases)
    list_profit = [0] * len(cases)
    list_subsidy = [0] * len(cases)
    list_ROI = [0] * len(cases)
    list_accident = [0] * len(cases)
    list_seafarer = [0] * len(cases)
    list_RDforTRL_b = [0] * len(cases)
    list_RDforTRL_n = [0] * len(cases)
    list_RDforTRL_m = [0] * len(cases)
    
    auto_ratio_2040 = [0] * len(cases)
    full_ratio_2050 = [0] * len(cases)
    num_crew_2040= [0] * len(cases)
    
    casename = []
    casetype = []
    # sub_type = []
    # reg_type = []
    # inv_type = []
    # ope_type = []
    for num, case in enumerate(cases):
        print(case)
        casename.append(case[0]+'_'+case[1]+'_'+case[2]+'_'+case[3]+'_'+str(case[4])+'_'+str(case[5])+'_'+str(case[6])+'_'+str(case[7])+'_'+str(case[8]))
        casetype.append([case[0], case[1], case[2], case[3]])
        safety = 0.1 # 1 if case[3] == 'Safety' else 0.1
        invest_tech = 'All' # case[2]
        share_rate_O = 0.01 if case[2] == 'Close' else 1.0
        insurance_rate = 0.0 if case[3] == 'Asis' else 1.0 if case[3] == 'Considered' else 2.0

        # subsidy_RandD = 5000000 if case[0] == 'R&D' else 4000000
        # subsidy_Adoption = 1000000 if case[0] == 'Ado' else 0
        # subsidy_Experience = 1000000 if case[0] == 'Exp' else 0

        subsidy_RandD = 3000000
        subsidy_Adoption = 1000000
        subsidy_Experience = 1000000

        TRLreg = 8 if case[1] == 'Asis' else 7
        
        numship_growth = case[4]
        TRL_Berth = case[5] * 10000000
        TRL_Navi = case[6] * 10000000
        TRL_Moni = case[7] * 10000000
        crew_cost_rate = case[8]
                
        set_tech(ope_safety_b, ope_TRL_factor)
        set_scenario(start_year, end_year, numship_init, numship_growth, ship_age, economy, safety, estimated_loss, subsidy_RandD, subsidy_Adoption, TRLreg, Mexp_to_production_loop, Oexp_to_TRL_loop, Oexp_to_safety_loop, ship_size)
        scenario_yml = get_yml('scenario')
        current_fleet, num_newbuilding = get_scenario(scenario_yml)

        Owner = ShipOwner('Owner', economy, safety, current_fleet, num_newbuilding, estimated_loss)
        Manufacturer = Investor()
        Regulator = PolicyMaker()
    
        cost_yml = get_yml(cost)
        tech_yml = get_yml('tech')
        ship_spec_yml = get_yml('ship_spec')
        tech, param = get_tech_ini(tech_yml, uncertainty, TRL_Berth, TRL_Navi, TRL_Moni)
        select_index = []
        
        fleet = make_dataframe_for_output(start_year, end_year, config_list)
        building = copy.copy(fleet)
        
        sim_year=start_year
        for i in range(sim_year-start_year, min(end_year-start_year+1,sim_year-start_year+dt_year), 1):    
            Manufacturer.reset(invest_tech,invest_amount)
            Regulator.reset(subsidy_RandD, subsidy_Adoption, subsidy_Experience, trial_times)
            Regulator.subsidize_investment(Manufacturer)

            tech = Manufacturer.invest(tech, Regulator)

            tech = calculate_tech(tech, param, Owner.fleet, ship_age, share_rate_O, share_rate_M, start_year+i-1)
            tech, acc_navi_semi = calculate_TRL_cost(tech, param, Mexp_to_production_loop, Oexp_to_TRL_loop, Oexp_to_safety_loop)

            spec_current = calculate_cost(ship_spec_yml, cost_yml, start_year+i, tech, acc_navi_semi, config_list, fuel_rate, crew_cost_rate, insurance_rate)
            
            select = Owner.select_ship(spec_current, tech, TRLreg)
            Owner.purchase_ship(config_list, select, i, start_year)
            select_index.append(select) # tentative

            if subsidy_Adoption > 0:
                Regulator.select_for_sub_adoption(spec_current, tech, TRLreg)
                Owner.purchase_ship_with_adoption(spec_current, config_list, select, tech, i, TRLreg, Regulator, start_year)

            if retrofit:
                Owner.select_retrofit_ship(spec_current, tech, TRLreg, ship_age, retrofit_cost, config_list, i, start_year, retrofit_limit)

            if subsidy_Experience > 0:
                Regulator.subsidize_experience(tech, TRLreg)

            # Ship Owner (Scrap)
            Owner.scrap_ship(ship_age, i, start_year)

            for config in config_list:
                fleet.at[start_year+i, config] = ((Owner.fleet['is_operational'] == True) & (Owner.fleet['config'] == config)).sum()
                building.at[start_year+i, config] = ((Owner.fleet['year_built'] == start_year+i) & (Owner.fleet['config'] == config) & ((Owner.fleet['misc'] == 'newbuilt') | (Owner.fleet['misc'] == 'newbuilt_subsidized'))).sum()

            
            spec = spec_current if i == 0 else pd.concat([spec, spec_current])
            tech_year = pd.concat([pd.DataFrame({'year': [start_year+i]*3}), tech], axis = 1)            
            tech_accum = tech_year if i == 0 else pd.concat([tech_accum, tech_year])
            
            subsidy_df = pd.DataFrame({'R&D': Regulator.sub_RandD, 'Adoption': Regulator.sub_Adoption, 
                        'Select_ship': Regulator.sub_select, 'Subsidy_used': Regulator.sub_used, 
                        'Subsidy_per_ship': Regulator.sub_per_ship, 'All_investment': Manufacturer.invest_used}, index=[i+start_year])
            subsidy_accum = subsidy_df if i == 0 else pd.concat([subsidy_accum, subsidy_df])

        # building = Owner.fleet[Owner.fleet.year >= start_year]

        # building.set_index('year', inplace=True)            
        # Owner.fleet.set_index('year', inplace=True)
        # fleet = copy.copy(building)
        # for i in range(start_year, end_year+1):
        #     fleet.loc[i,:] = Owner.fleet.loc[i-ship_age:i,:].sum()

        fleet_t = fleet.T
        fleet_ratio = (fleet_t/fleet_t.sum()).T        
        totalcost = copy.copy(building)
        accident = copy.copy(building)
        
        for s in config_list:
            totalcost[s] = 0
            accident[s] = 0
        
        for i in range(start_year, end_year+1):
            for s in config_list:
                for c in cost_list:
                    totalcost.loc[i,s] += spec[(spec['year'] == i) & (spec['config'] == s)][c].mean()
    
                for ac in accident_list:
                    accident.loc[i,s] += spec[(spec['year'] == i) & (spec['config'] == s)][ac].mean()
                    
        # # Save Tentative File for iterative simulation (and final results)
        # spec.to_csv(DIR+'/spec_'+casename+'.csv')
        # tech_accum.to_csv(DIR+'/tech_'+casename+'.csv')
        # Owner.fleet.to_csv(DIR+'/fleet_'+casename+'.csv')
        # subsidy_accum.to_csv(DIR+'/subsidy_'+casename+'.csv')
                    
        for c in cost_list+accident_list+crew_list+['Profit'] + cost_detail_list:
            fleet[c] = 0
        
        for i in range(start_year, end_year+1):
            for c in cost_list:
                for s in config_list:
                    fleet.loc[i,c] += fleet.loc[i,s] * spec[(spec['year'] == i) & (spec['config'] == s)][c].mean()
                    fleet.loc[i,'Profit'] += fleet.loc[i,s] * (spec[(spec['year'] == i) & (spec['config'] == 'NONE')][c].mean() - spec[(spec['year'] == i) & (spec['config'] == s)][c].mean())
                    
            for c in accident_list:
                for s in config_list:
                    fleet.loc[i,c] += fleet.loc[i,s] * spec[(spec['year'] == i) & (spec['config'] == s)][c].mean()

            for c in crew_list:
                for s in config_list:
                    fleet.loc[i,c] += fleet.loc[i,s] * spec[(spec['year'] == i) & (spec['config'] == s)][c].mean()
        
            for c in cost_detail_list:
                for s in config_list:
                    fleet.loc[i,c] += fleet.loc[i,s] * spec[(spec['year'] == i) & (spec['config'] == s)][c].mean()

        num_crew_all = fleet[crew_list].sum(axis=1)

        Berth = tech_accum[tech_accum['tech_name'] == 'Berth']
        Navi = tech_accum[tech_accum['tech_name'] == 'Navi']
        Moni = tech_accum[tech_accum['tech_name'] == 'Moni']
        Berth.set_index('year', inplace=True)
        Navi.set_index('year', inplace=True)
        Moni.set_index('year', inplace=True)
        
        if fleet['FULL'].sum() > 0:
            intro_year_full = int(fleet[fleet['FULL'] > 0].index[0])
        else:
            intro_year_full = 'NaN'

        intro_year_auto = end_year
        for i in range(1,11,1):
            if fleet[config_list[i]].sum() > 0:
                intro_year_tmp = int(fleet[fleet[config_list[i]] > 0].index[0])
                intro_year_auto = intro_year_tmp if intro_year_tmp < intro_year_auto else intro_year_auto 
        
        list_intro_auto[num] = intro_year_auto
        list_intro_full[num] = intro_year_full
        auto_ratio_2040[num] = 1 - fleet_ratio.at[2040, 'NONE']
        full_ratio_2050[num] = fleet_ratio.at[2050, 'FULL']
        num_crew_2040[num] = int(num_crew_all.at[2040])
        list_profit[num] = int(fleet['Profit'].sum())
        list_subsidy[num] = int(subsidy_accum['Subsidy_used'].sum())
        list_ROI[num] = fleet['Profit'].sum()/subsidy_accum['Subsidy_used'].sum()
        list_accident[num] = int(fleet[accident_list].sum(axis=1).sum())
        list_seafarer[num] = int(fleet[crew_list].sum(axis=1).sum() / (end_year-start_year + 1))
        list_RDforTRL_b[num] = param.rd_need_TRL[0]
        list_RDforTRL_n[num] = param.rd_need_TRL[1]
        list_RDforTRL_m[num] = param.rd_need_TRL[2]        
        
    list_intro_full_fillna = [end_year + 1 if e == 'nan' or e == 'NaN' else e for e in list_intro_full]
    # decisions = ('Subsidy', 'Regulation', 'Investment', 'Operation')
    # decisions = ('Subsidy', 'Regulation', 'Openness', 'Insurance')
    # for ii, decision in enumerate(decisions):
    #     show_tradespace_for_multiple_color(list_intro_full_fillna, list_profit, 'Introduction of FullAuto ship (year)', 'Profit (USD)', 'Intro(Full) vs Profit', casetype, ii, decision, DIR, True, False)
    #     show_tradespace_for_multiple_color(list_intro_full_fillna, list_ROI, 'Introduction of FullAuto ship (year)', 'RoI (-)', 'Intro(Full) vs RoI', casetype, ii, decision, DIR, True, False)
    #     show_tradespace_for_multiple_color(list_intro_full_fillna, list_accident, 'Introduction of FullAuto ship (year)', 'Estimated number of accidents (case/year)', 'Intro(Full) vs Safety', casetype, ii, decision, DIR, True, False)
    #     show_tradespace_for_multiple_color(list_ROI, list_accident, 'RoI (-)', 'Estimated number of accidents (case/year)', 'RoI vs Safety', casetype, ii, decision, DIR)
    #     show_tradespace_for_multiple_color(list_ROI, list_seafarer, 'RoI (-)', 'Average number of seafarer (person)', 'RoI vs Human Resource', casetype, ii, decision, DIR)
    #     show_tradespace_for_multiple_color(list_intro_auto, list_ROI, 'Introduction of Auto ship (year)', 'RoI (-)', 'Intro(Auto) vs RoI', casetype, ii, decision, DIR, True, False)
    #     show_tradespace_for_multiple_color(list_intro_auto, list_accident, 'Introduction of Auto ship (year)', 'Estimated number of accidents (case/year)', 'Intro(Auto) vs Safety', casetype, ii, decision, DIR, True, False)
    #     show_tradespace_for_multiple_color(list_intro_auto, list_intro_full_fillna, 'Introduction of Auto ship (year)', 'Introduction of FullAuto ship (year)', 'Intro(Auto) vs Intro(Full)', casetype, ii, decision, DIR, True, True)

    # タイトルは追って変数に紐づけ
    show_tradespace_for_multiple_color(list_intro_full_fillna, list_profit, 'Introduction of FullAuto ship (year)', 'Profit (USD)', 'Intro(Full) vs Profit', control_cases_list, uncertainty_cases, DIR, True, False)
    show_tradespace_for_multiple_color(list_intro_full_fillna, list_ROI, 'Introduction of FullAuto ship (year)', 'RoI (-)', 'Intro(Full) vs RoI', control_cases_list, uncertainty_cases, DIR, True, False)
    show_tradespace_for_multiple_color(list_intro_full_fillna, list_accident, 'Introduction of FullAuto ship (year)', 'Estimated number of accidents (case/year)', 'Intro(Full) vs Safety', control_cases_list, uncertainty_cases, DIR, True, False)
    show_tradespace_for_multiple_color(list_ROI, list_accident, 'RoI (-)', 'Estimated number of accidents (case/year)', 'RoI vs Safety', control_cases_list, uncertainty_cases, DIR)
    show_tradespace_for_multiple_color(list_ROI, list_seafarer, 'RoI (-)', 'Average number of seafarer (person)', 'RoI vs Human Resource', control_cases_list, uncertainty_cases, DIR)
    show_tradespace_for_multiple_color(list_intro_auto, list_ROI, 'Introduction of Auto ship (year)', 'RoI (-)', 'Intro(Auto) vs RoI', control_cases_list, uncertainty_cases, DIR, True, False)
    show_tradespace_for_multiple_color(list_intro_auto, list_accident, 'Introduction of Auto ship (year)', 'Estimated number of accidents (case/year)', 'Intro(Auto) vs Safety', control_cases_list, uncertainty_cases, DIR, True, False)
    show_tradespace_for_multiple_color(list_intro_auto, list_intro_full_fillna, 'Introduction of Auto ship (year)', 'Introduction of FullAuto ship (year)', 'Intro(Auto) vs Intro(Full)', control_cases_list, uncertainty_cases, DIR, True, True)
    show_tradespace_for_multiple_color(auto_ratio_2040, full_ratio_2050, 'Auto ship intro Ratio at 2040 (-)', 'Full Auto ship intro Ratio at 2050 (year)', 'Introrate(Auto)2040 vs Introrate(Full)2050', control_cases_list, uncertainty_cases, DIR, True, True)
    show_tradespace_for_multiple_color(auto_ratio_2040, list_accident, 'Auto ship intro Ratio at 2040 (-)', 'Estimated number of accidents (case/year)', 'Introrate(Auto)2040 vs Safety', control_cases_list, uncertainty_cases, DIR, True, True)
    show_tradespace_for_multiple_color(auto_ratio_2040, num_crew_2040, 'Auto ship intro Ratio at 2040 (-)', 'Num crew at 2040 (people)', 'Introrate(Auto)2040 vs Crew', control_cases_list, uncertainty_cases, DIR, True, True)
         
    result_df = pd.DataFrame({
        'Casename': casename,
        'Introduction Year (Full)': list_intro_auto, 
        'Introduction Year (Auto)': list_intro_full, 
        'Autonomous Ship introduction ratio at 2040 (-)': auto_ratio_2040,
        'Full Autonomous Ship introduction ratio at 2040 (-)': full_ratio_2050,
        'Number of crew at 2040': num_crew_2040,
        'Profit (USD)': list_profit, 
        'Subsidy (USD)': list_subsidy,
        'Subsidy ROI (-)': list_ROI,
        'Estimated num of Accident (case/year)': list_accident,
        'Estimated num of Seafarer (person)': list_seafarer,
        'Necessary R&D for TRL Berth (USD/TRL)': list_RDforTRL_b,
        'Necessary R&D for TRL Navi (USD/TRL)': list_RDforTRL_n,
        'Necessary R&D for TRL Moni (USD/TRL)': list_RDforTRL_m})

    result_df.to_csv(DIR+'/'+'multiple'+'.csv')

if __name__ =='__main__':
    multiple_run()