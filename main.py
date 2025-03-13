import discord
import pandas as pd

import os
from dotenv import load_dotenv

from utils.elo import *
from utils.players_elo import *

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

global history
history = pd.read_csv(history_file)
global players_elo
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


def resolve_game(mode:str, teamA: list[str], teamB: list[str], result:bool):
    meanA = 0
    meanB = 0
    meanA_mod = 0
    meanB_mod = 0
    for player in teamA:
        meanA += get_player_elo(player, 'general', players_elo)
        meanA_mod += get_player_elo(player, mode, players_elo)
    for player in teamB:
        meanB += get_player_elo(player, 'general', players_elo)
        meanB_mod += get_player_elo(player, mode, players_elo)
    meanA /= len(teamA)
    meanB /= len(teamB)
    meanA_mod /= len(teamA)
    meanB_mod /= len(teamB)

    for player in teamA:
        mod_elo = get_player_elo(player, mode, players_elo)
        general_elo = get_player_elo(player, 'general', players_elo)
        new_mod_elo = get_new_rating(mod_elo, meanB_mod, result)
        new_elo = get_new_rating(general_elo, meanB, result)
        set_player_elo(player, mode, new_elo, new_mod_elo, players_elo, players_elo_file)

    for player in teamB:
        mod_elo = get_player_elo(player, mode, players_elo)
        general_elo = get_player_elo(player, 'general', players_elo)
        new_mod_elo = get_new_rating(mod_elo, meanA_mod, 1 -  result)
        new_elo = get_new_rating(general_elo, meanA, 1 - result)
        set_player_elo(player, mode, new_elo, new_mod_elo, players_elo, players_elo_file)
    
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
        players_elo = resolve_game('1v1', [j1], [j2], result)
        await message.channel.send(f"Les nouveaux ELOs sont {get_player_elo(j1, 'general',players_elo)} pour {j1} et {get_player_elo(j2, 'general',players_elo)} pour {j2}")
        


client.run(bot_seed)

