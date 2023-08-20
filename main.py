import copy
import glob
import os
import random
import zipfile

import pandas as pd
import streamlit as st
from Agent import Investor, PolicyMaker, ShipOwner
from calculate import calculate_cost, calculate_tech, calculate_TRL_cost, get_tech_ini
from input import get_scenario, get_yml, set_scenario, set_tech
from output import (
    show_linechart_three,
    show_linechart_two,
    show_stackplot,
    show_tradespace_anime,
    show_tradespace_general,
    show_stacked_bar,
    make_dataframe_for_output
)
from PIL import Image

# Setting lists
crew_list = ['NaviCrew', 'EngiCrew', 'Cook', 'NaviCrewSCC', 'EngiCrewSCC']
cost_list = ['OPEX', 'CAPEX', 'VOYEX', 'AddCost']
opex_list = ['crew_cost', 'store_cost', 'maintenance_cost', 'insurance_cost', 'general_cost', 'dock_cost']
capex_list = ['material_cost', 'integrate_cost', 'add_eq_cost']
voyex_list = ['port_call', 'fuel_cost_ME', 'fuel_cost_AE']
addcost_list = ['SCC_Capex', 'SCC_Opex', 'SCC_Personal', 'Mnt_in_port']
cost_detail_list = opex_list + capex_list + voyex_list + addcost_list 
accident_list = ['accident_berth', 'accident_navi', 'accident_moni']
config_list = ['NONE', 'B', 'N1', 'N2', 'M', 'BN1', 'BN2', 'BM', 'N1M', 'N2M', 'BN1M', 'FULL']
# tech_list = ['berthing', 'navigation', 'monitoring']

