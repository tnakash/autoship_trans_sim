import matplotlib.pyplot as plt
import streamlit as st
from matplotlib.ticker import MaxNLocator

def show_tradespace(cost, spec, i, annual_cost, ac_loss, sf_sum, fuel_cost, selected_index):
    if cost.Year[i]%5==0:
        fig = plt.figure(figsize=(18,5))
        ax1 = fig.add_subplot(1, 3, 1)
        ax2 = fig.add_subplot(1, 3, 2)
        ax3 = fig.add_subplot(1, 3, 3)
        ax1.scatter(x=annual_cost, y=ac_loss)
        ax1.scatter(x=annual_cost[selected_index], y=ac_loss[selected_index],
            # label=f'Selected ({selected_ship[-1]})',
            marker='*', c='yellow', edgecolor='k', s=150)
        ax1.set_title("Economy vs Safety at " + str(cost.Year[i]))
        ax1.set_xlabel("Annual Cost (USD)")
        ax1.set_ylabel("Expected Accident Loss (USD)")

        ax2.scatter(x=annual_cost, y=sf_sum)
        ax2.scatter(x=annual_cost[selected_index], y=sf_sum[selected_index],
            # label=f'Selected ({selected_ship[-1]})',
            marker='*', c='yellow', edgecolor='k', s=150)
        ax2.set_title("Economy vs Labour at " + str(cost.Year[i]))
        ax2.set_xlabel("CAPEX (USD)")
        ax2.set_ylabel("Num of Seafarer (person)")
        
        ax3.scatter(x=annual_cost, y=fuel_cost)
        ax3.scatter(x=annual_cost[selected_index], y=fuel_cost[selected_index],
            # label=f'Selected ({selected_ship[-1]})',
            marker='*', c='yellow', edgecolor='k', s=150)
        ax3.set_title("Economy vs Environment at " + str(cost.Year[i]))
        ax3.set_xlabel("CAPEX (USD)")
        ax3.set_ylabel("Fuel Cost (USD)")
        
        for j, label in enumerate(spec.index.values):
            ax1.text(annual_cost[j], ac_loss[j], label)
            ax2.text(annual_cost[j], sf_sum[j], label)
            ax3.text(annual_cost[j], fuel_cost[j], label)
        # plt.show()
        st.pyplot(fig)


# Show Outputs
def show_output(result, labels1, spec):
    fig = plt.figure(figsize=(20,10)) #.gca()
    ax1 = fig.add_subplot(2, 2, 1)
    ax2 = fig.add_subplot(2, 2, 2)
    ax3 = fig.add_subplot(2, 2, 3)
    ax4 = fig.add_subplot(2, 2, 4)

    ax1.stackplot(result.Year, [result[s] for s in labels1], labels=labels1)
#    ax1.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax1.set_title("Number of ships for each autonomous level")
    ax1.legend(loc="upper left")

    labels2 = ['LossDamagePerVessel']
    ax2.stackplot(result.Year, result.LossDamagePerVessel, labels=labels2)
#    ax2.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax2.set_title("Number of Expected Accidents")
    ax2.legend(loc="upper right")

    labels3 = ['Seafarer', 'ShoreOperator']
    ax3.stackplot(result.Year, result.Seafarer, result.ShoreOperator, labels=labels3)
#    ax3.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax3.set_title("Number of Seafarers")
    ax3.legend(loc="upper right")

    labels4 = ['LabourCost', 'LossDamage', 'FuelCost', 'OpeCost', 'OnboardAsset', 'ShoreAsset']
    ax4.stackplot(result.Year, result.LabourCost, result.LossDamage, result.FuelCost, result.OpeCost, result.OnboardAsset, result.ShoreAsset, labels=labels4)
#    ax4.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax4.set_title("Cost for Each Vessel")
    ax4.legend(loc="upper right")
    # plt.show()
    st.pyplot(fig)

    for s in labels1:
        i = spec.index[spec.ship_type == s].tolist()[0]
        st.write(s, '| SituationAwareness:', spec.SituationAwareness[i], '| Planning:', spec.Planning[i], '| Control:', spec.Control[i], '| Remote:', spec.Remote[i])