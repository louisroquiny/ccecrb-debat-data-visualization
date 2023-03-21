# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 16:31:10 2023

@author: loro
"""
import pandas as pd
from datetime import datetime as dt

fullvariable = "1.1.0.0.OVGD,1.2.0.0.OVGD"
country = "ALB,AUT,BEL,BIH,BGR,HRV,CYP,CZE,DNK,EST,EU27,FIN,FRA,DEU,GRC,HUN,ISL,IRL,ITA,XKX,LVA,LIE,LTU,LUX,MLT,MNE,NLD,MKD,NOR,POL,PRT,ROU,SRB,SVK,SVN,ESP,SWE,CHE,GBR"
years = ",".join(str(i) for i in range(2001, dt.now().year + 4)

url = "https://ec.europa.eu/economy_finance/ameco/wq/series?fullVariable={}&countries={}&years={}&lastYear=0&yearOrder=DESC".format(fullvariable, country, years)

# Lire le tableau présent dans la page HTML
dfs = pd.read_html(url)

# Récupérer le premier tableau (dans ce cas, il n'y en a qu'un seul)
df = dfs[0]

# Melt du DataFrame
df_melt = df.melt(id_vars=['Country', 'Label', 'Unit'], var_name='year', value_name='value')
print(df_melt)



