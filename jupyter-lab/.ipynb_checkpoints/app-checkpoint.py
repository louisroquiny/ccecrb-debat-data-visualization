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

# Initialisation de l'application Dash
app_treemap = Dash(__name__)
app = app_treemap.server
app_treemap.config.suppress_callback_exceptions = False

# Sources de mes données
source_fig = html.Div(id='source_fig', children=[
        html.B('Data sources : Eurostat'),
        html.P('fig 1 & fig2 : General government expenditure by function (COFOG) [GOV_10A_EXP__custom_4563149]'),
        html.P('Available online at:'),
        html.A('https://ec.europa.eu/eurostat/databrowser/bookmark/2f...', href='https://ec.europa.eu/eurostat/databrowser/bookmark/2f7bf2e7-1f91-4311-8780-2147ad8a9f3e?lang=en', style={'display': 'inline-block'}),
        html.P(),
        html.A('Download the table', href='https://raw.githubusercontent.com/louisroquiny/treemap-ccecrb-debat/main/gov_10a_exp__custom_4563149.csv'),

        html.P(' fig3: General government expenditure by function (COFOG) [GOV_10A_EXP__custom_4563149]'),
        html.P('Available online at: '),
        html.A('https://ec.europa.eu/eurostat/databrowser/bookmark/03...', href='https://ec.europa.eu/eurostat/databrowser/bookmark/0388f2fa-cd24-44e1-934a-d6f94cddd1e2?lang=en', style={'display': 'inline-block'}),
        html.P(),
        html.A('Download the table', href='https://raw.githubusercontent.com/louisroquiny/treemap-ccecrb-debat/main/gov_10dd_edpt1__custom_4582036_page_spreadsheet%20(1).csv')
    ],style={
        'font-family': 'Calibri',
        'font-size': '10px', 
        'color' : 'grey', 
        'align' : 'right'
    })

# Chargement des données à partir d'une url
url = 'https://raw.githubusercontent.com/louisroquiny/treemap-ccecrb-debat/main/gov_10a_exp__custom_4563149.csv'
data = pd.read_csv(url, sep = ';')

# Préparation des données en utilisant la fonction melt de pandas
data = data.melt(id_vars=['geo', 'code', 'thema', 'subthema'], var_name='year', value_name='value')

# Conversion de la colonne year en entier
data.year = pd.to_numeric(data['year'], downcast='integer')

# Remplacement des valeurs manquantes par 0
data.value = data.value.replace("#VALEUR!", 0)

# Conversion de la colonne value en entier
data.value =  pd.to_numeric(data['value'], downcast='integer')

# Obtention des options de pays, d'années et de secteurs pour les menus déroulants
country_options = data["geo"].unique()
country_options = sorted(country_options)
years = data['year'].unique()
year_options = {str(year): str(year) for year in years}
thema_options = data.thema.unique()
thema_options = sorted(thema_options)
thema_options.insert(0, 'All sectors')

# Deuxième jeu de données : surplus-déficit
# Chargement des données à partir d'une url
url2 = 'https://raw.githubusercontent.com/louisroquiny/treemap-ccecrb-debat/main/gov_10dd_edpt1__custom_4582036_page_spreadsheet%20(1).csv'
deficit = pd.read_csv(url2, sep = ';')

# Préparation des données
deficit = deficit.melt(id_vars=['geo'], var_name='year', value_name='value')

# Conversion des colonnes year et value en entier
deficit.year = pd.to_numeric(deficit['year'], downcast='integer')
deficit.value = deficit.value.str.replace(",", ".")
deficit.value =  deficit.value.astype(float)


