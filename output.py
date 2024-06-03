import altair as alt
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import streamlit as st
import pandas as pd
import numpy as np
from adjustText import adjust_text
import seaborn as sns


# Define custom colormap
cmap_colors = [
    (0.7, 0.7, 0.7),   # NONE - Light Gray
    (1, 0, 0),         # B - Red
    (0, 0.9, 1),       # N1 - Light Blue
    (0, 0.5, 1),       # N2 - Dark Blue
    (1, 1, 0),         # M - Yellow
    (1, 0, 1),         # BN1 - Light Purple
    (0.6, 0, 1),       # BN2 - Dark Purple
    (1, 0.5, 0),       # BM - Orange
    (0, 1, 0),         # N1M - Light Green
    (0, 0.5, 0),       # N2M - Dark Green
    (0.2, 0.5, 0.5),   # BN1M - Dark Gray
    (0.2, 0.2, 0.2)    # FULL - Black
]

cmap_name = 'custom_cmap'
custom_cmap = plt.cm.colors.ListedColormap(cmap_colors, name=cmap_name, N=len(cmap_colors))

cmap_colors_crew = [
    (0, 0.5, 1),       # N1 - Light Blue
    (0, 0, 0.5),       # N2 - Dark Blue
    (1, 1, 0),         # M - Yellow
    (1, 0, 1),         # BN1 - Light Purple
    (0.6, 0, 1),       # BN2 - Dark Purple
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


# def make_dataframe_for_output_multiple(start_year, end_year, config_list, ship_type_list):
#     for i in range(len(ship_type_list)):
#         df = pd.DataFrame({'year': range(start_year, end_year),
#                             config_list[0]: [0] * (end_year - start_year),
#                             config_list[1]: [0] * (end_year - start_year),
#                             config_list[2]: [0] * (end_year - start_year),
#                             config_list[3]: [0] * (end_year - start_year),
#                             config_list[4]: [0] * (end_year - start_year),
#                             config_list[5]: [0] * (end_year - start_year),
#                             config_list[6]: [0] * (end_year - start_year),
#                             config_list[7]: [0] * (end_year - start_year),
#                             config_list[8]: [0] * (end_year - start_year),
#                             config_list[9]: [0] * (end_year - start_year),
#                             config_list[10]: [0] * (end_year - start_year),
#                             config_list[11]: [0] * (end_year - start_year)})
#         df_new = df.set_index('year')
#         df_new['ship_type'] = ship_type_list[i]
#         df_merge = df_new if i == 0 else pd.concat([df_merge, df_new])
    
#     return df_merge


# def show_stackplot(result, label, title, directory):
#     fig = plt.figure(figsize=(20,10))
#     cm=plt.get_cmap('tab20')
#     ax1 = fig.add_subplot(1, 1, 1)
#     ax1.stackplot(result.index, [result[s] for s in label], labels=label, colors= [cm(i) for i in range(12)])
#     ax1.set_title(title, fontsize=16)
#     ax1.legend(loc='upper left', fontsize=16)
#     st.pyplot(fig)
#     fig.savefig(directory+'/'+title+'.png')


# def plot_graph(data, x, y, hue, ylabel, title):
#     fig = plt.figure(figsize=(12, 6))
#     sns.barplot(x=x, y=y, hue=hue, data=data, ci=None, estimator=sum)
#     plt.xlabel('Year', fontsize=16)
#     plt.ylabel(ylabel, fontsize=16)
#     plt.title(title, fontsize=16)
#     plt.xticks(rotation=45)
#     plt.tight_layout()
#     st.pyplot(fig)
#     # fig.savefig(directory + '/' + title + '.png')


# def plot_graph_stack(data, x, y_list, ylabel_list, ylabel_total, title):
#     fig = plt.figure(figsize=(12, 6))
#     cm = plt.get_cmap('tab20')
#     for i, y_each in range(y_list):
#         sns.barplot(x=x, y=y_each, data=data, color=cm(i), label=ylabel_list(i), ci=None)

#     plt.xlabel('Year', fontsize=16)
#     plt.ylabel(ylabel_total, fontsize=16)
#     plt.title(title, fontsize=16)
#     plt.xticks(rotation=45, fontsize=16)
#     plt.tight_layout()
#     st.pyplot(fig)
#     # fig.savefig(directory + '/' + title + '.png')


def show_stacked_bar(result, label, title, directory, cmap = None):
    fig = plt.figure(figsize=(20, 10))
    cm = plt.get_cmap('tab20')
    ax1 = fig.add_subplot(1, 1, 1)

    # 各データセットを積み上げ棒グラフとして描画
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

    # plt.ylim(0, max_y_value)

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


# def show_linechart_two(x, y1, y2, label, title, directory):
#     fig = plt.figure(figsize=(20,10))
#     ax = fig.add_subplot(1, 1, 1)
#     ax.plot(x, y1, label='Profit')
#     ax.plot(x, y2, label='Subsidy')
#     ax.set_ylabel(label)
#     ax.set_title(title)
#     ax.legend(loc='upper left')

#     ax.set_xticks(x)
#     ax.set_xticklabels([int(label) for label in x])

#     st.pyplot(fig)
#     fig.savefig(directory+'/'+title+'.png')


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


# def get_resultsareachart(result_data):
#     result_data = result_data.reset_index().melt('year', var_name='type', value_name='y')
#     hover = alt.selection_single(
#         fields=['year'],
#         nearest=True,
#         on='mouseover',
#         empty='none',
#     )
#     graphbase = (
#         alt.Chart(result_data)
#         .mark_area()
#         .encode(
#             alt.X('year', title=''),
#             alt.Y('y', title=''),
#             color='type',
#         )
#     )
#     # Draw points on the line, and highlight based on selection
#     graphpoints = graphbase.transform_filter(hover).mark_circle(size=65)
#     # Draw a rule at the location of the selection
#     graphtooltips = (
#         alt.Chart(result_data)
#         .mark_rule()
#         .encode(
#             alt.X('year'),
#             alt.Y('y'),
#             opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
#             tooltip=[
#                 alt.Tooltip('year', title='year'),
#                 alt.Tooltip('y', title='value'),
#             ],
#         )
#         .add_selection(hover)
#     )
#     return (graphbase+ graphpoints+ graphtooltips).interactive()


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
    # データのピボットテーブル化
    grouped_data_ship = grouped_data.query(f"ship_type == '{ship_type}'").pivot_table(index=['year'], columns='config', values='ship_id', aggfunc='sum', fill_value=0)

    # 欠けている設定の補完
    missing_configs = set(config_list) - set(grouped_data_ship.columns)
    for missing_config in missing_configs:
        grouped_data_ship[missing_config] = 0

    # データフレームの整形
    grouped_data_ship.reset_index(inplace=True)
    grouped_data_ship = grouped_data_ship.rename(columns={'index': 'year'})
    grouped_data_ship.reset_index(drop=True, inplace=True)

    # グラフの表示
    show_stacked_bar(grouped_data_ship, config_list, f"Number of Ships by Configuration ({title_suffix}) [ship]", dir_fig, 'config')
