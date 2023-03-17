# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 16:31:10 2023

@author: loro
"""
import pandas as pd

fullvariable = "1.1.0.0.OVGD,1.2.0.0.OVGD"
country = "AUT,BEL,BGR,CYP,CZE,DEU,DNK,EA19,EA20,ESP,EST,EU27,FIN,FRA,GRC,HRV,HUN,IRL,ITA,LTU,LUX,LVA,MLT,NLD,POL,PRT,ROM,SVK,SVN,SWE"
years = ",".join(str(i) for i in range(2001, 2025))

url = "https://ec.europa.eu/economy_finance/ameco/wq/series?fullVariable={}&countries={}&years={}&lastYear=0&yearOrder=DESC".format(fullvariable, country, years)

# Lire le tableau présent dans la page HTML
dfs = pd.read_html(url)

# Récupérer le premier tableau (dans ce cas, il n'y en a qu'un seul)
df = dfs[0]

# Melt du DataFrame
df_melt = df.melt(id_vars=['Country', 'Label', 'Unit'], var_name='year', value_name='value')
print(df_melt)



