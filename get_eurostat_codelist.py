# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 10:10:49 2023

@author: loro
"""

def get_eurostat_codelist(links, json_name) :
    """
    Fonction qui permet de sauvegarder les codelist des dimensions eurostat 
    dans un fichier json. 
    
    links = list
    liste de fichiers reprenant les codelist des différentes dimensions 
    reprises dans les databases. 
    
    json_name = str
    direction + nom + .json 
    """
    
    # Enregistrement du dictionnaire dans un fichier JSON
    import json
    import pandas as pd
    
    meta = {}
    for link in links : 
        metadata = pd.read_csv(
            link, 
            sep = '\t',
            header = None, 
            index_col = 0)
        meta = meta | metadata.to_dict()[1]
    
    with open(json_name, "w") as f:
        json.dump(meta, f)
    
    return (print(json_name + ' sauvergardé'))
        