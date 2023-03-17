# -*- coding: utf-8 -*-
"""
Created on Mon Dec 12 14:07:04 2022

@author: loro
"""
import dash
from dash import Dash, html, dcc, Input, Output
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.colors as pl_colors
import pandas as pd
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

"""
Bootstrap theme : 
    FLATLY
    LITERA
    VAPOR
"""

# =============================================================================
# Initialisation de l'application Dash
# =============================================================================

app_treemap = Dash(__name__, external_stylesheets=[dbc.themes.LITERA])
app = app_treemap.server
app_treemap.config.suppress_callback_exceptions = False

load_figure_template('LITERA')

# Chargement des données à partir d'une url
git = 'https://raw.githubusercontent.com/louisroquiny/treemap-ccecrb-debat/main/data/'
expenditure_url = git + 'expenditure.csv'
deficit_debt_url = git + 'deficit_debt.csv'
gdp_url = git + 'gdp.csv'
revenue_url = git + 'revenue.csv'

# expenditure_url = 'C:/Users/loro.CCECRB/Documents/GitHub/treemap-ccecrb-debat/data/expenditure.csv'
# deficit_debt_url = 'C:/Users/loro.CCECRB/Documents/GitHub/treemap-ccecrb-debat/data/deficit_debt.csv'
# gdp_url = 'C:/Users/loro.CCECRB/Documents/GitHub/treemap-ccecrb-debat/data/gdp.csv'

# Sourcing du projet
data_sources = '''
#### Data sources : Eurostat

General government expenditure by function (COFOG) [GOV_10A_EXP__custom_4770037]. 
Available online at:[https://ec.europa.eu/eurostat/databrowser/bookmark/728cdcda-e024-4c32-8d33-d7d4759a8ead?lang=en)

[Download the table](https://raw.githubusercontent.com/louisroquiny/treemap-ccecrb-debat/main/data/expenditure.csv)


Government deficit/surplus, debt and associated data [GOV_10DD_EDPT1__custom_4811714].
Available online at: [https://ec.europa.eu/eurostat/databrowser/bookmark/2f225175-f29b-4495-bbc1-fbef4c7f773e?lang=en)

[Download the table](https://raw.githubusercontent.com/louisroquiny/treemap-ccecrb-debat/main/data/deficit_debt.csv)
    '''

# Chargement des données à partir d'une url
def load_data(url, sep):
    data = pd.read_csv(url, sep = sep)
    return data

expenditure = load_data(expenditure_url, ';')
deficit = load_data(deficit_debt_url, ';')
gdp = load_data(gdp_url, ';')
revenue = load_data(revenue_url, ';')

# Préparation des données en utilisant la fonction melt de pandas
def prepare_data(data, cols):
    data.columns = cols
    data.geo = data.geo.replace(
        'European Union - 27 countries (from 2020)', 'Europe')
    data.geo = data.geo.replace(
        'Germany (until 1990 former territory of the FRG)', 'Germany')
    # data.value = data.value.replace("#VALEUR!", 0)
    return data

expenditure = prepare_data(
    expenditure, ['unit', 'sector', 'subsector', 'geo', 'year', 'value'])
deficit = prepare_data(
    deficit, ['unit', 'labels', 'geo', 'year', 'value'])
gdp = prepare_data(
    gdp, ['geo', 'year', 'value'])
# gdp.value = gdp.value*1000
revenue = prepare_data(revenue, ['unit', 'labels', 'geo', 'year', 'value'])
revenue.value = revenue.value/100


# Obtention des options de pays, d'années et de secteurs pour les menus déroulants
def get_options(data, column):
    options = data[column].unique()
    options = sorted(options)
    return options

country_options = get_options(expenditure, "geo")
sector_options = get_options(expenditure, "sector")
sector_options.insert(0, 'All sectors')
years = get_options(expenditure, "year")
year_options = {str(year): str(year) for year in years}

# Generation des div pour les menus déroulants
def generate_dropdown(id, options, value, label, multi = False):
    return html.Div([
        html.Label(label),
        dcc.Dropdown(
            id=id,
            options=[{'label': i, 'value': i} for i in options],
            value=value, 
            multi = multi
        )
    ])

# Generation des div pour les graphiques
def generate_graph(id, markdown = None, style = None, style_graph = None):
    return html.Div(children = [
        html.Div([dcc.Markdown(markdown)]), 
        html.Div([dcc.Graph(
            id = id,
            style=style_graph,
            config={'displayModeBar': False})])
        ], style = style)

