import glob
import os
import zipfile

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
import pygwalker as pyg

from Agent import Investor, PolicyMaker, ShipOwner
from TechAsset import Technology, Vehicle
from World import World
from input import (
    get_scenario, 
    get_yml, 
    set_scenario, 
)
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

# Accident lists should be 
accident_list = [
    'accident_berth', 
    'accident_navi', 
    'accident_moni'
    ]

# Modify Berth etc. to a part of Tech 240723
# -------------------------------------------------------
# Main Function with Streamlit UI
# -------------------------------------------------------

def main():
    # -------------------------------------------------------
    # Setting Streamlit UI
    # -------------------------------------------------------
    '''
    ## Autonomous Ship Transition Simulator
    '''
    img = Image.open('fig/logo.png')
    # st.set_page_config(layout="wide")
    st.sidebar.image(img, width = 300)

    st.markdown('#### 1. Scenario Setting')
    
    st.write('1.1 Basic Setting')
    fleet_type = st.selectbox('Fleet Type', ('domestic', 'international', 'APEX'))
    casename = st.text_input('Casename', value='241014')

    # World/Environment
    start_year, end_year = st.slider('Simulation Year', 2020, 2070, (2023, 2050))
    numship_growth = st.slider('Annual growth rate of ship demand[-]', 0.900, 1.100, 1.01) # 1.072 for Average
    scaling_factor = st.slider('To save the simulation time, reduce the number of ship and people to 1/X', 1, 10, 1)

    if fleet_type == 'domestic':
        # Special setting for "Double in 10 years"
        growth_scenario = st.selectbox('Scenario for Growth (assume double in 10 yrs)', ('Average', 'Small', 'Large'))
        numship_growth = 1.072 if growth_scenario == 'Average' else numship_growth
        fleet_yml = get_yml('fleet_domestic')
    elif fleet_type == 'international':
        growth_scenario = 'Average'
        fleet_yml = get_yml('fleet_international')
    elif fleet_type == 'APEX':
        growth_scenario = 'Average'
        fleet_yml = get_yml('fleet_Apex')

    # dt_year = end_year - start_year + 1
    ship_age = st.slider('Average Ship Lifeyear', 20, 30, 25)
    ship_per_scccrew = st.slider('Number of ships for one SCC operator', 1, 12, 3)

    st.write('1.2 Additional Setting')
    Mexp_to_production_loop = st.checkbox('Include effect of Manufacturing experience to Production cost', value = True)
    Oexp_to_TRL_loop = st.checkbox('Include effect of Operational experience to TRL', value = True)
    Oexp_to_safety_loop = st.checkbox('Include effect of Operational experience to Safety', value = True)

    # Setting for Simulator
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
    estimated_loss = ship_age
    economy = 1
    safety = st.sidebar.slider('Safety weight Compared to Profitability', 0, 10, 1)
    
    # num_ship_owners = st.slider('Number of Ship Owners', 1, 5, 1)
    # owner_name = [''] * num_ship_owners
    # estimated_loss = [] * num_ship_owners
    # economy = [] * num_ship_owners
    # safety = [] * num_ship_owners

    # st.sidebar.write("Parameters for ship adoption of each owner")
    # for i in num_ship_owners:
    #     owner_name[i] = st.text_input('Owners name', value='owner_'+str(i))
    #     estimated_loss[i] = ship_age # st.sidebar.number_input('Estimated Accident Loss Amount (compared to annual CAPEX) [times]', value = 25) 
    #     economy[i] = 1  # st.sidebar.slider('Profitability weight[-]', 0.0, 1.0, 1.0)
    #     safety[i] = st.sidebar.slider('Safety weight Compared to Profitability', 0, 10, 1)

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

    # # growth_scenario
    # if growth_scenario == 'Small':
    #     numship_growth_list = [1.145, 1.145, 1.145, 1., 1.]
    # elif growth_scenario == 'Large':
    #     numship_growth_list = [1., 1., 1., 1.0975, 1.0975]
    # else:
    #     numship_growth_list = [numship_growth] * len(list(fleet_yml))

    # ---------------------------------------------------
    # Set scenario and cost, ship, spec, tech parameters
    # ---------------------------------------------------
    set_scenario(
        start_year, end_year, 
        economy, safety, estimated_loss, subsidy_RandD, subsidy_Adoption, TRLreg, 
        Mexp_to_production_loop, Oexp_to_TRL_loop, Oexp_to_safety_loop)

    scenario_yml = get_yml('scenario')
    tech_yml = get_yml('tech')
    ship_spec_yml = get_yml('ship_spec')
    config_list = list(ship_spec_yml)

    # ----------------------------------
    # Instantiate Simulation Environment
    # ----------------------------------
    Environment = World(casename, fleet_type, start_year, end_year, scaling_factor)
    Environment.set_demand(numship_growth, growth_scenario)

    # ----------------------------------
    # Instantiate Ship(s)
    # ----------------------------------
    Ship = Vehicle(fleet_yml)
    Ship.initiate_spec()

    # Set as World attribute: 240723
    # fleet should be an Owner's attribute, but in this case, the fleet is not divided by the Owners...
    current_fleet, num_newbuilding, ship_age_list, ship_size_list = get_scenario(scenario_yml, fleet_yml, Ship.ship_types, fleet_type)

    # ----------------------------------
    # Instantiate Technology(s)
    # ----------------------------------
    Tech = Technology()
    Tech.get_tech_ini(tech_yml, uncertainty, TRL_Berth, TRL_Navi, TRL_Moni)

    cost_yml = [''] * len(Ship.ship_types)
    for i in range(len(Ship.cost_types)):
        cost_yml[i] = get_yml(Ship.cost_types[i])

    # If need to generalize cost_list, reset cost_list
    # cost_list = list(cost_yml[0])[:-1] # Without "Others"

    # ---------------------------------
    # (Ref) Set result directory
    # ---------------------------------
    DIR = "result/"+casename
    if not os.path.exists(DIR):
        os.makedirs(DIR)
    
    DIR_FIG = "result/"+casename+'/fig'
    if not os.path.exists(DIR_FIG):
        os.makedirs(DIR_FIG)

    # ---------------------------------------------------
    # Set agents
    # ---------------------------------------------------

    Owner = ShipOwner('Owner', economy, safety, current_fleet, num_newbuilding, estimated_loss)
    # Owner_1 = ShipOwner('Owner_1', economy, safety, current_fleet, num_newbuilding, estimated_loss)
    # Owner_2 = ShipOwner('Owner_2', economy, safety, current_fleet, num_newbuilding, estimated_loss)
    Manufacturer = Investor('Manufacturer_1')
    Regulator = PolicyMaker('Regulator_1', TRLreg)

    # ---------------------------------------------------
    # Start Simulation
    # ---------------------------------------------------

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
            Tech.tech_accum = pd.read_csv('csv/tech_'+casename+'.csv', index_col=0)
            Tech.tech = Tech.tech_accum[-(len(tech_yml)-1):].drop('year', axis=1)
        
        sim_year=st.session_state.Year
        st.write('Simulation from '+str(sim_year)+' to '+str(end_year))

        # -----------------------------------------------
        # Annual iteration
        # -----------------------------------------------
        for i in range(sim_year-start_year, end_year-start_year+1, 1):    
            Manufacturer.reset(invest_tech,invest_amount)
            Regulator.reset(subsidy_RandD, subsidy_Adoption, subsidy_Experience, trial_times) 
            if i > 0:
                Owner.one_step(start_year+i)
                # Owner_1.one_step(start_year+i)
                # Owner_2.one_step(start_year+i)

            # Owner_fleet = pd.concat([Owner_1.fleet, Owner_2.fleet])

            # Regulator(s) Subsidizes for Manufacturer(s) (Increase the investment amount)
            Regulator.subsidize_investment(Manufacturer)
            
            # Manufacturers invest for R&D (if no R&D investment, give subsidy back)
            Tech.tech = Manufacturer.invest(Tech.tech, Regulator)
            
            # World (Technology Development)
            # Share_rate should be 240723
            Tech.tech = Environment.calculate_tech(Tech.tech, Owner.fleet, share_rate_O, share_rate_M, start_year+i-1, scaling_factor)
            Tech.tech, Tech.acc_navi_semi = Environment.calculate_TRL_cost(Tech.tech, Tech.param, Mexp_to_production_loop, Oexp_to_TRL_loop, Oexp_to_safety_loop)
                        
            # Iteration for ship_type
            for j in range(len(Ship.ship_types)):
                # World (Consider Cost Reduction and Safety Improvement for each ship spec)
                Ship.spec_current[j]= Environment.calculate_cost(ship_spec_yml, cost_yml[j], start_year+i, Tech.tech, Tech.acc_navi_semi, fuel_rate, crew_cost_rate, insurance_rate, ship_per_scccrew)

                # Ship Owner (Adoption and Purchase)
                # for owner in owner_list:
                select = Owner.select_ship(Ship.spec_current[j], Tech.tech, Regulator.TRLreg)
                Owner.purchase_ship(config_list, select, i, start_year, ship_size_list[j], Ship.ship_types[j])                

                # select_1 = Owner_1.select_ship(spec_current[j], tech, Regulator.TRLreg)
                # Owner_1.purchase_ship(config_list, select_1, i, start_year, ship_size_list[j], ship_types[j])                

                # select_2 = Owner_2.select_ship(spec_current[j], tech, Regulator.TRLreg)
                # Owner_2.purchase_ship(config_list, select_2, i, start_year, ship_size_list[j], ship_types[j])                

                # Regulator (Subsidy for Adoption)
                if subsidy_Adoption > 0:
                    Regulator.select_for_sub_adoption(Ship.spec_current[j], Tech.tech)
                    Owner.purchase_ship_with_adoption(Ship.spec_current[j], config_list, select, Tech.tech, i, Regulator.TRLreg, Regulator, start_year, ship_size_list[j])
                    # Owner_1.purchase_ship_with_adoption(spec_current[j], config_list, select_1, tech, i, Regulator.TRLreg, Regulator, start_year, ship_size_list[j])
                    # Owner_2.purchase_ship_with_adoption(spec_current[j], config_list, select_2, tech, i, Regulator.TRLreg, Regulator, start_year, ship_size_list[j])


                # Ship Owner (Retrofit)
                if retrofit:
                    # for owner in owner_list:
                    Owner.select_retrofit_ship(Ship.spec_current[j], Tech.tech, Regulator.TRLreg, ship_age_list[j], retrofit_cost, config_list, i, start_year, retrofit_limit, ship_size_list[j])
                    # Owner_1.select_retrofit_ship(spec_current[j], tech, Regulator.TRLreg, ship_age_list[j], retrofit_cost, config_list, i, start_year, retrofit_limit, ship_size_list[j])
                    # Owner_2.select_retrofit_ship(spec_current[j], tech, Regulator.TRLreg, ship_age_list[j], retrofit_cost, config_list, i, start_year, retrofit_limit, ship_size_list[j])

                # Regulator (Grand Challenge)
                if subsidy_Experience > 0:
                    Regulator.subsidize_experience(Tech.tech)

                # Ship Owner (Scrap)
                # for owner in owner_list:
                Owner.scrap_ship(ship_age_list[j], i, start_year)
                # Owner_1.scrap_ship(ship_age_list[j], i, start_year)
                # Owner_2.scrap_ship(ship_age_list[j], i, start_year)

                # select = select_1

                # Show Tradespace
                if show_tradespace and (start_year+i) % tradespace_interval == 0:
                    show_tradespace_general(Ship.spec_current[j].OPEX+Ship.spec_current[j].CAPEX+Ship.spec_current[j].VOYEX+Ship.spec_current[j].AddCost,
                                            Ship.spec_current[j].accident_berth+Ship.spec_current[j].accident_navi+Ship.spec_current[j].accident_moni, 
                                            "Total Cost(USD/year)", "Accident Ratio (-)", "Profitability vs Safety at "+str(start_year+i), 
                                            Ship.spec_current[j].config.values.tolist(), select, DIR_FIG)

                # pandas dataframe should be an Ship's attribute? Moreover, perhaps Ships should be "Fleet"... 240723
                Ship.spec_each[j] = Ship.spec_current[j] if st.session_state['Year'] == start_year and i == 0 else pd.concat([Ship.spec_each[j], Ship.spec_current[j]])
                Ship.spec_each[j]['ship_type'] = Ship.ship_types[j]
                
                # just set the Tech time series 240723
                tech_year = pd.concat([pd.DataFrame({'year': [start_year+i]*3}), Tech.tech], axis = 1)            
                tech_accum = tech_year if st.session_state['Year'] == start_year and i == 0 else pd.concat([tech_accum, tech_year])

                subsidy_df = pd.DataFrame({'R&D': Regulator.sub_RandD, 'Adoption': Regulator.sub_Adoption, 
                            'Select_ship': Regulator.sub_select, 'Subsidy_used': Regulator.sub_used, 
                            'Subsidy_per_ship': Regulator.sub_per_ship, 'All_investment': Manufacturer.invest_used}, index=[i+start_year])
                subsidy_accum = subsidy_df if st.session_state['Year'] == start_year and i == 0 else pd.concat([subsidy_accum, subsidy_df])
        
        for j in range(len(Ship.ship_types)):
            spec = Ship.spec_each[j] if j == 0 else pd.concat([spec, Ship.spec_each[j]])
        
        # proceed year
        st.session_state.Year += end_year - start_year + 1 # dt_year
        
        # -----------------------------------------------
        # Organize and Visualize Simulation Results
        # -----------------------------------------------

        # Owner_fleet = pd.concat([Owner_1.fleet, Owner_2.fleet])
        # merged_data = pd.merge(Owner_fleet, spec, on=['year', 'ship_type', 'config'], how='inner')
        merged_data = pd.merge(Owner.fleet, spec, on=['year', 'ship_type', 'config'], how='inner')

        # pyg_html = pyg.walk(merged_data, env='Streamlit', return_html=True)
        # components.html(pyg_html, width=1300, height=1000, scrolling=True)

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
            for ship_type, cost_type in zip(Ship.ship_types, Ship.cost_types):
                process_ship_data(grouped_data, ship_type, config_list, cost_type, DIR_FIG)

        grouped_data_ship_type = grouped_data.pivot_table(index=['year'], columns='ship_type', values='ship_id', aggfunc='sum', fill_value=0)
        grouped_data_ship_type.reset_index(inplace=True)
        grouped_data_ship_type = grouped_data_ship_type.rename(columns={'index': 'year'})
        grouped_data_ship_type.reset_index(drop=True, inplace=True)
        show_stacked_bar(grouped_data_ship_type, Ship.ship_types, "Number of Ships by Ship Type [ship]", DIR_FIG, 'ship_type')
                
        summary = merged_data.groupby('year').agg({
            'CAPEX': 'sum',
            'OPEX': 'sum',
            'VOYEX': 'sum',
            'AddCost': 'sum',
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
                 'R&D Need TRL': Tech.param.rd_need_TRL}
        st.write(final)

        '''
        ### Download Results
        '''
        st.download_button('Download result files (compressed)', open(DIR+'/'+casename+'.zip', 'br'), casename+'.zip')

if __name__ =='__main__':
    main()