# -*- coding: utf-8 -*-
"""
Created on Mon Dec 12 14:07:04 2022

@author: loro
"""
import dash
from dash import Dash, html, dcc, Input, Output
import plotly.express as px
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


# Initialisation de l'application Dash
app_treemap = Dash(__name__, external_stylesheets=[dbc.themes.LITERA])
app = app_treemap.server
app_treemap.config.suppress_callback_exceptions = False

load_figure_template('LITERA')

# Chargement des données à partir d'une url
url = 'https://raw.githubusercontent.com/louisroquiny/treemap-ccecrb-debat/main/gov_10a_exp__custom_4563149.csv'
url2 = 'https://raw.githubusercontent.com/louisroquiny/treemap-ccecrb-debat/main/gov_10dd_edpt1__custom_4582036_page_spreadsheet%20(1).csv'

# Sourcing du projet
data_sources = '''
#### Data sources : Eurostat

General government expenditure by function (COFOG) (GOV_10A_EXP__custom_4563149). 
Available online at:[https://ec.europa.eu/eurostat/databrowser/bookmark/2f...](https://ec.europa.eu/eurostat/databrowser/bookmark/2f7bf2e7-1f91-4311-8780-2147ad8a9f3e?lang=en)

[Download the table](https://raw.githubusercontent.com/louisroquiny/treemap-ccecrb-debat/main/gov_10a_exp__custom_4563149.csv)


General government expenditure by function (COFOG) (GOV_10A_EXP__custom_4563149).
Available online at: [https://ec.europa.eu/eurostat/databrowser/bookmark/03...](https://ec.europa.eu/eurostat/databrowser/bookmark/0388f2fa-cd24-44e1-934a-d6f94cddd1e2?lang=en)

[Download the table](https://raw.githubusercontent.com/louisroquiny/treemap-ccecrb-debat/main/gov_10dd_edpt1__custom_4582036_page_spreadsheet%20(1).csv)
    '''

# Chargement des données à partir d'une url
def load_data(url, sep):
    data = pd.read_csv(url, sep = sep)
    return data

data = load_data(url, ';')
deficit = load_data(url2, ';')

# Préparation des données en utilisant la fonction melt de pandas
def prepare_data(data, col_to_melt, multiplicator = False):
    data = data.melt(id_vars=col_to_melt, var_name='year', value_name='value')
    data.year = pd.to_numeric(data['year'], downcast='integer')
    data.value = data.value.replace("#VALEUR!", 0)
    data.value =  data.value.str.replace(",", ".")
    data.value =  data.value.astype(float)
    if multiplicator is True:
        data.value = data.value*10
    else :
        pass
    return data

data = prepare_data(data, ['geo', 'code', 'thema', 'subthema'])
deficit = prepare_data(deficit, ['geo'], multiplicator = True)

# Obtention des options de pays, d'années et de secteurs pour les menus déroulants
def get_options(data, column):
    options = data[column].unique()
    options = sorted(options)
    return options

country_options = get_options(data, "geo")
thema_options = get_options(data, "thema")
thema_options.insert(0, 'All sectors')
years = get_options(data, "year")
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
def generate_graph(id, markdown, style = None):
    return html.Div(children = [
        html.Div([dcc.Markdown(markdown)]), 
        html.Div([dcc.Graph(
            id = id,
            style=style)])
        ])

