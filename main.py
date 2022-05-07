from Agent import ShipOwner, Investor, PolicyMaker
from output import show_tradespace_general
from input import get_yml, get_scenario, set_scenario, set_tech
from calculate import calculate_cost, calculate_tech, get_tech_ini, calculate_TRL_cost

import streamlit as st
import pandas as pd
import altair as alt

from PIL import Image
import zipfile
import matplotlib.pyplot as plt


def main():    
    img = Image.open('fig/logo.png')
    st.image(img, width = 300)
    st.markdown('#### 1. Scenario Setting')

    # Selecting params for simulation scenario
    st.write('1.1 Basic Setting')
    casename = st.text_input("Casename", value="test_0503")
    start_year, end_year = st.slider('Simulation Year',2020,2070,(2022,2050))
    numship_init = st.slider('Initial Number of ships[ship]',1,10000,1000)
    numship_growth = st.slider('Annual growth rate of ship demand[-]',0.90,1.10,1.01)
    ship_age = 25 # st.slider('Average Ship Lifeyear',20,30,25)
    dt_year = st.slider('Interval for Reset parameters[year]',1,50,50)
    set_scenario(casename, start_year, end_year, numship_init, numship_growth, ship_age)
    # Get scenario from yml file (just made)    
    scenario_yml = get_yml('scenario')
    current_fleet, num_newbuilding = get_scenario(scenario_yml)
    
    # Agent Parameter Setting
    st.sidebar.markdown('## 2. Agent Parameter Setting')
    # Selecting params for Shipowners
    st.sidebar.markdown('### 2.1 Ship Owner')
    st.sidebar.write("Parameters for ship adoption")
    economy = st.sidebar.slider('Profitability weight[-]',0.0,1.0,1.0)
    safety = st.sidebar.slider('Safety weight[-]',0.0,1.0,0.5) 
    estimated_loss = st.sidebar.slider('Estimated average accident loss[USD]',0,50000000,10000000)

    # Selecting params for Investors        
    st.sidebar.markdown('### 2.2 Manufacturer (R&D Investor))')
    st.sidebar.write("Technology type and Amount of investment")    
    invest_tech = st.sidebar.selectbox("Investment Strategy",["All","Berth","Navi","Moni"])
    invest_amount = st.sidebar.slider('Investment Amount [USD/year]',0,1000000,500000)
    # invest_berth = st.sidebar.slider('Investment Amount (Berth)',0,2000000,2000000)
    # invest_navi = st.sidebar.slider('Investment Amount (Navi)',0,2000000,2000000)
    # invest_moni = st.sidebar.slider('Investment Amount (Moni)',0,2000000,2000000)

    # Selecting params for Policy Makerss        
    st.sidebar.markdown('### 2.3 Policy Maker')
    st.sidebar.write("Type and amount of subsidy")    
    # subsidy_type = st.sidebar.selectbox("Subsidy for",["R&D","Adoption"])
    # subsidy_amount = st.sidebar.slider('Subsidy Amount',0,200000,100000)
    subsidy_RandD = st.sidebar.slider('Subsidy Amount (R&D)[USD/year]',0,20000000,10000000)
    subsidy_Adoption =  st.sidebar.slider('Subsidy Amount (Adoption)[USD/year]',0,20000000,0)
    if subsidy_Adoption > 0:
        sub_list_min, sub_list_max = st.sidebar.slider('Give subsidy from Config. ',1,11,(9,11))
        sub_list = range(sub_list_min, sub_list_max)
    TRLreg = st.sidebar.selectbox('TRL regulation (minimum TRL for deployment)', (7, 8))
    
    # Set agents
    Owner = ShipOwner(economy, safety, current_fleet, num_newbuilding, estimated_loss)
    Manufacturer = Investor()
    Manufacturer.reset(invest_tech,invest_amount)
    # Manufacturer.reset(invest_berth, invest_navi, invest_moni)
    Regulator = PolicyMaker()
    # Regulator.reset(subsidy_type, subsidy_amount)
    Regulator.reset(subsidy_RandD, subsidy_Adoption)

    # Regulator (Subsidy for Manufacturer) (Increase the investment amount)
    Regulator.subsidize_investment(Manufacturer)

    st.write('1.2 Additional Setting (You can skip!)')    
    Mexp_to_production_loop = st.checkbox('Include effect of Manufacturing experience to Production cost',value=True)
    Oexp_to_TRL_loop = st.checkbox('Include effect of Operational experience to TRL',value=True)
    Oexp_to_safety_loop = st.checkbox('Include effect of Operational experience to Safety',value=True)
    
    # Additional Parameter Setting
    # set_add = st.button('Want to set additional parameters?')
    tech_integ_factor = st.slider('Initial integration cost ratio for each tech',1.0,2.0,1.2)
    integ_b = st.slider('Integration cost reduction ratio b (y = ax**(-b))',0.0,1.0,0.3)
    ope_safety_b = st.slider('Accident reduction ratio b (y = ax**(-b))', 0.0,1.0,0.2)
    acc_reduction_full = st.slider('Human Erron Rate [-]', 0.0, 1.0, 0.9)
    ope_TRL_factor = st.slider('Operational experience R&D value (USD/times)',0.0,10.0,0.4)
    rd_need_TRL = st.slider('Necessary R&D Amount for 1TRL-up (MUSD(*year)/TRL)',1,30,20) * 1000000
    randd_base = st.slider('Base R&D Amount (without Investment) (MUSD/year)',0,30,1) * 1000000
    # manu_max = st.slider('Max Manufacturing times (ship)',1,1000,100)
    # ope_max = st.slider('Max Operation times (year*ship)',1,10000,10000)    
    set_tech(tech_integ_factor, integ_b, ope_safety_b, ope_TRL_factor, rd_need_TRL, randd_base, acc_reduction_full)
    
    # Input from YML file
    cost_yml = get_yml('cost')
    tech_yml = get_yml('tech')
    ship_spec_yml = get_yml('ship_spec')
    tech, param = get_tech_ini(tech_yml)
    
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
            
            # Manufacturer (R&D (Investment))
            tech = Manufacturer.invest(tech)
            
            # World (Technology Development)
            tech = calculate_tech(tech, param, Owner.fleet, ship_age)
            tech = calculate_TRL_cost(tech, param, Mexp_to_production_loop, Oexp_to_TRL_loop, Oexp_to_safety_loop)
            
            # World (Cost Reduction and Safety Improvement)
            spec_current = calculate_cost(ship_spec_yml, cost_yml, start_year+i, tech)
            
            # Regulator (Subsidy for Adoption)
            if subsidy_Adoption > 0:
                spec_current = Regulator.subsidize_Adoption(spec_current,num_newbuilding.ship[i],sub_list)
            
            # Ship Owner (Adoption and Purchase)
            select = Owner.select_ship(spec_current, tech, TRLreg)
            Owner.purchase_ship(select, i)

            # Show Tradespace
            if (start_year+i)%10 == 0:
                show_tradespace_general(spec_current.OPEX+spec_current.CAPEX+spec_current.VOYEX+spec_current.AddCost,
                                        spec_current.accident_berth+spec_current.accident_navi+spec_current.accident_moni, 
                                        "Total Cost(USD/year)", "Accident Ratio (-)", "Profitability vs Safety at "+str(start_year+i), 
                                        spec_current.config.values.tolist(), select)
            
            spec = spec_current if st.session_state['Year'] == start_year and i == 0 else pd.concat([spec, spec_current])
            tech_year = pd.concat([pd.DataFrame({'year': [start_year+i]*3}), tech], axis = 1)            
            tech_accum = tech_year if st.session_state['Year'] == start_year and i == 0 else pd.concat([tech_accum, tech_year])

        # proceed year
        st.session_state.Year += dt_year
   
        # Save Tentative File for iterative simulation
        spec.to_csv('csv/spec'+casename+'.csv')
        tech_accum.to_csv('csv/tech'+casename+'.csv')
        Owner.fleet.to_csv('csv/fleet'+casename+'.csv')

        # Visualize results                        
        """
        Fleet Transition (Number of new shipbuilding[ship])
        """
        Owner.fleet.set_index("year", inplace=True)
        st.area_chart(Owner.fleet)
        ## 【参考】Altairでの可視化
        # data = pd.melt(Owner.fleet, id_vars=['year']).rename(columns={'value': 'Num of newbuilding (ship)'})
        # st.write(data)
        # chart = (
        #     alt.Chart(data)
        #     .mark_line(opacity = 0.8, clip = True)
        #     .encode(
        #         x="year",
        #         y=alt.Y('Num of newbuilding (ship)', stack=None),
        #         color='variable:N'
        #     )
        # )
        # st.altair_chart(chart, use_container_width=True)

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
        
        """
        Cost of each type of autonomous ship
        """
        st.write('under construction ...')
    
        with zipfile.ZipFile('csv/'+casename+'.zip', 'w', compression=zipfile.ZIP_DEFLATED) as z:
            z.write('csv/spec'+casename+'.csv')
            z.write('csv/tech'+casename+'.csv')
            z.write('csv/fleet'+casename+'.csv')

        st.markdown('#### Download Results')
        st.download_button('Download result files (compressed)',open('csv/'+casename+'.zip', 'br'), casename+'.zip')

        if st.session_state.Year >= end_year:
            st.write('Simulation Done!!!!!')

if __name__ =='__main__':
    '''
    ## Autonomous Ship Transition Simulator
    '''
    main()