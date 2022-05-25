import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import streamlit as st
import altair as alt 
import matplotlib.animation as animation
import seaborn as sns
from adjustText import adjust_text

def show_tradespace_general(a, b, alabel, blabel, title, list, selected_index, directory):
    fig = plt.figure(figsize=(10,10))
        
    plt.scatter(x=a, y=b)
    plt.scatter(x=a[selected_index], y=b[selected_index],
        label=f'Selected (Config{selected_index})',
        marker='*', c='yellow', edgecolor='k', s=150)
    plt.title(title)
    plt.xlabel(alabel)
    plt.ylabel(blabel)
    for j, label in enumerate(list):
        plt.annotate(label, (a[j], b[j]))
    
    st.pyplot(fig)
    fig.savefig(directory+'/'+title+'.png')

def show_tradespace_for_multiple(a, b, alabel, blabel, title, list, directory, x_int=False, y_int=False):
    fig = plt.figure(figsize=(15,15))
    plt.scatter(x=a, y=b)
    plt.title(title)
    plt.xlabel(alabel)
    plt.ylabel(blabel)
    if x_int:
        plt.gca().get_xaxis().set_major_locator(ticker.MaxNLocator(integer=True))
    if y_int:
        plt.gca().get_yaxis().set_major_locator(ticker.MaxNLocator(integer=True))

    texts = []
    for j, label in enumerate(list):
        text = plt.annotate(label, (a[j], b[j]))
        texts.append(text)
        
    adjust_text(texts, arrowprops=dict(arrowstyle='-', color='gray', lw=0.5))
    fig.savefig(directory+'/'+title+'.png')

def show_tradespace(i, annual_cost, ac_loss, sf_sum, fuel_cost, selected_index):
    if i%10==0: # Need to change
        fig = plt.figure(figsize=(18,5))
        ax1 = fig.add_subplot(1, 3, 1)
        ax2 = fig.add_subplot(1, 3, 2)
        ax3 = fig.add_subplot(1, 3, 3)
        ax1.scatter(x=annual_cost, y=ac_loss)
        ax1.scatter(x=annual_cost[selected_index], y=ac_loss[selected_index],
            # label=f'Selected ({selected_ship[-1]})',
            marker='*', c='yellow', edgecolor='k', s=150)
        ax1.set_title("Economy vs Safety at " + str(i))
        ax1.set_xlabel("Annual Cost (USD)")
        ax1.set_ylabel("Expected Accident (-)")

        ax2.scatter(x=annual_cost, y=sf_sum)
        ax2.scatter(x=annual_cost[selected_index], y=sf_sum[selected_index],
            # label=f'Selected ({selected_ship[-1]})',
            marker='*', c='yellow', edgecolor='k', s=150)
        ax2.set_title("Economy vs Labour at " + str(i))
        ax2.set_xlabel("CAPEX (USD)")
        ax2.set_ylabel("Num of Seafarer (person)")
        
        ax3.scatter(x=annual_cost, y=fuel_cost)
        ax3.scatter(x=annual_cost[selected_index], y=fuel_cost[selected_index],
            # label=f'Selected ({selected_ship[-1]})',
            marker='*', c='yellow', edgecolor='k', s=150)
        ax3.set_title("Economy vs Environment at " + str(i))
        ax3.set_xlabel("CAPEX (USD)")
        ax3.set_ylabel("Fuel Cost (USD)")
        
        # for j, label in enumerate(spec.index.values):
        #     ax1.text(annual_cost[j], ac_loss[j], label)
        #     ax2.text(annual_cost[j], sf_sum[j], label)
        #     ax3.text(annual_cost[j], fuel_cost[j], label)
        plt.show()
        st.pyplot(fig)
        
def show_stackplot(result, label, title, directory):
    fig = plt.figure(figsize=(20,10))
    cm=plt.get_cmap("tab20")
    ax1 = fig.add_subplot(1, 1, 1)
    ax1.stackplot(result.index, [result[s] for s in label], labels=label, colors= [cm(i) for i in range(12)]) #, color=a, cmap=cm) #, color=color_maps)
    ax1.set_title(title)
    ax1.legend(loc="upper left")
    st.pyplot(fig)
    fig.savefig(directory+'/'+title+'.png')

