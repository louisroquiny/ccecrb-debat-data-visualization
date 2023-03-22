# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 16:31:10 2023

@author: loro

This is a Python script that uses web scraping to extract economic data from the AMECO website of the European Commission. It imports necessary libraries such as pandas, datetime, requests, and BeautifulSoup.

The script defines an ameco function that takes a dataset parameter and scrapes the AMECO website to retrieve data related to the specified dataset. The resulting data is processed and returned in the form of a pandas DataFrame.

The script then uses a mapping dictionary to map long indicator labels to shorter ones, and applies the mapping to a DataFrame of the scraped data.

The final DataFrame is melted and transformed before being saved as a pickle file.


"""
import pandas as pd
from datetime import datetime as dt
import requests
from bs4 import BeautifulSoup


def ameco(dataset):
    fullvariable = dataset
    country = "ALB,AUT,BEL,BIH,BGR,HRV,CYP,CZE,DNK,EST,EU27,FIN,FRA,DEU,GRC,HUN,ISL,IRL,ITA,XKX,LVA,LIE,LTU,LUX,MLT,MNE,NLD,MKD,NOR,POL,PRT,ROU,SRB,SVK,SVN,ESP,SWE,CHE,GBR"
    years = ",".join(str(i) for i in range(2001, dt.now().year + 10))
    
    url = f"https://ec.europa.eu/economy_finance/ameco/wq/series?fullVariable={fullvariable}&countries={country}&years={years}&lastYear=1&yearOrder=DESC"
    
    # Get HTML content and parse it
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Extract table data and convert it to DataFrame
    table = soup.find("table")
    df = pd.read_html(str(table))[0]
    
    # Melt the DataFrame and drop missing values
    df_melt = df.melt(id_vars=['Country', 'Label', 'Unit'], var_name='year', value_name='value').dropna().reset_index(drop = True)
    
    return df_melt

datasets = "1.0.99.0.UVGD,1.0.99.0.URCG,1.0.99.0.UUCG,1.0.99.0.UDGG,1.0.99.0.UBLG"

data = ameco(datasets)

mapping = {
    'General government consolidated gross debt :- Excessive deficit procedure (based on ESA 2010)': 'debt',
    'Gross domestic product at current prices': 'gdp',
    'Total current revenue: general government :- ESA 2010': 'revenue',
    'Total current expenditure: general government :- ESA 2010': 'expenditure',
    'Net lending (+) or net borrowing (-): general government :- ESA 2010': 'deficit'
}

data['Label'] = data['Label'].map(mapping)

gdp = data[data.Label == 'gdp'][['Country', 'Label', 'year', 'value']]

merged_df = data.merge(gdp, on=['Country', 'year'], how='left')
data = data.assign(pc_gdp=merged_df['value_x']*100/merged_df['value_y'])

data.rename(columns={'value' : 'mrd'}, inplace = True)

data_ameco = data.melt(id_vars=['Country', 'Label', 'Unit', 'year'], var_name='unit', value_name='value').dropna().reset_index(drop = True).drop(columns = 'Unit')

data_ameco.to_pickle('data/data_ameco.pkl')