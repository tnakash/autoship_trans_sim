from Agent import ShipOwner, Investor, PolicyMaker
from output import show_stackplot, show_tradespace_general, show_linechart, show_stackplot
from input import get_yml, get_scenario, set_scenario, set_tech
from calculate import calculate_cost, calculate_tech, get_tech_ini, calculate_TRL_cost

import streamlit as st
import pandas as pd
import os

from PIL import Image
import zipfile
import glob

def main():    
    img = Image.open('fig/logo.png')
    st.sidebar.image(img, width = 300)
    st.markdown('#### 1. Scenario Setting')

    # Selecting params for simulation scenario
    st.write('1.1 Basic Setting')
    casename = st.text_input("Casename", value="test_0503")
    start_year, end_year = st.slider('Simulation Year',2020,2070,(2022,2050))
    numship_init = st.slider('Initial Number of ships[ship]',1,10000,1000)
    numship_growth = st.slider('Annual growth rate of ship demand[-]',0.90,1.10,1.01)
    ship_age = 25 # st.slider('Average Ship Lifeyear',20,30,25)
    dt_year = 50 # st.slider('Interval for Reset parameters[year]',1,50,50)
    
    # Agent Parameter Setting
    st.sidebar.markdown('## 2. Agent Parameter Setting')
    
    # Selecting params for Shipowners
    st.sidebar.markdown('### 2.1 Ship Owner')
    st.sidebar.write("Parameters for ship adoption")
    economy = 1 # st.sidebar.slider('Profitability weight[-]',0.0,1.0,1.0)
    safety = st.sidebar.slider('Safety weight Compared to Profitability',1,10,1)
    estimated_loss = st.sidebar.number_input('Estimated Accident Loss Amount [USD/year]',value=34000000) # st.sidebar.number_input('Estimated average accident loss[USD]', value=10000000)
    
    # Selecting params for Investors        
    st.sidebar.markdown('### 2.2 Manufacturer (R&D Investor))')
    st.sidebar.write("Technology type and Amount of investment")    
    invest_tech = st.sidebar.selectbox("Investment Strategy",["All","Berth","Navi","Moni"])
    # invest_amount = st.sidebar.slider('Investment Amount [USD/year]',0,1000000,500000)
    invest_amount = st.sidebar.number_input('Investment Amount [USD/year]',value=500000)
    # invest_berth = st.sidebar.slider('Investment Amount (Berth)',0,2000000,2000000)
    # invest_navi = st.sidebar.slider('Investment Amount (Navi)',0,2000000,2000000)
    # invest_moni = st.sidebar.slider('Investment Amount (Moni)',0,2000000,2000000)

    # Selecting params for Policy Makerss        
    st.sidebar.markdown('### 2.3 Policy Maker')
    st.sidebar.write("Type and amount of subsidy")
    # subsidy_type = st.sidebar.selectbox("Subsidy for",["R&D","Adoption"])
    # subsidy_amount = st.sidebar.slider('Subsidy Amount',0,200000,100000)
    # subsidy_RandD = st.sidebar.slider('Subsidy Amount (R&D)[USD/year]',0,20000000,10000000)
    subsidy_RandD = st.sidebar.number_input('Subsidy Amount (R&D)[USD/year]', value=10000000)
    # subsidy_Adoption =  st.sidebar.slider('Subsidy Amount (Adoption)[USD/year]',0,20000000,0)
    subsidy_Adoption = st.sidebar.number_input('Subsidy Amount (Adoption)[USD/year]', value=0)
    # if subsidy_Adoption > 0:
    #     sub_list = st.sidebar.multiselect('Give subsidy from Config. ', range(12), default=range(1,12))
    TRLreg = st.sidebar.selectbox('TRL regulation (minimum TRL for deployment)', (7, 8))

    st.write('1.2 Additional Setting')    
    Mexp_to_production_loop = st.checkbox('Include effect of Manufacturing experience to Production cost',value=True)
    Oexp_to_TRL_loop = st.checkbox('Include effect of Operational experience to TRL',value=True)
    Oexp_to_safety_loop = st.checkbox('Include effect of Operational experience to Safety',value=True)
    
    # Additional Parameter Setting
    ope_safety_b = st.slider('Accident reduction ratio b (y = ax**(-b))', 0.0,1.0,0.2)
    ope_TRL_factor = st.number_input('Operational experience R&D value (USD/times)', value=10000)
    set_tech(ope_safety_b, ope_TRL_factor)
    
    set_scenario(start_year, end_year, numship_init, numship_growth, ship_age, economy, safety, estimated_loss, subsidy_RandD, subsidy_Adoption, TRLreg, Mexp_to_production_loop, Oexp_to_TRL_loop, Oexp_to_safety_loop)
    # Get scenario from yml file (just made)    
    scenario_yml = get_yml('scenario')
    current_fleet, num_newbuilding = get_scenario(scenario_yml)

    # Set agents
    Owner = ShipOwner(economy, safety, current_fleet, num_newbuilding, estimated_loss)
    Manufacturer = Investor()
    Regulator = PolicyMaker()
    
    # Input from YML file
    cost_yml = get_yml('cost')
    tech_yml = get_yml('tech')
    ship_spec_yml = get_yml('ship_spec')
    tech, param = get_tech_ini(tech_yml)
    
    DIR = "result/"+casename
    if not os.path.exists(DIR):
        os.makedirs(DIR)
    
    DIR_FIG = "result/"+casename+'/fig'
    if not os.path.exists(DIR_FIG):
        os.makedirs(DIR_FIG)
    
    # # Write settings
    # other_params = pd.DataFrame({'economy': economy, 'safety': safety, 'estimated loss': estimated_loss, 'subsidy R&D': subsidy_RandD, 
    #         'subsidy adoption': subsidy_Adoption, 'TRL regulation': TRLreg, 'Manu Loop': Mexp_to_production_loop, 
    #         'Ope Loop (TRL)': Oexp_to_TRL_loop, 'Ope Loop (Safety)': Oexp_to_safety_loop},index=['value']).T
    # other_params.to_csv('csv/setting'+casename+'.csv')
    
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
            # spec_current = spec[-len(ship_spec_yml):]
            Owner.fleet = pd.read_csv('csv/fleet'+casename+'.csv', index_col=0)
            tech_accum = pd.read_csv('csv/tech'+casename+'.csv', index_col=0)
            tech = tech_accum[-(len(tech_yml)-1):].drop('year', axis=1)
        
        sim_year=st.session_state.Year
        st.write('Simulation from '+str(sim_year)+' to '+str(min(end_year,sim_year+dt_year-1)))         
        
        # Annual iteration           
        for i in range(sim_year-start_year, min(end_year-start_year+1,sim_year-start_year+dt_year), 1):    
            Manufacturer.reset(invest_tech,invest_amount)
            Regulator.reset(subsidy_RandD, subsidy_Adoption)
            # Regulator (Subsidy for Manufacturer) (Increase the investment amount)
            Regulator.subsidize_investment(Manufacturer)
            
            # Manufacturer (R&D (Investment))
            tech = Manufacturer.invest(tech, Regulator)
            
            # World (Technology Development)
            tech = calculate_tech(tech, param, Owner.fleet, ship_age)
            tech, acc_navi_semi = calculate_TRL_cost(tech, param, Mexp_to_production_loop, Oexp_to_TRL_loop, Oexp_to_safety_loop)
            
            # World (Cost Reduction and Safety Improvement)
            spec_current = calculate_cost(ship_spec_yml, cost_yml, start_year+i, tech, acc_navi_semi)
            
            # # Regulator (Subsidy for Adoption) NOT IN USE
            # if subsidy_Adoption > 0:
            #     spec_current = Regulator.subsidize_Adoption(spec_current,num_newbuilding.ship[i],sub_list)
            
            # Ship Owner (Adoption and Purchase)
            select = Owner.select_ship(spec_current, tech, TRLreg)
            Owner.purchase_ship(select, i)
            
            # Regulator (Subsidy for Adoption)
            if subsidy_Adoption > 0:
                Regulator.select_for_sub_adoption(spec_current, tech, TRLreg)
                Owner.purchase_ship_with_adoption(spec_current, select, tech, i, TRLreg, Regulator)

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
   
        # Save Tentative File for iterative simulation (and final results)
        
        spec.to_csv(DIR+'/spec_'+casename+'.csv')
        tech_accum.to_csv(DIR+'/tech_'+casename+'.csv')
        Owner.fleet.to_csv(DIR+'/fleet_'+casename+'.csv')
        subsidy_accum.to_csv(DIR+'/subsidy_'+casename+'.csv')
        building = Owner.fleet[Owner.fleet.year >= start_year]

        # Visualize results                        
        # """
        # Number of new shipbuilding[ship]
        # """
        building.set_index("year", inplace=True)
        # st.area_chart(building)
        
        Owner.fleet.set_index("year", inplace=True)
        fleet = building
        for i in range(start_year, end_year+1):
            fleet.loc[i,:] = Owner.fleet.loc[i-ship_age:i,:].sum()
        
        crew_list = ['NaviCrew', 'EngiCrew', 'Cook']
        cost_list = ['OPEX', 'CAPEX', 'VOYEX', 'AddCost']
        opex_list = ['crew_cost', 'store_cost', 'maintenance_cost', 'insurance_cost', 'general_cost', 'dock_cost']
        capex_list = ['material_cost', 'integrate_cost', 'add_eq_cost']
        voyex_list = ['port_call', 'fuel_cost_ME', 'fuel_cost_AE']
        addcost_list = ['SCC_Capex', 'SCC_Opex', 'SCC_Personal', 'Mnt_in_port']
        cost_detail_list = opex_list + capex_list + voyex_list + addcost_list 
        accident_list = ['accident_berth', 'accident_navi', 'accident_moni']
        config_list = ['config0', 'config1', 'config2', 'config3', 'config4', 'config5', 'config6', 'config7', 'config8', 'config9', 'config10', 'config11']

        """
        Fleet Breakdown [ship]
        """
        show_stackplot(fleet, config_list, "Number of ships for each autonomous level", DIR_FIG)
        
        for c in cost_list+accident_list+crew_list+['Profit'] + cost_detail_list:
            fleet[c] = 0
        
        for i in range(start_year, end_year+1):
            for c in cost_list:
                for s in config_list:
                    fleet[c][i] += fleet[s][i] * spec[(spec['year'] == i) & (spec['config'] == s)][c].mean()
                    fleet['Profit'][i] += fleet[s][i] * (spec[(spec['year'] == i) & (spec['config'] == 'config0')][c].mean() - spec[(spec['year'] == i) & (spec['config'] == s)][c].mean())
                    
            for c in accident_list:
                for s in config_list:
                    fleet[c][i] += fleet[s][i] * spec[(spec['year'] == i) & (spec['config'] == s)][c].mean()

            for c in crew_list:
                for s in config_list:
                    fleet[c][i] += fleet[s][i] * spec[(spec['year'] == i) & (spec['config'] == s)][c].mean()
        
            for c in cost_detail_list:
                for s in config_list:
                    fleet[c][i] += fleet[s][i] * spec[(spec['year'] == i) & (spec['config'] == s)][c].mean()


        """
        Cost of Each Vessel [USD]
        """
        # num_ship = fleet[config_list].sum(axis=1)
        show_stackplot(fleet, fleet[cost_list], "Cost of Each Vessel [USD]", DIR_FIG)
        
        """
        Cost of Each Vessel (detailed) [USD]
        """
        show_stackplot(fleet, fleet[cost_detail_list], "Cost of Each Vessel (detailed) [USD]", DIR_FIG)
        
        """
        Number of Expected Accidents [num of accidents]
        """
        show_stackplot(fleet, fleet[accident_list], "Number of Expected Accidents [num of accidents]", DIR_FIG)
        
        """
        Number of Seafarers [people]
        """
        show_stackplot(fleet, fleet[crew_list], "Number of Seafarers [people]", DIR_FIG)        
        
        """
        Profit of the Industry (Difference from 'existing vessel' fleet) [USD]
        """ 
        # st.line_chart(fleet['Profit'])
        show_linechart(fleet.index, fleet['Profit'], "Profit [USD]", "Profit of the Industry", DIR_FIG)
        
        """
        Subsidy used [USD]
        """         
        # st.line_chart(subsidy_accum['Subsidy_used'])
        show_linechart(subsidy_accum.index, subsidy_accum['Subsidy_used'], "Subsidy used [USD]", "Subsidy used", DIR_FIG)
        
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
        TRL = pd.DataFrame({"Berth": Berth.TRL, "Navi": Navi.TRL, "Moni": Moni.TRL})
        st.line_chart(TRL)
        Integ_cost = pd.DataFrame({"Berth_Integration_Cost": Berth.integ_factor, "Navi_Integration_Cost": Navi.integ_factor, "Moni_Integration_Cost": Moni.integ_factor})
        st.line_chart(Integ_cost)
        Rexp = pd.DataFrame({"Berth_Rexp": Berth.Rexp, "Navi_Rexp": Navi.Rexp, "Moni_Rexp": Moni.Rexp})
        st.line_chart(Rexp)
        Mexp = pd.DataFrame({"Berth_Mexp": Berth.Mexp, "Navi_Mexp": Navi.Mexp, "Moni_Mexp": Moni.Mexp})
        st.line_chart(Mexp)
        Oexp = pd.DataFrame({"Berth_Oexp": Berth.Oexp, "Navi_Oexp": Navi.Oexp, "Moni_Oexp": Moni.Oexp})
        st.line_chart(Oexp)
        
        """
        Accident of each type of autonomous ship ≒ [accidents/year]
        """
        Tech_accident = pd.DataFrame({"Berth_accident": Berth.accident_ratio, "Navi_accident": Navi.accident_ratio, "Moni_accident": Moni.accident_ratio})
        st.line_chart(Tech_accident)
        # results_accident =get_resultsareachart(Tech_accident)
        # st.altair_chart(results_accident, use_container_width=True)
        
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
            z.write('yml/cost.yml')
            z.write('yml/ship_spec.yml')

        if st.session_state.Year >= end_year:
            st.write('Simulation Done!!')
            st.session_state['Year'] = start_year
        
        final = {'Full Autonomous Ship introduction (year)': int(fleet[fleet['config11'] > 0].index[0]),
                 'Total Profit [USD]': int(fleet['Profit'].sum()), 
                 'Total Investment (incl. Subsidy) [USD]': int(subsidy_accum['All_investment'].sum()),
                 'Total Subsidy [USD]': int(subsidy_accum['Subsidy_used'].sum()), 
                 'Total Accident [times]': int(fleet[accident_list].sum(axis=1).sum())}
        st.write(final)

        '''
        ### Download Results
        '''
        st.download_button('Download result files (compressed)',open(DIR+'/'+casename+'.zip', 'br'), casename+'.zip', disabled=True)

if __name__ =='__main__':
    '''
    ## Autonomous Ship Transition Simulator
    '''
    main()