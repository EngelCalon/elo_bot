import discord
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
from datetime import datetime
from utils.elo import *

# Charger les variables du fichier .env
load_dotenv()
history_file = os.getenv("HISTORY_FILE")
players_elo_file = os.getenv("PLAYERS_ELO_FILE")
bot_seed = os.getenv("BOT_SEED")

if not os.path.exists(history_file):
    df = pd.DataFrame(columns=[ 'id',
                                'mode',
                               'team_A_p1', 'team_A_p1_pick',
                                'team_A_p2', 'team_A_p2_pick',
                                'team_A_p3', 'team_A_p3_pick',
                                'team_B_p1', 'team_B_p1_pick',
                                'team_B_p2', 'team_B_p2_pick',
                                'team_B_p3', 'team_B_p3_pick',
                                'date_time',
                                'result'])
    df.to_csv(history_file, index=False, sep= ';')


if not os.path.exists(players_elo_file):
    df = pd.DataFrame(columns=['id', 'player', 'general_elo', '1v1_elo', '2v2_elo', '3v3_elo', 'date_time'])
    df.to_csv(players_elo_file, index=False, sep= ';')

history = pd.read_csv(history_file)
players_elo = pd.read_csv(players_elo_file)

# def add_game(mode:str, teamA: list[str], teamB: list[str], result:bool):
#     new_row = {'id': history['id'].max() + 1,
#                'mode': mode,
#                'team_A_p1': teamA[0], 'team_A_p1_pick': 'random',
#                'team_A_p2': teamA[1], 'team_A_p2_pick': 'random',
#                'team_A_p3': teamA[2], 'team_A_p3_pick': 'random',
#                'team_B_p1': teamB[0], 'team_B_p1_pick': 'random',
#                'team_B_p2': teamB[1], 'team_B_p2_pick': 'random',
#                'team_B_p3': teamB[2], 'team_B_p3_pick': 'random',
#                'date_time': datetime.now(),
#                'result': result}
#     history = history.append(new_row, ignore_index=True)
#     history.to_csv(history_file, index=False, sep= ';')
#     return history

def get_player_elo(player: str, mode: str) -> float:
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

def set_player_elo(player: str, mode: str, new_elo: float, new_mod_elo: float):
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

def resolve_game(mode:str, teamA: list[str], teamB: list[str], result:bool):
    meanA = 0
    meanB = 0
    meanA_mod = 0
    meanB_mod = 0
    for player in teamA:
        meanA += get_player_elo(player, 'general')
        meanA_mod += get_player_elo(player, mode)
    for player in teamB:
        meanB += get_player_elo(player, 'general')
        meanB_mod += get_player_elo(player, mode)
    meanA /= len(teamA)
    meanB /= len(teamB)
    meanA_mod /= len(teamA)
    meanB_mod /= len(teamB)

    for player in teamA:
        mod_elo = get_player_elo(player, mode)
        general_elo = get_player_elo(player, 'general')
        new_mod_elo = get_new_rating(mod_elo, meanB_mod, result)
        new_elo = get_new_rating(general_elo, meanB, result)
        set_player_elo(player, mode, new_elo, new_mod_elo)

    for player in teamB:
        mod_elo = get_player_elo(player, mode)
        general_elo = get_player_elo(player, 'general')
        new_mod_elo = get_new_rating(mod_elo, meanA_mod, 1 -  result)
        new_elo = get_new_rating(general_elo, meanA, 1 - result)
        set_player_elo(player, mode, new_elo, new_mod_elo)
    
    return pd.read_csv(players_elo_file)


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
@client.event
async def on_ready():
    print("Je suis bien prêt !")

@client.event
async def on_message(message):
    if message.content.startswith("!elo"):
        parts = message.content.split(" ")
        if len(parts) != 4:
            await message.channel.send("Non d'un petit bonhomme!\n !elo @user1 @user2 result (1 si le joueur 1 gagne, 0 si le joueur 2 gagne)")
            return
        j1 = parts[1]
        j2 = parts[2]
        result = int(parts[3])
        if result != 0 and result != 1:
            await message.channel.send("Tu m'as pris pour un jambon ! Le résultat doit être 0 ou 1")
            return
        elo1 = 1000
        elo2= 1200
        j1_new_el = get_new_rating(elo1, elo2, result)
        j2_new_el = get_new_rating(elo2, elo1, 1 - result)
        await message.channel.send(f"Les nouveaux ELOs sont {j1_new_el} pour {j1} et {j2_new_el} pour {j2}")
        


client.run(bot_seed)

