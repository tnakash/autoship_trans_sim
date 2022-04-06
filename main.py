from curses import A_ALTCHARSET
from invest import investment
from output import show_tradespace, show_output
from adopt import select_ship
from input import *
from result import *

def main(casename = 'test_0331'):
    set_scenario(casename, 2022, 2070, 5200, 1.01, 20)
    reset_spec(casename)
    '''
    Import YAML files and check the input data
    '''
    # Import from yaml files
    demand, ship_age = get_scenario('scenario_'+casename)
    cost = get_cost(demand.Year, 'cost_'+casename)
    spec = get_spec('spec_'+casename)

    # Select Ship and show Tradespace
    select = [0] * len(cost.Year)
    labels = []

    '''
    Trade Space Analysis
    '''
    # Select Ship
    #@title What will you prioritize for selecting ships?　{ run: "auto" }
    economy = 1 #@param {type:"slider", min:0, max:1, step:0.1}
    environment = 0 #@param {type:"slider", min:0, max:1, step:0.1}
    safety = 0 #@param {type:"slider", min:0, max:1, step:0.1}
    labour = 0 #@param {type:"slider", min:0, max:1, step:0.1}

    for i in range(len(cost.Year)):
        select[i], annual_cost, opex_sum, capex_sum, ac_loss, sf_sum, fuel_cost = select_ship(spec, cost, i, ship_age, economy, environment, safety, labour)
        
        # Invest Technology and Adoption Model Change
        delay = 3 # Tentative
        if cost.Year[i]%5==0 and i+delay<len(cost.Year):
            
            # Invest Technology
            invest = input("Set invest option at "+str(cost.Year[i])+" (Comm/Situ/Plan/Exec): ")
            
            # Adoption Model Change
            economy = float(input("Parameter for Economy (0-1): "))
            environment = float(input("Parameter for Environment (0-1): "))
            safety = float(input("Parameter for Safety (0-1): "))
            labour = float(input("Parameter for Labour (0-1): "))

        # Get Tradespace
        if cost.Year[i]%10==0:
            show_tradespace(cost, spec, i, annual_cost, ac_loss, sf_sum, fuel_cost)    

    # Initiate result dataframe and calculate the number of annual newbuildings and scraps
    result, conv_ship = initiate_result(demand,spec,cost,select,ship_age)

    # Selected Ship labeling
    labels1 = selected_ship_label(spec,select,conv_ship)

    # Add and calculate Other Parameters
    result_addrow(result)
    calculate_result(result,spec,cost,demand,ship_age,labels1)

    # Get Possible roadmap for Autonomous Ship Transition
    show_output(result, labels1, spec)

if __name__ =='__main__':
    main('test_0331')