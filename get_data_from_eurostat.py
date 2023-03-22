# -*- coding: utf-8 -*-
"""
Created on Mon Jan 30 10:57:36 2023

@author: loro
"""

import pandas as pd
import numpy as np
# import eurostat
# import io
import json

def map_my_dataframe(data, mapping): 
    for col in data.columns : 
        if col not in ['TIME_PERIOD', 'OBS_VALUE'] :
            data[col] = data[col].map(mapping, inplace=True)
    return data

# Chargement du dictionnaire à partir du fichier JSON
with open("codelist.json", "r") as file:
    codelist = json.load(file)    
    
# Date scope
StartPeriod = 2001
EndPeriod = 2021

# URL
url_expenditure = 'https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/GOV_10A_EXP/A.MIO_EUR+PC_GDP.S13.GF02+GF01+GF04+GF03+GF06+GF05+GF08+GF07+GF09+GF10+GF1001+GF0908+GF0505+GF0703+GF0901+GF0108+GF0306+GF0504+GF0702+GF0705+GF0903+GF0506+GF0704+GF0902+GF0905+GF0706+GF0904+GF0907+GF0906+GF0101+GF0103+GF0301+GF0102+GF0105+GF0303+GF0501+GF0104+GF0302+GF0107+GF0305+GF0503+GF0701+GF0106+GF0304+GF0502+GF1003+GF1002+GF1005+GF1004+GF1007+GF1006+GF1009+GF1008+GF0406+GF0604+GF0802+GF0405+GF0603+GF0801+GF0408+GF0606+GF0804+GF0407+GF0605+GF0803+GF0806+GF0409+GF0805+GF0202+GF0201+GF0204+GF0402+GF0203+GF0401+GF0404+GF0602+GF0205+GF0403+GF0601.TE.DE+NO+BE+FI+PT+BG+DK+LT+LU+HR+LV+FR+HU+SE+SI+SK+EU27_2020+IE+EE+CH+EL+MT+IS+IT+ES+AT+CY+CZ+PL+RO+NL/?format=SDMX-CSV&startPeriod={start}&endPeriod={end}&lang=en'
url_deficit_debt = 'https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/GOV_10DD_EDPT1/A.MIO_EUR+PC_GDP.S13.B9+GD.EU27_2020+EA19+BE+BG+CZ+DK+DE+EE+IE+EL+ES+FR+HR+IT+CY+LV+LT+LU+HU+MT+NL+AT+PL+PT+RO+SI+SK+FI+SE/?format=SDMX-CSV&startPeriod={start}&endPeriod={end}'
url_revenue = 'https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/GOV_10A_MAIN/A.MIO_EUR+PC_GDP.S13.B9+TE+TR.EU27_2020+EA20+EA19+BE+BG+CZ+DK+DE+EE+IE+EL+ES+FR+HR+IT+CY+LV+LT+LU+HU+MT+NL+AT+PL+PT+RO+SI+SK+FI+SE+IS+NO+CH/?format=SDMX-CSV&startPeriod={start}&endPeriod={end}'
url_gdp = 'https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/NAMA_10_GDP/A.CP_MEUR.B1GQ.DE+NO+RS+BE+FI+PT+BG+DK+LT+LU+HR+LV+FR+HU+SE+SI+UK+SK+ME+EU27_2020+IE+MK+EE+CH+EL+MT+IS+IT+AL+ES+AT+XK+CY+CZ+PL+RO+LI+NL+TR+BA/?format=SDMX-CSV&startPeriod={start}&endPeriod={end}'


def dataframed(url) :
    url_formated = url.format(start = StartPeriod, end = EndPeriod)
    # Lecture de l'URL
    data = pd.read_csv(url_formated,  sep=',')
    return data

expenditure = dataframed(url_expenditure)
deficit_debt = dataframed(url_deficit_debt)
revenue = dataframed(url_revenue)
gdp = dataframed(url_gdp)

# Sectorisation
sector = [s for s in expenditure.cofog99.unique() if len(s) == 4]

# Nettoyage
expenditure = expenditure[['unit', 'sector', 'cofog99','geo', 'TIME_PERIOD', 'OBS_VALUE']]
expenditure = expenditure[~expenditure.cofog99.isin(sector)]
deficit_debt = deficit_debt[['unit', 'na_item','geo', 'TIME_PERIOD', 'OBS_VALUE']]
revenue = revenue[['unit', 'na_item', 'geo', 'TIME_PERIOD', 'OBS_VALUE']]
gdp = gdp[['geo','TIME_PERIOD', 'OBS_VALUE']]

for s in sector : 
    filt = expenditure.cofog99.str.contains(s)
    expenditure.sector = np.where(filt, s, expenditure.sector)

dfs = [expenditure, deficit_debt, revenue, gdp]
for df in dfs:
    map_my_dataframe(df, codelist)

# Save new file in cache
dfs = [expenditure, deficit_debt, revenue, gdp]
filenames = ['expenditure', 'deficit_debt', 'revenue', 'gdp']
for df, name in zip(dfs, filenames):
    df.to_csv(f'data/{name}.csv', sep=';', index=False)


# new_file = io.StringIO(file_content)

# from Push2Github import *
# Push2Github(file_content, 'expenditure.csv', "updated expenditure data file")