# Développement du layout de mon app
app_treemap.layout = html.Div([
    # Titre
    html.H1('How do European countries manage their public finances?'),
    # Sous-titre
    html.H5('This dashboard allows you to view some public finance indicators. Select one or more countries to compare them. You can also isolate a specific spending sector for a better visualisation. I wish you a good work!'),
    # Menus déroulants
    html.Div(style={'margin-top': '5%', 'margin-bottom': '5%', "width" : "100%"}, 
    children=[
        generate_dropdown('select-country', country_options, 'Belgium', 'Select countries:', multi = True),
        generate_dropdown('select-thema', thema_options, 'All sectors', 'Select sector:'),
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
        id = 'geo-graph',
        markdown = '''
##### Distribution of expenditure (/1000 of GDP)
Each country has a budget of 1000 euros, equivalent to 100% of its GDP. Let's see how it allocates its budget between the different spending sectors.  
    ''', 
        style = {'height' : 600}),
    # Graphique 2
    generate_graph(
        id = 'evolution-graph',
        markdown = '''
##### Evolution of expenditure (/1000 of GDP)
    '''),
    # Graphique 3
    generate_graph(
        id = 'deficit-graph',
        markdown = '''
##### Evolution of the deficit/surplus ratio by country (/1000 of GDP).
     '''),
    # Sources du projet
    html.Div([
        dcc.Markdown(data_sources) 
    ])
])

# Fonction de mise à jour du graphique en fonction des sélections de l'utilisateur
@app_treemap.callback(
    [Output('geo-graph', 'figure'),
     Output('evolution-graph', 'figure'), 
     Output('deficit-graph', 'figure')
     ],
    [Input('select-country', 'value'),
     Input('select-year', 'value'), 
    Input('select-thema', 'value')
    ]
    )

def update_graph(selected_countries, selected_year, selected_thema):
    
    # Formatage des callbacks
    if type(selected_countries) == str :
        countries = [selected_countries]
    else : 
        countries = selected_countries
    
    if selected_thema == "All sectors" :
        themas = sorted(data.thema.unique())
    elif type(selected_thema) == str :
        themas = [selected_thema]
    elif selected_thema is None:
        themas = sorted(data.thema.unique())
    else : 
        themas = selected_thema
    
    # Filtrer les données en fonction des sélections de l'utilisateur
    filtered_data = data[data["geo"].isin(countries) & data["thema"].isin(themas)]  
    filtered_data_for_treemap = filtered_data[filtered_data['year'] == selected_year]
    
    # Création du Treemap
    def create_treemap(data, maxdepth = None) :
        fig = px.treemap(
            data, 
            path=['geo', 'thema', 'subthema'], 
            values='value',  
            maxdepth=maxdepth, 
            color = 'thema'
            )
        return fig
    if len(themas) == 1 :
        # Générer le graphique en utilisant les données filtrées
        fig = create_treemap(filtered_data_for_treemap)
    else : 
        # Générer le graphique en utilisant les données filtrées
        fig = create_treemap(filtered_data_for_treemap, maxdepth = 2)
    
    # Mise en forme de la bulle d'info au survol
    fig.data[0].hovertemplate = (
      '<b>%{label}</b>'
      '<br>'
      '<b>%{value}</b> out of <b>1000 euros</b> are spent'
      '<br>'
       )
    
    # Mise en forme de la légende
    fig.update_traces(
        textinfo = "label+value",
        root_color="lightgrey"
    )
    

    # Grouper les données par année et pays
    grouped_data = filtered_data.groupby(['geo', 'year'])['value'].sum()
    grouped_data = grouped_data.reset_index()
    
    def create_pxline(data, labels) :
        fig = px.line(
            data, 
            x = "year", 
            y = 'value', 
            color = 'geo', 
            labels = labels
            )
        return fig
    
    if len(themas) == 1 :
        # Ajout d'une colonne pour le secteur de dépense
        grouped_data["thema"] = themas[0]
        fig2 = create_pxline(grouped_data, labels = {'geo' : themas[0]})
    else : 
        fig2 = create_pxline(grouped_data, labels = {'geo' : 'country'})
        
    # Création de la troisième figure
    # Tri des données
    filtered_deficit = deficit[deficit["geo"].isin(countries)]
    fig3 = create_pxline(filtered_deficit, labels = {'geo' : 'country'})
    
    # Adaptation des traces
    for figure in [fig2, fig3]:
        figure.update_traces(line=dict(shape='spline', width = 5))
    
    return fig, fig2, fig3

if __name__ == '__main__':
     app_treemap.run_server(debug=True)
