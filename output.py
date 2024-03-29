import altair as alt
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import streamlit as st
import pandas as pd
import numpy as np
from adjustText import adjust_text
import seaborn as sns


# カスタムカラーマップの定義
cmap_colors = [
    (0.7, 0.7, 0.7),   # NONE - 薄いグレー
    (1, 0, 0),         # B - 赤
    (0, 0.9, 1),       # N1 - 薄い青
    (0, 0.5, 1),       # N2 - 濃い青
    (1, 1, 0),         # M - 黄色
    (1, 0, 1),         # BN1 - 薄い紫
    (0.6, 0, 1),       # BN2 - 濃い紫
    (1, 0.5, 0),       # BM - オレンジ
    (0, 1, 0),         # N1M - 薄い緑
    (0, 0.5, 0),       # N2M - 濃い緑
    (0.2, 0.5, 0.5),   # BN1M - 濃いグレー
    (0.2, 0.2, 0.2)    # FULL - 黒
]

cmap_name = 'custom_cmap'
custom_cmap = plt.cm.colors.ListedColormap(cmap_colors, name=cmap_name, N=len(cmap_colors))

cmap_colors_crew = [
    (0, 0.5, 1),       # N1 - 薄い青
    (0, 0, 0.5),       # N2 - 濃い青
    (1, 1, 0),         # M - 黄色
    (1, 0, 1),         # BN1 - 薄い紫
    (0.6, 0, 1),       # BN2 - 濃い紫
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


# def show_tradespace_for_multiple(a, b, alabel, blabel, title, list, directory, x_int=False, y_int=False):
#     fig = plt.figure(figsize=(15,15))
#     plt.scatter(x=a,y=b)
#     plt.title(title)
#     plt.xlabel(alabel)
#     plt.ylabel(blabel)
#     if x_int:
#         plt.gca().get_xaxis().set_major_locator(ticker.MaxNLocator(integer=True))
#     if y_int:
#         plt.gca().get_yaxis().set_major_locator(ticker.MaxNLocator(integer=True))

#     texts = []
#     for j, label in enumerate(list):
#         text = plt.annotate(label, (a[j], b[j]))
#         texts.append(text)
#     adjust_text(texts, arrowprops=dict(arrowstyle='-', color='gray', lw=0.5))
#     fig.savefig(directory+'/'+title+'.png')


def show_tradespace_for_multiple_color_old(a, b, alabel, blabel, title, cases, k, color, directory, x_int=False, y_int=False):
    fig = plt.figure(figsize=(15,15))
    sub = ('R&D', 'Ado', 'Exp')
    reg = ('Asis', 'Relax')
    # inv = ('All', 'Berth', 'Navi', 'Moni')
    # ope = ('Safety', 'Profit')
    # prop ={'Subsidy': sub, 'Regulation': reg, 'Investment': inv, 'Operation': ope}
    
    share = ('Close', 'Open') #0.1, 1.0)
    insurance = ('Asis', 'Considered') #(0.0, 1.0)    

    # prop ={'Subsidy': sub, 'Regulation': reg, 'Investment': inv, 'Operation': ope}    
    prop ={'Subsidy': sub, 'Regulation': reg, 'Openness': share, 'Insurance': insurance}
    cm=plt.get_cmap('tab10')
    
    for j, option in enumerate(prop[color]):
        a_0 = [aa for i, aa in enumerate(a) if cases[i][k] == option]
        b_0 = [bb for i, bb in enumerate(b) if cases[i][k] == option]
        plt.scatter(x=a_0, y=b_0, c=[cm(j)], label=option)
        
    plt.title(title)
    plt.xlabel(alabel)
    plt.ylabel(blabel)
    plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
    if x_int:
        plt.gca().get_xaxis().set_major_locator(ticker.MaxNLocator(integer=True))
    if y_int:
        plt.gca().get_yaxis().set_major_locator(ticker.MaxNLocator(integer=True))
    
    texts = []
    for j, case in enumerate(cases):
        text = plt.annotate(case[0]+'_'+case[1]+'_'+case[2]+'_'+case[3], (a[j], b[j]))
        texts.append(text)
    # adjust_text(texts, arrowprops=dict(arrowstyle='-', color='gray', lw=0.5))
    fig.savefig(directory+'/'+title+'_'+color+'.png')
    plt.close()

def show_tradespace_for_multiple_color_notext(a, b, alabel, blabel, title, cases, k, color, directory, x_int=False, y_int=False):
    fig = plt.figure(figsize=(15,15))
    sub = ('R&D', 'Ado', 'Exp')
    reg = ('Asis', 'Relax')
    # inv = ('All', 'Berth', 'Navi', 'Moni')
    # ope = ('Safety', 'Profit')
    share = ('Close', 'Open') #0.1, 1.0)
    insurance = ('Asis', 'Considered') #(0.0, 1.0)    

    # prop ={'Subsidy': sub, 'Regulation': reg, 'Investment': inv, 'Operation': ope}    
    prop ={'Subsidy': sub, 'Regulation': reg, 'Openness': share, 'Insurance': insurance}
    cm=plt.get_cmap('tab10')

    for j, option in enumerate(prop[color]):
        a_0 = [aa for i, aa in enumerate(a) if cases[i][k] == option]
        b_0 = [bb for i, bb in enumerate(b) if cases[i][k] == option]
        plt.scatter(x=a_0, y=b_0, c=[cm(j)], label=option)
        
    plt.title(title)
    plt.xlabel(alabel)
    plt.ylabel(blabel)
    plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
    if x_int:
        plt.gca().get_xaxis().set_major_locator(ticker.MaxNLocator(integer=True))
    if y_int:
        plt.gca().get_yaxis().set_major_locator(ticker.MaxNLocator(integer=True))
    
    # texts = []
    # for j, case in enumerate(cases):
    #     text = plt.annotate(case[0]+'_'+case[1]+'_'+case[2]+'_'+case[3], (a[j], b[j]))
    #     texts.append(text)
    # adjust_text(texts, arrowprops=dict(arrowstyle='-', color='gray', lw=0.5))
    fig.savefig(directory+'/'+title+'_'+color+'.png')
    plt.close()


def show_tradespace(i, annual_cost, ac_loss, sf_sum, fuel_cost, selected_index):
    if i % 10 == 0:  # Need to change
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

        # for j, label in enumerate(spec.index.values):
        #     ax1.text(annual_cost[j], ac_loss[j], label)
        #     ax2.text(annual_cost[j], sf_sum[j], label)
        #     ax3.text(annual_cost[j], fuel_cost[j], label)
        plt.show()
        st.pyplot(fig)


def make_dataframe_for_output(start_year, end_year, config_list):
    df = pd.DataFrame({'year': range(start_year, end_year),
                        config_list[0]: [0] * (end_year - start_year),
                        config_list[1]: [0] * (end_year - start_year),
                        config_list[2]: [0] * (end_year - start_year),
                        config_list[3]: [0] * (end_year - start_year),
                        config_list[4]: [0] * (end_year - start_year),
                        config_list[5]: [0] * (end_year - start_year),
                        config_list[6]: [0] * (end_year - start_year),
                        config_list[7]: [0] * (end_year - start_year),
                        config_list[8]: [0] * (end_year - start_year),
                        config_list[9]: [0] * (end_year - start_year),
                        config_list[10]: [0] * (end_year - start_year),
                        config_list[11]: [0] * (end_year - start_year)})
    df_new = df.set_index('year')
    
    return df_new


def make_dataframe_for_output_multiple(start_year, end_year, config_list, ship_type_list):
    for i in range(len(ship_type_list)):
        df = pd.DataFrame({'year': range(start_year, end_year),
                            config_list[0]: [0] * (end_year - start_year),
                            config_list[1]: [0] * (end_year - start_year),
                            config_list[2]: [0] * (end_year - start_year),
                            config_list[3]: [0] * (end_year - start_year),
                            config_list[4]: [0] * (end_year - start_year),
                            config_list[5]: [0] * (end_year - start_year),
                            config_list[6]: [0] * (end_year - start_year),
                            config_list[7]: [0] * (end_year - start_year),
                            config_list[8]: [0] * (end_year - start_year),
                            config_list[9]: [0] * (end_year - start_year),
                            config_list[10]: [0] * (end_year - start_year),
                            config_list[11]: [0] * (end_year - start_year)})
        df_new = df.set_index('year')
        df_new['ship_type'] = ship_type_list[i]
        df_merge = df_new if i == 0 else pd.concat([df_merge, df_new])
    
    return df_merge


def show_stackplot(result, label, title, directory):
    fig = plt.figure(figsize=(20,10))
    cm=plt.get_cmap('tab20')
    ax1 = fig.add_subplot(1, 1, 1)
    ax1.stackplot(result.index, [result[s] for s in label], labels=label, colors= [cm(i) for i in range(12)]) #, color=a, cmap=cm) #, color=color_maps)
    ax1.set_title(title, fontsize=16)
    ax1.legend(loc='upper left', fontsize=16)
    st.pyplot(fig)
    fig.savefig(directory+'/'+title+'.png')


def plot_graph(data, x, y, hue, ylabel, title):
    fig = plt.figure(figsize=(12, 6))
    sns.barplot(x=x, y=y, hue=hue, data=data, ci=None, estimator=sum)
    plt.xlabel('Year', fontsize=16)
    plt.ylabel(ylabel, fontsize=16)
    plt.title(title, fontsize=16)
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
    # fig.savefig(directory + '/' + title + '.png')


def plot_graph_stack(data, x, y_list, ylabel_list, ylabel_total, title):
    fig = plt.figure(figsize=(12, 6))
    cm = plt.get_cmap('tab20')
    for i, y_each in range(y_list):
        sns.barplot(x=x, y=y_each, data=data, color=cm(i), label=ylabel_list(i), ci=None)

    plt.xlabel('Year', fontsize=16)
    plt.ylabel(ylabel_total, fontsize=16)
    plt.title(title, fontsize=16)
    plt.xticks(rotation=45, fontsize=16)
    plt.tight_layout()
    st.pyplot(fig)
    # fig.savefig(directory + '/' + title + '.png')


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


def show_linechart_two(x, y1, y2, label, title, directory):
    fig = plt.figure(figsize=(20,10))
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(x, y1, label='Profit')
    ax.plot(x, y2, label='Subsidy')
    ax.set_ylabel(label)
    ax.set_title(title)
    ax.legend(loc='upper left')

    ax.set_xticks(x)
    ax.set_xticklabels([int(label) for label in x])

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


def get_resultsareachart(result_data):
    result_data = result_data.reset_index().melt('year', var_name='type', value_name='y')
    hover = alt.selection_single(
        fields=['year'],
        nearest=True,
        on='mouseover',
        empty='none',
    )
    graphbase = (
        alt.Chart(result_data)
        .mark_area()
        .encode(
            alt.X('year', title=''),
            alt.Y('y', title=''),
            color='type',
        )
    )
    # Draw points on the line, and highlight based on selection
    graphpoints = graphbase.transform_filter(hover).mark_circle(size=65)
    # Draw a rule at the location of the selection
    graphtooltips = (
        alt.Chart(result_data)
        .mark_rule()
        .encode(
            alt.X('year'),
            alt.Y('y'),
            opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
            tooltip=[
                alt.Tooltip('year', title='year'),
                alt.Tooltip('y', title='value'),
            ],
        )
        .add_selection(hover)
    )
    return (graphbase+ graphpoints+ graphtooltips).interactive()


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
    
    # texts = []
    # for j, case in enumerate(control_cases):
    #     # text = plt.annotate(case[0]+'_'+case[1]+'_'+case[2]+'_'+case[3], (a[j], b[j]))
    #     text = plt.annotate(case, (a[uncertainty_cases*j], b[uncertainty_cases*j]))
    #     texts.append(text)
    # adjust_text(texts, arrowprops=dict(arrowstyle='-', color='gray', lw=0.5))
    fig.savefig(directory+'/'+title +'.png', bbox_inches='tight')
    plt.close()