# Mise en place de la structure de l'application
app_treemap.layout = html.Div([
    html.Div([
        html.H2('How much do European countries spend on their public finances?')
    ]),
    html.Div([
        html.H3('Budget: 1000 euros')
    ]),
    html.Div([
        html.Label('Select one or more countries:'),
        dcc.Dropdown(
            id='select-country',
            options=[{'label': i, 'value': i} for i in country_options],
            value='Belgium',
            multi = True
        )
    ],style={'width': '40%','display': 'inline-block'}),
    html.Div([
        html.Label('Select one sector:'),
        dcc.Dropdown(
            id='select-themas',
            options=[{'label': i, 'value': i} for i in thema_options], 
            value = 'All sectors',
            #multi = True, 
        )
    ],style={'width': '30%','display': 'inline-block'}),
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
    ],style={ 'width': '100%','display': 'inline-block', }),
    html.Div([
        dcc.Graph(
            id='geo-graph'), 
    ]),
    html.Div([
        dcc.Graph(
            id='evolution-graph'), 
    ],style={}),
    html.Div([
        dcc.Graph(
            id='deficit-graph')
    ],style={}),
    
    source_fig
])

# Fonction de mise à jour du graphique en fonction des sélections de l'utilisateur
@app_treemap.callback(
    [Output('geo-graph', 'figure'),
     Output('evolution-graph', 'figure'), 
     Output('deficit-graph', 'figure')
     ],
    [Input('select-country', 'value'),
     Input('select-year', 'value'), 
    Input('select-themas', 'value')
    ]
    )

def update_graph(selected_countries, selected_year, selected_thema):
    

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
    filtered_data = filtered_data[filtered_data['year'] == selected_year]
    
    if len(themas) == 1 :
        # Générer le graphique en utilisant les données filtrées
        fig = px.treemap(
            filtered_data, 
            path=['geo', 'thema', 'subthema'], 
            values='value',  
            #maxdepth=2, 
            color = 'subthema', 
        )
    else : 
        # Générer le graphique en utilisant les données filtrées
        fig = px.treemap(
            filtered_data, 
            path=['geo', 'thema', 'subthema'], 
            values='value',  
            maxdepth=2, 
            color = 'thema', 
        )
    
    # Mise en forme de la bulle d'info au survol
    fig.data[0].hovertemplate = (
      '<b>%{label}</b>'
      '<br>'
      '<b>%{value} euros</b>  from the budget of <b>1000 euros</b> are spent'
      '<br>'
       )
    
    # Mise en forme de la légende
    fig.update_traces(
        textinfo = "label+value",
        root_color="lightgrey"
    )
    
    
    # Filtrer les données en fonction des pays et des thèmes sélectionnés
    filtered_data2 = data[data["geo"].isin(countries) & data["thema"].isin(themas)]
    # Grouper les données par année et pays
    grouped_data = filtered_data2.groupby(['geo', 'year'])['value'].sum()
    grouped_data = grouped_data.reset_index()
    
    if len(themas) == 1 :
        grouped_data["thema"] = themas[0]
        fig2 = px.line(
            grouped_data, 
            x = "year", 
            y = 'value', 
            color = 'geo', 
            template = "simple_white",
            labels = {'geo' : themas[0]}
            )
    else : 
        fig2 = px.line(
            grouped_data, 
            x = "year", 
            y = 'value', 
            color = 'geo', 
            template = "simple_white",
            labels = {'geo' : 'country'}
            )
        
    # Création de la troisième figure
    # Tri des données
    filtered_deficit = deficit[deficit["geo"].isin(countries)]
    fig3 = px.line(
        filtered_deficit, 
        x = "year", 
        y = 'value', 
        color = 'geo', 
        template = "simple_white",
        labels = {'geo' : 'country'})
    
    # Ecriture des titres
    fig.update_layout(
    title=dict(text="Repartition of depenses", x=0.5, font=dict(family='Calibri',size=10))
    )
    fig2.update_layout(
    title=dict(text="Evolutions of depenses", x=0.5, font=dict(family='Calibri',size=10))
    )
    fig3.update_layout(
    title=dict(text="Evolution of country deficit", x=0.5, font=dict(family='Calibri',size=10))
    )
    
    # Adaptation des traces
    for figure in [fig2, fig3]:
        figure.update_traces(line=dict(shape='spline'))

    
    return fig, fig2, fig3

if __name__ == '__main__':
    app_treemap.run_server(debug=True)