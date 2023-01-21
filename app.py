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


# Initialisation de l'application Dash
app_treemap = Dash(__name__, external_stylesheets=[dbc.themes.LITERA])
app = app_treemap.server
app_treemap.config.suppress_callback_exceptions = False

load_figure_template('LITERA')

# Chargement des données à partir d'une url
url = 'https://raw.githubusercontent.com/louisroquiny/treemap-ccecrb-debat/main/gov_10a_exp.csv'
url2 = 'https://raw.githubusercontent.com/louisroquiny/treemap-ccecrb-debat/main/gov_10dd_edpt1.csv'

# Sourcing du projet
data_sources = '''
#### Data sources : Eurostat

General government expenditure by function (COFOG) (GOV_10A_EXP__custom_4563149). 
Available online at:[https://ec.europa.eu/eurostat/databrowser/bookmark/2f...](https://ec.europa.eu/eurostat/databrowser/bookmark/2f7bf2e7-1f91-4311-8780-2147ad8a9f3e?lang=en)

[Download the table](https://raw.githubusercontent.com/louisroquiny/treemap-ccecrb-debat/main/gov_10a_exp.csv)


Government deficit/surplus, debt and associated data [GOV_10DD_EDPT1__custom_4582036].
Available online at: [https://ec.europa.eu/eurostat/databrowser/bookmark/03...](https://ec.europa.eu/eurostat/databrowser/bookmark/0388f2fa-cd24-44e1-934a-d6f94cddd1e2?lang=en)

[Download the table](https://raw.githubusercontent.com/louisroquiny/treemap-ccecrb-debat/main/gov_10dd_edpt1.csv)
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
    data.geo = data.geo.replace('European Union - 27 countries (from 2020)', 'Europe')
    data.geo = data.geo.replace('Germany (until 1990 former territory of the FRG)', 'Germany')
    data.value = data.value.replace("#VALEUR!", 0)
    data.value =  data.value.str.replace(",", ".")
    data.value =  data.value.astype(float)
    if multiplicator is True:
        data.value = data.value*10
    else :
        pass
    return data

data = prepare_data(data, ['geo', 'code', 'thema', 'subthema'])
deficit = prepare_data(deficit, ['geo', 'labels'], multiplicator = True)

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
def generate_graph(id, markdown = None, style = None, style_graph = None):
    return html.Div(children = [
        html.Div([dcc.Markdown(markdown)]), 
        html.Div([dcc.Graph(
            id = id,
            style=style_graph)])
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
        style_graph = {'height' : 600}),
    # Graphique 2
    generate_graph(
        id = 'evolution-graph',
        style = {'width' : '50%', 'height' : '50%', 'display' : 'inline-block'}),
    # Graphique 3
    generate_graph(
        id = 'decomposition-graph',
        style = {'width' : '50%', 'height' : '50%', 'display' : 'inline-block'}
        ),
    # séparateur
    html.Hr(style={'width': '75%', 'margin-left': 'auto', 'margin-right': 'auto'}),
    # Graphique 4
    generate_graph(
        id = 'deficit-graph'),
    # Graphique 4
    generate_graph(
        id = 'debt-graph'),
    # Sources du projet
    html.Div([
        html.Div(style={'margin-top': '80px', 'margin-bottom': '10px'}),
        html.Hr(),
        dcc.Markdown(data_sources)
    ])
])

# Fonction de mise à jour du graphique en fonction des sélections de l'utilisateur
@app_treemap.callback(
    [Output('geo-graph', 'figure'),
     Output('evolution-graph', 'figure'), 
     Output('decomposition-graph', 'figure'),
     Output('deficit-graph', 'figure'), 
     Output("debt-graph", 'figure')
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
        countries = sorted(selected_countries)
    
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
    
    # Create a dictionary to store the color for each country
    colors = {}
    palette = pl_colors.qualitative.Plotly
    
    # Création du Treemap
    def create_treemap(data, color, maxdepth = None) :
        fig = px.treemap(
            data, 
            path=['geo', 'thema', 'subthema'], 
            values='value',  
            color = color,
            maxdepth = maxdepth, 
            color_discrete_sequence=palette
            )
        return fig
    if len(themas) == 1 :
        # Générer le graphique en utilisant les données filtrées
        fig = create_treemap(filtered_data_for_treemap, color = 'subthema')
    else : 
        # Générer le graphique en utilisant les données filtrées
        fig = create_treemap(filtered_data_for_treemap, color = 'thema', maxdepth = 2)
    
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
    
    # Iterate over all countries
    for i, country in enumerate(countries):
        # Generate a random color for current country
        colors[country] = palette[i]
    
    def create_pxline(data, labels):
        data = data.sort_values(['year', 'geo'])
        data['color'] = data['geo'].map(colors)
        fig = px.line(data, x = "year", y = 'value', color = 'geo', labels = labels)
        for i, trace in enumerate(fig.data):
           trace.line.color = palette[i]
        return fig
    
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
        for i, country in enumerate(countries):
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
    # Graphique 2
    if len(themas) == 1 :
        # Ajout d'une colonne pour le secteur de dépense
        grouped_data["thema"] = themas[0]
        fig2 = create_pxline(grouped_data, labels = {'geo' : themas[0]})
    else : 
        fig2 = create_pxline(grouped_data, labels = {'geo' : 'country'})
    
    # Graphique 5
    if len(themas) == 1 :
        # Préparez vos données en regroupant les sous-thèmes par thème et pays
        data_grouped = filtered_data_for_treemap.groupby(['thema','geo', 'subthema'])['value'].sum().reset_index()
        data_grouped_sorted = data_grouped.sort_values(['geo', 'value'])
        data_grouped_sorted['percentage'] = data_grouped_sorted.groupby('thema')['value'].transform(lambda x: round(x / x.sum(), 2))
        fig5 = px.histogram(data_grouped_sorted, x='geo', y='percentage', color = 'subthema', color_discrete_sequence = palette, labels = {'subthema': 'Subsector'})
        fig5.update_layout(xaxis_title="", yaxis_title="", bargap=0.8,  yaxis_tickformat = '%')
        fig5.update_traces(texttemplate='%{y}%', textposition='outside')
    else : 
        data_grouped = filtered_data_for_treemap.groupby(['geo'])['value'].sum().reset_index()
        data_grouped_sorted = data_grouped.sort_values(['geo', 'value'])
        fig5 = px.histogram(data_grouped_sorted, x = 'geo', y = 'value', color = 'geo', color_discrete_sequence = palette)
        fig5.update_layout(showlegend=False, xaxis_title="", yaxis_title="", bargap=0.8)
        fig5.update_traces(texttemplate='%{y:.2s}', textposition='outside')
       
    # Création de la troisième figure
    # Tri des données
    filtered_deficit = deficit[(deficit["geo"].isin(countries)) & (deficit.labels == "Net lending (+) /net borrowing (-)")]
    #fig3 = create_pxline(filtered_deficit, labels = {'geo' : 'country'})
    fig3 = create_pxscatter(filtered_deficit, labels = {'geo' : 'Country'}, threshold_up = -30, text_up = "Target : -30", dist = 10)
    
    # Création de la quatrième figure
    # Tri des données
    filtered_debt = deficit[(deficit["geo"].isin(countries)) & (deficit.labels == "Government consolidated gross debt")]
    fig4 = create_pxscatter(filtered_debt, labels = {'geo' : 'Country'}, threshold_up = 1000, threshold_down = 600, text_up = "GDP exceeded", text_down = 'Target : 600', dist = 50)
    
    # Adaptation des traces
    for figure in [fig2]:
        figure.update_traces(line=dict(shape='spline', width = 4))
        figure.update_layout(xaxis_title="", yaxis_title="")
        
    def add_title(fig, title):
        fig.update_layout(
            title_text=title,
            title_font=dict(size=14, family='Calibri'),
        )

    add_title(fig2, title = 'Evolution of expenditure (/1000 of GDP)')
    add_title(fig3, title = 'Evolution of the deficit/surplus ratio by country (/1000 of GDP)')
    if len(themas) == 1 : 
        add_title(fig5, title = 'Repartition of expenditure by subsector (% of sector)')
    else : 
        add_title(fig5, title = 'Total of expenditure by country (/1000 of GDP)')
    add_title(fig4, title = 'Evolution of the government consolidated gross debt (/1000 of GDP)')
    
    return fig, fig2, fig5, fig3, fig4

if __name__ == '__main__':
     app_treemap.run_server(debug=True)
