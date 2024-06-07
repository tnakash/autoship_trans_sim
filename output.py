import matplotlib.animation as animation
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import streamlit as st
import pandas as pd

# Define custom colormap
cmap_colors = [
    (0.9, 0.9, 0.9),   # NONE - Light Gray
    (0.8, 0.1, 0.1),   # B - Crimson Red
    (0.2, 0.8, 0.9),   # N1 - Sky Blue
    (0, 0.4, 0.8),     # N2 - Royal Blue
    (0.95, 0.9, 0.25), # M - Golden Yellow
    (0.8, 0.4, 0.8),   # BN1 - Lavender
    (0.5, 0.2, 0.7),   # BN2 - Violet
    (1, 0.6, 0.2),     # BM - Tangerine
    (0.4, 0.8, 0.4),   # N1M - Mint Green
    (0, 0.6, 0.2),     # N2M - Forest Green
    (0.4, 0.4, 0.4),   # BN1M - Medium Gray
    (0.1, 0.1, 0.1)    # FULL - Charcoal Black
]

cmap_name = 'custom_cmap'
custom_cmap = plt.cm.colors.ListedColormap(cmap_colors, name=cmap_name, N=len(cmap_colors))

cmap_colors_crew = [
    (0.2, 0.8, 0.9),   # Sky Blue
    (0, 0.2, 0.5),     # Navy Blue
    (0.95, 0.9, 0.25), # Golden Yellow
    (0.8, 0.4, 0.8),   # Lavender
    (0.5, 0.2, 0.7),   # Violet
]

cmap_name = 'custom_cmap_crew'
custom_cmap_crew = plt.cm.colors.ListedColormap(cmap_colors_crew, name=cmap_name, N=len(cmap_colors_crew))

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
    fig.savefig(directory + '/' + title + '.png')


def show_tradespace(i, annual_cost, ac_loss, sf_sum, fuel_cost, selected_index, interval):
    if i % interval == 0:
        fig = plt.figure(figsize=(18,5))
        ax1 = fig.add_subplot(1, 3, 1)
        ax2 = fig.add_subplot(1, 3, 2)
        ax3 = fig.add_subplot(1, 3, 3)
        ax1.scatter(x=annual_cost, y=ac_loss)
        ax1.scatter(x=annual_cost[selected_index], y=ac_loss[selected_index],
            # label=f'Selected ({selected_ship[-1]})',
            marker='*', c='yellow', edgecolor='k', s=150)
        ax1.set_title('Economy vs Safety at ' + str(i))
        ax1.set_xlabel('Annual Cost (USD)')
        ax1.set_ylabel('Expected Accident (-)')

        ax2.scatter(x=annual_cost, y=sf_sum)
        ax2.scatter(x=annual_cost[selected_index], y=sf_sum[selected_index],
            # label=f'Selected ({selected_ship[-1]})',
            marker='*', c='yellow', edgecolor='k', s=150)
        ax2.set_title('Economy vs Labour at ' + str(i))
        ax2.set_xlabel('CAPEX (USD)')
        ax2.set_ylabel('Num of Seafarer (person)')

        ax3.scatter(x=annual_cost, y=fuel_cost)
        ax3.scatter(x=annual_cost[selected_index], y=fuel_cost[selected_index],
            # label=f'Selected ({selected_ship[-1]})',
            marker='*', c='yellow', edgecolor='k', s=150)
        ax3.set_title('Economy vs Environment at ' + str(i))
        ax3.set_xlabel('CAPEX (USD)')
        ax3.set_ylabel('Fuel Cost (USD)')

        plt.show()
        st.pyplot(fig)


def make_dataframe_for_output(start_year, end_year, config_list):
    data = {'year': range(start_year, end_year)}
    for config in config_list:
        data[config] = [0] * (end_year - start_year)
    df = pd.DataFrame(data)
    df_new = df.set_index('year')    

    return df_new


def make_dataframe_for_output_multiple(start_year, end_year, config_list, ship_type_list):
    df_merge = pd.DataFrame()
    for ship_type in ship_type_list:
        data = {'year': range(start_year, end_year)}
        for config in config_list:
            data[config] = [0] * (end_year - start_year)

        df = pd.DataFrame(data)        
        df_new = df.set_index('year')
        df_new['ship_type'] = ship_type
        df_merge = pd.concat([df_merge, df_new])
    
    return df_merge