# Développement du layout de mon app
app_treemap.layout = html.Div([
    # Titre
    html.H1('How do European countries manage their public finances?'),
    # Sous-titre
    html.H5('This dashboard allows you to view some public finance indicators. Select one or more countries to compare them. You can also isolate a specific spending sector for a better visualisation. I wish you a good work!'),
    # Menus déroulants
    html.Div(style={'margin-top': '5%', 'margin-bottom': '5%', "width" : "100%"}, 
    children=[
        generate_dropdown('select-country', country_options, ['Belgium', 'France', 'Netherlands', 'Germany'], 'Select countries:', multi = True),
        generate_dropdown('select-sector', sector_options, 'All sectors', 'Select sector:'),
        # Date Slider
        html.Div([
               html.Label('Select date:'),
               dcc.Slider(
                   id='select-year',
                   min=min(years),
                   max=max(years),
                   step=None,
                   marks={i: {"label":str(i), "style": {"transform": "rotate(45deg)", "white-space": "nowrap"}} for i in year_options},
                   value=max(years), 
               )
       ],style={ 'width': '100%' }),
    ]),
    # Graphique 1
    generate_graph(
        id = 'treemap-graph',
        markdown = '''
##### Distribution of expenditure (/1000 of GDP)
Each country has a budget of 1000 euros, equivalent to 100% of its GDP. Let's see how it allocates its budget between the different spending sectors.  
    ''', 
        style_graph = {'height' : 600}),
    # Graphique
    generate_graph(
        id = 'evolution-graph',
        style = {'width' : '50%', 'height' : '50%', 'display' : 'inline-block'}),
    # Graphique
    generate_graph(
        id = 'decomposition-graph',
        style = {'width' : '50%', 'height' : '50%', 'display' : 'inline-block'}
        ),
    # séparateur
    html.Hr(style={'width': '75%', 'margin-left': 'auto', 'margin-right': 'auto'}),
    # Graphique
    generate_graph(
        id = 'revenue-graph'),
    # Graphique
    generate_graph(
        id = 'deficit-graph'),
    # Graphique
    generate_graph(
        id = 'debt-graph'),
    # Sources du projet
    html.Div([
        html.Div(style={'margin-top': '80px', 'margin-bottom': '10px'}),
        html.Hr(),
        dcc.Markdown(data_sources, link_target="_blank")
    ])
])

# =============================================================================
# Fonction de mise à jour du graphique en fonction des sélections de l'utilisateur
# =============================================================================

@app_treemap.callback(
    [Output('treemap-graph', 'figure'),
     Output('evolution-graph', 'figure'), 
     Output('decomposition-graph', 'figure'),
     Output('revenue-graph', 'figure'),
     Output('deficit-graph', 'figure'), 
     Output("debt-graph", 'figure')
     ],
    [Input('select-country', 'value'),
     Input('select-year', 'value'), 
    Input('select-sector', 'value')
    ]
    )

def update_graph(selected_countries, selected_year, selected_sector):
           
# =============================================================================
# Formatage des callbacks
# =============================================================================
    
    ## Liste de un ou plusieurs pays
    if type(selected_countries) == str :
        countries = list(selected_countries)
    else : 
        countries = sorted(selected_countries)
    ## Liste de thématiques
    if selected_sector == "All sectors" :
        sectors = sorted(expenditure.sector.unique())
    elif type(selected_sector) == str :
        sectors = [selected_sector]
    elif selected_sector is None:
        sectors = sorted(expenditure.sector.unique())
    else : 
        sectors = selected_sector
    
# =============================================================================
# Define color palette
# =============================================================================
    
    # Create a dictionary to store the color for each country
    def fix_colors(mylist, palette) :
        colors = {}
        # Iterate over all items of my list
        for i, item in enumerate(mylist):
            # Generate a random color for current country
            colors[item] = palette[i]
        return colors
    
    palette = pl_colors.qualitative.Bold 
    colors = fix_colors(countries, palette)
    colors_sector = fix_colors(sectors, palette)
    
