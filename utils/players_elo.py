from datetime import datetime
import pandas as pd
from utils.elo import *


def get_player_elo(player: str, mode: str, players_elo: pd.DataFrame) -> float:
    if player not in players_elo['player'].values:
        return 1000
    player_row = players_elo[players_elo['player'] == player].sort_values('date_time').iloc[-1]
    if mode == '1v1':
        return player_row['1v1_elo']
    elif mode == '2v2':
        return player_row['2v2_elo']
    elif mode == '3v3':
        return player_row['3v3_elo']
    else:
        return player_row['general_elo']

def set_player_elo(player: str, mode: str, new_elo: float, new_mod_elo: float, players_elo: pd.DataFrame, players_elo_file:str):
    if player not in players_elo['player'].values:
        players_elo = players_elo.append({'id': players_elo['id'].max() +1 ,
                                          'player': player,
                                          'general_elo': 1000,
                                          '1v1_elo': 1000,
                                          '2v2_elo': 1000, 
                                          '3v3_elo': 1000, 
                                          'date_time': datetime.now()}, 
                                          ignore_index=True)

    player_row = players_elo[players_elo['player'] == player].sort_values('date_time').iloc[-1]
    new_row = player_row.copy()
    new_row['id'] = players_elo['id'].max() + 1
    new_row['date_time'] = datetime.now()
    new_row['general_elo'] = new_elo

    if mode == '1v1':
        new_row['1v1_elo'] = new_mod_elo    
    elif mode == '2v2':
        new_row['2v2_elo'] = new_mod_elo  
    elif mode == '3v3':
        new_row['3v3_elo'] = new_mod_elo 

    players_elo = players_elo.append(new_row)
    players_elo.to_csv(players_elo_file, index=False)
    return players_elo