def main():
    '''
    ## Autonomous Ship Transition Simulator
    '''
    img = Image.open('fig/logo.png')
    st.sidebar.image(img, width = 300)

    st.markdown('#### 1. Scenario Setting')
    
    st.write('1.1 Basic Setting')
    casename = st.text_input('Casename', value='test_0503')
    start_year, end_year = st.slider('Simulation Year', 2020, 2070, (2022, 2050))
    numship_init = st.slider('Initial Number of ships[ship]', 1, 10000, 3000)
    numship_growth = st.slider('Annual growth rate of ship demand[-]', 0.90, 1.10, 1.00)
    ship_age = 25  # st.slider('Average Ship Lifeyear', 20, 30, 25)
    dt_year = 50  # st.slider('Interval for Reset parameters[year]', 1, 50, 50)

    st.write('1.2 Additional Setting')
    Mexp_to_production_loop = st.checkbox('Include effect of Manufacturing experience to Production cost', value = True)
    Oexp_to_TRL_loop = st.checkbox('Include effect of Operational experience to TRL', value = True)
    Oexp_to_safety_loop = st.checkbox('Include effect of Operational experience to Safety', value = True)
    ope_safety_b = st.slider('Accident reduction ratio b (y = ax**(-b))', 0.0, 1.0, 0.2)
    ope_TRL_factor = st.number_input('Operational experience R&D value (USD/times)', value = 10000)
    animation = st.checkbox('Output animation', value = False)
    uncertainty = st.checkbox('Set Uncertainty', value = False)
    fuel_rate = st.slider('Fuel rate (times)', 0, 5, 1)
    
    ship_size = st.selectbox('Ship size (DWT)', (499, 80000))
    cost = 'cost_' + str(ship_size)
    
    share_rate_O = st.slider('Sharing ratio of operational experience', 0.0, 1.0, 1.0)
    share_rate_M = st.slider('Sharing ratio of Manufacturing experience', 0.0, 1.0, 1.0)
    crew_cost_rate = st.slider('Crew Cost rate', 1.0, 2.0, 1.0)
    insurance_rate = st.slider('Insurance Cost Discount rate', 0.0, 1.0, 0.0)
    retrofit = st.checkbox('Consider retrofit?', value = False)
    retrofit_cost = st.number_input('Retrofit Cost [USD]', value = 30000)
    retrofit_limit = st.number_input('Retrofit limit per year [ship/year]', value = 100)
    
    st.sidebar.markdown('## 2. Agent Parameter Setting')
    
    st.sidebar.markdown('### 2.1 Ship Owner')
    st.sidebar.write("Parameters for ship adoption")
    economy = 1  # st.sidebar.slider('Profitability weight[-]', 0.0, 1.0, 1.0)
    safety = st.sidebar.slider('Safety weight Compared to Profitability', 0, 10, 1)
    estimated_loss = st.sidebar.number_input('Estimated Accident Loss Amount [USD/year]', value = 34000000) 
    
    st.sidebar.markdown('### 2.2 Manufacturer (R&D Investor))')
    st.sidebar.write("Technology type and Amount of investment")    
    invest_tech = st.sidebar.selectbox("Investment Strategy", ["All", "Berth", "Navi", "Moni"])
    invest_amount = st.sidebar.number_input('Investment Amount [USD/year]', value = 5000000)
    # invest_berth = st.sidebar.slider('Investment Amount (Berth)',0,2000000,2000000)
    # invest_navi = st.sidebar.slider('Investment Amount (Navi)',0,2000000,2000000)
    # invest_moni = st.sidebar.slider('Investment Amount (Moni)',0,2000000,2000000)

    st.sidebar.markdown('### 2.3 Policy Maker')
    st.sidebar.write("Type and amount of subsidy")
    subsidy_RandD = st.sidebar.number_input('Subsidy Amount (R&D)[USD/year]', value = 5000000)
    subsidy_Adoption = st.sidebar.number_input('Subsidy Amount (Adoption)[USD/year]', value = 0)
    subsidy_Experience = st.sidebar.number_input('Subsidy Amount for Prototyping [USD/year]', value = 0)
    trial_times = 1  # number of trials for getting one experience
    TRLreg = st.sidebar.selectbox('TRL regulation (minimum TRL for deployment)', (8, 7))

    # Set scenario and cost, ship, spec, tech parameters
    set_scenario(
        start_year, end_year, numship_init, numship_growth, ship_age, 
        economy, safety, estimated_loss, subsidy_RandD, subsidy_Adoption, TRLreg, 
        Mexp_to_production_loop, Oexp_to_TRL_loop, Oexp_to_safety_loop,
        ship_size)
    scenario_yml = get_yml('scenario')
    current_fleet, num_newbuilding = get_scenario(scenario_yml)

    # Set parameters (cost, tech and ship spec)
    set_tech(ope_safety_b, ope_TRL_factor)
    cost_yml = get_yml(cost)
    tech_yml = get_yml('tech')
    ship_spec_yml = get_yml('ship_spec')
    tech, param = get_tech_ini(tech_yml, uncertainty)
    select_index = []

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
    
    # Set dataframe for output
    fleet = make_dataframe_for_output(start_year, end_year, config_list)
    building = copy.copy(fleet)
    
    # Start Simulation
    if 'Year' not in st.session_state:
        st.session_state['Year'] = start_year
    
    st.sidebar.write("## 3. Run Simulation")
    next_step = st.sidebar.button('Start/Restart')
    if next_step:
        if st.session_state['Year'] == start_year:
            st.write("Simulation Started!")
        else:
            # Read temporary saved parameters
            spec = pd.read_csv('csv/spec'+casename+'.csv', index_col=0)
            Owner.fleet = pd.read_csv('csv/fleet'+casename+'.csv', index_col=0)
            tech_accum = pd.read_csv('csv/tech'+casename+'.csv', index_col=0)
            tech = tech_accum[-(len(tech_yml)-1):].drop('year', axis=1)
        
        sim_year=st.session_state.Year
        st.write('Simulation from '+str(sim_year)+' to '+str(min(end_year,sim_year+dt_year-1)))         
        
        # Annual iteration           
        for i in range(sim_year-start_year, min(end_year-start_year+1,sim_year-start_year+dt_year), 1):    
            Manufacturer.reset(invest_tech,invest_amount)
            Regulator.reset(subsidy_RandD, subsidy_Adoption, subsidy_Experience, trial_times)

            # Regulator (Subsidy for Manufacturer) (Increase the investment amount)
            Regulator.subsidize_investment(Manufacturer)
            
            # Manufacturer (R&D (Investment))
            tech = Manufacturer.invest(tech, Regulator)
            
            # World (Technology Development)
            tech = calculate_tech(tech, param, Owner.fleet, ship_age, share_rate_O, share_rate_M, start_year+i-1)
            tech, acc_navi_semi = calculate_TRL_cost(tech, param, Mexp_to_production_loop, Oexp_to_TRL_loop, Oexp_to_safety_loop)
            
            # World (Cost Reduction and Safety Improvement)
            spec_current = calculate_cost(ship_spec_yml, cost_yml, start_year+i, tech, acc_navi_semi, config_list, fuel_rate, crew_cost_rate, insurance_rate)
            
            # Ship Owner (Adoption and Purchase)
            select = Owner.select_ship(spec_current, tech, TRLreg)
            Owner.purchase_ship(config_list, select, i, start_year)
            select_index.append(select) # tentative

            # Regulator (Subsidy for Adoption)
            if subsidy_Adoption > 0:
                Regulator.select_for_sub_adoption(spec_current, tech, TRLreg)
                Owner.purchase_ship_with_adoption(spec_current, config_list, select, tech, i, TRLreg, Regulator, start_year)

            # Ship Owner (Retrofit)
            if retrofit:
                Owner.select_retrofit_ship(spec_current, tech, TRLreg, ship_age, retrofit_cost, config_list, i, start_year, retrofit_limit)

            # Regulator (Grand Challenge)
            if subsidy_Experience > 0:
                Regulator.subsidize_experience(tech, TRLreg)

            # Ship Owner (Scrap)
            Owner.scrap_ship(ship_age, i, start_year)
            
            for config in config_list:
                fleet.at[start_year+i, config] = ((Owner.fleet['is_operational'] == True) & (Owner.fleet['config'] == config)).sum()
                building.at[start_year+i, config] = ((Owner.fleet['year_built'] == start_year+i) & (Owner.fleet['config'] == config) & ((Owner.fleet['misc'] == 'newbuilt') | (Owner.fleet['misc'] == 'newbuilt_subsidized'))).sum()

            # Show Tradespace
            if (start_year+i)%10 == 0:
                show_tradespace_general(spec_current.OPEX+spec_current.CAPEX+spec_current.VOYEX+spec_current.AddCost,
                                        spec_current.accident_berth+spec_current.accident_navi+spec_current.accident_moni, 
                                        "Total Cost(USD/year)", "Accident Ratio (-)", "Profitability vs Safety at "+str(start_year+i), 
                                        spec_current.config.values.tolist(), select, DIR_FIG)

            spec = spec_current if st.session_state['Year'] == start_year and i == 0 else pd.concat([spec, spec_current])
            tech_year = pd.concat([pd.DataFrame({'year': [start_year+i]*3}), tech], axis = 1)            
            tech_accum = tech_year if st.session_state['Year'] == start_year and i == 0 else pd.concat([tech_accum, tech_year])

            subsidy_df = pd.DataFrame({'R&D': Regulator.sub_RandD, 'Adoption': Regulator.sub_Adoption, 
                          'Select_ship': Regulator.sub_select, 'Subsidy_used': Regulator.sub_used, 
                          'Subsidy_per_ship': Regulator.sub_per_ship, 'All_investment': Manufacturer.invest_used}, index=[i+start_year])
            subsidy_accum = subsidy_df if st.session_state['Year'] == start_year and i == 0 else pd.concat([subsidy_accum, subsidy_df])

        # proceed year
        st.session_state.Year += dt_year
        
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
        
        if animation:
            show_tradespace_anime(totalcost, accident, 
                                "Total Cost(USD/year)", "Accident Ratio (-)", 
                                config_list, select_index, DIR_FIG, config_list)
        
        # Save Tentative File for iterative simulation (and final results)
        spec.to_csv(DIR+'/spec_'+casename+'.csv')
        tech_accum.to_csv(DIR+'/tech_'+casename+'.csv')
        Owner.fleet.to_csv(DIR+'/fleet_'+casename+'.csv')
        subsidy_accum.to_csv(DIR+'/subsidy_'+casename+'.csv')
        
        """
        Fleet Breakdown [ship]
        """
        show_stackplot(fleet, config_list, "Number of ships for each autonomous level", DIR_FIG)
        # show_stacked_bar(fleet, config_list, "Number of ships for each autonomous level", DIR_FIG)
        
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


        """
        Cost of Each Vessel [USD]
        """
        # num_ship = fleet[config_list].sum(axis=1)
        show_stackplot(fleet, fleet[cost_list], "Cost of Each Vessel [USD]", DIR_FIG)
        # show_stacked_bar(fleet, fleet[cost_list], "Cost of Each Vessel [USD]", DIR_FIG)
        
        """
        Cost of Each Vessel (detailed) [USD]
        """
        show_stackplot(fleet, fleet[cost_detail_list], "Cost of Each Vessel (detailed) [USD]", DIR_FIG)
        #show_stacked_bar(fleet, fleet[cost_detail_list], "Cost of Each Vessel (detailed) [USD]", DIR_FIG)        

        """
        Number of Expected Accidents [num of accidents]
        """
        show_stackplot(fleet, fleet[accident_list], "Number of Expected Accidents [num of accidents]", DIR_FIG)
        #show_stacked_bar(fleet, fleet[accident_list], "Number of Expected Accidents [num of accidents]", DIR_FIG)
        
        """
        Number of Seafarers [people]
        """
        show_stackplot(fleet, fleet[crew_list], "Number of Seafarers [people]", DIR_FIG)        
        #show_stacked_bar(fleet, fleet[crew_list], "Number of Seafarers [people]", DIR_FIG)        
        
        """
        Profit of the Industry (Difference from 'existing vessel' fleet) [USD] and Subsidy used [USD]

        """ 
        show_linechart_two(fleet.index, fleet['Profit'], subsidy_accum['Subsidy_used'], "Profit and subsidy [USD]", "Profit of the Industry", DIR_FIG)
        
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
            z.write('yml/'+cost+'.yml')
            z.write('yml/ship_spec.yml')

        if st.session_state.Year >= end_year:
            st.write('Simulation Done!!')
            st.session_state['Year'] = start_year
        
        if fleet['FULL'].sum() > 0:
            intro_year_full = int(fleet[fleet['FULL'] > 0].index[0])
        else:
            intro_year_full = 'NaN'

        intro_year_auto = end_year
        for i in range(1,11,1):
            if fleet[config_list[i]].sum() > 0:
                intro_year_tmp = int(fleet[fleet[config_list[i]] > 0].index[0])
                intro_year_auto = intro_year_tmp if intro_year_tmp < intro_year_auto else intro_year_auto 
        
        final = {'Autonomous Ship introduction (year)': intro_year_auto,
                 'Full Autonomous Ship introduction (year)': intro_year_full,
                #  'Autonomous Ship introduction ratio at 2040 (-)': autoratio_2040,
                #  'Full Autonomous Ship introduction ratio at 2040 (-)': fullratio_2040,
                 'Total Profit (USD)': int(fleet['Profit'].sum()), 
                 'Total Investment for R&D (incl. Subsidy) (USD)': int(subsidy_accum['All_investment'].sum()),
                 'Total Subsidy (USD)': int(subsidy_accum['Subsidy_used'].sum()), 
                 'ROI (R&D Expenditure based)': fleet['Profit'].sum()/subsidy_accum['All_investment'].sum(),
                 'ROI (Subsidy based)': fleet['Profit'].sum()/subsidy_accum['Subsidy_used'].sum(),
                 'Average number of Accident (case/year)': int(fleet[accident_list].sum(axis=1).sum()/(end_year-start_year+1)),
                 'Average number of seafarer (person/year)': int(fleet[crew_list].sum(axis=1).sum()/(end_year-start_year+1)),
                 'R&D Need TRL': param.rd_need_TRL}
        st.write(final)

        '''
        ### Download Results
        '''
        st.download_button('Download result files (compressed)', open(DIR+'/'+casename+'.zip', 'br'), casename+'.zip')

if __name__ =='__main__':
    main()