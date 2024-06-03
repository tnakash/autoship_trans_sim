import copy
import glob
import os
import random
import zipfile
import yaml

import pandas as pd
import streamlit as st
from PIL import Image

from Agent import Investor, PolicyMaker, ShipOwner
from calculate import calculate_cost, calculate_tech, calculate_TRL_cost, get_tech_ini
from input import get_scenario, get_yml, set_scenario, set_tech, save_uploaded_file
from output import (
    show_linechart_three,
    show_tradespace_general,
    show_stacked_bar,
    process_ship_data,
)

'''
Setting lists
'''
crew_list = [
    'NaviCrew', 
    'EngiCrew', 
    'Steward', 
    'NaviCrewSCC', 
    'EngiCrewSCC'
    ]

cost_list = [
    'OPEX', 
    'CAPEX', 
    'VOYEX', 
    'AddCost'
    ]

accident_list = [
    'accident_berth', 
    'accident_navi', 
    'accident_moni'
    ]

'''
Main Function with Streamlit UI
'''
def main():
    '''
    ## Autonomous Ship Transition Simulator
    '''
    img = Image.open('fig/logo.png')
    st.sidebar.image(img, width = 300)

    st.markdown('#### 1. Scenario Setting')
    
    st.write('1.1 Basic Setting')
    fleet_type = st.selectbox('Fleet Type', ('domestic', 'international'))
    casename = st.text_input('Casename', value='240123')

    start_year, end_year = st.slider('Simulation Year', 2020, 2070, (2023, 2050))
    numship_growth = st.slider('Annual growth rate of ship demand[-]', 0.900, 1.100, 1.01) # 1.072 for Average
    scaling_factor = st.slider('To save the simulation time, reduce the number of ship and people to 1/X', 1, 10, 1)

    if fleet_type == 'domestic':
        growth_scenario = st.selectbox('Scenario for Growth (assume double in 10 yrs)', ('Average', 'Small', 'Large'))
        numship_growth = 1.072 if growth_scenario == 'Average' else numship_growth
        fleet_yml = get_yml('fleet_domestic')
    elif fleet_type == 'international':
        growth_scenario = 'Average'
        fleet_yml = get_yml('fleet_international')

    ship_types = list(fleet_yml)
    cost_types = [f'cost_{fleet_yml[ship]["ship_size"]}' for ship in fleet_yml]

    # dt_year = end_year - start_year + 1
    ship_age = st.slider('Average Ship Lifeyear', 20, 30, 25)
    ship_per_scccrew = st.slider('Number of ships for one SCC operator', 1, 12, 3)

    st.write('1.2 Additional Setting')
    Mexp_to_production_loop = st.checkbox('Include effect of Manufacturing experience to Production cost', value = True)
    Oexp_to_TRL_loop = st.checkbox('Include effect of Operational experience to TRL', value = True)
    Oexp_to_safety_loop = st.checkbox('Include effect of Operational experience to Safety', value = True)
        
    show_tradespace = st.checkbox('Show Tradespace', value = False)
    tradespace_interval = 10
    uncertainty = True # st.checkbox('Set Uncertainty', value = False)
    fuel_rate = st.slider('Fuel rate (times)', 0, 5, 1)
        
    share_rate_O = st.slider('Sharing ratio of operational experience', 0.0, 1.0, 1.0)
    share_rate_M = st.slider('Sharing ratio of Manufacturing experience', 0.0, 1.0, 1.0)
    crew_cost_rate = st.slider('Crew Cost rate', 1.0, 2.0, 1.0)
    insurance_rate = st.slider('Insurance Cost Discount rate', -1.0, 2.0, 1.0)
    retrofit = st.checkbox('Consider retrofit?', value = True)
    retrofit_cost = st.number_input('Retrofit Cost rate per annual cost [-]', value = 0.01)
    retrofit_limit = st.number_input('Retrofit limit per year [ship/year]', value = 1000)
    
    TRL_Berth = st.number_input('Neccessary R&D for Technology Readiness of Berthing (USD/TRL)', value = 20000000)
    TRL_Navi = st.number_input('Neccessary R&D for Technology Readiness of Navigation (USD/TRL)', value = 20000000)
    TRL_Moni = st.number_input('Neccessary R&D for Technology Readiness of Monitoring (USD/TRL)', value = 20000000)
    
    st.sidebar.markdown('## 2. Agent Parameter Setting')
    
    st.sidebar.markdown('### 2.1 Ship Owner')
    st.sidebar.write("Parameters for ship adoption")
    estimated_loss = ship_age # st.sidebar.number_input('Estimated Accident Loss Amount (compared to annual CAPEX) [times]', value = 25) 
    economy = 1  # st.sidebar.slider('Profitability weight[-]', 0.0, 1.0, 1.0)
    safety = st.sidebar.slider('Safety weight Compared to Profitability', 0, 10, 1)

    st.sidebar.markdown('### 2.2 Manufacturer (R&D Investor))')
    st.sidebar.write("Technology type and Amount of investment")    
    invest_tech = st.sidebar.selectbox("Investment Strategy", ["All", "Berth", "Navi", "Moni"])
    invest_amount = st.sidebar.number_input('Investment Amount [USD/year]', value = 5000000)

    st.sidebar.markdown('### 2.3 Policy Maker')
    st.sidebar.write("Type and amount of subsidy")
    subsidy_RandD = st.sidebar.number_input('Subsidy Amount (R&D)[USD/year]', value = 5000000)
    subsidy_Adoption = st.sidebar.number_input('Subsidy Amount (Adoption)[USD/year]', value = 0)
    subsidy_Experience = st.sidebar.number_input('Subsidy Amount for Prototyping [USD/year]', value = 0)
    trial_times = 1  # number of trials for getting one experience
    TRLreg = st.sidebar.selectbox('TRL regulation (minimum TRL for deployment)', (8, 7))

    # uploaded_file = st.file_uploader("upload YAML file", type="yaml")
    # if uploaded_file is not None:
    #     save_folder = "yml/"
    #     if not os.path.exists(save_folder):
    #         os.makedirs(save_folder)
    #     file_path = save_uploaded_file(uploaded_file, save_folder)
    #     st.success(f"save YAML file: {file_path}")

    if growth_scenario == 'Small':
        numship_growth_list = [1.145, 1.145, 1.145, 1., 1.]
    elif growth_scenario == 'Large':
        numship_growth_list = [1., 1., 1., 1.0975, 1.0975]
    else:
        numship_growth_list = [numship_growth] * len(ship_types)
    
    # Set scenario and cost, ship, spec, tech parameters
    set_scenario(
        start_year, end_year, 
        economy, safety, estimated_loss, subsidy_RandD, subsidy_Adoption, TRLreg, 
        Mexp_to_production_loop, Oexp_to_TRL_loop, Oexp_to_safety_loop)

    scenario_yml = get_yml('scenario')

    # Fleet Lists
    current_fleet, num_newbuilding, ship_age_list, ship_size_list = get_scenario(scenario_yml, fleet_yml, ship_types, fleet_type)

    tech_yml = get_yml('tech')
    ship_spec_yml = get_yml('ship_spec')
    config_list = list(ship_spec_yml)
    tech, param = get_tech_ini(tech_yml, uncertainty, TRL_Berth, TRL_Navi, TRL_Moni)
    select_index = []

    cost_yml = [''] * len(ship_types)
    for i in range(len(cost_types)):
        cost_yml[i] = get_yml(cost_types[i])

    spec_each = [''] * len(ship_types)    

    # Set agents
    Owner = ShipOwner('Owner', economy, safety, current_fleet, num_newbuilding, estimated_loss)
    Manufacturer = Investor()
    Regulator = PolicyMaker()
    
    # Set result directory
    DIR = "result/"+casename
    if not os.path.exists(DIR):
        os.makedirs(DIR)
    
    DIR_FIG = "result/"+casename+'/fig'
    if not os.path.exists(DIR_FIG):
        os.makedirs(DIR_FIG)
    
    # Start Simulation
    if 'Year' not in st.session_state:
        st.session_state['Year'] = start_year
    
    st.sidebar.write("## 3. Run Simulation")
    next_step = st.sidebar.button('Start/Restart')
    if next_step:
        if st.session_state['Year'] == start_year:
            st.write("Simulation Started!")
        else:
            spec = pd.read_csv('csv/spec_'+casename+'.csv', index_col=0)
            Owner.fleet = pd.read_csv('csv/fleet_'+casename+'.csv', index_col=0)
            tech_accum = pd.read_csv('csv/tech_'+casename+'.csv', index_col=0)
            tech = tech_accum[-(len(tech_yml)-1):].drop('year', axis=1)
        
        sim_year=st.session_state.Year
        st.write('Simulation from '+str(sim_year)+' to '+str(end_year))

        # Annual iteration
        for i in range(sim_year-start_year, end_year-start_year+1, 1):    
            Manufacturer.reset(invest_tech,invest_amount)
            Regulator.reset(subsidy_RandD, subsidy_Adoption, subsidy_Experience, trial_times) 
            if i > 0:
                Owner.one_step(start_year+i)

            # Regulator (Subsidy for Manufacturer) (Increase the investment amount)
            Regulator.subsidize_investment(Manufacturer)
            
            # Manufacturer (R&D (Investment))
            tech = Manufacturer.invest(tech, Regulator)
            
            # World (Technology Development)
            tech = calculate_tech(tech, Owner.fleet, share_rate_O, share_rate_M, start_year+i-1, scaling_factor)
            tech, acc_navi_semi = calculate_TRL_cost(tech, param, Mexp_to_production_loop, Oexp_to_TRL_loop, Oexp_to_safety_loop)
            
            spec_current = [''] * len(cost_types)
            
            # Iteration for ship_type
            for j in range(len(ship_types)):
                # World (Cost Reduction and Safety Improvement)
                spec_current[j]= calculate_cost(ship_spec_yml, cost_yml[j], start_year+i, tech, acc_navi_semi, config_list, fuel_rate, crew_cost_rate, insurance_rate, ship_per_scccrew)
                # Ship Owner (Adoption and Purchase)
                select = Owner.select_ship(spec_current[j], tech, TRLreg)
                Owner.purchase_ship(config_list, select, i, start_year, ship_size_list[j], ship_types[j])                
                # Select the only one kind of ship at one year (TBD)
                select_index.append(select)
                # Regulator (Subsidy for Adoption)
                if subsidy_Adoption > 0:
                    Regulator.select_for_sub_adoption(spec_current[j], tech, TRLreg)
                    Owner.purchase_ship_with_adoption(spec_current[j], config_list, select, tech, i, TRLreg, Regulator, start_year, ship_size_list[j])
                # Ship Owner (Retrofit)
                if retrofit:
                    Owner.select_retrofit_ship(spec_current[j], tech, TRLreg, ship_age_list[j], retrofit_cost, config_list, i, start_year, retrofit_limit, ship_size_list[j])
                # Regulator (Grand Challenge)
                if subsidy_Experience > 0:
                    Regulator.subsidize_experience(tech, TRLreg)
                # Ship Owner (Scrap)
                Owner.scrap_ship(ship_age_list[j], i, start_year)
                # Show Tradespace
                if show_tradespace and (start_year+i) % tradespace_interval == 0:
                    show_tradespace_general(spec_current[j].OPEX+spec_current[j].CAPEX+spec_current[j].VOYEX+spec_current[j].AddCost,
                                            spec_current[j].accident_berth+spec_current[j].accident_navi+spec_current[j].accident_moni, 
                                            "Total Cost(USD/year)", "Accident Ratio (-)", "Profitability vs Safety at "+str(start_year+i), 
                                            spec_current[j].config.values.tolist(), select, DIR_FIG)

                spec_each[j] = spec_current[j] if st.session_state['Year'] == start_year and i == 0 else pd.concat([spec_each[j], spec_current[j]])
                spec_each[j]['ship_type'] = ship_types[j]
                tech_year = pd.concat([pd.DataFrame({'year': [start_year+i]*3}), tech], axis = 1)            
                tech_accum = tech_year if st.session_state['Year'] == start_year and i == 0 else pd.concat([tech_accum, tech_year])

                subsidy_df = pd.DataFrame({'R&D': Regulator.sub_RandD, 'Adoption': Regulator.sub_Adoption, 
                            'Select_ship': Regulator.sub_select, 'Subsidy_used': Regulator.sub_used, 
                            'Subsidy_per_ship': Regulator.sub_per_ship, 'All_investment': Manufacturer.invest_used}, index=[i+start_year])
                subsidy_accum = subsidy_df if st.session_state['Year'] == start_year and i == 0 else pd.concat([subsidy_accum, subsidy_df])
        
        for j in range(len(ship_types)):
            spec = spec_each[j] if j == 0 else pd.concat([spec, spec_each[j]])
        
        # proceed year
        st.session_state.Year += end_year - start_year + 1 # dt_year
        
        merged_data = pd.merge(Owner.fleet, spec, on=['year', 'ship_type', 'config'], how='inner')
        
        grouped_data = merged_data.groupby(['year', 'config', 'ship_type']).agg({
            'ship_id': 'count',
            }).reset_index()
        grouped_data['ship_id'] *= scaling_factor

        # Reshape the data
        grouped_data_pivot = grouped_data.pivot_table(index=['year'], columns='config', values='ship_id', aggfunc='sum', fill_value=0)
        missing_configs = set(config_list) - set(grouped_data_pivot.columns)
        for missing_config in missing_configs:
            grouped_data_pivot[missing_config] = 0

        grouped_data_pivot.reset_index(inplace=True)
        grouped_data_pivot = grouped_data_pivot.rename(columns={'index': 'year'})
        grouped_data_pivot.reset_index(drop=True, inplace=True)
        show_stacked_bar(grouped_data_pivot, config_list, "Number of Ships by Configuration [ship]", DIR_FIG, 'config')
 

        if fleet_type == 'domestic':
            for ship_type, cost_type in zip(ship_types, cost_types):
                process_ship_data(grouped_data, ship_type, config_list, cost_type, DIR_FIG)

        grouped_data_ship_type = grouped_data.pivot_table(index=['year'], columns='ship_type', values='ship_id', aggfunc='sum', fill_value=0)
        grouped_data_ship_type.reset_index(inplace=True)
        grouped_data_ship_type = grouped_data_ship_type.rename(columns={'index': 'year'})
        grouped_data_ship_type.reset_index(drop=True, inplace=True)
        show_stacked_bar(grouped_data_ship_type, ship_types, "Number of Ships by Ship Type [ship]", DIR_FIG, 'ship_type')
                
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

        summary_copy = summary.copy()
        summary_copy.loc[:, summary_copy.columns != 'year'] *= scaling_factor
        show_stacked_bar(summary_copy, cost_list, "Total cost of fleet [USD]", DIR_FIG)
        show_stacked_bar(summary_copy, accident_list, "Number of Accidents", DIR_FIG)
        show_stacked_bar(summary_copy, crew_list, "Number of Seafarers [people]", DIR_FIG, 'crew')

        # Save Tentative File for iterative simulation (and final results)
        spec.to_csv(DIR+'/spec_'+casename+'.csv')
        tech_accum.to_csv(DIR+'/tech_'+casename+'.csv')
        Owner.fleet.to_csv(DIR+'/fleet_'+casename+'.csv')
        subsidy_accum.to_csv(DIR+'/subsidy_'+casename+'.csv')
        
        """
        Technology Development
        """
        # Transfer dataframes for visualization        
        Berth = tech_accum[tech_accum['tech_name'] == 'Berth']
        Navi = tech_accum[tech_accum['tech_name'] == 'Navi']
        Moni = tech_accum[tech_accum['tech_name'] == 'Moni']
        Berth.set_index("year", inplace=True)
        Navi.set_index("year", inplace=True)
        Moni.set_index("year", inplace=True)
        
        # Visualization                    
        Rexp = pd.DataFrame({"Berth_Rexp": Berth.Rexp, "Navi_Rexp": Navi.Rexp, "Moni_Rexp": Moni.Rexp})
        st.line_chart(Rexp)
        Mexp = pd.DataFrame({"Berth_Mexp": Berth.Mexp, "Navi_Mexp": Navi.Mexp, "Moni_Mexp": Moni.Mexp})
        st.line_chart(Mexp)
        Oexp = pd.DataFrame({"Berth_Oexp": Berth.Oexp, "Navi_Oexp": Navi.Oexp, "Moni_Oexp": Moni.Oexp})
        st.line_chart(Oexp)
        
        show_linechart_three(Berth.index, Berth.TRL, Navi.TRL, Moni.TRL, "TRL [-]", "TRL of each technology", DIR_FIG, "upper left")
        show_linechart_three(Berth.index, Berth.integ_factor, Navi.integ_factor, Moni.integ_factor, "Integration Cost Factor [-]", "Integration Cost of Each Technology", DIR_FIG, "lower left")
                
        """
        Accident of each type of autonomous ship ≒ [accidents/year]
        """
        show_linechart_three(Berth.index, Berth.accident_ratio, Navi.accident_ratio, Moni.accident_ratio, "Annual Accident Ratio [case/ship]", "Accident Ratio", DIR_FIG, "lower left")
        
        with zipfile.ZipFile(DIR+'/'+casename+'.zip', 'w', compression=zipfile.ZIP_DEFLATED) as z:
            z.write(DIR+'/spec_'+casename+'.csv')
            z.write(DIR+'/tech_'+casename+'.csv')
            z.write(DIR+'/fleet_'+casename+'.csv')
            z.write(DIR+'/subsidy_'+casename+'.csv')
            files = glob.glob(DIR_FIG+'/*')
            for file in files:
                z.write(file)
            z.write('yml/tech.yml')
            z.write('yml/scenario.yml')
            # z.write('yml/'+cost+'.yml')
            z.write('yml/ship_spec.yml')

        if st.session_state.Year >= end_year:
            st.write('Simulation Done!!')
            st.session_state['Year'] = start_year

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

        summary['total_seafarer'] = summary[['NaviCrew', 'EngiCrew', 'Steward', 'NaviCrewSCC', 'EngiCrewSCC']].sum(axis=1)
        summary['seafarer_growth_rate'] = summary['total_seafarer'].diff() / summary['total_seafarer'].shift() * 100
        max_seafarer = summary['total_seafarer'].max()
        max_growth_rate = summary['seafarer_growth_rate'].abs().max()

        final = {'Autonomous Ship introduction (year)': intro_year_auto,
                 'Full Autonomous Ship introduction (year)': intro_year_full,
                 'Autonomous Ship introduction ratio at 2040 (%)': auto_2040,
                 'Full Autonomous Ship introduction ratio at 2040 (%)': full_2040,
                 'Number of Crew at 2040': number_of_seafarer_2040.values[0],
                 'Number of Onboard crew at 2040': number_of_onboard_seafarer_2040.values[0],
                 'Number of accidents at 2040': number_of_accidents_2040.values[0],
                 'Number of Maximum Crew': max_seafarer,
                 'Number of Maximum Growth Rate (%)': max_growth_rate,
                #  'Total Profit (USD)': int(fleet['Profit'].sum()), 
                 'Total Investment for R&D (incl. Subsidy) (USD)': int(subsidy_accum['All_investment'].sum()),
                 'Total Subsidy (USD)': int(subsidy_accum['Subsidy_used'].sum()), 
                #  'ROI (R&D Expenditure based) (-)': fleet['Profit'].sum()/subsidy_accum['All_investment'].sum(),
                #  'ROI (Subsidy based) (-)': fleet['Profit'].sum()/subsidy_accum['Subsidy_used'].sum(),
                 'Average number of Accident (case/ship/year)': average_accidents,
                 'Average number of seafarer (person/ship)': average_seafarer,
                 'R&D Need TRL': param.rd_need_TRL}
        st.write(final)

        '''
        ### Download Results
        '''
        st.download_button('Download result files (compressed)', open(DIR+'/'+casename+'.zip', 'br'), casename+'.zip')

if __name__ =='__main__':
    main()