def show_barchart(result, label, title, directory):
    fig = plt.figure(figsize=(20,10))
    cm=plt.get_cmap("tab20")
    ax1 = fig.add_subplot(1, 1, 1)
    for i in range(len(label)):
        ax1.bar(result.index, result[label[i]], bottom=result[label[:i]].sum())

    ax1.set_title(title)
    ax1.legend(loc="upper left")
    st.pyplot(fig)
    fig.savefig(directory+'/'+title+'.png')

def show_linechart(x, y, label, title, directory):
    fig = plt.figure(figsize=(20,10))
    ax1 = fig.add_subplot(1, 1, 1)
    ax1.plot(x, y)
    ax1.set_ylabel(label)
    ax1.set_title(title)
    ax1.legend(loc="upper left")
    st.pyplot(fig)
    fig.savefig(directory+'/'+title+'.png')

def show_linechart_two(x, y1, y2, label, title, directory):
    fig = plt.figure(figsize=(20,10))
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(x, y1, label='Profit')
    ax.plot(x, y2, label='Subsidy')
    ax.set_ylabel(label)
    ax.set_title(title)
    ax.legend(loc="upper left")
    st.pyplot(fig)
    fig.savefig(directory+'/'+title+'.png')

def show_linechart_three(x, y1, y2, y3, label, title, directory, legend_pos):
    fig = plt.figure(figsize=(20,10))
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(x, y1, label='Berthing')
    ax.plot(x, y2, label='Navigation')
    ax.plot(x, y3, label='Monitoring')
    ax.set_ylabel(label)
    ax.set_title(title)
    ax.legend(loc=legend_pos)
    st.pyplot(fig)
    fig.savefig(directory+'/'+title+'.png')

def get_resultsareachart(result_data):
    result_data = result_data.reset_index().melt('year', var_name='type', value_name='y')
    hover = alt.selection_single(
        fields=["year"],
        nearest=True,
        on="mouseover",
        empty="none",
    )
    graphbase = (
        alt.Chart(result_data)
        .mark_area()
        .encode(
            alt.X("year", title=''),
            alt.Y("y", title=''),
            color="type",
        )
    )
    # Draw points on the line, and highlight based on selection
    graphpoints = graphbase.transform_filter(hover).mark_circle(size=65)
    # Draw a rule at the location of the selection
    graphtooltips = (
        alt.Chart(result_data)
        .mark_rule()
        .encode(
            alt.X("year"),
            alt.Y("y"),
            opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
            tooltip=[
                alt.Tooltip("year", title="year"),
                alt.Tooltip("y", title="value"),
            ],
        )
        .add_selection(hover)
    )
    return (graphbase+ graphpoints+ graphtooltips).interactive()

def show_tradespace_anime(a, b, alabel, blabel, list, selected_index, directory):
    dRangex = [a.min().min()*0.95, a.max().max()*1.01]
    dRangey = [b.min().min()*0.95, b.max().max()*1.01]
    fig = plt.figure(figsize=(8,8))
    ax = plt.subplot(1,1,1)
    cmap = plt.get_cmap("tab20")
    ims = []
    legends_flag = True

    for i in range(a.index.min(), a.index.max()+1):
        image = []
        
        for c, j in enumerate(list):
            image += ax.plot(a[a.index == i][j], b[b.index == i][j], ".", a[a.index <= i][j], b[b.index <= i][j], "-", markersize=15, linewidth=1, color=cmap(c), label=j) # for c, j in enumerate(list)))
        
        image += ax.plot(a[a.index == i]['config'+str(selected_index[i-a.index.min()])], b[a.index == i]['config'+str(selected_index[i-a.index.min()])], '*',
                                       label=f'Selected', markersize =6, color='yellow') #, edgecolor='k', s=150)
        
        ax.set_xlabel(alabel)
        ax.set_ylabel(blabel)
        # Need to adjust the point to the center
        image.append(ax.text(6200000, 0.048, 'Profitability vs Safety at {:d}'.format(i), fontsize=10))
        ims.append(image)
                
        if legends_flag:
            ax.legend(loc='lower right', bbox_to_anchor=(1.15, 0))
            legends_flag = False
        
        ax.set_xlim(dRangex[0],dRangex[1])
        ax.set_ylim(dRangey[0],dRangey[1])

    ani = animation.ArtistAnimation(fig, ims, interval=300)
    ani.save(directory+'/tradespace.gif', writer="imagemagick")