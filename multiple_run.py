'''''
Multiple run for making tradespace 
'''''
import copy
import itertools
import os

import pandas as pd
import random as rd
from Agent import Investor, PolicyMaker, ShipOwner
from calculate import (
    calculate_cost, 
    calculate_tech, 
    calculate_TRL_cost, 
    get_tech_ini
)
from input import (
    get_scenario, 
    get_yml, 
    set_scenario, 
    set_tech
)
from output import show_tradespace_for_multiple_color

sim_name = '240222'
DIR = 'result/'+'multiple/'+sim_name
if not os.path.exists(DIR):
    os.makedirs(DIR)

crew_list = ['NaviCrew', 'EngiCrew', 'Steward']
cost_list = ['OPEX', 'CAPEX', 'VOYEX', 'AddCost']
accident_list = ['accident_berth', 'accident_navi', 'accident_moni']

# ship_types = ['ship_1', 'ship_2', 'ship_3', 'ship_4', 'ship_5']
# cost_types = ['cost_99', 'cost_199', 'cost_499', 'cost_749', 'cost_3000']

def multiple_run():
    '''
    Settings
    '''    
    fleet_type = 'domestic'

    if fleet_type == 'domestic':
        fleet_yml = get_yml('fleet_domestic')
    elif fleet_type == 'international':
        fleet_yml = get_yml('fleet_international')

    ship_types = list(fleet_yml)
    cost_types = [f'cost_{fleet_yml[ship]["ship_size"]}' for ship in fleet_yml]
    cost_yml = [''] * len(ship_types)
    spec_each = [''] * len(ship_types)    

    start_year, end_year = 2022, 2050
    ship_age = 25
    dt_year = 50

    economy = 1
    estimated_loss = 25
    invest_amount = 5000000
    trial_times = 1
    scaling_factor = 1

    Mexp_to_production_loop = True
    Oexp_to_TRL_loop = True
    Oexp_to_safety_loop = True

    '''
    Control Parameters
    '''    
    sub = ('R&D', 'Ado', 'Exp', 'ExpAdo',) #'R&D' #, 'Exp')
    # sub = ('R&D', 'Exp', 'Ado', 'ExpAdo')
    reg = ('Asis', 'Relax')
    # inv = ('All',) #, 'Berth', 'Navi', 'Moni')
    # ope = ('Profit',) #'Safety', 'Profit')
    share = ('Close', 'Open') #0.1, 1.0)
    # share = (0, 0.5, 1.0)    
    # insurance = ('Asis', 'Considered') #(0.0, 1.0)
    insurance = ('Resist', 'Considered') #(0.0, 1.0) 'Considered', 'Asis'
    
    control_cases_list = list(itertools.product(sub, reg, share, insurance))

    '''
    Uncertain Factors
    '''
    uncertainty = True
    monte_carlo = 1
    
    ship_growth = 1.072
    growth_scenario = ('Average', 'Small', 'Large')
    TRL_Berth_list = (2, 3)
    TRL_Navi_list = (2, 3)
    TRL_Moni_list = (2, 3)
    crew_cost_list = (1.0, 1.5, 2.0)
    ope_TRL_factor_list = (1000, 10000)

    ship_per_scccrew = 3
    ope_safety_b = 0.2
    fuel_rate = 1

    '''
    Other Parameters
    '''
    share_rate_M = 1.0

    retrofit = True
    retrofit_cost = 0.01
    retrofit_limit = 1000

    if monte_carlo == 1:
        cases = list(itertools.product(sub, reg, share, insurance, 
                                    growth_scenario, TRL_Berth_list, TRL_Navi_list, TRL_Moni_list, crew_cost_list, ope_TRL_factor_list))
        uncertainty_cases = len(list(itertools.product(growth_scenario, TRL_Berth_list, TRL_Navi_list, TRL_Moni_list, crew_cost_list, ope_TRL_factor_list)))
        # uncertainty_cases = len(list(itertools.product(growth_list, TRL_Berth_list, TRL_Navi_list, TRL_Moni_list, crew_cost_list, ope_TRL_factor_list)))
    else:
        cases = list(itertools.product(sub, reg, share, insurance, 
                                    growth_scenario, range(monte_carlo)))
        uncertainty_cases = len(list(itertools.product(growth_scenario, range(monte_carlo))))
        
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
    full_ratio_2040 = [0] * len(cases)
    num_crew_2040 = [0] * len(cases)
    num_onboard_crew_2040 = [0] * len(cases)
    num_acc_2040 = [0] * len(cases)
    max_seafarer_list = [0] * len(cases)
    growth_rate_list = [0] * len(cases)
    
    casename = []
    casetype = []

    for num, case in enumerate(cases):
        print(case)
        if monte_carlo == 1:            
            casename.append(case[0]+'_'+case[1]+'_'+case[2]+'_'+case[3]+'_'+str(case[4])+'_'+str(case[5])+'_'+str(case[6])+'_'+str(case[7])+'_'+str(case[8])+'_'+str(case[9]))
        else:
            casename.append(case[0]+'_'+case[1]+'_'+case[2]+'_'+case[3]+'_'+str(case[4])+'_'+str(case[5]))

        casetype.append([case[0], case[1], case[2], case[3]])
        safety = 1 # 1 if case[3] == 'Safety' else 0.1
        invest_tech = 'All' # case[2]
        share_rate_O = 0.01 if case[2] == 'Close' else 1.0
        insurance_rate = 0.0 if case[3] == 'Asis' else 1.0 if case[3] == 'Considered' else 0.0 if case[3] == 'Resist' else 2.0

        subsidy_RandD = 5000000 if case[0] == 'R&D' else 4000000
        subsidy_Adoption = 1000000 if case[0] == 'Ado' else 0
        subsidy_Experience = 1000000 if case[0] == 'Exp' else 0

        if case[0] == 'ExpAdo':
            subsidy_RandD = 3000000
            subsidy_Adoption = 1000000
            subsidy_Experience = 1000000

        TRLreg = 8 if case[1] == 'Asis' else 7
            
        if monte_carlo == 1:            
            # numship_growth = case[4]
            TRL_Berth = case[5] * 10000000
            TRL_Navi = case[6] * 10000000
            TRL_Moni = case[7] * 10000000
            crew_cost_rate = case[8]
            ope_TRL_factor = case[9]
        else:
            TRL_Berth = rd.uniform(2,3) * 10000000
            TRL_Navi = rd.uniform(2,3) * 10000000
            TRL_Moni = rd.uniform(2,3) * 10000000
            crew_cost_rate = rd.uniform(1,2)
            ope_TRL_factor = 10 ** (rd.uniform(3,4))
            # ship_per_scccrew = rd.randint(1,7)

        # TBD
        if case[4] == 'Small':
            numship_growth_list = [1.145, 1.145, 1.145, 1., 1.]
        elif case[4] == 'Large':
            numship_growth_list = [1., 1., 1., 1.0975, 1.0975]
        else:
            numship_growth_list = [ship_growth] * len(ship_types)
     
        set_tech(ope_safety_b, ope_TRL_factor)
        set_scenario(
            start_year, end_year, 
            # numship_growth_list, ship_age, 
            economy, safety, estimated_loss, subsidy_RandD, subsidy_Adoption, TRLreg, 
            Mexp_to_production_loop, Oexp_to_TRL_loop, Oexp_to_safety_loop) #, fleet_type)
        scenario_yml = get_yml('scenario')
        current_fleet, num_newbuilding, ship_age_list, ship_size_list  = get_scenario(scenario_yml, fleet_yml, ship_types, fleet_type)

        Owner = ShipOwner('Owner', economy, safety, current_fleet, num_newbuilding, estimated_loss)
        Manufacturer = Investor('Manufacturer')
        Regulator = PolicyMaker('Regulator')
    
        tech_yml = get_yml('tech')
        ship_spec_yml = get_yml('ship_spec')
        config_list = list(ship_spec_yml)
        tech, param = get_tech_ini(tech_yml, uncertainty, TRL_Berth, TRL_Navi, TRL_Moni)
        select_index = []

        for i in range(len(cost_types)):
            cost_yml[i] = get_yml(cost_types[i])

        # fleet = make_dataframe_for_output(start_year, end_year, config_list)
        # building = copy.copy(fleet)
        
        sim_year=start_year
        for i in range(sim_year-start_year, min(end_year-start_year+1,sim_year-start_year+dt_year), 1):    
            Manufacturer.reset(invest_tech,invest_amount)
            Regulator.reset(subsidy_RandD, subsidy_Adoption, subsidy_Experience, trial_times) 
            if i > 0:
                Owner.one_step(start_year+i)

            Regulator.subsidize_investment(Manufacturer)
            tech = Manufacturer.invest(tech, Regulator)
            tech = calculate_tech(tech, Owner.fleet, share_rate_O, share_rate_M, start_year+i-1, scaling_factor)
            tech, acc_navi_semi = calculate_TRL_cost(tech, param, Mexp_to_production_loop, Oexp_to_TRL_loop, Oexp_to_safety_loop)
            
            spec_current = [''] * len(cost_types)
            # Iteration for ship_type
            for j in range(len(ship_types)):
                spec_current[j]= calculate_cost(ship_spec_yml, cost_yml[j], start_year+i, tech, acc_navi_semi, fuel_rate, crew_cost_rate, insurance_rate, ship_per_scccrew)
                select = Owner.select_ship(spec_current[j], tech, TRLreg)
                Owner.purchase_ship(config_list, select, i, start_year, ship_size_list[j], ship_types[j])
                select_index.append(select) # tentative
                if subsidy_Adoption > 0:
                    Regulator.select_for_sub_adoption(spec_current[j], tech, TRLreg)
                    Owner.purchase_ship_with_adoption(spec_current[j], config_list, select, tech, i, TRLreg, Regulator, start_year, ship_size_list[j])

                if retrofit:
                    Owner.select_retrofit_ship(spec_current[j], tech, TRLreg, ship_age_list[j], retrofit_cost, config_list, i, start_year, retrofit_limit, ship_size_list[j])

                if subsidy_Experience > 0:
                    Regulator.subsidize_experience(tech, TRLreg)

                Owner.scrap_ship(ship_age_list[j], i, start_year)
                
                spec_each[j] = spec_current[j] if i == 0 else pd.concat([spec_each[j], spec_current[j]])
                spec_each[j]['ship_type'] = ship_types[j]
                tech_year = pd.concat([pd.DataFrame({'year': [start_year+i]*3}), tech], axis = 1)            
                tech_accum = tech_year if i == 0 else pd.concat([tech_accum, tech_year])            
                subsidy_df = pd.DataFrame({'R&D': Regulator.sub_RandD, 'Adoption': Regulator.sub_Adoption, 
                            'Select_ship': Regulator.sub_select, 'Subsidy_used': Regulator.sub_used, 
                            'Subsidy_per_ship': Regulator.sub_per_ship, 'All_investment': Manufacturer.invest_used}, index=[i+start_year])
                subsidy_accum = subsidy_df if i == 0 else pd.concat([subsidy_accum, subsidy_df])
            
        for j in range(len(ship_types)):
            spec = spec_each[j] if j == 0 else pd.concat([spec, spec_each[j]])


        merged_data = pd.merge(Owner.fleet, spec, on=['year', 'ship_type', 'config'], how='inner')
        
        grouped_data = merged_data.groupby(['year', 'config', 'ship_type']).agg({
            'ship_id': 'count',
            }).reset_index()
        
        grouped_data_ship_499 = grouped_data.query("ship_type == 'ship_4'")
                
        summary = merged_data.groupby('year').agg({
            'CAPEX': 'sum',
            'OPEX': 'sum',
            'VOYEX': 'sum',
            'AddCost': 'sum',
            'accident_berth': 'sum',
            'accident_navi': 'sum',
            'accident_moni': 'sum',
            'accident_berth': 'sum',
            'accident_navi': 'sum',
            'accident_moni': 'sum',
            'NaviCrew': 'sum', 
            'EngiCrew': 'sum', 
            'Steward': 'sum', 
            'NaviCrewSCC': 'sum', 
            'EngiCrewSCC': 'sum'
             }).reset_index()

        intro_year_auto = grouped_data[grouped_data['config'] != 'NONE']['year'].min()        
        intro_year_full = grouped_data[grouped_data['config'] == 'FULL']['year'].min()

        filtered_data = grouped_data[(grouped_data['year'] == 2040)]
        total_ships = filtered_data['ship_id'].sum()
        none_config_ships = filtered_data.loc[filtered_data['config'] == 'NONE', 'ship_id'].sum()
        full_auto_ships = filtered_data.loc[filtered_data['config'] == 'FULL', 'ship_id'].sum()
        auto_2040 = (total_ships - none_config_ships) / total_ships * 100
        full_2040 = full_auto_ships / total_ships * 100

        total_seafarer = merged_data[crew_list].sum(axis=1)
        total_accidents = merged_data[accident_list].sum(axis=1)
        average_seafarer = total_seafarer.mean()
        average_accidents = total_accidents.mean()

        row_2040 = summary[summary['year'] == 2040]
        number_of_seafarer_2040 = row_2040['NaviCrew'] + row_2040['EngiCrew'] + row_2040['Steward'] + row_2040['NaviCrewSCC'] + row_2040['EngiCrewSCC']
        number_of_onboard_seafarer_2040 = row_2040['NaviCrew'] + row_2040['EngiCrew'] + row_2040['Steward']
        number_of_accidents_2040 = row_2040['accident_berth'] + row_2040['accident_navi'] + row_2040['accident_moni']

        Berth = tech_accum[tech_accum['tech_name'] == 'Berth']
        Navi = tech_accum[tech_accum['tech_name'] == 'Navi']
        Moni = tech_accum[tech_accum['tech_name'] == 'Moni']
        Berth.set_index('year', inplace=True)
        Navi.set_index('year', inplace=True)
        Moni.set_index('year', inplace=True)

        summary['total_seafarer'] = summary[['NaviCrew', 'EngiCrew', 'Steward', 'NaviCrewSCC', 'EngiCrewSCC']].sum(axis=1)
        summary['seafarer_growth_rate'] = summary['total_seafarer'].diff() / summary['total_seafarer'].shift() * 100
        max_seafarer = summary['total_seafarer'].max()
        max_growth_rate = summary['seafarer_growth_rate'].abs().max()

        list_intro_auto[num] = intro_year_auto
        list_intro_full[num] = intro_year_full
        auto_ratio_2040[num] = auto_2040
        full_ratio_2040[num] = full_2040
        num_crew_2040[num] = number_of_seafarer_2040.values[0]
        num_acc_2040[num] = number_of_accidents_2040.values[0]
        num_onboard_crew_2040[num] = number_of_onboard_seafarer_2040
        # list_profit[num] = int(fleet['Profit'].sum())
        list_subsidy[num] = int(subsidy_accum['Subsidy_used'].sum())
        # list_ROI[num] = fleet['Profit'].sum()/subsidy_accum['Subsidy_used'].sum()
        list_accident[num] = average_accidents
        list_seafarer[num] = average_seafarer
        list_RDforTRL_b[num] = param.rd_need_TRL[0]
        list_RDforTRL_n[num] = param.rd_need_TRL[1]
        list_RDforTRL_m[num] = param.rd_need_TRL[2]
        max_seafarer_list[num] = max_seafarer
        growth_rate_list[num] = max_growth_rate
        
    list_intro_full_fillna = [end_year + 1 if e == 'nan' or e == 'NaN' else e for e in list_intro_full]

    result_df = pd.DataFrame({
        'Casename': casename,
        'Introduction Year (Full)': list_intro_auto, 
        'Introduction Year (Auto)': list_intro_full, 
        'Autonomous Ship introduction ratio at 2040 (-)': auto_ratio_2040,
        'Full Autonomous Ship introduction ratio at 2040 (-)': full_ratio_2040,
        'Number of crew at 2040': num_crew_2040,
        # 'Profit (USD)': list_profit, 
        'Subsidy (USD)': list_subsidy,
        # 'Subsidy ROI (-)': list_ROI,
        'Number of Maximum Crew': max_seafarer_list,
        'Number of Maximum Growth Rate (%)': growth_rate_list, 
        'Estimated num of Accident (case/year)': list_accident,
        'Estimated num of Seafarer (person)': list_seafarer,
        'Necessary R&D for TRL Berth (USD/TRL)': list_RDforTRL_b,
        'Necessary R&D for TRL Navi (USD/TRL)': list_RDforTRL_n,
        'Necessary R&D for TRL Moni (USD/TRL)': list_RDforTRL_m})

    result_df.to_csv(DIR+'/'+'multiple'+'.csv')

    # タイトルは追って変数に紐づけ
    show_tradespace_for_multiple_color(list_intro_full_fillna, list_seafarer, 'Introduction of FullAuto ship (year)', 'Average Seafarer (people)', 'Intro(Full) vs Seafarer', control_cases_list, uncertainty_cases, DIR, True, False)
    show_tradespace_for_multiple_color(list_intro_full_fillna, list_subsidy, 'Introduction of FullAuto ship (year)', 'Subsidy (USD)', 'Intro(Full) vs Subsidy', control_cases_list, uncertainty_cases, DIR, True, False)
    show_tradespace_for_multiple_color(list_intro_full_fillna, list_accident, 'Introduction of FullAuto ship (year)', 'Estimated number of accidents (case/year)', 'Intro(Full) vs Safety', control_cases_list, uncertainty_cases, DIR, True, False)
    show_tradespace_for_multiple_color(list_subsidy, list_accident, 'Subsidy (USD)', 'Estimated number of accidents (case/year)', 'Subsidy vs Safety', control_cases_list, uncertainty_cases, DIR)
    show_tradespace_for_multiple_color(list_subsidy, list_seafarer, 'Subsidy (USD)', 'Average number of seafarer (person)', 'Subsidy vs Human Resource', control_cases_list, uncertainty_cases, DIR)
    # show_tradespace_for_multiple_color(list_intro_auto, list_ROI, 'Introduction of Auto ship (year)', 'RoI (-)', 'Intro(Auto) vs RoI', control_cases_list, uncertainty_cases, DIR, True, False)
    show_tradespace_for_multiple_color(list_intro_auto, list_accident, 'Introduction of Auto ship (year)', 'Estimated number of accidents (case/year)', 'Intro(Auto) vs Safety', control_cases_list, uncertainty_cases, DIR, True, False)
    show_tradespace_for_multiple_color(list_intro_auto, list_seafarer, 'Introduction of Auto ship (year)', 'Average Seafarer (people)', 'Intro(Auto) vs Seafarer', control_cases_list, uncertainty_cases, DIR, True, False)
    show_tradespace_for_multiple_color(list_intro_auto, list_subsidy, 'Introduction of Auto ship (year)', 'Subsidy (USD)', 'Intro(Auto) vs Subsidy', control_cases_list, uncertainty_cases, DIR, True, False)
    show_tradespace_for_multiple_color(list_intro_auto, list_intro_full_fillna, 'Introduction of Auto ship (year)', 'Introduction of FullAuto ship (year)', 'Intro(Auto) vs Intro(Full)', control_cases_list, uncertainty_cases, DIR, True, True)
    show_tradespace_for_multiple_color(auto_ratio_2040, full_ratio_2040, 'Auto ship intro Ratio at 2040 (-)', 'Full Auto ship intro Ratio at 2040 (year)', 'Introrate(Auto)2040 vs Introrate(Full)2040', control_cases_list, uncertainty_cases, DIR, True, True)
    show_tradespace_for_multiple_color(auto_ratio_2040, num_acc_2040, 'Auto ship intro Ratio at 2040 (-)', 'Estimated number of accidents at 2040(case/year)', 'Introrate(Auto)2040 vs Safety', control_cases_list, uncertainty_cases, DIR, True, True)
    show_tradespace_for_multiple_color(auto_ratio_2040, num_crew_2040, 'Auto ship intro Ratio at 2040 (-)', 'Num crew at 2040 (people)', 'Introrate(Auto)2040 vs Crew', control_cases_list, uncertainty_cases, DIR, True, True)
    show_tradespace_for_multiple_color(full_ratio_2040, num_acc_2040, 'Full Auto ship intro Ratio at 2040 (-)', 'Estimated number of accidents at 2040(case/year)', 'Introrate(Full)2040 vs Safety', control_cases_list, uncertainty_cases, DIR, True, True)
    show_tradespace_for_multiple_color(full_ratio_2040, num_crew_2040, 'Full Auto ship intro Ratio at 2040 (-)', 'Num crew at 2040 (people)', 'Introrate(Full)2040 vs Crew', control_cases_list, uncertainty_cases, DIR, True, True)
    show_tradespace_for_multiple_color(growth_rate_list, max_seafarer_list, 'Seafarer Growth Rate (abs) (-)', 'Maximum Number of Seafarers', 'Seafarer Growth Rate vs MaxCrew', control_cases_list, uncertainty_cases, DIR, True, True)
    show_tradespace_for_multiple_color(growth_rate_list, full_ratio_2040, 'Seafarer Growth Rate (abs) (-)', 'Full Auto ship intro Ratio at 2040 (-)', 'Seafarer Growth Rate vs Introrate(Full)2040 ', control_cases_list, uncertainty_cases, DIR, True, True)
    show_tradespace_for_multiple_color(full_ratio_2040, max_seafarer_list, 'Full Auto ship intro Ratio at 2040 (-)', 'Maximum Number of Seafarers', 'Introrate(Full)2040 vs MaxCrew', control_cases_list, uncertainty_cases, DIR, True, True)


if __name__ =='__main__':
    multiple_run()