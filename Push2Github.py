# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 11:34:25 2023

@author: loro
"""

def Push2Github(file_content, file_name, commit) : 
    
    from github import Github
    import json 
    
    #file_path = input("Entrez le chemin d'accès au fichier de credentials :")
    
    with open("C:\\Users\loro.CCECRB\Documents\credentials.json", "r") as file:
        credentials = json.load(file)
        
        TOKEN = credentials['token']
    
    access_token = TOKEN
    g = Github(access_token)
    repo = g.get_user().get_repo("treemap-ccecrb-debat")
    contents = repo.get_contents('data/' + file_name)
    repo.update_file(contents.path, commit, contents.sha, file_content)
    
    return str(file_name + ' updated')
    