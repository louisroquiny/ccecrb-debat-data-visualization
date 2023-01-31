# -*- coding: utf-8 -*-
"""
Created on Mon Jan 30 10:57:36 2023

@author: loro
"""

import pandas as pd
import numpy as np
import eurostat
from github import Github



def get_keys_of_dic(code, dims) : 
    for key in eurostat.get_sdmx_dic(code, dims).keys():
        print("'{}',".format(key))
    return

# Mapping functions
def get_metadata(code): 
    metadata = {}
    for i, dims in enumerate(eurostat.get_sdmx_dims(code)) :
        try : 
            metadata = metadata | eurostat.get_sdmx_dic(expenditure_code, dims)
        except TypeError : 
            metadata = metadata 
    return metadata
def map_my_dataframe(data, mapping) :
    for col in data.columns : 
        if col not in ['YEAR', 'VALUE'] : 
            data[col] = data[col].map(mapping)
        else : 
            pass
    return data

# Date scope
StartPeriod = 2001
EndPeriod = 2020

# Geo scope
GEO = [
       'AT',
       'BE',
       'BG',
       'CH',
       'CY',
       'CZ',
       'DE',
       'DK',
       'EE',
       'EL',
       'ES',
       'EU27_2020',
       'FI',
       'FR',
       'HR',
       'HU',
       'IE',
       'IS',
       'IT',
       'LT',
       'LU',
       'LV',
       'MT',
       'NL',
       'NO',
       'PL',
       'PT',
       'RO',
       'SE',
       'SI',
       'SK',]

# Data code
expenditure_code = 'gov_10a_exp'

# Getting metadata
metadata = get_metadata(expenditure_code)

# Filter pars
expenditure_filter = {
    'FREQ' : ['A'],
    'SECTOR' : ['S13'],
    'UNIT' : ['PC_GDP', 'MIO_EUR'],
    'NA_ITEM' : ['TE'], 
    'GEO' : GEO
    }

# Get data from eurostat
expenditure = eurostat.get_sdmx_data_df(
    expenditure_code, 
    StartPeriod, 
    EndPeriod, 
    expenditure_filter, 
    flags = False)

# Drop redundant colums
expenditure_proper = expenditure.drop(
    ['FREQ', 'NA_ITEM'], 
    axis = 1
    )

# Melting
expenditure_melted = expenditure_proper.melt(
    id_vars=['UNIT', 'COFOG99', 'GEO', 'SECTOR'], 
    var_name='YEAR', 
    value_name='VALUE'
    )

# Sectorisation
sector = []
for s in expenditure_melted.COFOG99.unique():
    if len(s) == 4 : 
        sector.append(s) 

# Nettoyage
expenditure = expenditure_melted[
    (~expenditure_melted.COFOG99.isin(sector))&(expenditure_melted.COFOG99 != 'TOTAL')
    ]
# expenditure = expenditure[expenditure.COFOG99 != 'TOTAL']

for s in sector : 
    filt = expenditure.COFOG99.str.contains(s)
    expenditure['SECTOR'] = np.where(filt, s, expenditure['SECTOR'])


map_my_dataframe(expenditure, metadata)

expenditure.to_csv('C:\\Users\loro.CCECRB\Documents\GitHub\expenditure.csv', sep = ';')

# # Upload to my github repository
# access_token = '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'
# g = Github(access_token)
# repo = g.get_repo()
# contents = repo.get_contents("/data/expenditure.csv")
# repo.update_file(contents.path, "updated expenditure data file", "more tests")

