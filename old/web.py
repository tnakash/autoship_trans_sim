from Agent import ShipOwner, Investor, PolicyMaker

from output import show_tradespace, show_output
from input import *
from result import *

from calculate import calculate_cost, calculate_tech, get_tech_ini, calculate_TRL_cost

import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import csv

import altair as alt
import pandas as pd
import matplotlib.pyplot as plt

def stream():    
    img = Image.open('/Users/nakashima/Pictures/logo.png')
    st.image(img, width = 300)
    st.markdown('#### Scenario Setting')

    casename = st.text_input("Casename", value="test_0503")
    # sim_type = st.button("Input Iteratively")

    # Selecting params for simulation scenario    
    # if sim_type:
    start_year, end_year = st.slider('Simulation Year',2020,2070,(2022,2050))
    numship_init = st.slider('Initial Number of ships',300,10000,5200)
    numship_growth = st.slider('Annual growth of the number of ships',0.90,1.10,1.01)
    ship_age = st.slider('Average Ship Lifeyear',20,30,25)
    dt_year = st.slider('Interval for Reset parameters',1,50,50)
    set_scenario(casename, start_year, end_year, numship_init, numship_growth, ship_age)
    
    # set_scenario(casename, start_year, end_year, numship_init, numship_growth, age)
    scenario_yml = get_yml('scenario')
    demand, ship_age, current_fleet, num_newbuilding = get_scenario(scenario_yml)
    
    # Selecting params for Shipowners
    st.sidebar.markdown('## Agent Parameter Setting')
    st.sidebar.markdown('### Ship Owner')
    st.sidebar.write("Parameters for ship adoption")
    economy = st.sidebar.slider('Economy',0.0,1.0,1.0)
    safety = st.sidebar.slider('Safety',0.0,1.0,0.0)
    # environment = st.sidebar.slider('Environment',0.0,1.0,0.0)
    # labour = st.sidebar.slider('Labour',0.0,1.0,0.0)    

    # Selecting params for Investors        
    st.sidebar.markdown('### Manufacturer (R&D Investor))')
    st.sidebar.write("Technology type and Amount of investment")    
    invest_tech = st.sidebar.selectbox("Investment for",["Berth","Navi","Moni"])
    invest_amount = st.sidebar.slider('Investment Amount',1,200,100)

    # Selecting params for Governments        
    st.sidebar.markdown('### Policy Maker')
    st.sidebar.write("Type and amount of subsidy")    
    subsidy_type = st.sidebar.selectbox("Subsidy for",["R&D","Adoption"])
    subsidy_amount = st.sidebar.slider('Subsidy Amount',1,200,100)

    # Reset agents
    Owner = ShipOwner(economy, safety, current_fleet, num_newbuilding)
    Manufacturer = Investor()
    Regulator = PolicyMaker()
    
    # Owner.reset(economy, environment, safety, labour)
    Manufacturer.reset(invest_tech,invest_amount)
    Regulator.reset(subsidy_type, subsidy_amount)

    # select = [0] * len(num_newbuilding.year) # len(cost.Year)

    # Input YML file
    cost_yml = get_yml('cost')
    tech_yml = get_yml('tech')
    ship_spec_yml = get_yml('ship_spec')
    tech = get_tech_ini(tech_yml)
    
    # sim_year = start_year
    if 'Year' not in st.session_state:
        st.session_state['Year'] = start_year
    