# =============================================================================
# TREEMAP-GRAPH
# =============================================================================
    
    # Treemap function
    def create_treemap(data, color, maxdepth = None, palette = None, palette_map = None) :
        fig = px.treemap(
            data, 
            path=['geo', 'sector', 'subsector'], 
            values='value',  
            color = color,
            maxdepth = maxdepth,
            color_discrete_sequence = palette, 
            color_discrete_map = palette_map
            )
        return fig
    
    # Formatage des données
    filtered_data_for_treemap = expenditure[
        expenditure.geo.isin(countries) 
        & expenditure.sector.isin(sectors) 
        & (expenditure.year == selected_year)
        & (expenditure.unit == 'Percentage of gross domestic product (GDP)')
        ]
    filtered_data_for_treemap.drop('unit', axis = 1, inplace = True)
    filtered_data_for_treemap.value = filtered_data_for_treemap.value*10
    
    # Création du treemap
    if len(sectors) == 1 :
        # Générer le graphique en utilisant les données filtrées
        colors_subsector = fix_colors(filtered_data_for_treemap.subsector.unique(), palette)
        treemap_graph = create_treemap(filtered_data_for_treemap, color = 'subsector', palette_map = colors_subsector)
    else : 
        # Générer le graphique en utilisant les données filtrées
        treemap_graph = create_treemap(filtered_data_for_treemap, color = 'sector',maxdepth = 2, palette_map = colors_sector)
    
    # Mise en forme de la bulle d'info au survol
    treemap_graph.data[0].hovertemplate = (
      '<b>%{label}</b>'
      '<br>'
      '<b>%{value}</b> out of <b>1000 euros</b> are spent'
      '<br>'
        )
    
    # Mise en forme de la légende
    treemap_graph.update_traces(
        textinfo = "label+value",
        root_color="lightgrey"
        )
    
# =============================================================================
# line-chart
# =============================================================================

    # Line chart function
    def create_pxline(data, labels):
        data = data.sort_values(['year', 'geo'])
        data['color'] = data['geo'].map(colors)
        fig = px.line(data, x = "year", y = 'value', color = 'geo', labels = labels)
        for i, trace in enumerate(fig.data):
           trace.line.color = palette[i]
        return fig   
    
    # Grouper les données par année et pays
    filtered_data_for_line = expenditure[
        expenditure["geo"].isin(countries) 
        & expenditure["sector"].isin(sectors)
        ]
    filtered_data_for_line = filtered_data_for_line [
        filtered_data_for_line.unit == 'Percentage of gross domestic product (GDP)']
    filtered_data_for_line.value =  filtered_data_for_line.value / 100
    
    grouped_data_for_line = filtered_data_for_line.groupby(['geo', 'year'])['value'].sum()
    grouped_data_for_line = grouped_data_for_line.reset_index()
    
    # Création du graphique
    if len(sectors) == 1 :
        # Ajout d'une colonne pour le secteur de dépense
        grouped_data_for_line["sector"] = sectors[0]
        evolution_graph = create_pxline(grouped_data_for_line, labels = {'geo' : sectors[0]})
    else : 
        evolution_graph = create_pxline(grouped_data_for_line, labels = {'geo' : 'country'})
        
    # Adaptation des traces
    for figure in [evolution_graph]:
        figure.update_traces(line=dict(shape='spline', width = 4))
        figure.update_layout(xaxis_title="", yaxis_title="", hovermode = 'x')
        figure.layout.yaxis.tickformat = 'p'
        
    for trace in evolution_graph.data:
        trace.hovertemplate = '%{y:.2%}'
    
