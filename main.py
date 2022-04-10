from curses import A_ALTCHARSET
from invest import investment
from output import show_tradespace, show_output
from adopt import select_ship
from input import *
from result import *

import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import csv

def main(casename = 'test_0331'):
#    set_scenario(casename, start_year, end_year, 5200, 1.01, 20)
#    reset_spec(casename) 
    
    # # Import YAML files and check the input data
    # demand, ship_age = get_scenario('scenario_'+casename)
    # cost = get_cost(demand.Year, 'cost_'+casename)
    # spec = get_spec('spec_'+casename)

    # # Select Ship and show Tradespace
    # select = [0] * len(cost.Year)
    # labels = []

    # Select Ship
    #@title What will you prioritize for selecting ships?　{ run: "auto" }
    economy = 1 #@param {type:"slider", min:0, max:1, step:0.1}
    environment = 0 #@param {type:"slider", min:0, max:1, step:0.1}
    safety = 0 #@param {type:"slider", min:0, max:1, step:0.1}
    labour = 0 #@param {type:"slider", min:0, max:1, step:0.1}

    button = st.button('Next Step')
    st.write(button)
    
    # ii = 0
    # while not button:
    #     if ii == len(cost.Year):
    #         break

    #     st.write('Push the button!'+str(ii))
    #     if button:
    #         button = False
    #         ii += 1
    #         break        
    # st.write(ii)


    for i in range(len(cost.Year)):
        select[i], annual_cost, opex_sum, capex_sum, ac_loss, sf_sum, fuel_cost = select_ship(spec, cost, i, ship_age, economy, environment, safety, labour)
                
        # # Invest Technology and Adoption Model Change
        # delay = 3 # Tentative
        # if cost.Year[i]%5==0 and i+delay<len(cost.Year):
            
            # # Invest Technology
            # invest = input("Set invest option at "+str(cost.Year[i])+" (Comm/Situ/Plan/Exec): ")
            # investment(cost, cost.Year[i], delay, invest)
            
            # # Adoption Model Change
            # economy = float(input("Parameter for Economy (0-1): "))
            # environment = float(input("Parameter for Environment (0-1): "))
            # safety = float(input("Parameter for Safety (0-1): "))
            # labour = float(input("Parameter for Labour (0-1): "))

        # # Get Tradespace
        # if cost.Year[i]%10==0:
        #     show_tradespace(cost, spec, i, annual_cost, ac_loss, sf_sum, fuel_cost)    

    # Initiate result dataframe and calculate the number of annual newbuildings and scraps
    result, conv_ship = initiate_result(demand,spec,cost,select,ship_age)

    # Selected Ship labeling
    labels1 = selected_ship_label(spec,select,conv_ship)

    # Add and calculate Other Parameters
    result_addrow(result)
    calculate_result(result,spec,cost,demand,ship_age,labels1)

    # Get Possible roadmap for Autonomous Ship Transition
    # show_output(result, labels1, spec)
    st.write(result)
    st.line_chart(result)        

if __name__ =='__main__':
    '''
    ## Autonomous Ship Transition Simulator
    By using this simulator, xoxoxo.
    '''
    img = Image.open('/Users/nakashima/Pictures/logo.png')
    st.image(img, width = 200)
            
    start_year = st.selectbox('Start Year', list(range(2022,2030)))
    end_year = st.selectbox('End Year', list(range(2040,2071)))
    casename = st.text_input("Casename (e.g. test_0331)")

    # button_start = st.button("Start")
    # # Import YAML files and check the input data
    # if button_start:
    #     set_scenario(casename, start_year, end_year, 5200, 1.01, 20)
    #     demand, ship_age = get_scenario('scenario_'+casename)
    #     cost = get_cost(demand.Year, 'cost_'+casename)
    #     spec = get_spec('spec_'+casename)
    #     st.dataframe(spec)        
    #     select = [0] * len(cost.Year)
    #     st.write("Simulation Started!")
            
    # Side Bar
    st.sidebar.markdown('### What will you prioritize for selecting ships?')
    st.sidebar.write("Choose TechAdo Model Parameters")
    economy = st.sidebar.slider('Economy',0.0,1.0,1.0)
    environment = st.sidebar.slider('Environment',0.0,1.0,0.0)
    safety = st.sidebar.slider('Safety',0.0,1.0,0.0)
    labour = st.sidebar.slider('Labour',0.0,1.0,0.0)

    st.sidebar.markdown('### What kind of technology will you invest in?')
    st.sidebar.write("Choose a technology (and amount ... TBD)")    
    invest = st.sidebar.selectbox("Investment",["Situ","Plan","Exec","Comm"])

    # sim_year = start_year
    if 'Year' not in st.session_state:
        st.session_state['Year'] = start_year

    age = 20
    dt_year = 5
    
#    for ii in range((end_year-start_year)//dt_year+1):
    next_step = st.sidebar.button('Next Step')
    if next_step:
        if st.session_state['Year'] == start_year:
            set_scenario(casename, start_year, end_year, 5200, 1.01, age)
            demand, ship_age = get_scenario('scenario_'+casename)
            cost = get_cost(demand.Year, 'cost_'+casename)
            spec = get_spec('spec_'+casename)
            st.dataframe(spec)        
            select = [0] * len(cost.Year)
            st.write("Simulation Started!")
        else:
            demand = pd.read_csv('csv/demand'+casename+'.csv')
            ship_age = age
            cost = pd.read_csv('csv/cost'+casename+'.csv')
            spec = pd.read_csv('csv/spec'+casename+'.csv')
            # select = pd.read_csv('csv/select'+casename+'.csv')    
            with open('csv/select'+casename+'.csv', 'r') as csv_file:
                csv_reader = csv.reader(csv_file)
                select = list(csv_reader)
                select = list(map(int,select[0]))
                        
        st.write('Simulation from '+str(st.session_state.Year)) 
        st.write('Economy: '+str(economy), 'Environment: '+str(environment), 'Safety: '+str(safety), 'Labour: '+str(labour))
        
        # Invest Technology and Adoption Model Change
        # for i in range(len(cost.Year)):
        sim_year=st.session_state.Year
        
        for i in range(sim_year-start_year, min(end_year-start_year,sim_year-start_year+dt_year), 1):
            select[i], annual_cost, opex_sum, capex_sum, ac_loss, sf_sum, fuel_cost = select_ship(spec, cost, i, ship_age, economy, environment, safety, labour)
            delay = 0 # Tentative
            # if i+delay<len(cost.Year):
            investment(cost, i, delay, invest)
            # # Get Tradespace
            show_tradespace(cost, spec, i, annual_cost, ac_loss, sf_sum, fuel_cost)

        st.session_state.Year += dt_year
        demand.to_csv('csv/demand'+casename+'.csv')
        cost.to_csv('csv/cost'+casename+'.csv')
        spec.to_csv('csv/spec'+casename+'.csv')
        # select.to_csv('csv/select'+casename+'.csv')
        with open('csv/select'+casename+'.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(select)

    # Initiate result dataframe and calculate the number of annual newbuildings and scraps
        if st.session_state.Year >= end_year:
            st.write('Simulation Done!!!!!')
            
        result, conv_ship = initiate_result(demand,spec,cost,select,ship_age)
        # Selected Ship labeling
        labels1 = selected_ship_label(spec,select,conv_ship)
        # Add and calculate Other Parameters
        result_addrow(result)
        calculate_result(result,spec,cost,demand,ship_age,labels1)
        # Get Possible roadmap for Autonomous Ship Transition
        show_output(result, labels1, spec)
        # st.write(result)
        # st.line_chart(result)

    # main('test_0331')