#    for ii in range((end_year-start_year)//dt_year+1):
    # next_step = st.sidebar.button('Next Step')
    next_step = st.sidebar.button('Start')
    if next_step:
        if st.session_state['Year'] == start_year:
            # set_scenario(casename, start_year, end_year, numship_init, numship_growth, age)
            # demand, ship_age = get_scenario('scenario_'+casename)
            # base_cost = get_cost_df(demand.Year, cost_yml)
            # spec = get_spec('spec_'+casename)
            st.write("Simulation Started!")
        else:
            # fleet = pd.read_csv('csv/fleet'+casename+'.csv')
            tech_accum = pd.read_csv('csv/tech'+casename+'.csv')
            spec = pd.read_csv('csv/spec'+casename+'.csv')

            # ship_age = age
            # # select = pd.read_csv('csv/select'+casename+'.csv')    
            # with open('csv/select'+casename+'.csv', 'r') as csv_file:
            #     csv_reader = csv.reader(csv_file)
            #     select = list(csv_reader)
            #     select = list(map(int,select[0]))
                        
        st.write('Simulation from '+str(st.session_state.Year)) 
        
        # Invest Technology and Adoption Model Change
        sim_year=st.session_state.Year
        
        # Annual iteration           
        for i in range(sim_year-start_year, min(end_year-start_year+1,sim_year-start_year+dt_year), 1):
            
            Regulator.subsidize_Investment(Manufacturer)
            
            tech = Manufacturer.invest(tech)
            tech = calculate_tech(tech, Owner.fleet, i)
            tech = calculate_TRL_cost(tech)
            
            spec_current = calculate_cost(ship_spec_yml, cost_yml, start_year+i, tech)
            spec_current = Regulator.subsidize_Adoption(spec_current)
                        
            select = Owner.select_ship(spec_current)
            Owner.purchase_ship(select, i)
            show_tradespace(i, spec_current.OPEX, spec_current.CAPEX, spec_current.VOYEX, spec_current.AddCost, select)
            
            spec = spec_current if st.session_state['Year'] == start_year and i == 0 else pd.concat([spec, spec_current])

            tech_year = pd.concat([pd.DataFrame({'year': [start_year+i]*3}), tech], axis = 1)            
            tech_accum = tech_year if st.session_state['Year'] == start_year and i == 0 else pd.concat([tech_accum, tech_year])

        st.session_state.Year += dt_year
        # Save CSV File
        demand.to_csv('csv/demand'+casename+'.csv')
        spec.to_csv('csv/spec'+casename+'.csv')
        tech_accum.to_csv('csv/tech'+casename+'.csv')
        Owner.fleet.to_csv('csv/fleet'+casename+'.csv')
                        
        """
        Fleet Transition
        """
        st.write("Fleet Transition")
        Owner.fleet.set_index("year", inplace=True)
        st.area_chart(Owner.fleet)

        """
        Technology Development
        """
        st.write("Technology Development")

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
        Tech_cost = pd.DataFrame({"Berth_Oexp": Berth.tech_cost, "Navi_Oexp": Navi.tech_cost, "Moni_Oexp": Moni.tech_cost})
        st.line_chart(Tech_cost)
        Rexp = pd.DataFrame({"Berth_Rexp": Berth.Rexp, "Navi_Rexp": Navi.Rexp, "Moni_Rexp": Moni.Rexp})
        st.line_chart(Rexp)
        Mexp = pd.DataFrame({"Berth_Mexp": Berth.Mexp, "Navi_Mexp": Navi.Mexp, "Moni_Mexp": Moni.Mexp})
        st.line_chart(Mexp)
        Oexp = pd.DataFrame({"Berth_Oexp": Berth.Oexp, "Navi_Oexp": Navi.Oexp, "Moni_Oexp": Moni.Oexp})
        st.line_chart(Oexp)
        
        """
        Accident of each type of autonomous ship
        """
        st.write("Accident Ratio")
        Tech_accident = pd.DataFrame({"Berth_accident": Berth.accident_ratio, "Navi_accident": Navi.accident_ratio, "Moni_accident": Moni.accident_ratio})
        st.line_chart(Tech_accident)
        
        """
        Cost of each type of autonomous ship
        """        
        for i in range (12): # reset afterwards
            Config = spec[spec['config'] == 'Config'+str(i)]
                        
            fig = plt.figure(figsize=(20,10)) #.gca()
            ax = fig.add_subplot(1, 1, 1)
            cost_list = ['OPEX', 'CAPEX', 'VOYEX', 'AddCost'] # この辺使い回す・・・
            ax.stackplot(Config.year, Config.OPEX, Config.CAPEX, Config.VOYEX, Config.AddCost, labels=cost_list)
            ax.set_title("Cost for Each Vessel")
            ax.legend(loc="upper right")
            st.pyplot(fig)

        # fig = plt.figure(figsize=(20,10)) #.gca()
        # ax = fig.add_subplot(1, 1, 1)
        # label_config = ['config0', 'config1', 'config2', 'config3', 'config4', 'config5', 'config6', 'config7', 'config8', 'config9', 'config10', 'config11']
        # ax.stackplot(Owner.fleet.year, [Owner.fleet[s] for s in label_config], labels=label_config)
        # ax.set_title("Number of ships for each autonomous level")
        # ax.legend(loc="upper left")
        # st.pyplot(fig)
        
        # with open('csv/select'+casename+'.csv', 'w', newline='') as f:
        #     writer = csv.writer(f)
        #     writer.writerow(select)
            
        # result, conv_ship = initiate_result(demand,spec,cost,select,ship_age)
        
        # select_tmp = select[:st.session_state.Year-start_year]
                
        # labels1 = selected_ship_label(spec,select_tmp,conv_ship) # select
        
        # # Add and calculate Other Parameters
        # result_addrow(result)
        # calculate_result(result,spec,cost,demand,ship_age,labels1)

        # result_tmp = result[:st.session_state.Year-start_year]
        # show_output(result_tmp, labels1, spec)

        if st.session_state.Year >= end_year:
            st.write('Simulation Done!!!!!')