# =============================================================================
# PIB-chart
# =============================================================================
         
    # Création du graphique
    if len(sectors) == 1 :
        # Préparez vos données en regroupant les sous-thèmes par thème et pays
        dataframe_to_group = expenditure[expenditure.unit == 'Million euro']
        
        filtered_data_for_area = dataframe_to_group[
            dataframe_to_group.geo.isin(countries) 
            & (dataframe_to_group.year == selected_year)
            & (dataframe_to_group.sector ==  sectors[0])
            ]
    
        data_grouped = filtered_data_for_area.groupby(['sector','geo', 'subsector'])['value'].sum().reset_index()
        
        # data_grouped["colors_subsector"] = data_grouped.subsector.map(colors_subsector)
        data_grouped_sorted = data_grouped.sort_values(['geo', 'value'])
        # data_grouped_sorted['percentage'] = data_grouped_sorted.value.transform(lambda x: round(x / x.sum(),2)*100)
        
        decomposition_graph = px.histogram(
            data_grouped_sorted, 
            x='geo', 
            y='value', 
            color = 'subsector', 
            text_auto = True,
            color_discrete_map = colors_subsector, 
            labels = {'subsector': 'subsector'})
        
        decomposition_graph.update_layout(xaxis_title="", yaxis_title="", bargap=0.5)
        decomposition_graph.update_traces(textposition='inside', hovertemplate = "%{y} euros")
   
    else : 
        dataframe_to_group = expenditure[expenditure.unit == 'Million euro']
        expenditure_grouped = dataframe_to_group.groupby(['geo','year'])['value'].sum().reset_index()
        filtered_for_area_merged = pd.merge(expenditure_grouped, gdp,  how='left', left_on=['geo','year'], right_on = ['geo','year'], suffixes = ('_expenditure', '_gdp'))
        
        pc = expenditure[
            expenditure.geo.isin(countries)
            & (expenditure.year == selected_year)
            & (expenditure.unit == 'Percentage of gross domestic product (GDP)')
            ]
        pc.drop(['unit', 'year', 'sector', 'subsector'], axis = 1, inplace = True)
        pc = pc.groupby('geo')['value'].sum().reset_index()
        pc_dict = pc.set_index('geo')['value'].to_dict()
        
        filtered_for_area_melt = filtered_for_area_merged.melt(id_vars = ['geo', 'year'], var_name = 'label', value_name = 'value')
        
        filtered_data_for_area = filtered_for_area_melt[
            filtered_for_area_melt.geo.isin(countries) 
            & (filtered_for_area_melt.year == selected_year)
            ]
        data_grouped_sorted = filtered_data_for_area.sort_values(['geo', 'value'])
        data_grouped_sorted.label = data_grouped_sorted.label.map({'value_gdp' : 'GDP', 'value_expenditure' : 'Expenditure'})
        
        decomposition_graph = px.bar(
            data_grouped_sorted, 
            x = 'geo', 
            y = 'value',
            color = 'geo', 
            pattern_shape = 'label',
            pattern_shape_map={"GDP" : "", "Expenditure" : ""},
            barmode = 'overlay',
            hover_name = 'label',
            # orientation = 'h', 
            text = 'label',
            # text_auto= True,
            color_discrete_sequence = palette, 
            )
        
        decomposition_graph.update_layout(
            showlegend=False, 
            xaxis_title="", 
            yaxis_title="",
            hovermode='closest',
            uniformtext_minsize = 8, 
            uniformtext_mode='hide'
            )

        for trace in decomposition_graph.data:
            geo = trace.x[0]
            value = trace.y[0]
            label = trace.name
            trace.hovertemplate = f"{value:,} euros".replace(",", " ")
            pc_value = round(pc_dict.get(geo, 0), 3) # Récupération de la valeur de pc pour chaque geo
            # trace.hovertemplate = f"{value} euros"
            if "Expenditure" in label : 
                trace.hovertemplate = f"{value:,} euros<br>{pc_value}% GDP".replace(",", " ") # Mise à jour des labels

        decomposition_graph.update_layout(showlegend=False, xaxis_title="", yaxis_title="", bargap=0.5)
        

# =============================================================================
# revenue-chart 
# =============================================================================        

    revenue_filtered = revenue[
        (revenue["geo"].isin(countries)) 
        & (revenue['labels'].isin(['Total general government revenue', 'Total general government expenditure']))
        & (revenue.unit == 'Percentage of gross domestic product (GDP)')
        ].sort_values(['geo', 'year'])
    
    label_mapping = {
        'Total general government revenue' : 'revenue', 
        'Total general government expenditure' : 'expenditure'
        }
    
    revenue_filtered.labels = revenue_filtered.labels.map(label_mapping)

    revenue_chart = px.line(
        revenue_filtered,
        x = 'year', 
        y = 'value', 
        color = 'geo', 
        line_dash = 'labels',
        facet_col = 'geo', 
        color_discrete_map = colors, 
        labels = {'geo' : 'country'}, 
        # line_shape = 'spline', 
        line_dash_map = {
            'revenue' : 'solid' , 
            'expenditure' : 'dot'
            }
        )
    for i in range(len(countries)) : 
        revenue_chart.update_xaxes(title_text='', col= i+1)
        revenue_chart.layout.annotations[i]["text"] = ''
    
    revenue_chart.layout.yaxis.tickformat = 'p'
    revenue_chart.update_layout(xaxis_title="", yaxis_title="", hovermode = 'x')
    revenue_chart.update_traces(line=dict(width = 4))
    
    for trace in revenue_chart.data:
        split = trace.name.split(', ')
        geo = split[0]
        label = split[1]
        trace.name = f'{geo}<br>{label}'
        trace.hovertemplate = '%{y:.2%}'
            

