# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 10:46:45 2023

@author: loro
"""

# Importez les bibliothèques nécessaires
import json
import dash
from dash import Dash, html, dcc, Input, Output, dash_table
import pandas as pd
import dash_bootstrap_components as dbc


#importation de la bibliographie
# with open('C:/Users/loro.CCECRB/Desktop/finances_publiques.json') as json_file : 
#     data = json.load(json_file)
# biblio = pd.json_normalize(data,"author",  ['id', 'type', 'language', 'page', 'title', 'issued'], errors = 'ignore')

url = 'https://raw.githubusercontent.com/louisroquiny/treemap-ccecrb-debat/main/bibliography.json'
biblio = pd.read_json(url)
# biblio.fillna("", inplace=True)
biblio['author'] = biblio['author'].apply(lambda x: ', '.join([item.get('literal', '') + item.get('family', '') +' ' + item.get('given', '') for item in x]))
biblio['issued'] = biblio['issued'].apply(lambda x: x['date-parts'][0] if type(x) == dict else None)
biblio['issued'] = biblio['issued'].apply(lambda x:'/'.join(str(item)  for item in x)  if x else None)

biblio["issued"] = pd.to_datetime(biblio["issued"], infer_datetime_format= True)
biblio["issued"] = biblio["issued"].dt.date

biblio.fillna("", inplace=True)

biblio.URL = biblio.URL.astype(str).apply(lambda x : '[Link]('+ x + ')' if len(x) > 0 else "" )



#On récupère les colonnes à supprimer
columns_to_drop = list(biblio.columns[24:25]) + list(biblio.columns[28:])

#On supprime les colonnes
biblio.drop(columns_to_drop, axis = 1, inplace = True)


# biblio = biblio.astype(str)
biblio_to_display = biblio[['title', 'author','type', 'issued','URL']].sort_values('issued', ascending = False)

app_biblio = Dash(__name__, external_stylesheets=[dbc.themes.LITERA])
app = app_biblio.server
app_biblio.config.suppress_callback_exceptions = False

# Ajoutez un champ de recherche et un tableau à la page HTML
app_biblio.layout = dash_table.DataTable(
    biblio_to_display.to_dict("records"),
    #[{"name": i, "id": i} for i in biblio_to_display.columns],
    [{'id': x, 'name': x, 'presentation': 'markdown'} if x == 'URL' else {'id': x, 'name': x} for x in biblio_to_display.columns],
    filter_action="native",
    sort_action='native',
    sort_mode="multi",
    filter_options={"placeholder_text": "Filter column..."},
    # fixed_rows={'headers': True},
    page_size=15,
    style_table={
        'overflowX': 'auto',
        'height': '100%',
        # 'witdh' : 500
        },
    style_data={
    'whiteSpace': 'normal',
    'height': 'auto',
    },
    style_cell = {'font_size': '14px'},
    style_cell_conditional=[
        {
            'if': {'column_id': 'title'},
            'textAlign': 'left'
        }, 
        {
            'if': {'column_id': 'author'},
            'textAlign': 'left'
        }]
)

# Exécutez l'application
if __name__ == '__main__':
    app_biblio.run_server(debug=True)

