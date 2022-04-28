from curses import A_ALTCHARSET
from invest import Investor
from adopt import ShipOwner

from output import show_tradespace, show_output
from input import *
from result import *

import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import csv

def stream(age,dt_year):
    Owner = ShipOwner()
    Investor = Investor()
    
    img = Image.open('/Users/nakashima/Pictures/logo.png')
    st.image(img, width = 300)

    start_year, end_year = st.slider('Simulation Year',2020,2070,(2022,2050))
    casename = st.text_input("Casename",value="test_0331")
            
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

    # Set agents
    Owner.reset(economy, environment, safety, labour)

    # sim_year = start_year
    if 'Year' not in st.session_state:
        st.session_state['Year'] = start_year

#    for ii in range((end_year-start_year)//dt_year+1):
    next_step = st.sidebar.button('Next Step')
    if next_step:
        if st.session_state['Year'] == start_year:
            set_scenario(casename, start_year, end_year, 5200, 1.01, age)
            demand, ship_age = get_scenario('scenario_'+casename)
            cost = get_cost(demand.Year, 'cost_'+casename)
            spec = get_spec('spec_'+casename)
            # st.dataframe(spec)        
            select = [0] * len(cost.Year)
            st.write("Simulation Started!")
            st.line_chart(demand.NumofShip)
            st.line_chart(cost)
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
        sim_year=st.session_state.Year
        
        for i in range(sim_year-start_year, min(end_year-start_year+1,sim_year-start_year+dt_year), 1):
            select[i], annual_cost, opex_sum, capex_sum, ac_loss, sf_sum, fuel_cost = Owner.select_ship(spec, cost, i, ship_age)
            delay = 0 # Tentative
            # if i+delay<len(cost.Year):
            Investor.investment(cost, i, delay, invest)
            # # Get Tradespace
            show_tradespace(cost, spec, i, annual_cost, ac_loss, sf_sum, fuel_cost, select[i])

        st.session_state.Year += dt_year
        demand.to_csv('csv/demand'+casename+'.csv')
        cost.to_csv('csv/cost'+casename+'.csv')
        spec.to_csv('csv/spec'+casename+'.csv')
        
        with open('csv/select'+casename+'.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(select)
            
        result, conv_ship = initiate_result(demand,spec,cost,select,ship_age)
        
        select_tmp = select[:st.session_state.Year-start_year]
                
        labels1 = selected_ship_label(spec,select_tmp,conv_ship) # select
        
        # Add and calculate Other Parameters
        result_addrow(result)
        calculate_result(result,spec,cost,demand,ship_age,labels1)

        result_tmp = result[:st.session_state.Year-start_year]
        show_output(result_tmp, labels1, spec)

        if st.session_state.Year >= end_year:
            st.write('Simulation Done!!!!!')