# =============================================================================
# deficit-surplus-chart 
# =============================================================================
   
   
    # Area line chart function
    def create_pxarea(data, labels, threshold_up = None, threshold_down = None, text_up = None, text_down = None, dist = None):
        
        # Create subplots with rows and columns based on the number of countries
        fig = px.area(
            data,
            x='year', 
            y= 'value', 
            color = 'geo',
            facet_col= 'geo',
            #facet_col_wrap=4,
            color_discrete_map = colors, 
            labels = {'geo' : 'country'}
            )
        for i in range(len(countries)) : 
            fig.update_xaxes(title_text='', col= i+1)
            fig.layout.annotations[i]["text"] = ''
                           
        if threshold_up :
            fig.add_shape( # add a horizontal "target" line
                type="line", line_color="black", line_width=1, opacity=1, line_dash="dash",
                x0=0, x1=1, xref="paper", y0=threshold_up, y1=threshold_up, yref="y"
            )
            fig.add_annotation(text=text_up, align="right", x=1, xref="paper", y=threshold_up + dist, yref="y", showarrow=False)
        
        if threshold_down :
            fig.add_shape( # add a horizontal "target" line
                type="line", line_color="black", line_width=1, opacity=1, line_dash="dash",
                x0=0, x1=1, xref="paper", y0=threshold_down, y1=threshold_down, yref="y"
            )
            fig.add_annotation(text=text_down, align="right", x=1, xref="paper", y=threshold_down + dist, yref="y", showarrow=False)
        
        return fig

    #tri des données
    filtered_deficit = deficit[
        (deficit["geo"].isin(countries)) 
        & (deficit.labels == "Net lending (+) /net borrowing (-)")
        & (deficit.unit == 'Percentage of gross domestic product (GDP)')
        ].sort_values('geo')
    filtered_deficit.value = filtered_deficit.value / 100
    deficit_chart = create_pxarea(filtered_deficit, labels = {'geo' : 'Country'}, threshold_up = -0.03, text_up = "Target : -3%", dist = -0.01)
    deficit_chart.update_traces(line=dict(width = 4))
    deficit_chart.layout.yaxis.tickformat = 'p'
    deficit_chart.update_layout(hovermode = 'x')
    for trace in deficit_chart.data:
        trace.hovertemplate = '%{y:.2%}'


    