def show_stacked_bar(result, label, title, directory, cmap = None):
    fig = plt.figure(figsize=(20, 10))
    cm = plt.get_cmap('tab20')
    ax1 = fig.add_subplot(1, 1, 1)

    bottom = None
    for i, s in enumerate(label):
        if cmap == 'config':
            ax1.bar(result['year'], result[s], label=s, bottom=bottom, color=custom_cmap(i))
        elif cmap == 'crew':
            ax1.bar(result['year'], result[s], label=s, bottom=bottom, color=custom_cmap_crew(i))
        else:
            ax1.bar(result['year'], result[s], label=s, bottom=bottom, color=cm(i))
            
        if bottom is None:
            bottom = result[s]
        else:
            bottom += result[s]

    ax1.set_title(title, fontsize=16)
    ax1.legend(loc='upper left', fontsize=16)
    plt.xticks(result['year'], rotation=45)
    plt.tight_layout()
    plt.tick_params(labelsize=16)
    st.pyplot(fig)
    fig.savefig(directory + '/' + title + '.png')

def show_barchart(result, label, title, directory):
    fig = plt.figure(figsize=(20,10))
    cm=plt.get_cmap('tab20')
    ax1 = fig.add_subplot(1, 1, 1)
    for i in range(len(label)):
        ax1.bar(result.index, result[label[i]], bottom=result[label[:i]].sum())

    ax1.set_title(title, fontsize=16)
    ax1.legend(loc='upper left', fontsize=16)
    st.pyplot(fig)
    fig.savefig(directory+'/'+title+'.png')


def show_linechart(x, y, label, title, directory):
    fig = plt.figure(figsize=(20,10))
    ax1 = fig.add_subplot(1, 1, 1)
    ax1.plot(x, y)
    ax1.set_ylabel(label, fontsize=16)
    ax1.set_title(title, fontsize=16)
    ax1.legend(loc='upper left', fontsize=16)
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

    ax.set_xticks(x)
    ax.set_xticklabels([int(label) for label in x])
    
    st.pyplot(fig)
    fig.savefig(directory+'/'+title+'.png')


def show_tradespace_anime(a, b, alabel, blabel, list, selected_index, directory, config_list):
    dRangex = [a.min().min()*0.95, a.max().max()*1.01]
    dRangey = [b.min().min()*0.95, b.max().max()*1.01]
    fig = plt.figure(figsize=(8,8))
    ax = plt.subplot(1,1,1)
    cmap = plt.get_cmap('tab20')
    ims = []
    legends_flag = True

    for i in range(a.index.min(), a.index.max()+1):
        image = []
        
        for c, j in enumerate(list):
            image += ax.plot(a[a.index == i][j], b[b.index == i][j], '.', a[a.index <= i][j], b[b.index <= i][j], '-', markersize=15, linewidth=1, color=cmap(c), label=j) # for c, j in enumerate(list)))
        
        image += ax.plot(a[a.index == i][config_list[selected_index[i-a.index.min()]]], b[a.index == i][config_list[selected_index[i-a.index.min()]]], '*',
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
    ani.save(directory+'/tradespace.gif', writer='pillow')


def show_tradespace_for_multiple_color(a, b, alabel, blabel, title, control_cases, uncertainty_cases, directory, x_int=False, y_int=False):
    fig = plt.figure(figsize=(15,18))
    cm=plt.get_cmap('tab20')
    
    for i, case in enumerate(control_cases):
        plt.scatter(x=a[uncertainty_cases*i:uncertainty_cases*(i + 1)], 
                    y=b[uncertainty_cases*i:uncertainty_cases*(i + 1)], 
                    c=[cm(i)], label=case)
        
    plt.title(title, fontsize=16)
    plt.xlabel(alabel, fontsize=16)
    plt.ylabel(blabel, fontsize=16)
    plt.legend(bbox_to_anchor=(1.01, 1), loc='upper left', fontsize=16)
    if x_int:
        plt.gca().get_xaxis().set_major_locator(ticker.MaxNLocator(integer=True))
    if y_int:
        plt.gca().get_yaxis().set_major_locator(ticker.MaxNLocator(integer=True))
    
    fig.savefig(directory+'/'+title +'.png', bbox_inches='tight')
    plt.close()


def process_ship_data(grouped_data, ship_type, config_list, title_suffix, dir_fig):
    grouped_data_ship = grouped_data.query(f"ship_type == '{ship_type}'").pivot_table(index=['year'], columns='config', values='ship_id', aggfunc='sum', fill_value=0)

    missing_configs = set(config_list) - set(grouped_data_ship.columns)
    for missing_config in missing_configs:
        grouped_data_ship[missing_config] = 0

    grouped_data_ship.reset_index(inplace=True)
    grouped_data_ship = grouped_data_ship.rename(columns={'index': 'year'})
    grouped_data_ship.reset_index(drop=True, inplace=True)

    show_stacked_bar(grouped_data_ship, config_list, f"Number of Ships by Configuration ({title_suffix}) [ship]", dir_fig, 'config')