# =============================================================================
# debt-chart
# =============================================================================
    # Scatter chart function
    def create_pxscatter(data, labels, threshold_up = None, threshold_down = None, text_up = None, text_down = None, dist = None):
        
        # Create subplots with rows and columns based on the number of countries
        fig = make_subplots(rows=1, cols=len(countries), shared_yaxes=True)
        if threshold_up :
            fig.add_shape( # add a horizontal "target" line
                type="line", line_color="black", line_width=1, opacity=1, line_dash="dash",
                x0=0, x1=1, xref="paper", y0=threshold_up, y1=threshold_up, yref="y"
            )
            fig.add_annotation(text=text_up, align="right", x=1, xref="paper", y=threshold_up + dist, yref="y", showarrow=False)
        
        if threshold_down :
            fig.add_shape( # add a horizontal "target" line
                type="line", line_color="black", line_width=1, opacity=1, line_dash="dash",
                x0=0, x1=1, xref="paper", y0=threshold_down, y1=threshold_down, yref="y"
            )
            fig.add_annotation(text=text_down, align="right", x=1, xref="paper", y=threshold_down + dist, yref="y", showarrow=False)
        
        # Iterate over all countries
        for i, country in enumerate(sorted(countries)):
            # Filter data for current country
            country_data = data[data['geo'] == country]
        
            # Full line for current country
            fig.add_trace(
                go.Scattergl(
                    x=country_data.year, y=country_data.value, 
                    #line={'dash' : 'solid', 'color': colors[country], 'width':4, 'shape' : 'vh'},
                    marker = {'color': colors[country], 'size':8},
                    name=country, 
                    mode = 'markers',
                    opacity = 0.4
                ), 
                row=1, col=i+1
                )
        
            # Above threshold_up for current country
            fig.add_trace(
                go.Scattergl(
                    x=country_data.year, y=country_data.value.where(country_data.value > threshold_up), 
                    #line={'dash' : 'solid', 'color': colors[country], 'width':4, 'shape' : 'vh'}, 
                    marker = {'color': colors[country], 'size':8},
                    #name=country, 
                    showlegend = False, 
                    mode = 'markers',
                    ), 
                row=1, col=i+1
                )
            
            # below threshold_down for current country
            fig.add_trace(
                go.Scattergl(
                    x=country_data.year, y=country_data.value.where(country_data.value <= threshold_down), 
                    #line={'dash' : 'solid', 'color': colors[country], 'width':4, 'shape' : 'vh'}, 
                    marker = {'color': colors[country], 'size':8},
                    #name=country, 
                    showlegend = False, 
                    mode = 'markers',
                    ), 
                row=1, col=i+1
                )
        return fig
    
    # Bar chart function
    def create_pxbar(data, labels, threshold_up = None, threshold_down = None, text_up = None, text_down = None, dist = None):
        
        # Create subplots with rows and columns based on the number of countries
        fig = px.bar(
            data,
            x='year', 
            y= 'value', 
            color = 'geo',
            facet_col= 'geo',
            #facet_col_wrap=4,
            color_discrete_map = colors, 
            labels = {'geo' : 'country'}
            )
        for i in range(len(countries)) : 
            fig.update_xaxes(title_text='', col= i+1)
            fig.layout.annotations[i]["text"] = ''
                           
        if threshold_up :
            fig.add_shape( # add a horizontal "target" line
                type="line", line_color="black", line_width=1, opacity=1, line_dash="dash",
                x0=0, x1=1, xref="paper", y0=threshold_up, y1=threshold_up, yref="y"
            )
            fig.add_annotation(text=text_up, align="right", x=1, xref="paper", y=threshold_up + dist, yref="y", showarrow=False)
        
        if threshold_down :
            fig.add_shape( # add a horizontal "target" line
                type="line", line_color="black", line_width=1, opacity=1, line_dash="dash",
                x0=0, x1=1, xref="paper", y0=threshold_down, y1=threshold_down, yref="y"
            )
            fig.add_annotation(text=text_down, align="right", x=1, xref="paper", y=threshold_down + dist, yref="y", showarrow=False)
        
        return fig
    
    # Tri des données
    filtered_debt = deficit[
        (deficit["geo"].isin(countries)) 
        & (deficit.labels == "Government consolidated gross debt")
        & (deficit.unit == 'Percentage of gross domestic product (GDP)')
        ].sort_values('geo')
    filtered_debt.value = filtered_debt.value / 100
    # debt_chart = create_pxscatter(filtered_debt, labels = {'geo' : 'Country'}, threshold_up = 1, threshold_down = 0.60, text_up = "GDP exceeded", text_down = 'Target : 60%', dist = 0.05)
    # debt_chart.layout.yaxis.tickformat = 'p'
    debt_chart = create_pxbar(filtered_debt, labels = {'geo' : 'Country'}, threshold_up = 1, threshold_down = 0.60, text_up = "GDP exceeded", text_down = 'Target : 60%', dist = 0.05)
    debt_chart.layout.yaxis.tickformat = 'p'
    debt_chart.update_layout(hovermode = 'x')
    for trace in debt_chart.data:
        trace.hovertemplate = '%{y:.2%}'
# =============================================================================
# title
# =============================================================================
    # Title function
    def add_title(fig, title):
        fig.update_layout(
            title_text=title,
            title_font=dict(size=16, family='Calibri')
            )    
    add_title(treemap_graph, title = 'Distribution of expenditure for {}'.format(selected_year))
    add_title(evolution_graph, title = 'Evolution of expenditure (%GDP)')
    add_title(revenue_chart, title = 'Evolution of revenue and expenditure (%GDP)')
    add_title(deficit_chart, title = 'Evolution of the deficit/surplus ratio by country (%GDP)')
    if len(sectors) == 1 : 
        add_title(decomposition_graph, title = 'Repartition of expenditure by subsector for {} (milions of euros)'.format(selected_year))
    else : 
        add_title(decomposition_graph, title = 'Total of expenditure by country for {} (milions of euros)'.format(selected_year))
    add_title(debt_chart, title = 'Evolution of the government consolidated gross debt (%GDP)')
    
# =============================================================================
# return
# =============================================================================
    
    return treemap_graph, evolution_graph, decomposition_graph,revenue_chart, deficit_chart, debt_chart

if __name__ == '__main__':
     app_treemap.run_server(debug=True)
